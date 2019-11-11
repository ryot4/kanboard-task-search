#!/usr/bin/env python3

import argparse
import configparser
import json
import os
import sys
from datetime import datetime

from jinja2 import Environment
from kanboard import Client, ClientError


class Formatter:
    def __init__(self, template, nullify_zero_date=True):
        self._environment = Environment()
        self._template = self._environment.from_string(template)
        self.nullify_zero_date = nullify_zero_date

    def format(self, task, optional_vars={}):
        return self._template.render(self._convert_date(task))

    def _convert_date(self, task):
        for key in [k for k in task.keys() if k.startswith("date_")]:
            if self.nullify_zero_date and task[key] == "0":
                task[key] = None
            if task[key] is not None:
                task[key] = datetime.fromtimestamp(float(task[key]))
        return task


DEFAULT_CONFIG_FILE = os.path.join(os.getenv("HOME"),
                                   ".kanboard_task_search.conf")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config",
                    default=DEFAULT_CONFIG_FILE,
                    help="Specify the config file")
parser.add_argument("-f", "--format",
                    help="Format each task using the given Jinja2 template")
parser.add_argument("--preserve-zero-date",
                    action="store_true",
                    default=False,
                    help="Treat zeroes as Unix epoch when formatting date values")
parser.add_argument("-p", "--projects",
                    help="Search tasks from specified projects (comma-separated)")
parser.add_argument("query")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config)

kb = Client(config["kanboard"]["url"],
              config["kanboard"]["user"],
              config["kanboard"]["api_token"],
              cafile=config["kanboard"]["ca_certificate"])

all_projects = kb.get_my_projects_list()
if args.projects is not None:
    names = args.projects.split(",")
    project_ids = sorted([int(id) for (id, name) in all_projects.items()
                          if name in names])
else:
    project_ids = sorted([int(id) for id in all_projects.keys()])

if len(project_ids) == 0:
    print("No matching project exists: {}".format(args.projects),
          file=sys.stderr)
    sys.exit(1)

tasks = []
for id in project_ids:
    try:
        result = kb.search_tasks(project_id=id, query=args.query)
        tasks.extend(result)
    except ClientError as ex:
        print("error: {}".format(str(ex)), file=sys.stderr)
        sys.exit(1)

if args.format is not None:
    formatter = Formatter(args.format,
                          nullify_zero_date=not args.preserve_zero_date)
    for task in tasks:
        print(formatter.format(task))
else:
    print(json.dumps(tasks))
