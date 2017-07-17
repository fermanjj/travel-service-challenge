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
    json_return = {
        'pnr': pnr, 'message': 'success'
    }

    try:
        # fetch the pnrs endpoint from the Java app
        # quote_plus the passed in PNR for security
        pnr_response = requests.get(
            JAVA_ENDPOINT + 'pnrs/{}'.format(
                quote_plus(pnr)
            ))
        if pnr_response.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        LOGGER.exception('Request exception')
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
        LOGGER.debug('PNR response text: %s', pnr_response.text)
        json_return['message'] = 'invalid PNR parse'
        return jsonify(json_return)

    try:
        # get the ticket data from the java endpoint
        tickets_response = requests.get(
            JAVA_ENDPOINT + 'tickets/{}'.format(
                parsed_pnr_response['ticket_number']
            ))
        if tickets_response.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        json_return['message'] = 'error on tickets request'
        return jsonify(json_return)
    ticket_response_json = json.loads(tickets_response.text)

    # build the post request for the pricing
    price_post_data = []
    for x in parsed_pnr_response['segments']:
        price_post_data.append({
            'departureDate': x['departure_date'],
            'flightNumber': x['flight_number'],
            'origin': x['origin'],
            'destination': x['destination']
        })

    try:
        # get the prices based on the pnr parsed response
        price_response = requests.post(
            JAVA_ENDPOINT + 'price', json=price_post_data
        )
        if price_response.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        json_return['message'] = 'error on price request'
        return jsonify(json_return)

    price_response_json = json.loads(price_response.text)

    # do the price compare
    try:
        lower_prices = compare_prices(
            ticket_response_json, price_response_json)
    except Exception:
        LOGGER.exception("Error on price compare")
        LOGGER.debug("ticket_json: %s\nprice_json: %s",
                     (ticket_response_json, price_response_json))
        json_return['message'] = 'error on price compare'
        return jsonify(json_return)
    json_return['lower_prices'] = lower_prices

    return jsonify(json_return)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
