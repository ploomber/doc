import json


def hook_function(req, notebook, cwd):
   headers = req.request.headers
   user = headers.get('X-Auth-Name', 'Anonymous')
   with open("authentication_data.json", 'w') as json_file:
      json.dump({"user": user}, json_file)
   return notebook


c.Voila.prelaunch_hook = hook_function