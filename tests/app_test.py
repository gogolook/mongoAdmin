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
import urllib

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
        self.data = self.db.data

class AppTestCase(TestCase):
    
    #def test_site(self):
    #    res = self.client.get('/api/site')
    #    self.assert200(res)
    #    assert res.json['success'] == 'true'

    #    res = self.client.post('/api/site',
    #                           data=json.dumps({'link':'test123'}),
    #                           content_type='application/json')
    #    assert res.json['message'] == "site's name is needed"
    #    assert res.json['success'] == "false"

    def test_create_site(self):
        self.site.remove();

        rules = [
            {'price': '<span>price</span>'},
            {'size': '<span>size</span>'}
        ]
        res = self.client.post('/api/site',
            data=json.dumps({
                'name':'591 sale',
                'link':'www.591.com.tw',
                'rules': rules
            }), content_type='application/json'
        )
        print res.data
        assert res.json['id'] != None
        assert res.json['success'] == "true"

    def test_list_site(self):
        
        res = self.client.get('/api/site')
        print res.json
    #    #self.site_id = res.json['site'][0]['_id']

    #def test_show_site(self):
    #    
    #    res = self.client.get('/api/site')
    #    id = res.json['site'][0]['_id']
    #    url = '/api/site/' + id
    #    res = self.client.post(url,
    #        data=json.dumps({
    #            'field': 'floor',
    #            'rule': '<span>floor</span>'
    #        }), content_type='application/json'
    #    )
    #    assert res.json['message'] == 'creation is done'
    #    assert res.json['success'] == 'true'

    #    res = self.client.post(url,
    #        data=json.dumps({
    #            'field': 'floor',
    #            'rule': '<span>floor</span>'
    #        }), content_type='application/json'
    #    )
    #    
    #    assert res.json['message'] == 'field is exist'
    #    assert res.json['success'] == 'false'

    #def test_upate_rule(self):

    #    res = self.client.get('/api/site')
    #    id = res.json['site'][0]['_id']
    #    url = '/api/site/' + id
    #    res = self.client.put(url,
    #        data=json.dumps({
    #            'field': 'floor',
    #            'rule': 'test'
    #        }), content_type='application/json'
    #    )

    #    assert res.json['message'] == 'update is done'
    #    assert res.json['success'] == 'true'


class testCreateData(TestCase):

    def test_create_data(self):
        self.data.remove()
        
        res = self.client.get('/api/site')
        id = res.json['site'][0]['_id']
        print id
        url = '/api/site/' + id + '/data'
        print url
        data = {'name': "真正的好宅~~太子學院",
                'purpose': "電梯大樓",
                'layout': "2房2廳2衛1陽台",
                'price': 698,
                'unit_price': 17.07,
                'area': 40.9,
                'floor': 7,
                'address': '新北市板橋區龍泉街',
                'operator': '陳先生',
                'house_type': '房仲'
                }
        res = self.client.post(url,
            data=json.dumps({
                'data' : data
            }), content_type='application/json'
        )

        data['floor'] = 8
        res = self.client.post(url,
            data=json.dumps({
                'data' : data
            }), content_type='application/json'
        )

        print res.data
        assert res.json['success'] == 'true'

    def test_get_data(self):
        res = self.client.get('/api/site')
        id = res.json['site'][0]['_id']
        print id
        url = '/api/site/' + id + '/data'
        #print url
        res = self.client.get(url)
        #print res.data

    def test_get_query(self):
        res = self.client.get('api/site')
        id = res.json['site'][0]['_id']
        url = '/api/site/' + id + '/data?sdatetime=2011-03-10'
        res = self.client.get(url)
        assert res.json['data'] != None
        url = '/api/site/' + id + '/data?sdatetime=2011-03-11&edatetime=2011-03-13'
        res = self.client.get(url)
        print res.data
        print urllib.quote('房仲')
        url = '/api/site/' + id + '/data?house_type=' + urllib.quote('房仲')
        res = self.client.get(url)
        print res.data

if __name__ == '__main__':
    unittest.main()
