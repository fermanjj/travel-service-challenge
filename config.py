import os

DEBUG = True  # MUST set to False for production
PORT = 5000  # set to whatever available port you'd like
APP_SECRET = os.urandom(24)  # creates a secret key at runtime
