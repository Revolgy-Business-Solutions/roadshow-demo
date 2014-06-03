# -*- coding: utf-8 -*-
"""
Google Cloud Road Show demo.

Main application file.

BigQuery connection.

"""


import json
import os
import sys
import logging as log

import webapp2

# make google API client libraries available
LIB_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "lib")
sys.path.insert(0, LIB_PROJECT_DIR)

from apiclient.discovery import build
import httplib2
from oauth2client.appengine import AppAssertionCredentials


class BigQueryHandler(webapp2.RequestHandler):

    configuration = {
        "timeoutMs": 10 * 1000,
        "kind": "query",
        "useQueryCache": True,
        "maxResults": 2000,
    }

    credentials = AppAssertionCredentials(
        scope=["https://www.googleapis.com/auth/bigquery"])
    http = credentials.authorize(httplib2.Http())
    bq_service = build("bigquery", "v2", http=http)

    def github_info(self):
        # list languages by number of repositories
        q = ("SELECT COUNT(repository_language) as counter, repository_language FROM "
             "[githubarchive:github.timeline] GROUP BY repository_language ORDER BY counter DESC")
        log.info("running bigquery ...")
        # projectId to connect opportune billing to (mandatory)
        self.configuration["query"] = q
        response = self.bq_service.jobs().query(projectId="roadshow-demo",
                                                body=self.configuration).execute()
        # returns JSON
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(response))
        log.info("bigquery finished.")


routes = [
    webapp2.Route(r'/',
                  handler="main.BigQueryHandler:github_info",
                  name="githubinfo",
                  methods=["GET", ]),
]


# application instance
app = webapp2.WSGIApplication(routes=routes, debug=True)