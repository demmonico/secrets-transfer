import os
import sys
import boto3
from botocore.exceptions import ClientError
import json
import logging


class AwsSecretsManager:
    def __init__(self, client):
        self.client = client

    def get_secret(self, secret_name):
        try:
            response = self.client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ExpiredTokenException':
                raise ValueError("Oops! AWS token has been expired! Refresh it!")
            else:
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            if 'SecretString' not in response:
                raise ValueError("Oops! Unexpected binary value")

            return json.loads(response['SecretString'])

    def is_secret_exists(self, secret_name):
        try:
            self.get_secret(secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return 0
            else:
                raise ValueError("Oops! Unexpected error: %s" % e)
        else:
            return 1

    def create_secret(self, secret_name, secret_value):
        try:
            response = self.client.create_secret(
                Name=secret_name,
                SecretString=secret_value
            )

            print(f"Secret '{secret_name}' was successfully created")
        except ClientError as e:
            raise e
        else:
            return response

#------------------------------#

def get_client(region_name):
    # Create a Secrets Manager client
    # It requires to be logged in AWS (have AWS_PROFILE env var defined)
    session = boto3.session.Session(
        region_name=region_name
    )

    client = session.client(
        service_name='secretsmanager'
    )

    return client


def read_secrets_from_stdin():
    lines = sys.stdin.readlines()
    if len(lines) == 0:
        raise ValueError("Oops! No data at the STDIN")

    data = []
    for line in lines:
        line = line.rstrip()
        pair = line.split(': ')
        data.append(pair)

    print(f"There are {len(data)} secrets collected")

    return dict((k,v) for k,v in data)


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

    if len(sys.argv) > 2:
        action = sys.argv[1]
        secret_name = sys.argv[2]
    else:
        raise ValueError('Oops! Empty required args')

    region_name = os.environ.get('AWS_REGION', "eu-central-1")
    sm = AwsSecretsManager(get_client(region_name))

    if action == 'export':
        secrets = sm.get_secret(secret_name)
        for k,v in sorted(secrets.items()):
            print(f'{k}: {v}')

    elif action == 'import':
        secrets = json.dumps(read_secrets_from_stdin())
        print(f"Following secrets were received from the input: \n{secrets}")

        if sm.is_secret_exists(secret_name):
            raise ValueError(f"Oops! Secret naming '{secret_name}' exists. Unable to re-create it.")

        sm.create_secret(secret_name, secrets)

    else:
        raise ValueError(f'Oops! Unknown action "{action}"')

#------------------------------#

if __name__ == '__main__':
    main()
