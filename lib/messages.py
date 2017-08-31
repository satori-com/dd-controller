# vim: ts=4 sts=4 sw=4 et: syntax=python

import sys

def error(message):
    message = "ERROR: %s" % (message)
    print >> sys.stderr, '\x1b[0;31m' + message + '\x1b[0m'
    exit(1)

def warning(message):
    message = "WARNING: %s" % (message)
    print >> sys.stderr, '\x1b[0;33m' + message + '\x1b[0m'
