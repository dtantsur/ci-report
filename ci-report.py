#!/usr/bin/env python2

from __future__ import print_function

import logging
import os
import sys

import gertty.config
import gertty.db
import gertty.search
import gertty.sync
import yaml


class App(object):
    def __init__(self):
        self.config = gertty.config.Config()


def gertty_session(db_file_name):
    app = App()
    db = gertty.db.Database(app, 'sqlite:///%s' % db_file_name,
                            gertty.search.SearchCompiler(app.config.username))
    return db.getSession()


def generate_report(session, config):
    log = logging.getLogger('ci-report')
    project = config['project']
    branch = config.get('branch', 'master')

    changes = session.getChanges("project:%s branch:%s" % (project, branch))
    log.info("Got %d changes for %s", len(changes), project)


if __name__ == '__main__':
    try:
        config_file = sys.argv[1]
    except IndexError:
        sys.exit("Usage: %s <config file>" % sys.argv[0])

    with open(config_file, 'rt') as fp:
        config = yaml.safe_load(fp.read())

    db_file_name = os.path.expanduser(config['database'])
    with gertty_session(db_file_name) as session:
        logging.basicConfig(level=logging.INFO)
        generate_report(session, config)
