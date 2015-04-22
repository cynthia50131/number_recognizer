import unittest
import json
from tornado.testing import AsyncHTTPTestCase
import server


class BaseTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return server.Application()

    def decode_body(self, response):
        encode_type = "UTF-8"
        content_type = response.headers["Content-Type"]
        charset_part = "charset="
        charset_index = content_type.lower().find(charset_part)
        if charset_index > 0:
            encode_type = content_type[(charset_index + len(charset_part)):]
            encode_type = encode_type.split(";")[0]
        decoded = response.body.decode(encode_type)
        return decoded


class TestPredictionHandler(BaseTestCase):

    def test_predict(self):
        body = json.dumps({"data": [0] * 64})
        response = self.fetch("/predict", method="POST", body=body)
        r_body = self.decode_body(response)
        r_body_json = json.loads(r_body)

        self.assertTrue("result" in r_body_json)
        self.assertTrue(r_body_json["result"].isdigit())


class TestFeedbackHandler(BaseTestCase):

    def test_feedback(self):
        body = json.dumps({"data": [0] * 65})
        response = self.fetch("/feedback", method="POST", body=body)
        r_body = self.decode_body(response)
        print(r_body)
        r_body_json = json.loads(r_body)

        self.assertTrue("result" in r_body_json)
        self.assertFalse(r_body_json["result"])
