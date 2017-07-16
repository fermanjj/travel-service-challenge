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
from requests import get, HTTPError
from urllib.parse import quote_plus


app = Flask(__name__)
app.secret_key = APP_SECRET


@app.route('/pnrs/<string:pnr>')
def pnrs(pnr):
    """Accepts a GET requests with a string
    of a PNR.

    The idea here is to call the Java app's PNR
    endpoint and fetch what it would fetch.

    :param str pnr: Passenger Name Record
    :return: The result from the Java app or
        'PNR NOT FOUND'
    """
    # fetch the endpoint from the Java app
    # quote_plus the passed in PNR for security
    r = get(
        'http://localhost:8080/pnrs/{}'.format(
            quote_plus(pnr)
        ))

    # check for errors
    # we could also return a different message
    # for errors
    try:
        r.raise_for_status()
    except HTTPError:
        return 'PNR NOT FOUND'
    if r.status_code != 200:
        return 'PNR NOT FOUND'

    return r.text


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
