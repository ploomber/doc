from jinja2 import Environment, PackageLoader, StrictUndefined


env = Environment(
    loader=PackageLoader("mcp_ploomber", "templates"),
    undefined=StrictUndefined,
)

env.globals["enumerate"] = enumerate
