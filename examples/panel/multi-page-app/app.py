import panel as pn

pn.extension()

first = pn.panel("first")
second = pn.panel("second")

apps = {
    "first": first,
    "second": second,
}

pn.serve(apps, port=80, address="0.0.0.0", allow_websocket_origin=['*'])
