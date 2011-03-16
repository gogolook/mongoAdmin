#-*- coding:utf-8 -*-
from flask import Module, g, jsonify, request, render_template, make_response
from pymongo.objectid import ObjectId
import simplejson
import os
from subprocess import call

web = Module(__name__)

@web.before_request
def before_request():
    g.db = g.conn.estate
    g.site = g.db.site

def error(msg):
    pass

@web.route("/")
def index():
    return "Estate Db Restful Api"

@web.route("/crawler", methods=['GET', 'POST'])
def add_crawler():
    """
    GET: get site's data
    POST: create new site
    """
    if request.method == 'GET':
        entries = g.site.find_one()
        return render_template('create_crawler.html', entries = entries)
    if request.method == 'POST':
        eng_name = request.form.get('eng_name', None)
        chi_name = request.form.get('chi_name', None)
        url = request.form.get('url', None)
        regex_url = request.form.get('regex_url', None)

        eng_fields = request.form.getlist('eng_field', None)
        chi_fields = request.form.getlist('chi_field', None)
        rule_fields = request.form.getlist('rule', None)

        rules = []
        rule = {}
        index = 0
        while eng_fields and index < len(eng_fields):
            rule['eng'] = eng_fields[index]
            rule['chi'] = chi_fields[index]
            rule['key'] = rule_fields[index]
            rules.append(rule)
            index += 1

        if g.site.find_one({'name': eng_name}):
            return "this english name is existed"
        else:
            insert_id = g.site.insert({
                'name': eng_name,
                'link': url,
                'rules': rules
            })

        cfg = {}
        cfg['host'] = "173.255.240.110"
        cfg['_id'] = str(insert_id)
        cfg['fetch_page'] = regex_url
        cfg['start_url'] = url
        cfg['name'] = eng_name
        cfg['rules'] = rules

        cfg_file = simplejson.dumps(cfg)

        os.chdir("/home/kakashi/python/estate_crawler")
        os.system("scrapy genspider -t crawler %s %s %s" % (eng_name,url,eng_name))
        f = open("/home/kakashi/python/estate_crawler/cfg/%s" % eng_name, "w")
        f.write(cfg_file)
        f.close()

        response = make_response(jsonify(host="173.255.240.110",
                              _id = str(insert_id),
                              fetch_page = regex_url,
                              start_url = url,
                              name = eng_name,
                              rules = rules))

        return response
