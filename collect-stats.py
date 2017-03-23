#!/usr/bin/env python2

from __future__ import print_function

import argparse
import datetime
import logging
import os

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
    session = db.getSession()
    session.app = app
    return session


def get_ci_stats(session, revision, threshold):
    stats = {}
    for message in revision.messages:
        if message.created < threshold:
            continue

        for commentlink in session.app.config.commentlinks:
            test = commentlink.getTestResults(session.app, message.message)
            if not test:
                continue

            for key, value in test.items():
                stats[key] = {
                    'result': any('test-SUCCESS' in item
                                  for item in value
                                  if isinstance(item, tuple))
                }
    return stats


def generate_report(session, args):
    log = logging.getLogger('ci-report')
    stats = {}
    threshold = (datetime.datetime.now() -
                 datetime.timedelta(days=args.threshold))

    changes = session.getChanges("project:%s branch:%s" %
                                 (args.project, args.branch))
    changes = [c for c in changes if c.updated >= threshold]
    log.info("Got %d changes for %s", len(changes), args.project)
    for change in changes:
        log.debug("Processing change %s", change.number)
        change_stats = {}
        for revision in change.revisions:
            change_stats[revision.number] = get_ci_stats(session, revision,
                                                         threshold)
        stats[change.number] = change_stats

    log.info("Writing result to %s", args.output)
    with open(args.output, 'wt') as fp:
        yaml.safe_dump(stats, fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', help='Gertty database file',
                        default=os.path.expanduser('~/.gertty.db'))
    parser.add_argument('-b', '--branch', help='Git branch',
                        default='master')
    parser.add_argument('-o', '--output', help='Output file',
                        default='ci-stats.yaml')
    parser.add_argument('-t', '--threshold', help='Days to collect stats',
                        default=30, type=int)
    parser.add_argument('project', help='Project to collect stats for')
    args = parser.parse_args()

    with gertty_session(args.database) as session:
        logging.basicConfig(level=logging.INFO)
        generate_report(session, args)
