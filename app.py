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
from requests import get, HTTPError
from urllib.parse import quote_plus
import re


app = Flask(__name__)
app.secret_key = APP_SECRET


def parse_flight_text(data):
    """Parses the text from the pnrs endpoint.

    :param str data: The payload from the Java pnrs request
    :return: A dict of the flight data parsed out.
    """
    # parse the ticket number using regex
    ticket_number = re.search(
        r'[1-9][0-9]*\. AS ([0-9]{13})', data).group(1)

    # parse the flight segments using regex
    segments = re.findall(r'[a-z]\.(.*)$', data)

    # create an output dict
    output = {'ticket_number': ticket_number, 'segments': []}

    # iterate over the segments, parsing them
    for segment in segments:
        seg_dict = {}
        # clean the segment to just have single spaces
        seg_clean = re.sub(' +', ' ', segment).strip()

        # split the segment by spaces and assign values
        seg_split = seg_clean.split()
        seg_dict['flight_number'] = seg_split[0]
        seg_dict['departure_date'] = seg_split[1]
        seg_dict['origin_destination'] = seg_split[2]
        seg_dict['segment_status'] = seg_split[3]
        seg_dict['departure_time'] = seg_split[4]
        seg_dict['arrival_time'] = seg_split[5]
        seg_dict['fare_ladder'] = seg_split[6]

        # split up origin and destination
        seg_dict['origin'] = seg_dict['origin_destination'][:3]
        seg_dict['destination'] = seg_dict['origin_destination'][3:]

        output['segments'].append(seg_dict)

    return output


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
    r = get(
        'http://localhost:8080/pnrs/{}'.format(
            quote_plus(pnr)
        ))

    json_return = {
        'pnr': pnr, 'message': 'success'
    }

    # check for errors
    # we could also return a different message
    # for errors
    try:
        r.raise_for_status()
    except HTTPError:
        json_return['message'] = 'PNR NOT FOUND'
        return jsonify(json_return)
    if r.status_code != 200:
        json_return['message'] = 'PNR NOT FOUND'
        return jsonify(json_return)
    if r.text == 'PNR NOT FOUND':
        json_return['message'] = 'PNR NOT FOUND'
        return jsonify(json_return)

    parsed_response = parse_flight_text(r.text)
    print(parsed_response)

    return jsonify(json_return)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
