from datetime import datetime

from flask import Flask, jsonify, session, redirect, url_for, request, render_template, flash,make_response
import requests
import jwt
import uuid
bookMicroservUrl = 'http://book-microservices:8000'  # Added http:// to the URL
reviewMicroservUrl = 'http://review-microservices:8000'
userMicroservUrl = 'http://user-microservices:8000'
orderApiMicroservUrl = 'http://order-microservice-api:8000'
import logging
from logging.handlers import SysLogHandler
syslog_host = 'syslog-ng'
syslog_port = 514
logger = logging.getLogger('book_microservice')
logger.setLevel(logging.INFO)


syslog_handler = SysLogHandler(address=(syslog_host, syslog_port))
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if the data is from a form or JSON payload
        if request.form:
            # Form data submission (from HTML form)
            user_data = {
                "name": request.form.get('name'),
                "email": request.form.get('email'),
                "password": request.form.get('password'),
            }
        elif request.json:
            # JSON data submission (from an API client like Postman)
            user_data = request.json
        else:
            return jsonify({'error': 'Invalid input format'}), 400

        try:
            # Forward the data to the user-microservices register endpoint
            response = requests.post(f'{userMicroservUrl}/api/register', json=user_data)
            return redirect(url_for('login'))
            #return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500

    # For GET requests, render the registration form
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if the data is from a form or JSON payload
        if request.form:
            # Form data submission (from HTML form)
            login_data = {
                "email": request.form.get('email'),
                "password": request.form.get('password'),
            }
        elif request.json:
            # JSON data submission (from an API client like Postman)
            login_data = request.json
        else:
            return jsonify({'error': 'Invalid input format'}), 400

        try:
            # Forward the data to the user-microservices login endpoint
            response = requests.post(f'{userMicroservUrl}/api/login', json=login_data)
            if response.status_code == 200:
                print(response.json().get('access_token'))
                # Extract access token and save it in session
                session['token'] = response.json().get('access_token')

                #creare trace_id
                trace_id = str(uuid.uuid4())
                response1 = make_response(redirect(url_for('home')))
                response1.set_cookie('trace_id', trace_id, httponly=True)

                return response1  # Return the response with the cookie set

                # return redirect(url_for('home'))  # Redirect to home page
            else:
                return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500

    # For GET requests, render the login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session to log out the user
    session.pop('token', None)
    return redirect(url_for('login'))  # Redirect to login page


def login_required(f):
    def wrapper(*args, **kwargs):
        token = session.get('token')
        print(token)
        if not token:
            return redirect(url_for('login'))  # Redirect to login page if no token

        try:
            # Decode the token
            jwt.decode(token, '12345678910', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))  # Redirect if the token has expired
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))  # Redirect if the token is invalid

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/books') # NU BARA MENIU este pentru acel dropdown cand cauti o carte dupa nume
@login_required
def books():
    try:
        # Make a GET request to fetch books
        response = requests.get(f'{bookMicroservUrl}/api/book/')
        response.raise_for_status()  # Raise an exception for HTTP errors
        books = response.json()  # Parse the JSON response

        return jsonify(books)  # Return the books as JSON
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return jsonify({'error': str(e)}), 500


