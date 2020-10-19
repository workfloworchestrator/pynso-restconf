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
import unittest
from unittest import mock

import requests

from pynso.client import NSOClient
from pynso.connection import NSOConnection
from pynso.datastores import DatastoreType


def raise_http_error(status_code=500):
    mock_response = requests.Response()
    mock_response.status_code = status_code
    return requests.HTTPError("message", response=mock_response)


class TestClient(unittest.TestCase):
    def setUp(self):
        NSOClient.connectionCls = mock.MagicMock(spec=NSOConnection)
        self.mock_connection = NSOClient.connectionCls()
        self.client = NSOClient("test.com", "test", "testpass")

    def test_info(self):
        self.mock_connection.get.return_value = {"ietf-yang-library:modules-state": mock.sentinel.payload}

        info = self.client.info()

        self.assertEqual(info, mock.sentinel.payload)
        self.mock_connection.get.assert_called_once_with(data_store="data", path="ietf-yang-library:modules-state")

    def test_get_data(self):
        self.mock_connection.get.return_value = mock.sentinel.payload

        data = self.client.get_data(("devices", "ex0"))

        self.assertEqual(data, mock.sentinel.payload)
        self.mock_connection.get.assert_called_once_with(data_store="data", path="devices/ex0", params=None)

    def test_get_data_nonconfig(self):
        self.mock_connection.get.return_value = mock.sentinel.payload

        data = self.client.get_data(("devices", "ex0"), datastore=DatastoreType.NONCONFIG)

        self.assertEqual(data, mock.sentinel.payload)
        self.mock_connection.get.assert_called_once_with(
            data_store="data", path="devices/ex0", params={"content": "nonconfig"}
        )

    def test_exists(self):
        self.mock_connection.head.return_value = mock.sentinel.payload

        data = self.client.exists(("devices", "ex0"), datastore=DatastoreType.NONCONFIG)

        self.assertTrue(data)
        self.mock_connection.head.assert_called_once_with(
            data_store="data", path="devices/ex0", params={"content": "nonconfig"}
        )

    def test_exists_non_existing(self):
        self.mock_connection.head.side_effect = raise_http_error(404)

        data = self.client.exists(("devices", "ex0"), datastore=DatastoreType.NONCONFIG)

        self.assertFalse(data)
        self.mock_connection.head.assert_called_once_with(
            data_store="data", path="devices/ex0", params={"content": "nonconfig"}
        )

    def test_exists_error(self):
        self.mock_connection.head.side_effect = raise_http_error(500)

        with self.assertRaises(requests.HTTPError):
            self.client.exists(("devices", "ex0"), datastore=DatastoreType.NONCONFIG)

        self.mock_connection.head.assert_called_once_with(
            data_store="data", path="devices/ex0", params={"content": "nonconfig"}
        )

    def test_get_data_config(self):
        self.mock_connection.get.return_value = mock.sentinel.payload

        data = self.client.get_data(("devices", "ex0"), datastore=DatastoreType.CONFIG)

        self.assertEqual(data, mock.sentinel.payload)
        self.mock_connection.get.assert_called_once_with(
            data_store="data", path="devices/ex0", params={"content": "config"}
        )

    def test_set_data_value(self):
        self.mock_connection.put.return_value = mock.sentinel.payload
        test = {"my": "new"}

        data = self.client.set_data_value(("devices", "ex0"), test)

        self.assertIsNone(data)
        self.mock_connection.put.assert_called_once_with(
            data_store="data", path="devices/ex0", data={"my": "new"}, params=None
        )

    def test_create_data_value(self):
        self.mock_connection.post.return_value = mock.sentinel.payload
        test = {"my": "new"}

        data = self.client.create_data_value(("devices", "ex0"), test)

        self.assertIsNone(data)
        self.mock_connection.post.assert_called_once_with(
            data_store="data", path="devices/ex0", data={"my": "new"}, params=None
        )

    def test_call_operation(self):
        self.mock_connection.post.return_value = {"tailf-ncs:output": mock.sentinel.payload}
        test = {"my": "new"}

        data = self.client.call_operation(("devices", "ex0"), test)

        self.assertEqual(data, mock.sentinel.payload)
        self.mock_connection.post.assert_called_once_with(
            data_store="data", path="devices/ex0", data={"my": "new"}, params=None
        )

    def test_update_data_value(self):
        self.mock_connection.patch.return_value = mock.sentinel.payload
        test = {"my": "new"}

        data = self.client.update_data_value(("devices", "ex0"), test)

        self.assertIsNone(data)
        self.mock_connection.patch.assert_called_once_with(
            data_store="data", path="devices/ex0", data={"my": "new"}, params=None
        )

    def test_delete_path(self):
        self.mock_connection.delete.return_value = mock.sentinel.payload

        data = self.client.delete_path(("devices", "ex0"))

        self.assertIsNone(data)
        self.mock_connection.delete.assert_called_once_with(data_store="data", path="devices/ex0", params=None)

    def test_get_datastore(self):
        self.mock_connection.get.return_value = {"ietf-restconf:data": mock.sentinel.payload}

        data = self.client.get_datastore("running")

        self.assertEqual(data, mock.sentinel.payload)
        self.mock_connection.get.assert_called_once_with(path="ds/ietf-datastores:running", params=None)

    def test_get_rollbacks(self):
        self.mock_connection.get.return_value = {"tailf-rollback:rollback-files": {"file": mock.sentinel.payload}}

        rollbacks = self.client.get_rollbacks()

        self.assertEqual(rollbacks, mock.sentinel.payload)
        self.mock_connection.get.assert_called_once_with(path="tailf-rollback:rollback-files")

    def test_get_rollback(self):
        self.mock_connection.post.return_value = {"tailf-rollback:output": {"content": mock.sentinel.payload}}

        rollback = self.client.get_rollback(0)

        self.assertEqual(rollback, mock.sentinel.payload)
        self.mock_connection.post.assert_called_once_with(
            path="tailf-rollback:rollback-files/get-rollback-file", data={"input": {"id": 0}}
        )

    def test_apply_rollback(self):
        self.mock_connection.post.return_value = {"tailf-rollback:output": mock.sentinel.payload}

        data = self.client.apply_rollback(0)

        self.assertIsNone(data)
        self.mock_connection.post.assert_called_once_with(
            path="tailf-rollback:rollback-files/apply-rollback-file", data={"input": {"id": 0}}
        )

    def test_apply_rollback_options(self):
        self.mock_connection.post.return_value = {"tailf-rollback:output": mock.sentinel.payload}

        data = self.client.apply_rollback(0, selective=True, path="x")

        self.assertIsNone(data)
        self.mock_connection.post.assert_called_once_with(
            path="tailf-rollback:rollback-files/apply-rollback-file",
            data={"input": {"id": 0, "selective": {}, "path": "x"}},
        )

    def test_get_rollback_by_fixed_number(self):
        self.mock_connection.post.return_value = {"tailf-rollback:output": {"content": mock.sentinel.payload}}

        rollback = self.client.get_rollback_by_fixed_number(86)

        self.assertEqual(rollback, mock.sentinel.payload)
        self.mock_connection.post.assert_called_once_with(
            path="tailf-rollback:rollback-files/get-rollback-file", data={"input": {"fixed-number": 86}}
        )

    def test_apply_rollback_by_fixed_number(self):
        self.mock_connection.post.return_value = {"tailf-rollback:output": mock.sentinel.payload}

        data = self.client.apply_rollback_by_fixed_number(86)

        self.assertIsNone(data)
        self.mock_connection.post.assert_called_once_with(
            path="tailf-rollback:rollback-files/apply-rollback-file",
            data={"input": {"fixed-number": 86}},
        )

    def test_apply_rollback_by_fixed_number_options(self):
        self.mock_connection.post.return_value = {"tailf-rollback:output": mock.sentinel.payload}

        data = self.client.apply_rollback_by_fixed_number(86, selective=True, path="x")

        self.assertIsNone(data)
        self.mock_connection.post.assert_called_once_with(
            path="tailf-rollback:rollback-files/apply-rollback-file",
            data={"input": {"fixed-number": 86, "selective": {}, "path": "x"}},
        )

    def test_query(self):
        self.mock_connection.post.return_value = {"tailf-rest-query:query-result": mock.sentinel.payload}

        data = self.client.query(data={"immidiate-query": {}})

        self.assertEqual(data, mock.sentinel.payload)
        self.mock_connection.post.assert_called_once_with(path="tailf/query", data={"immidiate-query": {}})


if __name__ == "__main__":
    import sys

    sys.exit(unittest.main())
