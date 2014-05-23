# -*- coding: utf-8 -*-
"""
Google Cloud Road Show demo.

Main application file.
    - minimal, single-routed application

"""

import os
import sys
import logging as log
import datetime

import webapp2
from google.appengine.api import users

# make google API client libraries available
LIB_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "lib")
sys.path.insert(0, LIB_PROJECT_DIR)

from apiclient.discovery import build
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials

# TODO
# 1) show JSON stuff on one
# 2) add time and personal greeting (users)
# 3) simplify app.yaml as much as possible
class RequestHandler(webapp2.RequestHandler):
    def index(self):
        msg = "index AAA"
        log.info(msg)
        self.response.out.write(msg)

    def greeting(self):
        print "greeting AAA"


class BigQueryHandler(webapp2.RequestHandler):
    q = "SELECT count(1) FROM [publicdata:samples.wikipedia]"
    configuration = {
        'timeoutMs': 10 * 1000,
        'kind': 'query',
        'useQueryCache': True,
        'maxResults': 2000,
        'query': q,
    }

    def bigquery_no_auth(self):
        msg = "BIGQUERY NO AUTH for: %s" % users.get_current_user().email()
        log.info(msg)
        # passing no credentials:
        # HttpError: <HttpError 401 when requesting https://www.googleapis.com/bigquery/v2/projects/roadshow-demo/queries?alt=json returned "Login Required">
        http = httplib2.Http()
        bq_service = build("bigquery", "v2", http=http)
        bq_service.jobs().query(projectId="roadshow-demo", body=self.configuration).execute()
        self.response.out.write(msg)

    def bigquery(self):
        msg = "BIGQUERY WITH CREDENTIALS for: %s" % users.get_current_user().email()
        log.info(msg)

        # Click on "API Access" on the left, then "Create an OAuth2.0 client ID".
        # Choose Service Accounts and click on Create Client ID.
        # -> do screenshots, the one for "public api access -> create new key are useless"

        # OBTAIN THE KEY FROM THE GOOGLE APIs CONSOLE
        # More instructions here: http://goo.gl/w0YA0
        #f = file('privatekey.p12', 'rb')
        # did edit the file ... (formatting ...) ->
        # File "/base/data/home/runtimes/python27/python27_lib/versions/third_party/pycrypto-2.6/Crypto/PublicKey/RSA.py", line 588, in _importKeyDER
        # raise ValueError("RSA key format is not supported")
        # ValueError: RSA key format is not supported
        f = file('privatekey.pem', 'rb')

        # issue with the key:
        # 'PKCS12 format is not supported by the PyCrpto library. '
        # NotImplementedError: PKCS12 format is not supported by the PyCrpto library.
        # Try converting to a "PEM":
        # (openssl pkcs12 -in xxxxx.p12 -nodes -nocerts > privatekey.pem) or using PyOpenSSL if native code is an option.

        # another issue: running the command reuqires password, don't have it
        # downloading client secret JSON,
        # there is link
        # https://www.googleapis.com/robot/v1/metadata/x509/89371161002@developer.gserviceaccount.com
        # -> storing the cert as privatekey.pem
        key = f.read()
        f.close()
        SERVICE_ACCOUNT_EMAIL = "roadshow-demo@appspot.gserviceaccount.com"
        credentials = SignedJwtAssertionCredentials(
            SERVICE_ACCOUNT_EMAIL,
            key,
            scope='https://www.googleapis.com/auth/bigquery')
        http = httplib2.Http()
        http = credentials.authorize(http)
        bq_service = build("bigquery", "v2", http=http)
        # or projectId="roadshow-demo" project number?
        bq_service.jobs().query(projectId="roadshow-demo", body=self.configuration).execute()
        log.info("BQ done")
        self.response.out.write(msg)


routes = [
    webapp2.Route(r"/",
                  handler="main.RequestHandler:index",
                  name="index",
                  methods=["GET", ]),
    webapp2.Route(r"/greeting",
                  handler="main.RequestHandler:greeting",
                  name="greeting",
                  methods=["GET", ]),
    webapp2.Route(r"/bigquerynoauth",
                  handler="main.BigQueryHandler:bigquery_no_auth",
                  name="bigquerynoauth",
                  methods=["GET", ]),
    webapp2.Route(r"/bigquery",
                  handler="main.BigQueryHandler:bigquery",
                  name="bigquery",
                  methods=["GET", ]),
]


# application instance
app = webapp2.WSGIApplication(routes=routes, debug=True)