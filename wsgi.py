"""
WSGI entry point for the Flask application.
"""

from app import app  # Replace 'app' with the name of your main Flask file or package

application = app

if __name__ == "__main__":
    app.run()
