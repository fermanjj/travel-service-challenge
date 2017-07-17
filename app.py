"""
Author: JJ Ferman (fermanjj@gmail.com)

Creates a price check endpoint that accepts a PNR
and returns price drops.

The endpoint will query the Java endpoints
to gather the data and determine price drops
and returns a list.

"""
from flask import (
    Flask, jsonify
)
from config import *
import requests
from urllib.parse import quote_plus
from parse import parse_flight_text
import logging
import sys
import json


app = Flask(__name__)
app.secret_key = APP_SECRET

# set up a logger to log to stdout
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOGGER.addHandler(ch)


def check_request_errors(r):
    """A func to check for errors on a given
    request and

    :param r: A request response object
    :return: boolean
    """
    try:
        r.raise_for_status()
        if r.status_code != 200:
            raise requests.HTTPError
    except requests.HTTPError:
        LOGGER.exception("Error on request")
        return False
    return True


def compare_prices(ticket, prices):
    """This function does the price compare
    based on the class of service. If the amount
    is lower, then it gets added to the output list.

    :param dict ticket: The ticket response from the Java endpoint
    :param list prices: The price response from the Java endpoint
    :return: A list of lower prices, if any
    """
    out = []
    for price in prices:
        if ticket['classOfService'] == price['classOfService']:
            if ticket['price']['amount'] > price['price']['amount']:
                out.append(price)
    return out


@app.route('/price-check/<string:pnr>')
def price_check(pnr):
    """Accepts a GET requests with a string
    of a PNR.

    Fetch a list of lower prices based on the PNR.

    :param str pnr: Passenger Name Record
    :return: json
    """
    # fetch the pnrs endpoint from the Java app
    # quote_plus the passed in PNR for security
    pnr_response = requests.get(
        JAVA_ENDPOINT + 'pnrs/{}'.format(
            quote_plus(pnr)
        ))

    json_return = {
        'pnr': pnr, 'message': 'success'
    }

    # check for errors
    # we could also return a different message
    # for errors
    if not check_request_errors(pnr_response):
        json_return['message'] = 'error on pnr request'
        return jsonify(json_return)

    if pnr_response.text == 'PNR NOT FOUND':
        json_return['message'] = 'PNR NOT FOUND'
        return jsonify(json_return)

    # parse the response
    try:
        parsed_pnr_response = parse_flight_text(pnr_response.text)
    except Exception:
        LOGGER.exception('Error on parsing PNR response')
        json_return['message'] = 'invalid PNR parse'
        return jsonify(json_return)
    print(parsed_pnr_response)

    # get the ticket data from the java endpoint
    tickets_response = requests.get(
        JAVA_ENDPOINT + 'tickets/{}'.format(
            parsed_pnr_response['ticket_number']
        ))
    # check for errors
    if not check_request_errors(tickets_response):
        json_return['message'] = 'error on tickets request'
        return jsonify(json_return)
    clean_tickets_response = json.loads(tickets_response.text)
    print(clean_tickets_response)

    # get the prices based on the pnr parsed response
    # build the post request
    price_post_data = []
    for x in parsed_pnr_response['segments']:
        price_post_data.append({
            'departureDate': x['departure_date'],
            'flightNumber': x['flight_number'],
            'origin': x['origin'],
            'destination': x['destination']
        })

    price_response = requests.post(
        JAVA_ENDPOINT + 'price', json=price_post_data
    )
    # check for errors
    if not check_request_errors(price_response):
        json_return['message'] = 'error on price request'
        return jsonify(json_return)
    clean_price_response = json.loads(price_response.text)
    print(clean_price_response)

    # do the price compare
    try:
        lower_prices = compare_prices(
            clean_tickets_response, clean_price_response)
    except Exception:
        LOGGER.exception("Error on price compare")
        json_return['message'] = 'error on price compare'
        return jsonify(json_return)
    json_return['lower_prices'] = lower_prices

    return jsonify(json_return)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
