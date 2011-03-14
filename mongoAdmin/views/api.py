#-*- coding:utf-8 -*-
from flask import Module, g, jsonify, request, make_response
from pymongo.objectid import ObjectId
from datetime import datetime, timedelta
import time
import urllib
import simplejson

import logging
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

def getTimeStamp(datetime_str):
    if datetime_str:
        d = datetime.strptime(datetime_str, '%Y-%m-%d')
        return d
        #return time.mktime(d.timetuple()) + 1e-6 * d.microsecond
    else:
        return None

def parseQuery(request):
    search_sql = {}
    stimestamp = getTimeStamp(request.args.get('sdatetime', None))
    etimestamp = getTimeStamp(request.args.get('edatetime', None))
    house_type = request.args.get('house_type', None)
    id = request.args.get('id', None)
    region = request.args.get('region', None)

    if stimestamp or etimestamp:
        search_sql['date'] = {}
    if stimestamp:
        sql = {'$gte': stimestamp}
        search_sql['date'].update(sql)
    if etimestamp:
        sql = {'$lte': etimestamp}
        search_sql['date'].update(sql)
    if house_type:
        search_sql['info.house_type'] = urllib.unquote(house_type)
    if id:
        search_sql['_id'] = id
    if region:
        search_sql['info.address'] = {'$regex': urllib.unquote(region)}

    return search_sql

    #address = request.args.get('address', None)
    #address_contain = request.args.get('address_contain', None)

@api.route('/site/<site_id>/data', methods=['GET','POST'])
def data(site_id):
    site = g.site.find_one({'_id': ObjectId(site_id)})
    if not site:
        return error('false','id is wrong')

    if request.method == 'GET':
        search_sql = parseQuery(request)
        search_sql['site_id'] = ObjectId(site_id)
        limit_num = request.args.get('limit', 20)

        data = g.data.find(search_sql).sort('date').limit(limit_num)

        response = []
        for d in data:
            site = g.site.find_one({'_id': d['site_id']})
            #logging.debug('%s',d)
            if 'date' in d:
                logging.debug('%s', d['date'])
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
