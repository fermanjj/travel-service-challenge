import unittest
import requests
from config import *
import json
from parse import parse_flight_text
from app import compare_prices

APP_PROTOCOL = 'http'
APP_URL = 'localhost'
APP_PORT = PORT
APP_ENDPOINT = (
    APP_PROTOCOL + '://' +
    APP_URL + ':' + str(APP_PORT) + '/'
)


class TestApp(unittest.TestCase):
    """Runs a few test cases."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_main_response(self):
        # check that the ABC123 is successful
        r = requests.get(APP_ENDPOINT + 'price-check/ABC123')

        j = json.loads(r.text)

        assert j['message'] == 'success'

    def test_price_compare(self):
        # check that tickets with a higher price than the
        # prices get added and returned
        ticket = {
            'classOfService': 'BUSINESS',
            'price': {'amount': 2500}
        }
        prices = [
            {'classOfService': 'BUSINESS',
                'price': {'amount': 2600}},
            {'classOfService': 'ECONOMY',
                'price': {'amount': 240}},
            {'classOfService': 'BUSINESS',
                'price': {'amount': 2400}},
            {'classOfService': 'BUSINESS',
                'price': {'amount': 2300}}
        ]
        compare = compare_prices(ticket, prices)
        assert len(compare) == 2

        compare2 = compare_prices(ticket, prices[:-2])
        assert len(compare2) == 0

    def test_parsing(self):
        # this should have 3 segments parsed out
        s = """
              RECLOC: ABC123
              FLIGHTS:
              1. AS 0277850344766
                  a. 487K 10OCT SEALAX HK1   250P  535P /DCAS*HJQTEX /E*
                  b. 486T 18OCT LAXSEA HK1   230P  513P /DCAS*HJQTEX /E*l
                  c. 486T 18OCT LAXSEA HK1   230P  513P /DCAS*HJQTEX /E*l
        """
        parsed = parse_flight_text(s)

        assert len(parsed['segments']) == 3

        # This should only have 2 segments parsed out because of the regex
        # It's not expecting numbers to precede flight segments
        s = """
              RECLOC: ABC123
              FLIGHTS:
              1. AS 0277850344766
                  a. 487K 10OCT SEALAX HK1   250P  535P /DCAS*HJQTEX /E*
                  1. 486T 18OCT LAXSEA HK1   230P  513P /DCAS*HJQTEX /E*l
                  c. 486T 18OCT LAXSEA HK1   230P  513P /DCAS*HJQTEX /E*l
        """
        parsed = parse_flight_text(s)

        assert len(parsed['segments']) == 2

        # this should error because there's no text
        try:
            parse_flight_text('')
        except Exception:
            pass
        else:
            raise Exception('incorrect parse job')

if __name__ == '__main__':
    unittest.main()
