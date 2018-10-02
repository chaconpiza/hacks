#!/usr/bin/python

import datetime
import json
import requests
import sys
import time
from pprint import pprint

KEYSTONE_URI = 'http://localhost/identity/v3/auth/tokens'
EVENTS_API_URI = 'http://192.168.10.6:5656/v1.0/events'  


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
               #'Content-Type': 'torta/dejamon',
               'X-Auth-Token': token} 
    return headers


def events_data(event_type):
    format = '%Y-%m-%dT%H:%M:%SZ'
    unix_epoch = time.time()
    ts = datetime.datetime.fromtimestamp(unix_epoch)
    data = '''
    {
      "timestamp": "%s",
      "events": [
        {
          "dimensions": {
            "service": "compute",
            "topic": "notification.sample",
            "hostname": "nova-compute:compute"
          },
          "project_id": "887c838f758c4ea7ba88ad966542b28e",
          "event": {
            "event_type": "%s",
            "payload": {
              "nova_object.data": {
                "architecture": "x86_64",
                "availability_zone": "nova",
                "created_at": "2018-07-18T10:01:11Z",
                "deleted_at": null,
                "display_name": "some-server",
                "display_description": "some-server",
                "fault": null,
                "host": "compute",
                "host_name": "some-server",
                "ip_addresses": [
                  {
                    "nova_object.name": "IpPayload",
                    "nova_object.namespace": "nova",
                    "nova_object.version": "1.0",
                    "nova_object.data": {
                      "mac": "fa:16:3e:4c:2c:30",
                      "address": "192.168.1.3",
                      "port_uuid": "ce531f90-199f-48c0-816c-13e38010b442",
                      "meta": {},
                      "version": 4,
                      "label": "private-network",
                      "device_name": "tapce531f90-19"
                    }
                  }
                ],
                "key_name": "my-key",
                "auto_disk_config": "MANUAL",
                "kernel_id": "",
                "launched_at": "2018-07-18T10:02:11Z",
                "image_uuid": "155d900f-4e14-4e4c-a73d-069cbf4541e6",
                "metadata": {},
                "locked": false,
                "node": "fake-mini",
                "os_type": null,
                "progress": 0,
                "ramdisk_id": "",
                "reservation_id": "r-npxv0e40",
                "state": "active",
                "task_state": null,
                "power_state": "running",
                "tenant_id": "12345678123456781234567812345678",
                "terminated_at": null,
                "flavor": {
                  "nova_object.name": "FlavorPayload",
                  "nova_object.data": {
                    "flavorid": "a22d5517-147c-4147-a0d1-e698df5cd4e3",
                    "name": "test_flavor",
                    "projects": null,
                    "root_gb": 1,
                    "vcpus": 1,
                    "ephemeral_gb": 0,
                    "memory_mb": 512,
                    "disabled": false,
                    "rxtx_factor": 1.0,
                    "extra_specs": {
                      "hw:watchdog_action": "disabled"
                    },
                    "swap": 0,
                    "is_public": true,
                    "vcpu_weight": 0
                  },
                  "nova_object.version": "1.3",
                  "nova_object.namespace": "nova"
                },
                "user_id": "fake",
                "uuid": "178b0921-8f85-4257-88b6-2e743b5a975c"
              },
              "nova_object.name": "InstanceActionPayload",
              "nova_object.namespace": "nova",
              "nova_object.version": "1.3"
            },
            "priority": "INFO",
            "publisher_id": "nova-compute:compute"
          }
        }
      ]
    }
    ''' % (str(ts.strftime(format)), event_type)
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


def set_event(token, event_type):
    r = requests.post(
        EVENTS_API_URI,
        data=events_data(event_type),
        headers=events_headers(token))

    if r.status_code != 200:
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
    set_event(token, event_type)


if __name__ == "__main__":
    main(sys.argv[1:])

