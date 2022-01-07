# Secret Transfer Tool

This is a tool to move secrets from one provider to another one

### Providers and actions

There are 2 main types of actions:
- export - extract secrets (or part of secrets, e.g. for a single environment, like at Gitlab)
- import - insert exists secrets from the env file (`key: value` pairs) to provider 
Besides them, there exist few additional actions.

For now, there are only 2 providers, supported:
- AWS Secrets Manager
  - `export` action
  - `import` action
- Gitlab project's environment variables
  - `list` action - short list of variables without format validation and comments
  - `export` action
  - NOTE, action `import` is not supported now

### Setup

- pull this repo
- make sure, that you have Docker and Docker Compose installed
- copy `template.env` file to the `.env` file

### Usage

#### AWS Secrets Manager

Please note, you have to be able to log in to the AWS CLI and have defined `AWS_PROFILE` variable. 
AWS credentials within the `AWS_PROFILE` variable will be passed into the container

###### AWS - Import secrets

- prepare file with secrets' pairs 
- uncomment line to insert new secrets into AWS
- login to the AWS CLI
- run following

```shell
 ~ docker-compose up
[+] Running 1/1
 ⠿ Container secrets-transfer_app_1  Recreated                                                                                                                                                          0.1s
Attaching to app_1
app_1 exited with code 0
```

###### AWS - Export secrets

- login to the AWS CLI
- uncomment line to export secrets from AWS
- run following

```shell
 ~ docker-compose up
[+] Running 1/1
 ⠿ Container secrets-transfer_app_1  Recreated                                                                                                                                                          0.1s
Attaching to app_1
app_1  | There are 3 secrets collected
app_1  | Following secrets were received from the input:
app_1  | {"key1": "val1", "key2": "val2", "key3": "va#$_l\"'`~!2"}
app_1  | Secret 'test-secret2' was successfully created
app_1 exited with code 0
```

- then if you pipe secrets to output file, then you'll be able to find secrets there

```shell
 ~ cat secrets/test-secret2.env
key1: val1
key2: val2
key3: va#$_l"'`~!2
```

#### Gitlab environment variables

Please note, you have to be able to log in to the Gitlab API from your CLI and that you have proper defined `GITLAB_*` variables at the `.env` file.

###### AWS - List secrets

- uncomment line to list secrets from Gitlab
- run following

```shell
 ~ docker-compose up
[+] Running 1/1
 ⠿ Container secrets-transfer_app_1  Recreated                                                                                                                                                          0.1s
Attaching to app_1
app_1  | ...
app_1  | RABBITMQ_PASSWORD: abc   (masked: True, scope: staging)
app_1  | ...
app_1 exited with code 0
```

###### AWS - Export secrets

- uncomment line to export secrets from AWS
- run following

```shell
 ~ docker-compose up
[+] Running 1/1
 ⠿ Container secrets-transfer_app_1  Recreated                                                                                                                                                          0.1s
Attaching to app_1
app_1  | ...
app_1  |
app_1  | # masked: True, environment_scope: staging
app_1  | RABBITMQ_PASSWORD: abc
app_1  |
app_1  | ...
app_1 exited with code 0
```

- then if you pipe secrets to output file, then you'll be able to find secrets there

```shell
 ~ cat secrets/test-secret2.env
...

# masked: True, environment_scope: staging
RABBITMQ_PASSWORD: abc

...
```
