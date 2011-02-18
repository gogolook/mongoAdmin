#-*- coding:utf-8 -*-
from flask import Module, g, jsonify, request, make_response
from pymongo.objectid import ObjectId

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
        rules_list = request.json.get('rules', None)

        if not name:
            return error('false','site\'s name is needed')
        if rules_list and not isinstance(rules_list, dict):
            return error('false','rule list error!')

        if g.site.find_one({'name': name}):
            #should be redirected
            return error('false','this site is exist')
        else:
            insert_id = g.site.insert({
                'name': name,
                'link': link,
                'rules_list': rules_list
            })
            return ok(id = str(insert_id))
