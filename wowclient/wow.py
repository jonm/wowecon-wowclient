# Copyright (C) 2017-2020 Jonathan Moore
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import json
import logging
import time

from dateutil.parser import parse
import requests
from requests.auth import HTTPBasicAuth

class AuctionDataBatch:
    def __init__(self, url, last_modified):
        self.url = url
        self.last_modified = last_modified

    def __repr__(self):
        return "AuctionDataBatch(url=%s, last_modified=%s)" % (self.url.__repr__(),
                                                               self.last_modified.__repr__())

class WoWCommunityAPIClient:
    def __init__(self, client_id, client_secret, endpoint='https://us.api.blizzard.com', oauth_endpoint='https://us.battle.net'):
        self._client_id = client_id
        self._client_secret = client_secret
        self._endpoint = endpoint
        self._oauth_endpoint = oauth_endpoint
        self._access_token = None
        self._token_expires = None

    def _get_access_token(self):
        if (self._access_token is not None
            and self._token_expires is not None
            and time.time() + 3600.0 < self._token_expires):
            return self._access_token

        resp = requests.post("%s/oauth/token" % (self._oauth_endpoint,),
                             auth = HTTPBasicAuth(self._client_id,
                                                  self._client_secret),
                             data = { 'grant_type' : 'client_credentials' })
        resp.raise_for_status()
        body = resp.json()
        if ('access_token' not in body
            or 'token_type' not in body or body['token_type'] != 'bearer'
            or 'expires_in' not in body):
            msg = "unexpected JSON body: %s" % json.dumps(body)
            logging.error(msg)
            raise ValueError(msg)
        self._access_token = body['access_token']
        self._token_expires = time.time() + body['expires_in']
        return self._access_token

    def _oauth_get(self, uri):
        headers = { 'Authorization' :
                    "Bearer %s" % (self._get_access_token(),) }

        start = time.time()
        resp = requests.get(uri, headers = headers)
        end = time.time()
        logging.info("GET %s (%ld ms)" % (uri, int((end - start) * 1000.0)))
        resp.raise_for_status()
        return resp.json()
    
    def get_realm(self, realm, locale='en_US'):
        uri = "%s/data/wow/realm/%s?namespace=dynamic-us&locale=%s" % \
              (self._endpoint, realm, locale)
        return self._oauth_get(uri)

    def get_auction_data_status(self, realm, locale='en_US'):
        realm_info = self.get_realm(realm, locale)
        
        connected_realm = self._oauth_get(realm_info['connected_realm']['href'])


        headers = { 'Authorization' :
                    "Bearer %s" % (self._get_access_token(),) }
        start = time.time()
        uri = connected_realm['auctions']['href']
        resp = requests.get(uri, headers = headers)
        end = time.time()
        logging.info("HEAD %s (%ld ms)" % (uri, int((end - start) * 1000.0)))
        resp.raise_for_status()

        lm = parse(resp.headers['Last-Modified'])
        return [AuctionDataBatch(uri, lm)]

    def get_item_info(self, item_id, locale='en_US', context=None,
                      bonus_lists=[]):
        raise Exception("not implemented")

