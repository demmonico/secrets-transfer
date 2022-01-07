import sys
import os
import logging
import gitlab
import re


class GitlabVariablesManager:
    def __init__(self, client, project_id):
        self.client = client
        self.project_id = project_id
        self.project = self.client.projects.get(self.project_id)

    def fetch_all_variables(self):
        return self.project.variables.list(all=True)

    def get_variables(self, filter_env=''):
        variables_list = self.fetch_all_variables()
        variables = {}
        self.log = []

        if filter_env == '':
            # when filter is off - return all
            for var in variables_list:
                variables[f'{var.key}_{var.environment_scope}'] = {
                    "key": var.key,
                    "value": var.value,
                    "scope": var.environment_scope,
                    "origin": var,
                }

        else:
            # fetch default values
            for var in variables_list:
                if var.environment_scope == '*':
                    variables[var.key] = {
                        "key": var.key,
                        "value": var.value,
                        "scope": var.environment_scope,
                        "origin": var,
                    }

            # fetch vars for filtered scope values (within override default)
            for var in variables_list:
                if var.environment_scope == filter_env:
                    # log replacement fact
                    if var.key in variables:
                        self.log.append(f'{var.key}: {variables[var.key]["value"]} (scope {variables[var.key]["scope"]}) -> {var.key}: {var.value} (scope {var.environment_scope})')
                    # override default
                    variables[var.key] = {
                        "key": var.key,
                        "value": var.value,
                        "scope": var.environment_scope,
                        "origin": var,
                    }

        return variables

    def get_variables_with_logs(self, filter_env=''):
        return [self.get_variables(filter_env), self.log]

#------------------------------#

def containsAny(str, chars):
    # Check whether sequence str contains ANY of the items in set
    return 1 if any((c in chars) for c in str) else 0

def containsNotSupported(str, pattern = "A-Za-z0-9_"):
    return 1 if re.match('^[' + pattern + ']+$', str) is None else 0

def print_variables_as_list(variables):
    for k,var in sorted(variables.items()):
        print(f'{var["key"]}: {var["value"]}   (masked: {var["origin"].masked}, scope: {var["scope"]})')

def print_variables_with_validation(variables, logs):
    # print variables with the comments
    for k,var in sorted(variables.items()):
        print(f'# masked: {var["origin"].masked}, environment_scope: {var["scope"]}')
        print(f'{var["key"]}: {var["value"]}')

        validation_errors = []
        if containsNotSupported(var["key"]):
            validation_errors.append('!!WARNING!! Key contains not supported characters!')
        if containsAny(var['value'], set('":#')):
            validation_errors.append('!!WARNING!! Value contains special character!')
        if len(validation_errors) > 0:
            print('# ' + ', '.join(validation_errors))

        print()

    # print if there were logs
    if len(logs) > 0:
        print('# !!INFO!! LOGS:')
        for line in logs:
            print(f'# {line}')

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

    if len(sys.argv) > 2:
        action = sys.argv[1]
        project_id = sys.argv[2]
    else:
        raise ValueError('Oops! Empty required args')

    if len(sys.argv) > 3:
        filter_env = sys.argv[3]
    else:
        filter_env = ''

    gl_url = os.environ.get('GITLAB_URL', '')
    if gl_url == '':
        raise ValueError('Oops! Empty GITLAB_URL env var')
    gl_token = os.environ.get('GITLAB_TOKEN', '')
    if gl_token == '':
        raise ValueError('Oops! Empty GITLAB_TOKEN env var')

    manager = GitlabVariablesManager(
        gitlab.Gitlab(gl_url, private_token=gl_token),
        project_id
    )

    if action == 'list':
        variables = manager.get_variables(filter_env)
        print_variables_as_list(variables)

    elif action == 'export':
        variables, logs = manager.get_variables_with_logs(filter_env)
        print_variables_with_validation(variables, logs)

    elif action == 'import':
        # TODO add import action
        raise ValueError(f'Oops! Still TODO action "{action}"')

    else:
        raise ValueError(f'Oops! Unknown action "{action}"')

#------------------------------#

if __name__ == '__main__':
    main()
