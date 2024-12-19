from flask import Flask, jsonify, session, redirect, url_for, request, render_template
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
    book_details = None
    error_message = None
    if request.method == 'POST':
        book_name = request.form.get('book_name')
        if not book_name:
            return render_template('search_book.html', error="Please select a book name.",book_name=book_name)

        try:
                # Call the BookMicroservice to get details of the selected book
            response = requests.get(f'{bookMicroservUrl}/api/book/{book_name}')
            if response.status_code == 200:
                book_details = response.json()
                return render_template('search_book.html', book_details=book_details,book_name=book_name)
            else:
                return render_template('search_book.html', error="Book not found.",book_name=book_name)
        except requests.exceptions.RequestException as e:
            return render_template('search_book.html', error=str(e),book_name=book_name)

    # Render the search page for GET requests
    return render_template('search_book.html',book_name="")


if __name__ == '__main__':
    app.run(debug=True)
