#! /usr/bin/env python3

'''
workflow2env.py will parse the workflow file for GitHub Actions and output
environments variables.
'''

import shlex
import yaml


def workflow_to_env(res, workflow_env):
    for k, v in workflow_env.items():
        res[k] = v


def print_env(res):
    for k, v in res.items():
        k, v = (shlex.quote(k), shlex.quote(v))
        print(f'export {k}={v}')


def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser(
            prog=sys.argv[0],
            description='Parse workflow file and output env',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--workflow', '-w', default=None,
                        help='YAML workflow file')
    parser.add_argument('--job', '-j', default=None, help='Job name')
    parser.add_argument('--env', '-e', default=None,
                        help='Environments to print separated by commas (,)')
    args = parser.parse_args()

    with open(args.workflow) as f:
        y = yaml.safe_load(f)

    env = {}
    workflow_to_env(env, y['env'])

    if args.job:
        workflow_to_env(env, y['jobs'][args.job]['env'])

    if args.env:
        ee = {}
        for e in args.env.split(','):
            ee[e] = env[e]
        env = ee

    print_env(env)


if __name__ == '__main__':
    main()
