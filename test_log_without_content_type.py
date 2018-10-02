#!/usr/bin/python

import datetime
import json
import requests
import sys
import time
from pprint import pprint

KEYSTONE_URI = 'http://localhost/identity/v3/auth/tokens'
EVENTS_API_URI = 'http://192.168.10.6/logs/v3.0/logs'

def keystone_headers():
    return {'Content-Type': 'application/json'}


def keystone_data(user_name='mini-mon', user_password='password', project_name='mini-mon'):
    data = """
    { 
      "auth": {
        "identity": { 
          "methods": ["password"],
          "password": {
            "user": { 
              "name": "%s",
              "domain": { "id": "default" },
              "password": "%s"
            }
          }
        },
        "scope": {
          "project": {
            "domain": { "id": "default" },
            "name": "%s"
          }
        }
      }
    }
    """ % (user_name, user_password, project_name)
    return data


def events_headers(token):
    headers = {
               #'Content-Type': 'application/json',
               'X-Auth-Token': token} 
    return headers


def events_data(event_type, tenant_id):
    format = '%Y-%m-%dT%H:%M:%SZ'
    unix_epoch = time.time()
    ts = datetime.datetime.fromtimestamp(unix_epoch)
    data = '''
    {
       "dimensions":{},
       "logs":[
             {
               "message":"pizza",
               "dimensions":{
                  "component":"mysql",
                  "path":"/var/log/mysql.log"
               }
             }
           ]
    }
    '''
    return data


def get_token():
    r = requests.post(
        KEYSTONE_URI,
        data=keystone_data(),
        headers=keystone_headers())

    if r.status_code != 201:
        print "\n+++++++++++++++++++++++++++++++++"
        print "+ Error calling to Keystone     +"
        print "+++++++++++++++++++++++++++++++++"
        pprint(vars(r))
        raise Exception(r.status_code, r.text)
    print "\n+++++++++++++++++++++++++++++++++"
    print "+ Successful call to Keystone   +"
    print "+++++++++++++++++++++++++++++++++"
    pprint(vars(r))
    return r.headers['X-Subject-Token'], json.loads(r._content)['token']['project']['id']


def set_event(token, event_type, tenant_id):
    r = requests.post(
        EVENTS_API_URI,
        data=events_data(event_type, tenant_id),
        headers=events_headers(token))

    if r.status_code not in [200, 201, 202, 203, 204]:
        print "\n+++++++++++++++++++++++++++++++++"
        print "+ Error calling to Events Api   +"
        print "+++++++++++++++++++++++++++++++++"
        pprint(vars(r))
        raise Exception(r.status_code, r.text)
    print "\n+++++++++++++++++++++++++++++++++"
    print "+ Successful call to Events Api +"
    print "+++++++++++++++++++++++++++++++++"
    pprint(vars(r))


def main(argv):

    if len(sys.argv) == 1:
         event_type = 'instance.reboot.test'
    else:
         event_type = str(sys.argv[1])

    token, tenant_id = get_token()
    set_event(token, event_type, tenant_id)


if __name__ == "__main__":
    main(sys.argv[1:])

