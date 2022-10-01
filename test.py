from pathlib import Path


def likely_python_module(filename):
    paths = []

    if (p := Path(filename).resolve()).name == "__init__.py":
        paths.append(p.stem)

    while not Path(".").samefile(p := p.parent):
        paths.append(p.stem)

    return ".".join(reversed(paths))


# print(get_absolute_name_from_path("./bot/core/events.py"))
print(likely_python_module(Path("./bot/__init__.py")))
