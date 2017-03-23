#!/usr/bin/env python2

import argparse
import logging

import yaml


def generate_report(args):
    log = logging.getLogger('ci-report')

    log.info("Reading stats from %s", args.input)
    with open(args.input, 'rt') as fp:
        stats = yaml.safe_load(fp)

    log.info("Got %d changes with total of %d revisions", len(stats),
             sum(len(x) for x in stats.values()))

    excludes = args.exclude.split(',')

    report = {'jobs': {}}
    for change in stats.values():
        for revision in change.values():
            for job, info in revision.items():
                if any(x in job for x in excludes):
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
    parser.add_argument('-i', '--input', help='Input file',
                        default='ci-stats.yaml')
    parser.add_argument('-o', '--output', help='Output file',
                        default='ci-report.yaml')
    parser.add_argument('-x', '--exclude', help='List of patterns to exclude',
                        default='requirements,docs,releasenote,tox,api-ref,'
                        'install-guide,coverage,tripleo-ci')
    parser.add_argument('--max-failure-rate', default=0.75, type=float)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    generate_report(args)
