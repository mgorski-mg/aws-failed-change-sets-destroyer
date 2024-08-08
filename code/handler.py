import json
import boto3
import datetime
from botocore.config import Config


def lambda_handler(event, context):
    dry_run = get_dry_run_parameter(event)
    regions = get_regions_parameter(event)
    delete_only_if_created_before = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=-3)

    for region in regions:
        print('REGION: {}'.format(region))
        config = Config(retries={'max_attempts': 50, 'mode': 'standard'})
        cfn_client = boto3.client('cloudformation', region_name=region, config=config)

        n_failed_change_sets = delete_failed_change_sets(cfn_client, delete_only_if_created_before, dry_run)
        print('There were {} failed change sets in {}.'.format(n_failed_change_sets, region))


def delete_failed_change_sets(cfn_client, delete_only_if_created_before, dry_run):
    n_failed_changesets = 0

    stacks_paginator = cfn_client.get_paginator('list_stacks')
    for stacks_response in stacks_paginator.paginate(
            StackStatusFilter=['CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_FAILED', 'UPDATE_COMPLETE', 'UPDATE_FAILED', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE', 'IMPORT_COMPLETE', 'IMPORT_ROLLBACK_FAILED', 'IMPORT_ROLLBACK_COMPLETE']):
        for stack in stacks_response.get('StackSummaries'):
            stack_name = stack['StackName']
            n_failed_changesets += check_stack(stack_name, cfn_client, delete_only_if_created_before, dry_run)

    return n_failed_changesets


def check_stack(stack_name, cfn_client, delete_only_if_created_before, dry_run):
    n_failed_changesets = 0

    paginator = cfn_client.get_paginator('list_change_sets')
    for response in paginator.paginate(StackName=stack_name):
        for change_set in response.get('Summaries'):
            if change_set['Status'] == "FAILED" and change_set["CreationTime"] < delete_only_if_created_before:
                failed_change_set = ChangeSet(change_set['StackName'], change_set['ChangeSetName'])
                print('Removing changeset: {}'.format(json.dumps(failed_change_set, default=lambda x: x.__dict__)))
                n_failed_changesets += 1
                if not dry_run:
                    cfn_client.delete_change_set(StackName=failed_change_set.stack_name, ChangeSetName=failed_change_set.name)

    return n_failed_changesets

def get_dry_run_parameter(event):
    if 'dry_run' not in event:
        return 1
    else:
        return event['dry_run']


def get_regions_parameter(event):
    regions = []

    if 'regions' in event and type(event['regions']) == list:
        regions = event['regions']

    if not regions:
        region_response = boto3.client('ec2').describe_regions()
        regions = [region['RegionName'] for region in region_response['Regions']]

    return regions


class ChangeSet:
    def __init__(self, stack_name, name):
        self.name = name
        self.stack_name = stack_name
