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
import logging
import requests

logger = logging.getLogger(__name__)

__all__ = ['NSOConnection']


def _format_url(host, resource_type, path=None, ssl=True):
    protocol = 'https' if ssl else 'http'
    if resource_type is None:
        if path is None:
            return '%s://%s/api' % (protocol, host)
        return '%s://%s/api/%s' % (protocol, host, path)
    else:
        if path is None:
            return '%s://%s/api/%s' % (protocol, host, resource_type)
        else:
            return '%s://%s/api/%s/%s' % (protocol, host, resource_type, path)


def raise_for_status(response):
    """Raises stored :class:`HTTPError`, if one occurred."""

    try:
        message = response.json()['errors']['error'][0]['error-message']
    except Exception:
        message = response.text

    http_error_msg = ''

    if 400 <= response.status_code < 500:
        http_error_msg = u'%s Client Error: %s for url: %s reason: %s' % (response.status_code, response.reason, response.url, message)

    elif 500 <= response.status_code < 600:
        http_error_msg = u'%s Server Error: %s for url: %s reason: %s' % (response.status_code, response.reason, response.url, message)

    if http_error_msg:
        raise requests.HTTPError(http_error_msg, response=response)

class NSOConnection(object):
    response_type = 'json'

    def __init__(self, host, username, password, ssl, verify_ssl=True):
        self.host = host
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.ssl = ssl
        self.session.verify = verify_ssl

    def _request(self, function, resource_type, media_type, data, path=None, params=None):
        headers = self._get_headers(media_type)
        headers['Content-Type'] = 'application/vnd.yang.data+json'

        url = _format_url(self.host, resource_type, path, self.ssl)
        response = function(
            url,
            headers=headers,
            data=data,
            params=params)
        try:
            raise_for_status(response)

            if response.status_code not in (200, 201, 204):
                logger.warning('Unexpected status code for %s: %s', function.__name__, response.status_code)

            # Request was successful but returned no content
            if response.status_code in (201, 204):
                return True

            try:
                return response.json()
            except ValueError:
                logger.warning('Empty/Non valid JSON response')
                return response.text
        except requests.HTTPError as e:
            logger.exception(e)
            raise

    def get(self, resource_type, media_type, path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.get(
            url,
            headers=self._get_headers(media_type),
            params=params)
        try:
            raise_for_status(response)

            if response.status_code != 200:
                logger.warning('Unexpected status code for GET: %s', response.status_code)

            try:
                return response.json()
            except ValueError:
                logger.warning('Empty/Non valid JSON response')
                return response.text
        except requests.HTTPError as e:
            logger.exception(e)
            raise

    def get_plain(self, resource_type, media_type, path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.get(
            url,
            headers=self._get_headers(media_type),
            params=params)
        try:
            raise_for_status(response)

            if response.status_code != 200:
                logger.warning('Unexpected status code for GET: %s', response.status_code)

            return response.text
        except requests.HTTPError as e:
            logger.exception(e)
            raise

    def head(self, resource_type, media_type, path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.head(
            url,
            headers=self._get_headers(media_type),
            params=params)
        try:
            raise_for_status(response)

            if response.status_code != 200:
                logger.warning('Unexpected status code for HEAD: %s', response.status_code)

            return True
        except requests.HTTPError as e:
            logger.exception(e)
            raise

    def post(self, *args, **kwargs):
        return self._request(self.session.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request(self.session.put, *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request(self.session.patch, *args, **kwargs)

    def delete(self, resource_type, media_type, data=None,
               path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.delete(
            url,
            headers=self._get_headers(media_type),
            data=data,
            params=params)
        try:
            raise_for_status(response)
            if response.status_code != 204:
                logger.warning('Unexpected status code for DELETE: %s', response.status_code)

            return True
        except requests.HTTPError as e:
            logger.exception(e)
            raise

    # TODO: missing OPTIONS

    def _get_headers(self, media_type):
        return {
            'Accept': '%s+%s' % (media_type,
                                 NSOConnection.response_type)
        }
