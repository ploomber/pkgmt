from jinja2 import Environment, PackageLoader, StrictUndefined


env = Environment(
    loader=PackageLoader("$package_name", "templates"),
    undefined=StrictUndefined,
)

env.globals["enumerate"] = enumerate
