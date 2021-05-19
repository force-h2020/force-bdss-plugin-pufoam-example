import os


PATH = os.path.dirname(
    os.path.abspath(__file__)
)


def get_file(name, extension=".ttl"):
    return parse_dir(PATH, extension)[name]


def parse_dir(path, extension, libary=dict()):
    for element in os.listdir(path):
        element_path = os.path.join(path, element)
        name, ext = os.path.splitext(element)
        if os.path.isfile(element_path):
            if ext == extension:
                libary[name] = element_path
        else:
            libary = parse_dir(element_path, extension, libary=libary)
    return libary
