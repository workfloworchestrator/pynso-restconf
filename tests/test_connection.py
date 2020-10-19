# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest

import requests
import requests_mock

from pynso.connection import NSOConnection, _format_url


class TestConnection(unittest.TestCase):
    test_error = {"errors": {"error": [{"error-message": "test"}]}}

    def setUp(self):
        self.connection = NSOConnection("test.com", "test", "test", False)
        self.adapter = requests_mock.Adapter()
        self.connection.session.mount("http://test.com/", self.adapter)

    def test_url_format(self):
        self.assertEqual(
            _format_url(
                host="test.com",
                root="restconf",
                data_store="data",
                path="foo/bar",
            ),
            "https://test.com/restconf/data/foo/bar",
        )

    def test_url_format_http(self):
        self.assertEqual(
            _format_url(
                host="test.com",
                root="restconf",
                data_store="data",
                path="foo/bar",
                ssl=False,
            ),
            "http://test.com/restconf/data/foo/bar",
        )

    def test_url_format_http_no_path(self):
        self.assertEqual(
            _format_url(
                host="test.com",
                root="restconf",
                data_store="data",
                path=None,
                ssl=False,
            ),
            "http://test.com/restconf/data",
        )

    def test_url_format_base(self):
        self.assertEqual(
            _format_url(host="test.com", root="restconf", data_store=None, path=None, ssl=True),
            "https://test.com/restconf",
        )

    def test_url_format_path_(self):
        self.assertEqual(
            _format_url(host="test.com", root="restconf", data_store=None, path="foo/bar", ssl=True),
            "https://test.com/restconf/foo/bar",
        )

    def test_get(self):
        test = {"a": "b"}
        self.adapter.register_uri("GET", "/restconf/data", json=test, status_code=200)
        response = self.connection.get(
            "data",
        )
        self.assertEqual(test["a"], response["a"])

    def test_get_error(self):
        self.adapter.register_uri("GET", "/restconf/data", json=self.test_error, status_code=404)
        with self.assertRaises(requests.HTTPError):
            self.connection.get(
                "data",
            )

    def test_get_error_plain(self):
        self.adapter.register_uri("GET", "/restconf/data", text="should be json", status_code=200)
        with self.assertRaises(json.decoder.JSONDecodeError):
            self.connection.get(
                "data",
            )

    def test_head(self):
        self.adapter.register_uri("HEAD", "/restconf/data", status_code=200)
        response = self.connection.head(
            "data",
        )
        self.assertIsNone(response)

    def test_head_error(self):
        self.adapter.register_uri("HEAD", "/restconf/data", json=self.test_error, status_code=500)
        with self.assertRaises(requests.HTTPError):
            self.connection.head(
                "data",
            )

    def test_put(self):
        test = {"a": "b"}
        self.adapter.register_uri("PUT", "/restconf/data", json=test, status_code=200)
        response = self.connection.put("data", data={"test": "data"})
        self.assertEqual(test, response)

    def test_put_created(self):
        test = {"a": "b"}
        self.adapter.register_uri("PUT", "/restconf/data", json=test, status_code=201)
        response = self.connection.put("data", data={"test": "data"})
        self.assertIsNone(response)

    def test_put_no_response(self):
        self.adapter.register_uri("PUT", "/restconf/data", status_code=204)
        response = self.connection.put("data", data={"test": "data"})
        self.assertIsNone(response)

    def test_put_error(self):
        self.adapter.register_uri("PUT", "/restconf/data", json=self.test_error, status_code=404)
        with self.assertRaises(requests.HTTPError):
            self.connection.put("data", data={"test": "data"})

    def test_patch(self):
        self.adapter.register_uri("PATCH", "/restconf/data", status_code=204)
        response = self.connection.patch("data", data={"test": "data"})
        self.assertIsNone(response)

    def test_patch_error(self):
        self.adapter.register_uri("PATCH", "/restconf/data", json=self.test_error, status_code=404)
        with self.assertRaises(requests.HTTPError):
            self.connection.patch("data", data={"test": "data"})

    def test_delete(self):
        self.adapter.register_uri("DELETE", "/restconf/data", status_code=204)
        response = self.connection.delete("data", data={"test": "data"})
        self.assertIsNone(response)

    def test_delete_error(self):
        self.adapter.register_uri("DELETE", "/restconf/data", json=self.test_error, status_code=404)
        with self.assertRaises(requests.HTTPError):
            self.connection.delete("data", data={"test": "data"})

    def test_post(self):
        test = {"a": "b"}
        self.adapter.register_uri("POST", "/restconf/data", json=test, status_code=200)
        response = self.connection.post("data", data={"test": "data"})
        self.assertEqual(test, response)

    def test_post_no_response(self):
        self.adapter.register_uri("POST", "/restconf/data", status_code=204)
        response = self.connection.post("data", data={"test": "data"})
        self.assertIsNone(response)

    def test_post_error(self):
        self.adapter.register_uri("POST", "/restconf/data", json=self.test_error, status_code=404)
        with self.assertRaises(requests.HTTPError):
            self.connection.post("data", data={"test": "data"})

    def test_options(self):
        self.adapter.register_uri("OPTIONS", "/restconf/data", status_code=200, headers={"allow": "GET,PUT"})
        response = self.connection.options("data", data={"test": "data"})
        self.assertEqual(response, ["GET", "PUT"])

    def test_options_error(self):
        self.adapter.register_uri("OPTIONS", "/restconf/data", json=self.test_error, status_code=404)
        with self.assertRaises(requests.HTTPError):
            self.connection.options("data", data={"test": "data"})


if __name__ == "__main__":
    import sys

    sys.exit(unittest.main())
