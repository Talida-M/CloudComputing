from flask import Flask, jsonify, session, redirect, url_for, request, render_template, flash
import requests
import jwt

bookMicroservUrl = 'http://book-microservices:8000'  # Added http:// to the URL
reviewMicroservUrl = 'http://review-microservices:8000'
userMicroservUrl = 'http://user-microservices:8000'

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
                return redirect(url_for('home'))  # Redirect to home page
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

@app.route('/books')
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


@app.route('/m')
@login_required
def home():
    try:
        # Make a GET request to fetch books
        response = requests.get(f'{bookMicroservUrl}/api/book/')
        response.raise_for_status()  # Raise an exception for HTTP errors
        books = response.json()  # Parse the JSON response
        return render_template('booksView.html', books=books)
        #return jsonify(books)  # Return the books as JSON
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return jsonify({'error': str(e)}), 500

@app.route('/search-book', methods=['GET', 'POST'])
@login_required
def search_book():
    if request.method == 'POST':
        book_name = request.form.get('book_name')
        book_id = request.form.get('book_id')
        if not book_name:
            return render_template('search_book.html', error="Please select a book name.",book_name=book_name)

        try:
                # Call the BookMicroservice to get details of the selected book
            response = requests.get(f'{bookMicroservUrl}/api/book/byid/{book_id}')
            if response.status_code == 200:
                book_details = response.json()

                review_response = requests.get(f'{reviewMicroservUrl}/api/review/{book_id}')
                reviews = []
                if review_response.status_code == 200:
                    reviews = review_response.json()


                return render_template('search_book.html', book_details=book_details,book_name=book_name,reviews=reviews)
            else:
                return render_template('register.html')
                # return render_template('search_book.html', error="Book not found.",book_name=book_name)
        except requests.exceptions.RequestException as e:
            return render_template('search_book.html', error=str(e),book_name=book_name)

    # Render the search page for GET requests
    return render_template('search_book.html',book_name="")


@app.route('/submit-review', methods=['POST'])
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
    if not idbook or not rating or not comment:
       flash("All fields are required.","error")

        # Call the ReviewMicroservice to submit the review
    try:
        review_payload = {
            'iduser': iduser,
            'idbook': idbook,
            'rating': int(rating),
            'comment': comment
        }
        response = requests.post(f'{reviewMicroservUrl}/api/reviews', json=review_payload)
        if response.status_code == 200:
            flash("Review submitted successfully!", "success")
            return redirect(url_for('search_book'))
        else:
            flash("Failed to submit the review.", "error")

    except requests.exceptions.RequestException as e:
        flash("Caution.", "error")

if __name__ == '__main__':
    app.run(debug=True)
