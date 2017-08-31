#!/usr/bin/env python
# vim: ts=4 sts=4 sw=4 et: syntax=python

import sys

from argparse import ArgumentParser

from lib.comparator import Comparator
from lib.yaml_lib import format_yaml, get_yaml
from lib.exceptions import CustomException
from lib.common import list2map_ex
from lib.messages import error
from lib.remote_config import RemoteConfig
from lib.datadog_api import DatadogApi

EXAMPLE_MONITORS = '[HelloWorld AWS Sydney]'
EXAMPLE_SCREENBOARD = 'HelloWorld Production'

class Control(object):

    @classmethod
    def read(cls, args):
        print format_yaml(cls._get_remote_config(args))

    @classmethod
    def compare(cls, args):
        local_config = cls._get_local_config(args)
        RemoteConfig.check_config_static(local_config)

        remote_config = cls._get_remote_config(args)
        Comparator.compare("local config", cls._to_comparable(local_config),
                           "remote config", cls._to_comparable(remote_config))

    @classmethod
    def update(cls, args):
        remote_config = cls._get_remote_config_instance(args)
        remote_config.update(cls._get_local_config(args), args.update_only)
        print >> sys.stderr, "Updated via %d API calls." \
                             % (DatadogApi.get_api_calls())

    @classmethod
    def _to_comparable(cls, config):
        if "screenboard" in config:
            config["screenboard"]["widgets"]["items"] = \
                list2map_ex(config["screenboard"]["widgets"]["items"],
                            RemoteConfig.get_widget_key_field,
                            config["screenboard"]["widgets"]["defaults"])
        if "monitors" in config:
            config["monitors"]["items"] = \
                list2map_ex(config["monitors"]["items"],
                            RemoteConfig.get_monitor_key_field,
                            config["monitors"]["defaults"])

        return config

    @classmethod
    def _get_remote_config_instance(cls, args):
        return RemoteConfig(api_key=args.api_key, app_key=args.app_key)

    @classmethod
    def _get_remote_config(cls, args):
        remote_config = cls._get_remote_config_instance(args)
        return remote_config.get(monitors_filter=args.monitors,
                                 screenboard_name=args.screenboard)

    @classmethod
    def _get_local_config(cls, args):
        return get_yaml(args.config)

def add_monitors_arg(cmd):
    cmd.add_argument("--monitors", "-m",
                     metavar='MONITORS',
                     type=str,
                     help="is a monitors search filter")

def add_screenboard_arg(cmd):
    cmd.add_argument("--screenboard", "-s",
                     metavar='SCREENBOARD',
                     type=str,
                     help="is a screenboard name")

def add_config_arg(cmd):
    cmd.add_argument("config",
                     metavar='CONFIG',
                     type=str,
                     help="is a config file")

def create_read_command(parser):
    help_msg = ("Print a remote config in YaML format")
    epilog_msg = ("Example: %(cmd)s read"
                  " -m '%(example_monitors)s'"
                  " -s '%(example_screenboard)s'") \
                  % {"cmd": sys.argv[0],
                     "example_monitors": EXAMPLE_MONITORS,
                     "example_screenboard": EXAMPLE_SCREENBOARD}
    cmd = parser.add_parser("read", help=help_msg,
                            epilog=epilog_msg)
    add_monitors_arg(cmd)
    add_screenboard_arg(cmd)
    cmd.set_defaults(func=Control.read)

def create_compare_command(parser):
    help_msg = ("Compare the remote config with a local config file")
    epilog_msg = ("Example: %(cmd)s compare file1.yml"
                  " -m '%(example_monitors)s'"
                  " -s '%(example_screenboard)s'") \
                  % {"cmd": sys.argv[0],
                     "example_monitors": EXAMPLE_MONITORS,
                     "example_screenboard": EXAMPLE_SCREENBOARD}
    cmd = parser.add_parser("compare", help=help_msg,
                            epilog=epilog_msg)
    add_config_arg(cmd)
    add_monitors_arg(cmd)
    add_screenboard_arg(cmd)
    cmd.set_defaults(func=Control.compare)

def create_update_command(parser):
    help_msg = ("Update the remote config according to a local config file")
    epilog_msg = ("Example: %(cmd)s update file1.yml") \
                  % {"cmd": sys.argv[0]}
    cmd = parser.add_parser("update", help=help_msg,
                            epilog=epilog_msg)
    add_config_arg(cmd)
    cmd.add_argument("--update-only", "-u",
                     action='store_true',
                     help="only update the existing records")
    cmd.set_defaults(func=Control.update)

def main():
    description = ("Datadog controller:"
                   " a tool to search monitors by filter"
                   " and a screenboard by name"
                   " in the remote Dadadog,"
                   " to analyze and update the data")
    parser = ArgumentParser(description=description)
    commands_parser = parser.add_subparsers(title="commands",
                                            metavar="COMMAND",
                                            dest="command")
    parser.add_argument("--api-key",
                        help="is an API key",
                        type=str)
    parser.add_argument("--app-key",
                        help="is an app key",
                        type=str)

    create_read_command(parser=commands_parser)
    create_compare_command(parser=commands_parser)
    create_update_command(parser=commands_parser)

    args = parser.parse_args()
    try:
        args.func(args)
    except CustomException as ex:
        error(ex.message)

if __name__ == "__main__":
    main()
