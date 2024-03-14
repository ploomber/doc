c = get_config()  # noqa

c.ServerApp.ip = "0.0.0.0"  # listen on all IPs
c.ServerApp.allow_origin = "*"  # allow access from anywhere


c.LabApp.collaborative = True
