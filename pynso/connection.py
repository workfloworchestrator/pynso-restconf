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


def _format_error_message(response):
    try:
        message = response.json()['errors']['error'][0]['error-message']
    except KeyError:
        message = 'Failed to make request or error not returned as expected'
    except ValueError:
        message = 'No message, not json'
    return 'Error code %s: %s' % (response.status_code,
                                  message)


class NSOConnection(object):
    response_type = 'json'

    def __init__(self, host, username, password, ssl, verify_ssl=True):
        self.host = host
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.ssl = ssl
        self.verify_ssl = verify_ssl

    def get(self, resource_type, media_type, path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.get(
            url,
            verify=self.verify_ssl,
            headers=self._get_headers(media_type),
            params=params)
        try:
            response.raise_for_status()

            if response.status_code != 200:
                logger.warning('Unexpected status code for GET: {}'.format(response.status_code))

            return response.json()
        except ValueError:
            logger.warning('Empty/Non valid JSON response')
            return
        except requests.HTTPError:
            logger.error('Failed on request %s', url)
            message = _format_error_message(response)
            logger.error(message)
            raise

    def get_plain(self, resource_type, media_type, path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.get(
            url,
            verify=self.verify_ssl,
            headers=self._get_headers(media_type),
            params=params)
        try:
            response.raise_for_status()

            if response.status_code != 200:
                logger.warning('Unexpected status code for GET: {}'.format(response.status_code))

            return response.text
        except requests.HTTPError:
            logger.error('Failed on request %s', url)
            logger.error(_format_error_message(response))
            raise

    def head(self, resource_type, media_type, path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.head(
            url,
            verify=self.verify_ssl,
            headers=self._get_headers(media_type),
            params=params)
        try:
            response.raise_for_status()

            if response.status_code != 200:
                logger.warning('Unexpected status code for GET: {}'.format(response.status_code))

            return response.status_code == 200
        except requests.HTTPError:
            logger.error('Failed on request %s', url)
            logger.error(_format_error_message(response))
            raise

    def post(self, resource_type, media_type, data,
             path=None, params=None):

        headers = self._get_headers(media_type)
        headers['Content-Type'] = 'application/vnd.yang.data+json'

        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.post(
            url,
            verify=self.verify_ssl,
            headers=headers,
            data=data,
            params=params)
        try:
            response.raise_for_status()

            if response.status_code not in (200, 201, 204):
                logger.warning('Unexpected status code for POST: {}'.format(response.status_code))

            if response.status_code in (201, 204):
                return  True

            return response.json()
        except ValueError:
            logger.warning('Empty/Non valid JSON response')
            return
        except requests.HTTPError:
            logger.error('Failed on request %s', url)
            logger.error(_format_error_message(response))
            raise

    def put(self, resource_type, media_type, data,
            path=None, params=None):

        headers = self._get_headers(media_type)
        headers['Content-Type'] = 'application/vnd.yang.data+json'



        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.put(
            url,
            verify=self.verify_ssl,
            headers=headers,
            data=data,
            params=params)
        try:
            response.raise_for_status()
            if response.status_code not in (200, 201, 204):
                logger.warning('Unexpected status code for PUT: {}'.format(response.status_code))
            
            if response.status_code in (201, 204):
                return True

            return response.json()
        except ValueError:
            logger.warning('Empty/Non valid JSON response')
            return
        except requests.HTTPError:
            logger.error('Failed on request %s', url)
            logger.error(_format_error_message(response))
            raise

    def delete(self, resource_type, media_type, data=None,
               path=None, params=None):
        url = _format_url(self.host, resource_type, path, self.ssl)
        response = self.session.delete(
            url,
            verify=self.verify_ssl,
            headers=self._get_headers(media_type),
            data=data,
            params=params)
        try:
            response.raise_for_status()
            if response.status_code != 204:
                logger.warning('Unexpected status code for PUT: {}'.format(response.status_code))

            return True
        except requests.HTTPError:
            logger.error('Failed on request %s', url)
            logger.error(_format_error_message(response))
            raise

    # TODO: missing OPTIONS, PATCH


    def _get_headers(self, media_type):
        return {
            'Accept': '%s+%s' % (media_type,
                                 NSOConnection.response_type)
        }
