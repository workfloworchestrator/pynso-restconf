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

"""
The main client class for the NSO APIs
"""

from http import HTTPStatus
from typing import Optional, Iterable

import requests

from .connection import NSOConnection
from .datastores import DatastoreType
from .types import Params, JSON

__all__ = ["NSOClient"]


def _parse_datastore(datastore_type: DatastoreType, params: Optional[Params] = None) -> Optional[Params]:
    if datastore_type in (DatastoreType.CONFIG, DatastoreType.NONCONFIG) and params is None:
        params = {}

    if datastore_type == DatastoreType.CONFIG:
        assert params is not None
        params["content"] = "config"
    elif datastore_type == DatastoreType.NONCONFIG:
        assert params is not None
        params["content"] = "nonconfig"

    return params


class NSOClient(object):
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
        self.connection = self.connectionCls("%s:%s" % (host, port), username, password, ssl, verify_ssl, root)

    def info(self) -> JSON:
        """
        Returns API information
        """
        return self.connection.get(data_store="data", path="ietf-yang-library:modules-state")[
            "ietf-yang-library:modules-state"
        ]

    def get_datastore(self, datastore_name: str, *, params: Optional[Params] = None) -> JSON:
        """
        Get the details of a datastore

        :param datastore_name: The target datastore name
        :type  datastore_name: str
        """

        data = self.connection.get(path=f"ds/ietf-datastores:{datastore_name}", params=params)
        return data["ietf-restconf:data"]

    def exists(
        self,
        data_path: Iterable[str],
        *,
        datastore: DatastoreType = DatastoreType.UNIFIED,
        params: Optional[Params] = None,
    ) -> bool:
        """
        Check if a data entry in a datastore exists

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`

        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``
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
        datastore: DatastoreType = DatastoreType.UNIFIED,
        params: Optional[Params] = None,
    ) -> JSON:
        """
        Get a data entry in a datastore

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`

        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        return self.connection.get(data_store="data", path=path, params=params)

    def set_data_value(
        self,
        data_path: Iterable[str],
        data: JSON,
        *,
        datastore: DatastoreType = DatastoreType.UNIFIED,
        params: Optional[Params] = None,
    ) -> None:
        """
        Update (PUT) a complete data entry in a datastore

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`

        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``

        :param data: The new value at the given path
        :type  data: ``dict``

        :rtype: ``bool``
        :return: ``True`` if successful, otherwise error.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.put(data_store="data", path=path, data=data, params=params)

    def create_data_value(
        self,
        data_path: Iterable[str],
        data: JSON,
        *,
        datastore: DatastoreType = DatastoreType.UNIFIED,
        params: Optional[Params] = None,
    ) -> None:
        """
        Create (POST) a data entry in a datastore

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`

        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``

        :param data: The new value at the given path
        :type  data: ``dict``

        :rtype: ``bool``
        :return: ``True`` if successful, otherwise error.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.post(data_store="data", path=path, data=data, params=params)

    def update_data_value(
        self,
        data_path: Iterable[str],
        data: JSON,
        *,
        datastore: DatastoreType = DatastoreType.UNIFIED,
        params: Optional[Params] = None,
    ) -> None:
        """
        Partial update (PATCH) elements of a data entry in a datastore by only providing the changed items.

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`

        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``

        :param data: The new value at the given path
        :type  data: ``dict``

        :rtype: ``bool``
        :return: ``True`` if successful, otherwise error.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.patch(data_store="data", path=path, data=data, params=params)

    def delete_path(
        self,
        data_path: Iterable[str],
        *,
        datastore: DatastoreType = DatastoreType.UNIFIED,
        params: Optional[Params] = None,
    ) -> None:
        """
        Delete a data entry in a datastore

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`

        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``

        :rtype: ``bool``
        :return: ``True`` if successful, otherwise error.
        """
        path = "/".join(data_path)
        params = _parse_datastore(datastore, params)

        self.connection.delete(data_store="data", path=path, params=params)

    def call_operation(self, data_path: Iterable[str], data: JSON, *, params: Optional[Params] = None) -> JSON:
        """
        Call (POST) an operation to a datastore.

        :param datastore: The target datastore
        :type  datastore: :class:`DatastoreType`
        :param data_path: The list of paths
        :type  data_path: ``list`` of ``str`` or ``tuple``
        :param data: The new value at the given path
        :type  data: ``dict``
        :rtype: ``bool``

        :return: ``True`` if successful, otherwise error.
        """
        path = "/".join(data_path)

        data = self.connection.post(data_store="data", path=path, data=data, params=params)

        return data["tailf-ncs:output"]

    def get_rollbacks(self) -> JSON:
        """
        Get a list of stored rollbacks
        """
        data = self.connection.get(path="tailf-rollback:rollback-files")

        return data["tailf-rollback:rollback-files"]["file"]

    def get_rollback(self, id: int) -> str:
        """
        Get a list of stored rollbacks
        """
        data = self.connection.post(path="tailf-rollback:rollback-files/get-rollback-file", data={"input": {"id": id}})

        assert data

        return data["tailf-rollback:output"]["content"]

    def apply_rollback(self, id: int, selective: bool = False, path: Optional[str] = None) -> None:
        """
        Apply a system rollback
        """
        arguments: dict = {"id": id}
        if selective:
            arguments["selective"] = {}
        if path:
            arguments["path"] = path

        self.connection.post(path="tailf-rollback:rollback-files/apply-rollback-file", data={"input": arguments})

    def get_rollback_by_fixed_number(self, fixed_number: int) -> str:
        """
        Get a list of stored rollbacks
        """
        data = self.connection.post(
            path="tailf-rollback:rollback-files/get-rollback-file", data={"input": {"fixed-number": fixed_number}}
        )
        assert data

        return data["tailf-rollback:output"]["content"]

    def apply_rollback_by_fixed_number(
        self, fixed_number: int, selective: bool = False, path: Optional[str] = None
    ) -> None:
        """
        Apply a system rollback
        """
        arguments: dict = {"fixed-number": fixed_number}
        if selective:
            arguments["selective"] = {}
        if path:
            arguments["path"] = path

        self.connection.post(path="tailf-rollback:rollback-files/apply-rollback-file", data={"input": arguments})

    def query(self, data: JSON) -> JSON:
        data = self.connection.post(path="tailf/query", data=data)
        return data["tailf-rest-query:query-result"]
