#!/usr/bin/env python3
"""
Migrates all Kong 0.14.1 APIs to Services and Routes
Author: Pavel Jelinek, https://github.com/pajel
"""

import os
import requests

#export KONG_URL=http://127.0.0.1:8001
kong_url = os.environ["KONG_URL"]
try:
  kong_migrate = os.environ["KONG_MIGRATE"]
except KeyError:
  kong_migrate = 'False'

# Get first 1000 APIS and process them
resp_apis = requests.get("{}/apis/?size=1000".format(kong_url))
resp_apis_json = resp_apis.json()

if "data" in resp_apis_json:
  if kong_migrate == 'True':
    print("Running migrations: True")
    for api in resp_apis_json["data"]:
      data_service = {'name': api["name"], 'url': api["upstream_url"]}
      print("Migrating API with id: {}, name: {}".format(api["id"], api["name"]))
      print("  Creating service with data: {}".format(data_service))
      resp_service = requests.post("{}/services/".format(kong_url), data_service)
      resp_service_json = resp_service.json()
  
      if "methods" in api:
        data_route = {"paths": api["uris"], "methods": api["methods"], "service": {"id": resp_service_json["id"]}}
      else:
        data_route = {"paths": api["uris"], "service": {"id": resp_service_json["id"]}}
      print("  Creating route with data: {}".format(data_route))
      resp_route = requests.post("{}/routes/".format(kong_url), json=data_route)
  
      resp_plugins = requests.get("{}/plugins/?api_id={}".format(kong_url, api["id"]))
      resp_plugins_json = resp_plugins.json()
      if "data" in resp_plugins_json:
        for plugin in resp_plugins_json["data"]:
          data_plugin = {"name": plugin["name"], "id": plugin["id"], "created_at": plugin["created_at"], "enabled": plugin["enabled"], "service_id": resp_service_json["id"], "config": plugin["config"]}
          print("    Migrating plugin with name: {}".format(plugin["name"]))
          resp_plugin = requests.put("{}/plugins/".format(kong_url), json=data_plugin)
  
      print("  Deleting API: {}".format(api["name"]))
      requests.delete("{}/apis/{}".format(kong_url, api["name"]))
  else:
    print("Running migrations: False")
    for api in resp_apis_json["data"]:
      data_service = {'name': api["name"], 'url': api["upstream_url"]}
      print("Would migrate API with id: {}, name: {}".format(api["id"], api["name"]))
      print("  Would create service with data: {}".format(data_service))
      print("  Would create route with data: {}".format(api["uris"]))
      resp_plugins = requests.get("{}/plugins/?api_id={}".format(kong_url, api["id"]))
      resp_plugins_json = resp_plugins.json()
      if "data" in resp_plugins_json:
        for plugin in resp_plugins_json["data"]:
          print("    Would migrate plugin with name: {}".format(plugin["name"]))
      print("  Would delete API: {}".format(api["name"]))
else:
  print("Nothing to migrate")
