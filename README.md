# kanboard-task-search

Search tasks in [Kanboard](https://kanboard.org/) from the command line.

## Installation and configuration

Install dependencies:

```
$ pip install -r requirements.txt
```

Create the configuration file (`${HOME}/.kanboard_task_search.conf`):

```
[kanboard]
# Kanboard API endpoint
url = https://kanboard.example.com/jsonrpc.php

# Username in Kanboard
user = your-user-name

# Personal API access token
api_token = your-api-access-token

# CA certificate file path
# Necessary if your Kanboard instance uses a certificate signed by the private CA
ca_certificate = /path/to/ca-certificate.crt
```

## Usage

You can use the same query language as in Kanboard Web interface.

Search by keyword (`kanboard`):

```
$ kanboard-task-search kanboard
```

Search by task attributes:

```
$ kanboard-task-search 'status:open due:<"next month"'
```

See [Advanced Search Syntax in Kanboard documentation](https://docs.kanboard.org/en/latest/user_guide/search.html) for the details.

### Limiting search scope

By default, searching is done in all projects that you have access to.

To limit search scope, specify the comma-separeted list of project names with `-p` option.

```
$ kanboard-task-search -p Project1,Project2 status:open
```

### Formatting search results

By default, kanboard-task-search prints the response of [searchTasks API](https://docs.kanboard.org/en/latest/api/task_procedures.html#searchtasks) as is (in JSON format).

With `-f` option, you can format search results with Jinja2 template.

 - The template is applied to each task, and tasks are printed one per line
 - Keys in the API response can be used as variables in the template

The following example prints IDs and titles of open tasks assigned to you.

```
$ kanboard-task-search -f '#{{ id }} {{ title }}' 'status:open assignee:me'
```

The default format can be specified in the configuration. (You can disable it with `-u` option when necessary)

```
[default]
format = #{{ id }} {{ title }}
```
