from flask import (
    Flask, jsonify
)
from config import *


app = Flask(__name__)
app.secret_key = APP_SECRET


@app.route('/prns/')
def prns():
    return jsonify({})


if __name__ == '__main__':
    app(debug=DEBUG, port=PORT)
