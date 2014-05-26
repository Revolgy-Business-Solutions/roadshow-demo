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

        # Developer Console:
        #   CREATE NEW CLIENT ID (Service a/c) -> stores keys
        #   openssl commands starting on .p12 file
        #       [must be right set, otherwise getting various format, pycrypto errors ...]
        #   pass privatekey.pem and SERVICE_ACCOUNT_EMAIL
        #   https://developers.google.com/bigquery/docs/authorization#service-accounts-server
        #

        f = file('privatekey.pem', 'rb')
        key = f.read()
        f.close()
        CLIENT_EMAIL_FROM_CLIENT_SECRET = "89371161002-fureagtsc40aihlo6aqgk20ub9j3pcpf@developer.gserviceaccount.com"
        credentials = SignedJwtAssertionCredentials(
            CLIENT_EMAIL_FROM_CLIENT_SECRET,
            key,
            scope='https://www.googleapis.com/auth/bigquery')
        http = credentials.authorize(httplib2.Http())
        bq_service = build("bigquery", "v2", http=http)
        # or projectId="roadshow-demo" project number?
        response = bq_service.jobs().query(projectId="roadshow-demo", body=self.configuration).execute()
        log.info("BQ done")
        self.response.out.write(msg)
        self.response.out.write(response)


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