@app.route('/m') #afiseaza toate cartile existente
@login_required
def home():
    token = session.get('token')

    trace_id = request.cookies.get('trace_id')


    if not token:
        return redirect(url_for('login'))
    try:
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')  # Extract user_id from the payload
        headers = {'X-Trace-ID': trace_id,'Id-User': iduser}
        #stop token

        response1 = requests.post(f'{orderApiMicroservUrl}/api/order/{iduser}',data=None,headers=headers)

        if response1.status_code == 200:
            try:
                # Try to parse JSON response
                data = response1.json()
                # if 'idorder' in data:
                #     flash(data['idorder'], "success")
                # else:
                #     flash('No idorder found in response.', "error")
            except ValueError as e:
                # Handle JSON parsing error
                flash('Failed to parse JSON response from Order Microservice.', "error")
        else:
            flash(f'Error: {response1.status_code} - {response1.text}', "error")
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))
    try:
        # Make a GET request to fetch books
        response = requests.get(f'{bookMicroservUrl}/api/book/',data=None,headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        books = response.json()  # Parse the JSON response
        return render_template('booksView.html', books=books)
        #return jsonify(books)  # Return the books as JSON
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return jsonify({'error': str(e)}), 500

@app.route('/search-book', methods=['GET', 'POST']) #cauta o carte dupa nume si te lasa sa vezi si reviewurile cartii plus ai camp de adaugare review in html
@login_required
def search_book():
    global idorder
    trace_id = request.cookies.get('trace_id')
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    try:
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')  # Extract user_id from the payload
        headers = {'X-Trace-ID': trace_id}
        response1 = requests.post(f'{orderApiMicroservUrl}/api/order/{iduser}',data=None,headers=headers)
        if response1.status_code == 200:
            idorder = response1.json().get('idorder')
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))

    if request.method == 'POST':
        book_name = request.form.get('book_name')
        book_id = request.form.get('book_id')
        if not book_name:
            return render_template('search_book.html', error="Please select a book name.",book_name=book_name)

        try:
            headers1 = {'X-Trace-ID': trace_id, 'Id-User': iduser}
                # Call the BookMicroservice to get details of the selected book
            response = requests.get(f'{bookMicroservUrl}/api/book/byid/{book_id}',data=None,headers=headers1)
            if response.status_code == 200: #daca exista cartea cu acel id
                book_details = response.json()

                review_response = requests.get(f'{reviewMicroservUrl}/api/review/{book_id}',data=None,headers=headers1)
                reviews = []
                if review_response.status_code == 200:
                    reviews = review_response.json()


                return render_template('search_book.html', book_details=book_details,book_name=book_name,reviews=reviews,idorder=idorder,iduser=iduser,trace_id=trace_id)
            else:
                logger.error({
                    "date": datetime.today().date().isoformat(),
                    "user-id": iduser,
                    "trace_id": trace_id,
                    "message": f"book not found {book_name}"
                })
                return render_template('register.html')
                # return render_template('search_book.html', error="Book not found.",book_name=book_name)
        except requests.exceptions.RequestException as e:
            return render_template('search_book.html', error=str(e),book_name=book_name)

    # Render the search page for GET requests
    return render_template('search_book.html',book_name="")


@app.route('/submit-review', methods=['POST'])# # NU BARA MENIU pentru a trimite review-ul creat
@login_required
def submit_review():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    try:
        # Decode the token to extract user information
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')  # Extract user_id from the payload
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))

    idbook = request.form.get('idbook')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    trace_id = request.cookies.get('trace_id')
    if not idbook or not rating or not comment:
       flash("All fields are required.","error")

        # Call the ReviewMicroservice to submit the review
    try:
        review_payload = {
            'iduser': iduser,
            'idbook': idbook,
            'rating': int(rating),
            'comment': comment,
            'trace_id':trace_id # adaguaaat acuuuuum
        }
        response = requests.post(f'{reviewMicroservUrl}/api/reviews', json=review_payload)
        if response.status_code == 200:
            flash("Review submitted successfully!", "success")
            return redirect(url_for('search_book')) #pastrati asa
        else:
            flash("Failed to submit the review.", "error")

    except requests.exceptions.RequestException as e:
        flash("Caution.", "error")

@app.route('/add-to-order', methods=['POST']) ## NU BARA MENIU
@login_required
def add_to_order():
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.json
    idbook = data.get('idbook')
    idorder = data.get('idorder')
    price = data.get('price')
    name = data.get('name')

    if not all([idbook, idorder, price, name]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Forward the request to the OrderMicroservice
    try:
        trace_id = request.cookies.get('trace_id')
        headers = {'X-Trace-ID': trace_id, 'Id-User': iduser}
        response = requests.post(
            f'{orderApiMicroservUrl}/api/order/add/{idbook}/{idorder}/{price}/{name}'
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Book added to order successfully'}), 200



@app.route('/order',methods=['POST','GET'])## NU BARA MENIU
@login_required
def my_order():
    # Render the order.html template
    global order
    trace_id = request.cookies.get('trace_id')
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    try:
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')
        headers = {'X-Trace-ID': trace_id}
        response = requests.post(f'{orderApiMicroservUrl}/api/order/{iduser}',data=None,headers=headers)
        if response.status_code == 200:
            order = response.json()
            return render_template('order.html', order=order)
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))
    return render_template('order.html',order=order)




