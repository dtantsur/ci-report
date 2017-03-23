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

    report = {}
    for change in stats.values():
        for revision in change.values():
            for job, info in revision.items():
                if any(x in job for x in excludes):
                    continue

                job_info = report.setdefault(job, {'runs': 0, 'failures': 0})
                job_info['runs'] += 1
                if not info['result']:
                    job_info['failures'] += 1

    log.info("Total job runs: %d", sum(x['runs'] for x in report.values()))
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
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    generate_report(args)
