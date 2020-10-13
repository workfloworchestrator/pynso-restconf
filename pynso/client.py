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

"""The main client class for the NSO APIs."""

from http import HTTPStatus
from typing import Iterable, Optional

import requests

from .connection import NSOConnection
from .datastores import DatastoreType
from .types import JSON, Params

__all__ = ["NSOClient"]


def _parse_datastore(datastore_type: Optional[DatastoreType], params: Optional[Params]) -> Optional[Params]:
    if datastore_type is not None and params is None:
        params = {}

    if datastore_type is not None:
        assert params is not None  # noqa:S101
        params["content"] = datastore_type.value

    return params


class NSOClient(object):
    """The main client class for the NSO APIs."""

    connectionCls = NSOConnection
    connection: NSOConnection

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 8080,
        ssl: bool = False,
        verify_ssl: bool = True,
        root: str = "restconf",
    ):
        """Create a new api client.

        :param host: The hostname of NSO
        :param port: The port of the restconf api
        :param username: The username to use
        :param password: The password to use
        :param ssl: Use https
        :param verify_ssl: Check ssl certificates (Only set this to False if you know what you are doing)
        :param root: Optionally change the base api path (needs to match NSO configuration)
        """
        self.connection = self.connectionCls(f"{host}:{port}", username, password, ssl, verify_ssl, root)

    def info(self) -> JSON:
        """
        Return API information.

        This call returns the loaded yang modules.

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        return self.connection.get(data_store="data", path="ietf-yang-library:modules-state")[
            "ietf-yang-library:modules-state"
        ]

    def get_datastore(self, datastore_name: str, *, params: Optional[Params] = None) -> JSON:
        """
        Get the details of a datastore.

        :param datastore_name: The target datastore name
        :param params: Extra query parameters, see :data:`Params`

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        data = self.connection.get(path=f"ds/ietf-datastores:{datastore_name}", params=params)
        return data["ietf-restconf:data"]

    def exists(
        self,
        data_path: Iterable[str],
        *,
        datastore: Optional[DatastoreType] = None,
        params: Optional[Params] = None,
    ) -> bool:
        """
        Check if a data entry in a datastore exists.

        :param data_path: The list of paths segments
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on failures.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        try:
            self.connection.head(data_store="data", path=path, params=params)
            return True
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                return False
            else:
                raise e

    def get_data(
        self,
        data_path: Iterable[str],
        *,
        datastore: Optional[DatastoreType] = None,
        params: Optional[Params] = None,
    ) -> JSON:
        """
        Get a data entry in a datastore.

        :param data_path: The list of paths segments
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        return self.connection.get(data_store="data", path=path, params=params)

    def set_data_value(
        self,
        data_path: Iterable[str],
        data: JSON,
        *,
        datastore: Optional[DatastoreType] = None,
        params: Optional[Params] = None,
    ) -> None:
        """
        Update (PUT) a complete data entry in a datastore.

        :param data_path: The list of paths segments
        :param data: The new value at the given path
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on failures.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.put(data_store="data", path=path, data=data, params=params)

    def create_data_value(
        self,
        data_path: Iterable[str],
        data: JSON,
        *,
        datastore: Optional[DatastoreType] = None,
        params: Optional[Params] = None,
    ) -> None:
        """
        Create (POST) a data entry in a datastore.

        :param data_path: The list of paths segments
        :param data: The new value at the given path
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on failures.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.post(data_store="data", path=path, data=data, params=params)

    def update_data_value(
        self,
        data_path: Iterable[str],
        data: JSON,
        *,
        datastore: Optional[DatastoreType] = None,
        params: Optional[Params] = None,
    ) -> None:
        """
        Partial update (PATCH) elements of a data entry in a datastore by only providing the changed items.

        :param data_path: The list of paths segments
        :param data: The new value at the given path
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on failures.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.patch(data_store="data", path=path, data=data, params=params)

    def delete_path(
        self,
        data_path: Iterable[str],
        *,
        datastore: Optional[DatastoreType] = None,
        params: Optional[Params] = None,
    ) -> None:
        """
        Delete a data entry in a datastore.

        :param data_path: The list of paths segments
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on failures.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.delete(data_store="data", path=path, params=params)

    def call_operation(
        self, data_path: Iterable[str], data: JSON, *, params: Optional[Params] = None
    ) -> Optional[JSON]:
        """
        Call (POST) an operation to a datastore.

        :param data_path: The list of paths segments
        :param datastore: Optional target datastore, see :class:`pynso.datastores.DatastoreType`
        :param params: Optional Extra query parameters, see :data:`pynso.types.Params`

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        path = "/".join(data_path)

        data = self.connection.post(data_store="data", path=path, data=data, params=params)

        if data is not None:
            return data["tailf-ncs:output"]
        return None

    def get_rollbacks(self) -> JSON:
        """
        Get a list of stored rollbacks.

        Rollbacks have an id which start at the most recent change and a fixed number which starts at the oldest change.

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        data = self.connection.get(path="tailf-rollback:rollback-files")

        return data["tailf-rollback:rollback-files"]["file"]

    def get_rollback(self, id: int) -> str:
        """
        Get the contents of stored rollbacks.

        This returns the configuration diff as it was applied in the change by id.

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        data = self.connection.post(path="tailf-rollback:rollback-files/get-rollback-file", data={"input": {"id": id}})

        assert data  # noqa: S101

        return data["tailf-rollback:output"]["content"]

    def apply_rollback(self, id: int, selective: bool = False, path: Optional[str] = None) -> None:
        """
        Apply a system rollback.

        After applying a rollback this latest change gets id 0 which means that all other ids also change.

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        arguments: dict = {"id": id}
        if selective:
            arguments["selective"] = {}
        if path:
            arguments["path"] = path

        self.connection.post(path="tailf-rollback:rollback-files/apply-rollback-file", data={"input": arguments})

    def get_rollback_by_fixed_number(self, fixed_number: int) -> str:
        """
        Get the contents of stored rollbacks by fixed number.

        This returns the configuration diff as it was applied in the change by fixed-number.

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        data = self.connection.post(
            path="tailf-rollback:rollback-files/get-rollback-file", data={"input": {"fixed-number": fixed_number}}
        )
        assert data  # noqa: S101

        return data["tailf-rollback:output"]["content"]

    def apply_rollback_by_fixed_number(
        self, fixed_number: int, selective: bool = False, path: Optional[str] = None
    ) -> None:
        """
        Apply a system rollback by fixed number.

        After applying a rollback the fixed number is still the same.

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        arguments: dict = {"fixed-number": fixed_number}
        if selective:
            arguments["selective"] = {}
        if path:
            arguments["path"] = path

        self.connection.post(path="tailf-rollback:rollback-files/apply-rollback-file", data={"input": arguments})

    def query(self, data: JSON) -> JSON:
        """
        Call the nso query api.

        The API consists of the following Requests:

            - start-query: Start a query and return a query handle.
            - fetch-query-result: Use a query handle to repeatedly fetch chunks of the result.
            - immediate-query: Start a query and return the entire result immediately.
            - reset-query: (Re)set where the next fetched result will begin from.
            - stop-query: Stop (and close) the query.

        The API consists of the following Replies:

            - start-query-result: Reply to the start-query request
            - query-result: Reply to the fetch-query-result and immediate-query requests

        Example:
            Example payload:

            .. code-block:: json

                {
                    "start-query": {
                        "foreach": "/x/host[enabled = 'true']",
                        "select": [
                            {
                                "label": "Host name",
                                "expression": "name",
                                "result-type": ["string"]
                            },
                            {
                                "expression": "address",
                                "result-type": ["string"]
                            }
                        ],
                        "sort-by": ["name"],
                        "limit": 100,
                        "offset": 1
                    }
                }

        Raises :class:`requests.HTTPError` on request failures or :class:`json.JSONDecodeError` on invalid json.
        """
        data = self.connection.post(path="tailf/query", data=data)
        return data["tailf-rest-query:query-result"]
