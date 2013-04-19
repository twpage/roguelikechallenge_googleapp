"""
Todd Page
4/21/2012
"""

## standard libraries
import os, sys

## third-party libraries
from google.appengine.ext.webapp import template


#from google.appengine.ext import webapp
import webapp2
#from google.appengine.ext.webapp2.util import run_wsgi_app

## custom libraries
from app import views, ajax


app = webapp2.WSGIApplication(
    [("/", views.LandingPage),
     ("/xyzzy", views.DataLoadHandler),
     ("/ajax/(.*)", ajax.AjaxHandler)
    ],
   debug=True)
    