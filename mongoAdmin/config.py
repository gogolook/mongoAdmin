# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~~~

    Default configuration
    
    :copyright: (c) 2011 by Kakashi Liu
"""

class DefaultConfig(object):
    """
    Default configuration from a mongodb web admin 
    """

    DEBUG = True

    SECRET_KEY = 'testvulu,4'

    MONGODB_HOST = "localhost"
    MONGODB_PORT = 27017

    DEBUG_LOG = 'logs/debug.log'
    ERROR_LOG = 'logs/error.log'

    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
