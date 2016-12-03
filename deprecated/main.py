#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# [ START demo app ]
# import webapp2

# class MainHandler(webapp2.RequestHandler):
#     def get(self):
#         self.response.write('Hello world!')

# app = webapp2.WSGIApplication([
#     ('/', MainHandler)
# ], debug=True)
# [ END demo app ]

# [START app]
import logging

from flask import Flask, render_template, request
from threading import Lock
from google.appengine.ext import ndb
from models import Item
import uuid

app = Flask(__name__)
app.config.from_object('config')

print "I'm here!"

counter=0
catList=[]
probList=[]
lock=Lock()

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

@app.route('/wwForm')
def wwForm():
    global counter
    with lock:
        counter+=1
        print (counter)
    return render_template('form.html')

@app.route('/wwSubmitted', methods=['POST'])
def wwSubmitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']
    return render_template(
        'submitted_form.html',
        name=name,
        email=email,
        site=site,
        comments=comments)

def hello():
    return 'Hello World!'

from views import *

# [END app]
