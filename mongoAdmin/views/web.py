#-*- coding:utf-8 -*-
from flask import Module, g, jsonify, request, render_template
from pymongo.objectid import ObjectId

web = Module(__name__)

@web.before_request
def before_request():
    pass

def error(msg):
    pass

@web.route("/")
def index():
    return "Estate Db Restful Api"

@web.route("/site", methods=['GET', 'POST'])
def site():
    """
    GET: get site's data
    POST: create new site
    """
    pass
