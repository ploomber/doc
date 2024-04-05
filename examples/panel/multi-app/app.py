import panel as pn

pn.extension()

first = pn.panel("first")
second = pn.panel("second")

apps = {
    "first": first,
    "second": second,
}

pn.serve(apps)
