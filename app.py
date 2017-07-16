"""
Author: JJ Ferman (fermanjj@gmail.com)

This is a few endpoints implemented in the
Flask web framework to receive PNRs and
determine price drops on similar or exact
flights.

"""
from flask import (
    Flask, jsonify
)
from config import *


app = Flask(__name__)
app.secret_key = APP_SECRET


@app.route('/pnrs/<string:pnr>')
def pnrs(pnr):
    """Accepts a GET requests with a string
    of a PNR.
    Currently just returns the passed in PNR.

    :param str pnr: Passenger Name Record
    :return: pnr
    """
    return jsonify(pnr)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
