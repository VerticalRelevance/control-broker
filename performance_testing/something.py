mydict = {
    "executionArn": "arn:aws:states:us-east-1:899456967600:express:OuterEvalEngine-4xU7ThrzEa6d:c8d80fe6-0d78-46bd-a143-2ec914a068ff:b1dae69c-a8dc-4690-ac86-972b287f9251",
    "stateMachineArn": "arn:aws:states:us-east-1:899456967600:stateMachine:OuterEvalEngine-4xU7ThrzEa6d",
    "name": "c8d80fe6-0d78-46bd-a143-2ec914a068ff",
    "startDate": datetime.datetime(2022, 2, 24, 14, 21, 30, 294000, tzinfo=tzlocal()),
    "stopDate": datetime.datetime(2022, 2, 24, 14, 21, 30, 863000, tzinfo=tzlocal()),
    "status": "SUCCEEDED",
    "input": '{"CFN": {"Bucket": "controlbrokerevalenginec-synthedtemplates0e9d7f0b-gglzcwvj3muj", "Keys": ["performance_testing_example_cfn_template.json"]}}',
    "inputDetails": {"included": True},
    "output": '{"CFN":{"Bucket":"controlbrokerevalenginec-synthedtemplates0e9d7f0b-gglzcwvj3muj","Keys":["performance_testing_example_cfn_template.json"]},"ForEachTemplate":[{"Template":{"Bucket":"controlbrokerevalenginec-synthedtemplates0e9d7f0b-gglzcwvj3muj","Key":"performance_testing_example_cfn_template.json"},"TemplateToNestedSFN":{"BillingDetails":{"BilledDurationInMilliseconds":600,"BilledMemoryUsedInMB":64},"ExecutionArn":"arn:aws:states:us-east-1:899456967600:express:InnerEvalEngine-N89zbR76HmB3:43b60995-1964-4674-9751-c4bb96a7d920:4ece06fa-3f4b-41df-b704-5f9a25798c66","Input":"{\\"Template\\":{\\"Bucket\\":\\"controlbrokerevalenginec-synthedtemplates0e9d7f0b-gglzcwvj3muj\\",\\"Key\\":\\"performance_testing_example_cfn_template.json\\"}}","InputDetails":{"Included":true},"Name":"43b60995-1964-4674-9751-c4bb96a7d920","Output":"{\\"JsonInput\\":{\\"Bucket\\":\\"controlbrokerevalenginec-synthedtemplates0e9d7f0b-gglzcwvj3muj\\",\\"Key\\":\\"performance_testing_example_cfn_template.json\\"},\\"GetMetadata\\":{\\"Metadata\\":{\\"BootstrapVersion\\":{\\"Type\\":\\"AWS::SSM::Parameter::Value<String>\\",\\"Default\\":\\"/cdk-bootstrap/hnb659fds/version\\",\\"Description\\":\\"Version of the CDK Bootstrap resources in this environment, automatically retrieved from SSM Parameter Store. [cdk:skip]\\"}}},\\"OpaEvalSingleThreaded\\":{\\"Payload\\":{\\"OpaEvalResults\\":[{\\"PackagePlaceholder\\":{\\"allow\\":true,\\"infraction\\":[],\\"obedient_resources\\":[],\\"offending_resources\\":[],\\"resources\\":{},\\"type\\":\\"AWS::SNS::Subscription\\"}},{\\"PackagePlaceholder\\":{\\"allow\\":true,\\"infraction\\":[],\\"obedient_resources\\":[],\\"offending_resources\\":[],\\"resources\\":{},\\"type\\":\\"AWS::SNS::Topic\\"}},{\\"PackagePlaceholder\\":{\\"allow\\":true,\\"infraction\\":[],\\"obedient_resources\\":[],\\"offending_resources\\":[],\\"resources\\":{},\\"type\\":\\"AWS::SNS::Topic\\"}},{\\"PackagePlaceholder\\":{\\"allow\\":true,\\"infraction\\":[],\\"obedient_resources\\":[],\\"offending_resources\\":[],\\"resources\\":{},\\"type\\":\\"AWS::SQS::Queue\\"}},{\\"PackagePlaceholder\\":{\\"allow\\":true,\\"infraction\\":[],\\"obedient_resources\\":[],\\"offending_resources\\":[],\\"resources\\":{},\\"type\\":\\"AWS::SQS::Queue\\"}}]}},\\"QueryEvalResultsTable\\":{\\"Items\\":[]}}","OutputDetails":{"Included":true},"StartDate":"2022-02-24T19:21:30.313Z","StateMachineArn":"arn:aws:states:us-east-1:899456967600:stateMachine:InnerEvalEngine-N89zbR76HmB3","Status":"SUCCEEDED","StopDate":"2022-02-24T19:21:30.856Z"}}]}',
    "outputDetails": {"included": True},
    "billingDetails": {"billedMemoryUsedInMB": 64, "billedDurationInMilliseconds": 600},
    "ResponseMetadata": {
        "RequestId": "0a532e16-9994-49f3-8cba-e211d4b9e638",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid": "0a532e16-9994-49f3-8cba-e211d4b9e638",
            "date": "Thu, 24 Feb 2022 19:21:30 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "3607",
        },
        "RetryAttempts": 0,
    },
}
