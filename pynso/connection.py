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
import logging
from http import HTTPStatus
from typing import Any, Callable, List, Optional

import requests

from .types import JSON, Params

logger = logging.getLogger(__name__)

__all__ = ["NSOConnection"]


def _format_url(
    host: str, root: str, data_store: Optional[str] = None, path: Optional[str] = None, ssl: bool = True
) -> str:
    protocol = "https" if ssl else "http"
    path_str = f"/{path}" if path else ""
    data_store_str = f"/{data_store}" if data_store else ""

    return f"{protocol}://{host}/{root}{data_store_str}{path_str}"


def raise_for_status(response: requests.Response) -> None:
    """Raises stored :class:`requests.HTTPError`, if one occurred."""

    try:
        message = response.json()["errors"]["error"][0]["error-message"]
    except Exception:
        message = response.text

    http_error_msg = ""

    if 400 <= response.status_code < 500:
        http_error_msg = (
            f"{response.status_code} Client Error: {response.reason} for url: {response.url} reason: {message}"
        )

    elif 500 <= response.status_code < 600:
        http_error_msg = (
            f"{response.status_code} Server Error: {response.reason} for url: {response.url} reason: {message}"
        )

    if http_error_msg:
        raise requests.HTTPError(http_error_msg, response=response)


def _handle_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        logger.warning("Empty/Non valid JSON response")
        raise


class NSOConnection:
    host: str
    session: requests.Session
    ssl: bool
    root: str

    def __init__(
        self, host: str, username: str, password: str, ssl: bool = True, verify_ssl: bool = True, root: str = "restconf"
    ):
        self.host = host
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.ssl = ssl
        self.session.verify = verify_ssl
        self.root = root

    def _request(
        self,
        function: Callable,
        data_store: Optional[str] = None,
        data: Optional[JSON] = None,
        path: Optional[str] = None,
        params: Optional[Params] = None,
    ) -> requests.Response:
        headers = {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }

        url = _format_url(self.host, self.root, data_store, path, self.ssl)
        response = function(url, headers=headers, data=data, params=params)
        try:
            raise_for_status(response)

            return response
        except requests.HTTPError as e:
            logger.exception(e)
            raise

    def get(self, *args: Any, **kwargs: Any) -> JSON:
        response = self._request(self.session.get, *args, **kwargs)

        if response.status_code != HTTPStatus.OK:
            logger.warning("Unexpected status code for GET: %s", response.status_code)

        return _handle_json(response)

    def head(self, *args: Any, **kwargs: Any) -> None:
        response = self._request(self.session.head, *args, **kwargs)

        if response.status_code != HTTPStatus.OK:
            logger.warning("Unexpected status code for HEAD: %s", response.status_code)

    def post(self, *args: Any, **kwargs: Any) -> Optional[JSON]:
        response = self._request(self.session.post, *args, **kwargs)

        if response.status_code in (HTTPStatus.NO_CONTENT, HTTPStatus.CREATED):
            return None

        if response.status_code != HTTPStatus.OK:
            logger.warning("Unexpected status code for POST: %s", response.status_code)

        return _handle_json(response)

    def put(self, *args: Any, **kwargs: Any) -> Optional[JSON]:
        response = self._request(self.session.put, *args, **kwargs)

        if response.status_code in (HTTPStatus.NO_CONTENT, HTTPStatus.CREATED):
            return None

        if response.status_code != HTTPStatus.OK:
            logger.warning("Unexpected status code for PUT: %s", response.status_code)

        return _handle_json(response)

    def patch(self, *args: Any, **kwargs: Any) -> None:
        response = self._request(self.session.patch, *args, **kwargs)

        if response.status_code != HTTPStatus.NO_CONTENT:
            logger.warning("Unexpected status code for PATCH: %s", response.status_code)

    def delete(self, *args: Any, **kwargs: Any) -> None:
        response = self._request(self.session.delete, *args, **kwargs)

        if response.status_code != HTTPStatus.NO_CONTENT:
            logger.warning("Unexpected status code for DELETE: %s", response.status_code)

    def options(self, *args: Any, **kwargs: Any) -> List[str]:
        response = self._request(self.session.options, *args, **kwargs)

        if response.status_code != HTTPStatus.OK:
            logger.warning("Unexpected status code for OPTIONS: %s", response.status_code)

        return response.headers["ALLOW"].split(",")
