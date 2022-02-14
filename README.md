# AWS Failed Change Set Destroyer
Failed Change Set Destroyer deletes failed change sets from CloudFormation stacks.

Available on the [AWS Serverless Application Repository](https://aws.amazon.com/serverless) - [failed-change-sets-destroyer](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/create/app?applicationId=arn:aws:serverlessrepo:eu-west-1:275418140668:applications/failed-change-sets-destroyer)

## Why is it helpful?
Deploying an unchanged stack creates failed change set which may lead to failure with the following error message:
```
An error occurred (LimitExceededException) when calling the CreateChangeSet operation: ChangeSet limit exceeded for stack ...
```
It means the maximum number of change sets for a stack was reached.

This lambda is removing all failed change sets so the error should not occur.

## Getting Started
### Prerequisites
- Python 3.8+
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

### Deployment
To deploy Failed Change Set Destroyer edit deploy.bat file and change
- \<stack-name> - new stack name 
- \<s3-bucket-name> - s3 bucket name for code and template file needed for deployment of the AWS Lambda
- \<s3-bucket-prefix> - logical folder for the code and template file

Then run the Lambda.

### Input Lambda Event
```json
{
    "dry_run": true,
    "regions": ["us-west-1", "..."]
}
```
### Default values
- dry_run: true
- regions: all regions

# **It is strongly recommended to use dry_run mode first!!**

## Scheduler
Failed Change Set Destroyer by default is scheduled every first day of the month. 

The schedule can be changed by overriding `SchedulerCronParameter`.

The scheduler can be disabled using `SchedulerEnabledParameter`.