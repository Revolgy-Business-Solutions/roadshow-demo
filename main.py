# -*- coding: utf-8 -*-
"""
Google Cloud Road Show demo.

Main application file.

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
from oauth2client.appengine import AppAssertionCredentials

# TODO, on 01 branch:
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
    # SELECT count(1) FROM [publicdata:samples.github_timeline]  :  6219749
    # SELECT count(DISTINCT repository_language) FROM [publicdata:samples.github_timeline]  :  90
    # SELECT repository_language FROM [publicdata:samples.github_timeline] GROUP BY repository_language ORDER BY repository_language
    # q = "SELECT count(1) FROM [publicdata:samples.wikipedia]"
    q = "SELECT repository_language FROM [publicdata:samples.github_timeline] GROUP BY repository_language ORDER BY repository_language"
    configuration = {
        'timeoutMs': 10 * 1000,
        'kind': 'query',
        'useQueryCache': True,
        'maxResults': 2000,
        'query': q,
    }

    def bigquery(self):
        msg = "BIGQUERY WITH CREDENTIALS for: %s" % users.get_current_user().email()
        log.info(msg)

        credentials = AppAssertionCredentials(scope=[
        'https://www.googleapis.com/auth/bigquery',])
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
    webapp2.Route(r"/bigquery",
                  handler="main.BigQueryHandler:bigquery",
                  name="bigquery",
                  methods=["GET", ]),
]


# application instance
app = webapp2.WSGIApplication(routes=routes, debug=True)