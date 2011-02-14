#-*- coding:utf-8 -*-
from flask import Module, jsonify, request

api = Module(__name__)

@api.route("/search/")
def search():
    pass

@api.route("/user/<username>/")
def test():
    pass
