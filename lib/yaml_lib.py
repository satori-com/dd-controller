# vim: ts=4 sts=4 sw=4 et: syntax=python

import yaml

def get_yaml(path):
    with open(path) as filehandle:
        return yaml.load(filehandle.read())

def format_yaml(config):
    return yaml.safe_dump(config,
                          encoding='utf-8',
                          default_flow_style=False,
                          width=200)
