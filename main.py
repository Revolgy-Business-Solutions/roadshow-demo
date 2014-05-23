# -*- coding: utf-8 -*-
"""
Google Cloud Road Show demo.

Main application file.
    - minimal, single-routed application

"""


import logging as log
import datetime

import webapp2
from google.appengine.api import users


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


routes = [
    webapp2.Route(r"/",
                  handler="main.RequestHandler:index",
                  name="index",
                  methods=["GET", ]),
    webapp2.Route(r"/greeting",
                  handler="main.RequestHandler:greeting",
                  name="greeting",
                  methods=["GET", ]),
]


# application instance
app = webapp2.WSGIApplication(routes=routes, debug=True)