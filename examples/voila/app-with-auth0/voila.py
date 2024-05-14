import nbformat


def hook_function(req, notebook, cwd):
   headers = req.request.headers
   notebook.metadata.user = headers.get('X-Auth-Name', 'Anonymous')
   with open("app_updated.ipynb", 'w') as f:
      nbformat.write(notebook, f)
   return notebook


c.Voila.prelaunch_hook = hook_function