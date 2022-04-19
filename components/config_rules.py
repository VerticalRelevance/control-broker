import builtins
from typing import Dict
from aws_cdk import aws_config, aws_lambda, Duration, aws_stepfunctions
from constructs import Construct
from utils import paths

class ControlBrokerConfigRule(Construct):
    """L3 construct Config rule that calls the Control Broker on resource changes."""

    def __init__(
        self,
        scope: Construct,
        id: builtins.str,
        control_broker_statemachine: aws_stepfunctions.StateMachine,
        rule_scope: aws_config.RuleScope,
        lambda_function_kwargs: Dict = dict(
            memory_size=512,
            timeout=Duration.seconds(60),
        ),
    ):
        super().__init__(scope, id)
        self.custom_config_lambda_fn = aws_lambda.Function(
            self,
            f"{id}CustomLambdaFn",
            code=aws_lambda.Code.from_asset(str(paths.LAMBDA_FUNCTIONS / 'custom_config')),
            handler='lambda_function.lambda_handler',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            environment=dict(
                ProcessingSfnArn=control_broker_statemachine.state_machine_arn
            ),
            **lambda_function_kwargs
        )
        control_broker_statemachine.grant_start_execution(self.custom_config_lambda_fn)
        control_broker_statemachine.grant_start_sync_execution(self.custom_config_lambda_fn)

        self.custom_config_rule = aws_config.CustomRule(
            self,
            f"{id}CustomConfigRule",
            rule_scope=rule_scope,
            lambda_function=self.custom_config_lambda_fn,
            configuration_changes=True,
        )

