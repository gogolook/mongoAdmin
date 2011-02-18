# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~

    mongoAdmin functional testing

    :copyright: (c) 2011 by kakashi Liu
"""
import os
import sys
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

from flask import g, json
from flaskext.testing import TestCase as Base, Twill
import unittest
from pymongo import Connection
from mongoAdmin import create_app

class TestCase(Base):
    """
    Base TestClass for your application
    """

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        self.twill = Twill(app, port=3000)
        return app
    
    def setUp(self):
        self.db = Connection('localhost', 27017).estate
        self.site = self.db.site

class AppTestCase(TestCase):
    
    def test_site(self):
        res = self.client.get('/api/site')
        self.assert200(res)
        assert res.json['success'] == 'true'

        res = self.client.post('/api/site',
                               data=json.dumps({'link':'test123'}),
                               content_type='application/json')
        assert res.json['message'] == "site's name is needed"
        assert res.json['success'] == "false"


    def test_create_site(self):
        self.site.remove({'name': '591 rent!'});

        rules = {
            'price': '<span>price</span>',
            'size': '<span>size</span>'
        }
        res = self.client.post('/api/site',
            data=json.dumps({
                'name':'591 rent!',
                'link':'www.591.com.tw',
                'rules': rules
            }), content_type='application/json'
        )
        #print res.data
        assert res.json['id'] != None
        assert res.json['success'] == "true"

    #def test_list_site(self):
        
    #    res = self.client.get('/api/site')
    #    print res.data

if __name__ == '__main__':
    unittest.main()
