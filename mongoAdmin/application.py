#/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    main.py
    
    this is mongodb admin

    :copyright: (c) 2011 by Kakashi Liu
"""
import os
import sys

BASE_DIR = os.path.join('/var/www/mongoAdmin')
sys.path.append(BASE_DIR)

from flask import Flask, request, make_response, g, session, url_for, redirect
from config import DefaultConfig
from pymongo import Connection
from pymongo.objectid import ObjectId
from ConfigParser import SafeConfigParser

from mongoAdmin import views

__all__ = ['create_app']

DEFAULT_APP_NAME = "mongoAdmin"
DEFAULT_MODULES  = (
    (views.api, "/api"),
    (views.web, "/web"),
)

def create_app(config=None, app_name=None, modules=None):
    
    if app_name is None:
        app_name = DEFAULT_APP_NAME

    if modules is None:
        modules = DEFAULT_MODULES

    app = Flask(app_name)
    configure_app(app, config)
    configure_db(app)
    configure_modules(app, modules)

    return app

def configure_app(app, config):
    
    app.config.from_object(DefaultConfig())

    if config is not None:
        app.config.from_object(config)

def configure_db(app):
    
    @app.before_request
    def connect_MongoDB():
        g.conn = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])

def configure_modules(app, modules):
    
    for module, url_prefix in modules:
        app.register_module(module, url_prefix=url_prefix)

if __name__ == '__main__':
    create_app().run()
