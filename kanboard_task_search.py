#!/usr/bin/env python3

import argparse
import configparser
import json
import os
import sys

from kanboard import Kanboard
from kanboard.exceptions import KanboardClientException

DEFAULT_CONFIG_FILE = os.path.join(os.getenv("HOME"),
                                   ".kanboard_task_search/config")

parser = argparse.ArgumentParser()
parser.add_argument("--config",
                    default=DEFAULT_CONFIG_FILE,
                    help="Kanboard API config")
parser.add_argument("--projects",
                    help="Comma separated list of project names")
parser.add_argument("query")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config)

kb = Kanboard(config["kanboard"]["url"],
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
    except KanboardClientException as ex:
        print("error: {}".format(str(ex)), file=sys.stderr)
        sys.exit(1)
print(json.dumps(tasks))
