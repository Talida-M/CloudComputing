from flask import Flask, jsonify
import requests

bookMicroservUrl = 'http://book-microservices:8000'  # Added http:// to the URL
reviewMicroservUrl = 'http://review-microservices:8000'
userMicroservUrl = 'http://user-microservices:8000'

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # Make a GET request to fetch books
        response = requests.get(f'{bookMicroservUrl}/api/book/')
        response.raise_for_status()  # Raise an exception for HTTP errors
        books = response.json()  # Parse the JSON response
        return jsonify(books)  # Return the books as JSON
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
