import os

DEBUG = True  # MUST set to False for production
PORT = 5000  # set to whatever available port you'd like
APP_SECRET = os.urandom(24)  # creates a secret key at runtime

JAVA_PROTOCOL = 'http'
JAVA_URL = 'localhost'
JAVA_PORT = 8080

JAVA_ENDPOINT = (
    JAVA_PROTOCOL + '://' +
    JAVA_URL + str(JAVA_PORT) + '/'
)
