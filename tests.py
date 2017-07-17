import unittest
import requests
from config import *
import json
from parse import parse_flight_text

APP_PROTOCOL = 'http'
APP_URL = 'localhost'
APP_PORT = PORT
APP_ENDPOINT = (
    APP_PROTOCOL + '://' +
    APP_URL + ':' + str(APP_PORT) + '/'
)


class TestApp(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_main_response(self):
        r = requests.get(APP_ENDPOINT + 'price-check/ABC123')

        j = json.loads(r.text)

        assert j['message'] == 'success'

    def test_parsing(self):
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

        try:
            parse_flight_text('')
        except Exception:
            pass
        else:
            raise Exception('incorrect parse job')

if __name__ == '__main__':
    unittest.main()
