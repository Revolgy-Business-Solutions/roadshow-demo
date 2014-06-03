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
from webapp2_extras import jinja2

# make google API client libraries available
LIB_PROJECT_DIR = os.path.join(os.path.dirname(__file__), "lib")
sys.path.insert(0, LIB_PROJECT_DIR)

from apiclient.discovery import build
import httplib2
from oauth2client.appengine import AppAssertionCredentials
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote


class BigQueryService(object):
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

    def github_info(self, repo_lang=None):
        # list languages by number of repositories
        q = ("SELECT COUNT(repository_language) as counter, repository_language FROM "
             "[githubarchive:github.timeline] %(where)s GROUP BY repository_language ORDER BY counter DESC")
        where = "WHERE repository_language='%s'" % repo_lang if repo_lang else ''
        q = q % dict(where=where)
        log.info("running bigquery '%s' ..." % q)
        # projectId to connect opportune billing to (mandatory)
        self.configuration["query"] = q
        response = self.bq_service.jobs().query(projectId="roadshow-demo",
                                                body=self.configuration).execute()
        log.info("bigquery finished.")
        return response


class BigQueryHandler(webapp2.RequestHandler):

    def github_info(self):
        bq_service = BigQueryService()
        # returns JSON
        response = bq_service.github_info()
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(response))
        log.info("bigquery finished.")

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def frontend(self):
        data = dict()
        self.response.out.write(self.jinja2.render_template("index.html", **data))


class RepoQuery(messages.Message):
    repo_lang = messages.StringField(1, required=True)


class SingleRepoResponse(messages.Message):
    repo_counter = messages.StringField(1, required=True)
    repo_lang = messages.StringField(2, required=True)


class ReposResponse(messages.Message):
    repos = messages.MessageField(SingleRepoResponse, 1, repeated=True)


@endpoints.api(name="github",
               version="v1",
               description="Github API",
               # possible access control via client_id
               # config.settings.client_id if generated
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID])
class GithubBQApi(remote.Service):
    @endpoints.method(message_types.VoidMessage,
                      ReposResponse,
                      name="repos",
                      path="repos",
                      http_method="GET")
    def repos(self, _):
        bq_service = BigQueryService()
        # result["schema"]["fields"][0]["name"] is "counter"
        # result["schema"]["fields"][1]["name"] is "repository_language"
        result = bq_service.github_info()
        resp = ReposResponse()
        resp.repos = []
        for lang in result["rows"]:
            resp_row = SingleRepoResponse()
            resp_row.repo_counter = lang["f"][0]["v"]
            # str() b/c of opportune empty/null values
            resp_row.repo_lang = str(lang["f"][1]["v"])
            resp.repos.append(resp_row)
        return resp

    @endpoints.method(RepoQuery,
                      SingleRepoResponse,
                      name="repo",
                      path="repo",
                      http_method="GET")
    def repo(self, repo_query):
        bq_service = BigQueryService()
        result = bq_service.github_info(repo_lang=repo_query.repo_lang)
        log.debug(result)
        resp = SingleRepoResponse()
        if result["totalRows"] == '0':
            resp.repo_counter = "n/a"
            resp.repo_lang = "n/a"
            return resp
        resp.repo_counter = result["rows"][0]["f"][0]["v"]
        resp.repo_lang = result["rows"][0]["f"][1]["v"]
        return resp


endpoints_launcher = endpoints.api_server([GithubBQApi])


routes = [
    webapp2.Route(r'/githubinfo',
                  handler="main.BigQueryHandler:github_info",
                  name="githubinfo",
                  methods=["GET", ]),
    webapp2.Route(r'/',
                  handler="main.BigQueryHandler:frontend",
                  name="frontend",
                  methods=["GET", ]),
]


# Configure webapp2, templates
webapp2_config = {}
webapp2_config['webapp2_extras.jinja2'] = dict(
    template_path='app',
    environment_args=dict(autoescape=True,
                          block_start_string='<%',
                          block_end_string='%>',
                          variable_start_string='%%',
                          variable_end_string='%%',
                          comment_start_string='<#',
                          comment_end_string='#>'),)


# application instance
app = webapp2.WSGIApplication(routes=routes, debug=True, config=webapp2_config)