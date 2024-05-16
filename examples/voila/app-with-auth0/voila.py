import nbformat


def hook_function(req, notebook, cwd):
   headers = req.request.headers
   user = headers.get('X-Auth-Name', 'Anonymous')
   set_user_cell = f"user = '{user}'\n"
   print_user_cell = f"print(f\"Welcome {user}\")"
   user_cell = nbformat.v4.new_code_cell(source=f"{set_user_cell}{print_user_cell}")
   notebook.cells.insert(0, user_cell)
   return notebook


c.Voila.prelaunch_hook = hook_function