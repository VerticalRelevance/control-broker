import aws_cdk as core
import aws_cdk.assertions as assertions

from control_broker_eval_engine_cdk.control_broker_eval_engine_cdk_stack import ControlBrokerEvalEngineCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in control_broker_eval_engine_cdk/control_broker_eval_engine_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ControlBrokerEvalEngineCdkStack(app, "control-broker-eval-engine-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })