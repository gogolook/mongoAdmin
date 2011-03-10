#-*- coding:utf-8 -*-
from flask import Module, g, jsonify, request, make_response
from pymongo.objectid import ObjectId
from datetime import datetime, timedelta

import urllib
import logging
import simplejson
LOG_FILENAME = '/var/www/mongoAdmin/debug.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


api = Module(__name__)

@api.before_request
def before_request():
    g.db = g.conn.estate
    g.sitegroup = g.db.sitegroup
    g.site = g.db.site
    g.data = g.db.data

def error(code, msg):
    response = make_response(jsonify(success = code, message = msg))
    response.status_code = 404
    response.mimetype = 'applcation/json'
    return response

def ok(*args, **kwargs):
    kwargs['success'] = 'true'
    response = make_response(jsonify(*args, **kwargs))
    response.status_code = 200
    response.mimetype = 'application/json'
    return response

@api.route("/")
def index():
    return "Estate Db Restful Api"

@api.route("/site", methods=['GET', 'POST'])
def site():
    """
    GET: get site's data
    POST: create new site
    """
    if request.method == 'GET':
        sites = g.site.find()
        data = []
        for site in sites:
            site['_id'] = str(site['_id'])
            data.append(site)
        
        return ok(site = data)

    elif request.method == 'POST':
        if not request.json:
            return error('false','it is not a json format')
        
        name = request.json.get('name', None)
        link = request.json.get('link', None)
        rules = request.json.get('rules', None)

        if not name:
            return error('false','site\'s name is needed')
        if rules and not isinstance(rules, list):
            return error('false','rule list error!')

        if g.site.find_one({'name': name}):
            #should be redirected
            return error('false','this site is exist')
        else:
            insert_id = g.site.insert({
                'name': name,
                'link': link,
                'rules': rules
            })
            return ok(id = str(insert_id))

@api.route('/site/<id>', methods=['GET','POST','PUT'])
def show_site(id):
    if request.method == 'GET':
        site = g.site.find({'_id': ObjectId(id)})
        if site:
            return ok(site = site)
        else:
            return error('false','this site isn\'t exist')
    elif request.method == 'POST':
        if not request.json:
            return error('false','this is not json format')
        
        #i18n issue
        field = request.json.get('field', None)
        rule = request.json.get('rule', None)

        if not field or not rule:
            return error('false','lack of argument')
        
        site = g.site.find_one({'_id': ObjectId(id)})
        if not site:
            return error('false','id is wrong')

        for r in site['rules']:
            if field in r:
                return error('false','field is exist')
        
        g.site.update({'_id': ObjectId(id)},
            {"$push": {'rules': {field: rule}}})

        return ok(message='creation is done')

    elif request.method == 'PUT':
        if not request.json:
            return error('false','this is not json format')

        field = request.json.get('field', None)
        rule = request.json.get('rule', None)

        if not field or not rule:
            return error('false','lack of argument')

        site = g.site.find_one({'_id': ObjectId(id)})
        if not site:
            return error('false','id is wrong')

        for r in site['rules']:
            if field in r:
                g.site.update({'_id': ObjectId(id)},
                    {'rules': {field: rule}})
                return ok(message='update is done')

        return error('false','field is not exist')

@api.route('/site/<site_id>/data', methods=['GET','POST'])
def data(site_id):
    if request.method == 'GET':
        region = request.args.get('region', None)

        search_sql = {}
        if region: search_sql['info.address'] = {'$regex': urllib.unquote(region)}
        data = g.data.find(search_sql).sort('date')

        response = []
        for d in data:
            site = g.site.find_one({'_id': d['site_id']})
            #logging.debug('%s',d)
            if 'date' in d:
                utc_offset = 8*60*60
                d['date'] = d['date'] + timedelta(seconds=int(utc_offset))
                d['date'] = d['date'].strftime('%Y-%m-%d %H:%M:%S')

            response.append(dict(info=d['info'],
                                 created_at=d['date'],
                                 site_name=site['name'],
                                 site_link=site['link']))

        return ok(data = response)

    elif request.method == 'POST':
        try:
            if not request.json:
                return error('false','it is not a json format')
        except simplejson.decoder.JSONDecodeError:
            return error('false','check out your json format')

	#data = request.json['data']
	#logging.debug("%s", request.json)
        data = request.json.get('data', None)
        if not data:
            return error('false','no data')

        #TODO: check which field is not be setting
        #check_valid(data)

        #logging.debug("%s",site_id)
        site = g.site.find_one({'_id': ObjectId(site_id)})
        if not site:
            return error('false','id is wrong')

        #logging.debug("%s", site_id)
        #logging.debug("real case:%s", str(g.site.find_one()['_id']))
        data_id = g.data.insert({
            'site_id': ObjectId(site_id),
            'info': data,
            'date': datetime.utcnow()
        })
        #logging.debug("real case:%s", str(g.data.find_one()['site_id']))

        return ok(id = str(data_id))
