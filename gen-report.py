#!/usr/bin/env python2

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


def generate_stats(session, args, config):
    log = logging.getLogger('ci-report')
    stats = {}
    threshold = (datetime.datetime.now() -
                 datetime.timedelta(days=args.threshold))

    changes = session.getChanges("project:%s branch:%s" %
                                 (config['project'], config['branch']))
    changes = [c for c in changes if c.updated >= threshold]
    log.info("Got %d changes for %s", len(changes), config['project'])
    for change in changes:
        log.debug("Processing change %s", change.number)
        change_stats = {}
        for revision in change.revisions:
            change_stats[revision.number] = get_ci_stats(session, revision,
                                                         threshold)
        stats[change.number] = change_stats

    log.info("Writing detailed stats to %s", args.stats)
    with open(args.stats, 'wt') as fp:
        yaml.safe_dump(stats, fp)


def generate_report(args, config):
    log = logging.getLogger('ci-report')

    log.debug("Reading stats from %s", args.stats)
    with open(args.stats, 'rt') as fp:
        stats = yaml.safe_load(fp)

    log.info("Got %d changes with total of %d revisions", len(stats),
             sum(len(x) for x in stats.values()))

    report = {'jobs': {}}
    for change in stats.values():
        for revision in change.values():
            for job, info in revision.items():
                if any(x in job for x in config['exclude']):
                    continue

                job_info = report['jobs'].setdefault(
                    job, {'runs': 0, 'failures': 0})
                job_info['runs'] += 1
                if not info['result']:
                    job_info['failures'] += 1

    failure_rates = {}
    for job, data in report['jobs'].items():
        if data['runs']:
            data['failure_rate'] = float(data['failures']) / data['runs']
            if data['failure_rate'] > args.max_failure_rate:
                failure_rates[job] = data['failure_rate']

    report['worst_failure_rates'] = [
        {'job': job, 'rate': rate} for (job, rate) in
        sorted(failure_rates.items(), key=lambda x: x[1],
               reverse=True)
    ]

    log.info("Total job runs: %d", sum(x['runs'] for x in
                                       report['jobs'].values()))
    log.info("Writing result to %s", args.output)
    with open(args.output, 'wt') as fp:
        yaml.safe_dump(report, fp, default_flow_style=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database', help='Gertty database file',
                        default=os.path.expanduser('~/.gertty.db'))
    parser.add_argument('-t', '--threshold', help='Days to collect stats',
                        default=30, type=int)
    parser.add_argument('-s', '--stats', help='Stats input file',
                        default='ci-stats.yaml')
    parser.add_argument('-o', '--output', help='Final output file',
                        default='ci-report.yaml')
    parser.add_argument('--max-failure-rate', default=0.75, type=float)
    parser.add_argument('config', help='Project configuration')
    args = parser.parse_args()

    with open(args.config, 'rt') as fp:
        config = yaml.safe_load(fp)

    with gertty_session(args.database) as session:
        logging.basicConfig(level=logging.INFO)
        generate_stats(session, args, config)

    generate_report(args, config)