@app.route('/add-book', methods=['POST'])# NU BARA MENIU
@login_required
def add_book_to_order():
    token = session.get('token')
    payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
    iduser = payload.get('iduser')

    data = request.json
    idbook = data.get('idbook')
    idorder = data.get('idorder')
    price = data.get('price')
    name = data.get('name')

    # if response.status_code == 200:
    #     flash("Book added to order successfully.", "success")
    #
    # else:
    #     flash("Failed to add book to order.", "error")
    try:
        trace_id = request.cookies.get('trace_id')
        headers = {'X-Trace-ID': trace_id, 'Id-User': iduser}
        response = requests.post(
            f'{orderApiMicroservUrl}/api/order/add/{idbook}/{idorder}/{price}/{name}',data = None, headers = headers
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Book added to order successfully'}), 200


@app.route('/remove-book', methods=['DELETE'])# NU BARA MENIU
@login_required
def remove_book_from_order():
    token = session.get('token')
    payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
    iduser = payload.get('iduser')

    data = request.json
    idbook = data.get('idbook')
    idorder = data.get('idorder')
    try:
        trace_id = request.cookies.get('trace_id')
        headers = {'X-Trace-ID': trace_id, 'Id-User': iduser}
        response = requests.delete(
            f'{orderApiMicroservUrl}/api/order/remove/{idbook}/{idorder}',data = None, headers = headers
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Book added to order successfully'}), 200


@app.route('/decrem-book', methods=['DELETE'])# NU BARA MENIU
@login_required
def decrement_book_from_order():
    token = session.get('token')
    payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
    iduser = payload.get('iduser')

    data = request.json
    idbook = data.get('idbook')
    idorder = data.get('idorder')
    try:
        trace_id = request.cookies.get('trace_id')
        headers = {'X-Trace-ID': trace_id, 'Id-User': iduser}
        response = requests.delete(
            f'{orderApiMicroservUrl}/api/order/decrem/{idbook}/{idorder}',data = None, headers = headers
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Book added to order successfully'}), 200


########new it will be on click sent button
@app.route('/sent',methods=['PUT'])# NU BARA MENIU
@login_required
def sent_order(): #when click
    trace_id = request.cookies.get('trace_id')
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    try:
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')  # Extract user_id from the payload
        headers = {'X-Trace-ID': trace_id}
        response = requests.put(f'{orderApiMicroservUrl}/api/order/pending/{iduser}',data = None, headers = headers)
        if response.status_code == 200:
            order = response.json()
            requests.put(f'{orderApiMicroservUrl}/api/order/send/{iduser}',data = None, headers = headers)
            return {"message": "Order sent successfully"}, 200  # Return a JSON response
        else:
            return {"error": "Failed to update order status"}, response.status_code
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))
    except Exception as e:
        return {"error": str(e)}, 500  # Handle unexpected errors
    # return redirect(url_for('home'))

#
@app.route('/allorders',methods=['POST','GET']) #afiseaza toate orderurile
@login_required
def all_pending_success_orders():
    global orders
    trace_id = request.cookies.get('trace_id')
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    try:
        payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
        iduser = payload.get('iduser')  # Extract user_id from the payload
        headers = {'X-Trace-ID': trace_id}
        response = requests.get(f'{orderApiMicroservUrl}/api/order/allorders/{iduser}',data = None, headers = headers)

        if response.status_code == 200:
            orders = response.json()
            return render_template('allorders.html', orders=orders)
    except jwt.InvalidTokenError:
        return redirect(url_for('login'))
    return render_template('allorders.html', orders=orders)

# @app.route('/latest-orders', methods=['GET'])
# @login_required
# def all_pending_success_orders():
#     token = session.get('token')
#     if not token:
#         return redirect(url_for('login'))
#     try:
#         payload = jwt.decode(token, '12345678910', algorithms=['HS256'])
#         iduser = payload.get('iduser')
#
#         response = requests.get(f'{orderApiMicroservUrl}/api/order/allorders/{iduser}')
#         if response.status_code == 200:
#             orders = response.json()
#             return render_template('allorders.html', orders=orders)
#         else:
#             return jsonify({'error': 'Failed to fetch book details'}), 500
#
#     except Exception as e:
#         return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500



    #             for ord in orders:
    #                 for detail in ord.get('order_orderdetails', []):
    #                     idbook = detail.get('idbook')
    #
    #                     response1 = requests.get(f'{bookMicroservUrl}/api/book/byid/{idbook}')
    #                     if response1.status_code==200:
    #                         book = response1.json()
    #                         detail['idbook'] = book.get('name')
    #             return render_template('allorders.html', orders=orders)
    #         except ValueError as e:
    #             return jsonify({'error': 'Error parsing JSON response from API'}), 500
    #     else:
    #         return jsonify({'error': 'Failed to fetch orders', 'status_code': response.status_code}), 500
    # except requests.exceptions.RequestException as e:
    #     return jsonify({'error': f'Request failed: {str(e)}'}), 500
    # except jwt.InvalidTokenError:
    #     return redirect(url_for('login'))
    # except Exception as e:
    #     return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
