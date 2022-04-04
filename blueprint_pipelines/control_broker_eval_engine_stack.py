import os
import json
from typing import List

from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_codecommit,
    aws_dynamodb,
    aws_s3,
    aws_s3_deployment,
    aws_codebuild,
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_lambda,
    aws_stepfunctions,
    aws_iam,
    aws_logs,
    aws_events
)

from constructs import Construct

class ControlBrokerEvalEngineStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        application_team_cdk_app: dict,
        **kwargs
    ) -> None:
        
        super().__init__(scope, construct_id, **kwargs)
        self.application_team_cdk_app = application_team_cdk_app

        self.pipeline_ownership_metadata =  {}
        self.pipeline_ownership_metadata['Directory'], self.pipeline_ownership_metadata['Suffix'] = os.path.split(application_team_cdk_app['PipelineOwnershipMetadata'])

        self.deploy_utils()
        self.s3_deploy_local_assets()
        self.deploy_inner_sfn_lambdas()
        self.deploy_inner_sfn()
        self.deploy_outer_sfn()
        self.deploy_root_pipeline()
        
    def deploy_utils(self):

        self.table_eval_results = aws_dynamodb.Table(self,"EvalResults",
            partition_key = aws_dynamodb.Attribute(name="pk", type=aws_dynamodb.AttributeType.STRING),
            sort_key = aws_dynamodb.Attribute(name="sk", type=aws_dynamodb.AttributeType.STRING),
            billing_mode = aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy = RemovalPolicy.DESTROY,
        )
        
        self.bucket_synthed_templates = aws_s3.Bucket(self, "SynthedTemplates",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )
 
        # event bridge bus
        
        self.event_bus_infractions = aws_events.EventBus(self, "Infractions")
        
        # debug event bridge by logging events
        
        logs_infraction_events = aws_logs.LogGroup(self, "InfractionEvents",
          removal_policy= RemovalPolicy.DESTROY
        )
        logs_infraction_events.grant_write(aws_iam.ServicePrincipal("events.amazonaws.com"))
        
        cfn_rule = aws_events.CfnRule(self, "ListenAllInfractions",
            state="ENABLED",
            event_bus_name=self.event_bus_infractions.event_bus_name,
            event_pattern=aws_events.EventPattern(
              account= ["899456967600"]
            ),
            targets=[aws_events.CfnRule.TargetProperty(
                arn=logs_infraction_events.log_group_arn,
                id = "InfractionEvents"
            )]
        )
        
    def s3_deploy_local_assets(self):
      
        self.repo_app_team_cdk = aws_codecommit.Repository(self, "ApplicationTeamExampleAppRepository",
            repository_name = "ControlBrokerEvalEngine-ApplicationTeam-ExampleApp",
            code = aws_codecommit.Code.from_directory(
              './supplementary_files/application_team_example_app',
              "main"
            )
        )
        self.repo_app_team_cdk.apply_removal_policy(RemovalPolicy.DESTROY)

        CfnOutput(self, "ApplicationTeamExampleAppRepositoryCloneSSH",
            value = self.repo_app_team_cdk.repository_clone_url_ssh
        )
        CfnOutput(self, "ApplicationTeamExampleAppRepositoryCloneHTTP",
            value = self.repo_app_team_cdk.repository_clone_url_http
        )
      
        # buildspec
        
        self.bucket_buildspec = aws_s3.Bucket(self, "Buildspec",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )
        
        aws_s3_deployment.BucketDeployment(self, "Buildspec.yaml",
            sources=[aws_s3_deployment.Source.asset("./supplementary_files/buildspec")],
            destination_bucket=self.bucket_buildspec,
            retain_on_delete = False
        )
        
        # pipeline ownership metadata
        
        self.bucket_pipeline_ownership_metadata = aws_s3.Bucket(self, "PipelineOwnershipMetadata",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )
        
        aws_s3_deployment.BucketDeployment(self, "PipelineOwnershipMetadataDir",
            sources=[aws_s3_deployment.Source.asset(self.pipeline_ownership_metadata['Directory'])],
            destination_bucket=self.bucket_pipeline_ownership_metadata,
            retain_on_delete = False
        )
        
        # opa policies
        
        self.bucket_opa_policies = aws_s3.Bucket(self,"OpaPolicies",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )
        
        aws_s3_deployment.BucketDeployment(self, "OpaPoliciesByService",
            sources=[aws_s3_deployment.Source.asset("./supplementary_files/opa-policies")],
            destination_bucket=self.bucket_opa_policies,
            retain_on_delete = False
        )
    
    def deploy_inner_sfn_lambdas(self):
        
        # opa eval - python subprocess - single threaded
        
        self.lambda_opa_eval_python_subprocess_single_threaded = aws_lambda.Function(self, "OpaEvalPythonSubprocessSingleThreaded",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 10240, # todo power-tune
            code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/opa-eval/python-subprocess/single-threaded")
        )
        
        self.lambda_opa_eval_python_subprocess_single_threaded.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:HeadObject",
                "s3:GetObject",
                "s3:List*",
            ],
            resources=[
                self.bucket_opa_policies.bucket_arn,
                f'{self.bucket_opa_policies.bucket_arn}/*',
                f'{self.bucket_synthed_templates.bucket_arn}/*',
            ]
        ))
        
        # s3 select
        
        self.lambda_s3_select = aws_lambda.Function(self, "S3Select",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 1024,
            code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/s3-select")
        )
        
        self.lambda_s3_select.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:HeadObject",
                "s3:GetObject",
                "s3:List*",
                "s3:SelectObjectContent",
            ],
            resources=[
                self.bucket_pipeline_ownership_metadata.bucket_arn,
                f'{self.bucket_pipeline_ownership_metadata.bucket_arn}/*',
            ]
        ))
        
    def deploy_inner_sfn(self):
        
        log_group_inner_eval_engine_sfn = aws_logs.LogGroup(self,"InnerEvalEngineSfnLogs",
          log_group_name = "/aws/vendedlogs/states/InnerEvalEngineSfnLogs",
          removal_policy= RemovalPolicy.DESTROY
        )
        
        role_inner_eval_engine_sfn = aws_iam.Role(self, "InnerEvalEngineSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )
        
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                # "logs:*",
                "logs:CreateLogDelivery",
                "logs:GetLogDelivery",
                "logs:UpdateLogDelivery",
                "logs:DeleteLogDelivery",
                "logs:ListLogDeliveries",
                "logs:PutResourcePolicy",
                "logs:DescribeResourcePolicies",
                "logs:DescribeLogGroups",
            ],
            resources=[
                "*",
                log_group_inner_eval_engine_sfn.log_group_arn,
                f'{log_group_inner_eval_engine_sfn.log_group_arn}*'
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "lambda:InvokeFunction"
            ],
            resources=[
                self.lambda_opa_eval_python_subprocess_single_threaded.function_arn,
                self.lambda_s3_select.function_arn
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "dynamodb:UpdateItem",
                "dynamodb:Query",
            ],
            resources=[
                self.table_eval_results.table_arn,
                f'{self.table_eval_results.table_arn}/*'
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:GetObject",
            ],
            resources=[
                self.bucket_synthed_templates.bucket_arn,
                f'{self.bucket_synthed_templates.bucket_arn}/*',
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "events:PutEvents",
            ],
            resources=[
                self.event_bus_infractions.event_bus_arn,
                f"{self.event_bus_infractions.event_bus_arn}*",
            ]
        ))
        
        self.sfn_inner_eval_engine = aws_stepfunctions.CfnStateMachine(self, "InnerEvalEngine",
            state_machine_type = "EXPRESS",
            role_arn = role_inner_eval_engine_sfn.role_arn,
        
            logging_configuration = aws_stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                destinations = [aws_stepfunctions.CfnStateMachine.LogDestinationProperty(
                    cloud_watch_logs_log_group = aws_stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                        log_group_arn = log_group_inner_eval_engine_sfn.log_group_arn
                    )
                )],
                include_execution_data=False,
                level="ERROR"
            ),
            
            definition_string=json.dumps({
                "StartAt" : "ParseInput",
                "States" : {
                  "ParseInput" : {
                    "Type" : "Pass",
                    "Next" : "GetMetadata",
                    "Parameters" : {
                      "JsonInput" : {
                        "Bucket.$" : "$.Template.Bucket",
                        "Key.$"    : "$.Template.Key"
                      },
                      "OuterEvalEngineSfnExecutionId.$":"$.OuterEvalEngineSfn.ExecutionId" 
                    },
                    "ResultPath" : "$"
                  },
                  "GetMetadata" : {
                    "Type" : "Task",
                    "Next" : "OpaEval",
                    "ResultPath" : "$.GetMetadata",
                    "Resource" : "arn:aws:states:::lambda:invoke",
                    "Parameters" : {
                      "FunctionName" : self.lambda_s3_select.function_name,
                      "Payload" : {
                        "Bucket" : self.bucket_pipeline_ownership_metadata.bucket_name,
                        "Key" : self.pipeline_ownership_metadata['Suffix'],
                        "Expression":"SELECT * from S3Object s",
                      }
                    },
                    "ResultSelector" : {
                      "Metadata.$" : "$.Payload.Selected"
                    }
                  },
                  "OpaEval" : {
                    "Type" : "Task",
                    "Next" : "SetMaxIndexZero",
                    "ResultPath" : "$.OpaEval",
                    "Resource" : "arn:aws:states:::lambda:invoke",
                    "Parameters" : {
                      "FunctionName" : self.lambda_opa_eval_python_subprocess_single_threaded.function_name,
                      "Payload" : {
                        "JsonInput.$" : "$.JsonInput",
                        "OpaPolicies" : {
                          "Bucket" : self.bucket_opa_policies.bucket_name
                        }
                      }
                    },
                    "ResultSelector" : {
                      "Payload.$" : "$.Payload"
                    }
                  },
                  "SetMaxIndexZero" : {
                    "Type" : "Task",
                    "Next" : "ForEachEvalResult",
                    "ResultPath" : "$.SetMaxIndexZero",
                    "Resource" : "arn:aws:states:::dynamodb:updateItem",
                    "ResultSelector" : {
                      "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                    },
                    "Parameters" : {
                      "TableName" : self.table_eval_results.table_name,
                      "Key" : {
                        "pk" : {
                          "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"
                        },
                        "sk" : {
                          "S" : "MaxIndex"
                        }
                      },
                      "ExpressionAttributeNames" : {
                        "#maxindex" : "MaxIndex",
                      },
                      "ExpressionAttributeValues" : {
                        ":zero" : {
                          "N" : "0"
                        },
                      },
                      "UpdateExpression" : "SET #maxindex=:zero",
                    }
                  },
                  "ForEachEvalResult" : {
                    "Type" : "Map",
                    "Next" : "IncrementMaxIndex",
                    "ResultPath" : None,
                    "ItemsPath" : "$.OpaEval.Payload.OpaEvalResults",
                    "Parameters" : {
                      "EvalResult.$" : "$$.Map.Item.Value",
                      "JsonInput.$" : "$.JsonInput",
                      "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                      "Metadata.$": "$.GetMetadata.Metadata",
                      "EvalResultContextIndex.$": "$$.Map.Item.Index",
                    },
                    "Iterator" : {
                      "StartAt" : "SetMaxIndex",
                      "States" : {
                        "SetMaxIndex" : {
                            "Type" : "Task",
                            "Next" : "ChoiceIsAllowed",
                            "ResultPath" : "$.SetMaxIndex",
                            "Resource" : "arn:aws:states:::dynamodb:updateItem",
                            "ResultSelector" : {
                              "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                            },
                            "Parameters" : {
                              "TableName" : self.table_eval_results.table_name,
                              "Key" : {
                                "pk" : {
                                  "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"
                                },
                                "sk" : {
                                  "S": "MaxIndex"
                                }
                              },
                              "ExpressionAttributeNames" : {
                                "#maxindex" : "MaxIndex",
                              },
                              "ExpressionAttributeValues" : {
                                ":currentindex" : {
                                  "N.$" : "States.JsonToString($.EvalResultContextIndex)"
                                },
                              },
                              "UpdateExpression" : "SET #maxindex=:currentindex",
                              "ConditionExpression" : ":currentindex > #maxindex"
                            },
                              "Catch": [
                              {
                                "ErrorEquals": [
                                  "DynamoDB.ConditionalCheckFailedException"
                                ],
                                "Next": "ChoiceIsAllowed",
                                "ResultPath": "$.ErrorSetMaxIndex"
                              }
                            ]
                        },
                        "ChoiceIsAllowed" : {
                          "Type" : "Choice",
                          "Default" : "ForEachInfraction",
                          "Choices" : [
                            {
                              "Variable" : "$.EvalResult.PackagePlaceholder.infraction[0]",
                              "IsPresent" : False,
                              "Next" : "IncrementAllowedCount"
                            }
                          ]
                        },
                        "IncrementAllowedCount" : {
                            "Type" : "Task",
                            "End" : True,
                            "ResultPath" : "$.IncrementAllowed",
                            "Resource" : "arn:aws:states:::dynamodb:updateItem",
                            "ResultSelector" : {
                              "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                            },
                            "Parameters" : {
                              "TableName" : self.table_eval_results.table_name,
                              "Key" : {
                                "pk" : {
                                  "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"
                                },
                                "sk" : {
                                  "S" : "AllowedCount"
                                }
                              },
                              "ExpressionAttributeNames" : {
                                "#allowedcount" : "AllowedCount",
                              },
                              "ExpressionAttributeValues" : {
                                ":increment" : {
                                    "N" : "1"
                                },
                              },
                              "UpdateExpression" : "ADD #allowedcount :increment"
                            }
                        },
                        "ForEachInfraction" : {
                          "Type" : "Map",
                          "End" : True,
                          "ResultPath" : "$.ForEachInfraction",
                          "ItemsPath" : "$.EvalResult.PackagePlaceholder.infraction",
                          "Parameters" : {
                            "Infraction.$" : "$$.Map.Item.Value",
                            "JsonInput.$" : "$.JsonInput",
                            "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                            "Metadata.$": "$.Metadata",
                            "InfractionContextIndex.$": "$$.Map.Item.Index",
                            "InfractionContextValue.$": "$$.Map.Item.Value"
                          },
                          "Iterator" : {
                            "StartAt" : "WriteInfractionToDDB",
                            "States" : {
                              "WriteInfractionToDDB" : {
                                "Type" : "Task",
                                "Next" : "PushInfractionEventToEB",
                                "ResultPath" : "$.WriteEvalResultToDDB",
                                "Resource" : "arn:aws:states:::dynamodb:updateItem",
                                "ResultSelector" : {
                                  "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                                },
                                "Parameters" : {
                                  "TableName" : self.table_eval_results.table_name,
                                  "Key" : {
                                    "pk" : {
                                      "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"
                                    #   "S.$" : "$.OuterEvalEngineSfnExecutionId"
                                    },
                                    "sk" : {
                                      "S.$" : "States.Format('{}#{}#{}', $.JsonInput.Key, $.Infraction.resource, $.Infraction.reason)"
                                    #   "S.$" : "$$.Execution.Id"
                                    }
                                  },
                                  "ExpressionAttributeNames" : {
                                    "#allow" : "allow",
                                    "#reason" : "reason",
                                    "#resource" : "resource",
                                    "#cfnkey": "CFNKey",
                                    "#businessunit": "BusinessUnit",
                                    "#billingcode": "BillingCode",
                                    "#targetenv": "TargetProvisioningEnvironment",
                                    "#ownername": "PipelineOwnerName",
                                    "#owneremail": "PipelineOwnerEmail",
                                    "#executionstart": "ExecutionStart",
                                  },
                                  "ExpressionAttributeValues" : {
                                    ":cfnkey" : {
                                      "S.$" : "$.JsonInput.Key"
                                    },
                                    ":allow" : {
                                      "S.$" : "States.JsonToString($.Infraction.allow)"
                                    },
                                    ":reason" : {
                                      "S.$" : "$.Infraction.reason"
                                    },
                                    ":resource" : {
                                      "S.$" : "$.Infraction.resource"
                                    },
                                    ":businessunit" : {
                                      "S.$" : "$.Metadata.BusinessUnit"
                                    },
                                    ":billingcode" : {
                                      "S.$" : "$.Metadata.BillingCode"
                                    },
                                    ":targetenv" : {
                                      "S.$" : "$.Metadata.TargetProvisioningEnvironment"
                                    },
                                    ":ownername" : {
                                      "S.$" : "$.Metadata.PipelineOwner.Name"
                                    },
                                    ":owneremail" : {
                                      "S.$" : "$.Metadata.PipelineOwner.Email"
                                    },
                                    ":executionstart" : {
                                      "S.$" : "$$.Execution.StartTime"
                                    },
                                  },
                                  "UpdateExpression" : "SET #cfnkey=:cfnkey, #allow=:allow, #reason=:reason, #resource=:resource, #businessunit=:businessunit, #billingcode=:billingcode, #targetenv=:targetenv, #ownername=:ownername, #owneremail=:owneremail, #executionstart=:executionstart"
                                }
                              },
                              "PushInfractionEventToEB" : {
                                "Type" : "Task",
                                "End" : True,
                                "ResultPath" : "$.PushInfractionEventToEB",
                                "Resource" : "arn:aws:states:::events:putEvents",
                                "Parameters" : {
                                    "Entries": [
                                      {
                                        "Detail": {
                                            "allow.$" : "States.JsonToString($.Infraction.allow)",
                                            "reason.$": "$.Infraction.reason",
                                            "resource.$": "$.Infraction.resource",
                                            "BusinessUnit.$": "$.Metadata.BusinessUnit",
                                            "BillingCode.$": "$.Metadata.BusinessUnit",
                                            "TargetProvisioningEnvironment.$": "$.Metadata.TargetProvisioningEnvironment",
                                            "PipelineOwner.$": "$.Metadata.PipelineOwner",
                                            "OuterEvalEngineSfnExecutionId.$": "$.OuterEvalEngineSfnExecutionId",
                                            "CFNKey.$": "$.JsonInput.Key",
                                            "ExecutionStart.$": "$$.Execution.StartTime"
                                        },
                                        "DetailType": "eval-engine-infraction",
                                        "EventBusName": self.event_bus_infractions.event_bus_name,
                                        "Source.$": "$$.StateMachine.Id"
                                      }
                                    ]
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  },
                  "IncrementMaxIndex" : {
                    "Comment": "Map index is zero-indexed. Increment is one-indexed. This compensates.",
                    "Type" : "Task",
                    "Next" : "GetMaxIndex",
                    "ResultPath" : "$.IncrementMaxIndex",
                    "Resource" : "arn:aws:states:::dynamodb:updateItem",
                    "ResultSelector" : {
                      "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                    },
                    "Parameters" : {
                      "TableName" : self.table_eval_results.table_name,
                      "Key" : {
                        "pk" : {
                          "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"

                        },
                        "sk" : {
                          "S" : "MaxIndex"
                        }
                      },
                      "ExpressionAttributeNames" : {
                              "#maxindex" : "MaxIndex",
                            },
                        "ExpressionAttributeValues" : {
                          ":increment" : {
                            "N" : "1"
                          },
                        },
                        "UpdateExpression" : "ADD #maxindex :increment"
                    }
                  },
                  "GetMaxIndex" : {
                    "Type" : "Task",
                    "Next" : "GetAllowedCount",
                    "ResultPath" : "$.GetMaxIndex",
                    "Resource" : "arn:aws:states:::aws-sdk:dynamodb:query",
                    "ResultSelector" : {
                      "Items.$" : "$.Items"
                    },
                    "Parameters" : {
                      "TableName" : self.table_eval_results.table_name,
                      "ExpressionAttributeValues" : {
                        ":pk" : {
                          "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"
                        },
                        ":sk" : {
                          "S" : "MaxIndex"
                        },
                      },
                      "KeyConditionExpression" : "pk = :pk AND sk = :sk"
                    }
                  },
                  "GetAllowedCount" : {
                    "Type" : "Task",
                    "Next" : "ChoiceAllowedExists",
                    "ResultPath" : "$.GetAllowedCount",
                    "Resource" : "arn:aws:states:::aws-sdk:dynamodb:query",
                    "ResultSelector" : {
                      "Items.$" : "$.Items"
                    },
                    "Parameters" : {
                      "TableName" : self.table_eval_results.table_name,
                      "ExpressionAttributeValues" : {
                        ":pk" : {
                          "S.$" : "States.Format('{}#{}', $.OuterEvalEngineSfnExecutionId, $$.Execution.Id)"
                        },
                        ":sk" : {
                          "S" : "AllowedCount"
                        },
                      },
                      "KeyConditionExpression" : "pk = :pk AND sk = :sk"
                    }
                  },
                  "ChoiceAllowedExists": {
                    "Type" : "Choice",
                    "Default" : "InfractionsExist",
                    "Choices" : [
                      {
                        "Variable" : "$.GetAllowedCount.Items[0]",
                        "IsPresent" : True,
                        "Next" : "ChoiceInfractionsExist"
                      }
                    ]
                  },
                  "ChoiceInfractionsExist" : {
                    "Type" : "Choice",
                    "Default" : "InfractionsExist",
                    "Choices" : [
                      {
                        "Variable" : "$.GetMaxIndex.Items[0].MaxIndex.N",
                        "StringEqualsPath" : "$.GetAllowedCount.Items[0].AllowedCount.N",
                        "Next" : "NoInfractions"
                      }
                    ]
                  },
                  "InfractionsExist" : {
                    "Type" : "Fail",
                    "Cause" : "InfractionsExist"
                  },
                  "NoInfractions" : {
                    "Type" : "Succeed",
                  },
                }
            })
        )
    
        self.sfn_inner_eval_engine.node.add_dependency(role_inner_eval_engine_sfn)
    
    def deploy_outer_sfn(self):
        
        log_group_outer_eval_engine_sfn = aws_logs.LogGroup(self,"OuterEvalEngineSfnLogs",
          log_group_name = "/aws/vendedlogs/states/OuterEvalEngineSfnLogs",
          removal_policy= RemovalPolicy.DESTROY
        )
        
        role_outer_eval_engine_sfn = aws_iam.Role(self, "OuterEvalEngineSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )
        
        role_outer_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                # "logs:*",
                "logs:CreateLogDelivery",
                "logs:GetLogDelivery",
                "logs:UpdateLogDelivery",
                "logs:DeleteLogDelivery",
                "logs:ListLogDeliveries",
                "logs:PutResourcePolicy",
                "logs:DescribeResourcePolicies",
                "logs:DescribeLogGroups"
            ],
            resources=[
                "*",
                log_group_outer_eval_engine_sfn.log_group_arn,
                f'{log_group_outer_eval_engine_sfn.log_group_arn}*'

            ]
        ))
        role_outer_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "states:StartExecution",
                "states:StartSyncExecution",
            ],
            resources=[
                self.sfn_inner_eval_engine.attr_arn
            ]
        ))
        role_outer_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "states:DescribeExecution",
                "states:StopExecution"
            ],
            resources=[
                "*"
            ]
        ))
        role_outer_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions = [
              "events:PutTargets",
              "events:PutRule",
              "events:DescribeRule"
            ],
            resources = [
              f"arn:aws:events:{os.getenv('CDK_DEFAULT_REGION')}:{os.getenv('CDK_DEFAULT_ACCOUNT')}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule",
              "*"
            ]
        ))
        
        self.sfn_outer_eval_engine = aws_stepfunctions.CfnStateMachine(self, "OuterEvalEngine",
            state_machine_type = "EXPRESS",
            
            role_arn = role_outer_eval_engine_sfn.role_arn,
            
            logging_configuration = aws_stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                destinations = [aws_stepfunctions.CfnStateMachine.LogDestinationProperty(
                    cloud_watch_logs_log_group = aws_stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                        log_group_arn = log_group_outer_eval_engine_sfn.log_group_arn
                    )
                )],
                include_execution_data=False,
                level="ERROR"
            ),
            
            definition_string=json.dumps({
                "StartAt" : "ForEachTemplate",
                "States" : {
                  "ForEachTemplate" : {
                    "Type" : "Map",
                    "End" : True,
                    "ResultPath" : "$.ForEachTemplate",
                    "ItemsPath" : "$.CFN.Keys",
                    "Parameters" : {
                      "Template" : {
                        "Bucket.$" : "$.CFN.Bucket",
                        "Key.$" : "$$.Map.Item.Value",
                      }
                    },
                    "Iterator" : {
                      "StartAt" : "TemplateToNestedSFN",
                      "States" : {
                        "TemplateToNestedSFN" : {
                            "Type" : "Task",
                            "End" : True,
                            "ResultPath" : "$.TemplateToNestedSFN",
                            "Resource" : "arn:aws:states:::aws-sdk:sfn:startSyncExecution",
                            "Parameters" : {
                                "StateMachineArn" : self.sfn_inner_eval_engine.attr_arn,
                                "Input" : {
                                    "Template.$" : "$.Template",
                                    "OuterEvalEngineSfn": {
                                        "ExecutionId.$":"$$.Execution.Id"
                                    }
                                }
                            }
                        }
                      }
                    }
            
                  }
                }
            }),
            
        )
        
        self.sfn_outer_eval_engine.node.add_dependency(role_outer_eval_engine_sfn)
        
    def deploy_root_pipeline(self):
       
        # source
        
        artifact_source = aws_codepipeline.Artifact()
        
        action_source = aws_codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=self.repo_app_team_cdk,
            branch = "main",
            output=artifact_source
        )
        
        # add buildspec
        
        # lambda_add_buildspec = aws_lambda.Function(self, "AddBuildspec",
        #     runtime=aws_lambda.Runtime.PYTHON_3_9,
        #     handler="lambda_function.lambda_handler",
        #     timeout = Duration.seconds(60),
        #     memory_size = 1024,
        #     code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/add-buildspec")
        # )
        
        # lambda_add_buildspec.role.add_to_policy(aws_iam.PolicyStatement(
        #     actions=[
        #         "s3:HeadObject",
        #         "s3:GetObject"
        #     ],
        #     resources=[
        #         f'{self.bucket_buildspec.bucket_arn}/*'
        #     ]
        # ))
        
        # artifact_repo_and_buildspec = aws_codepipeline.Artifact()
        
        # action_add_buildspec = aws_codepipeline_actions.LambdaInvokeAction(
        #     action_name="AddBuildspec",
        #     inputs=[
        #         artifact_source
        #     ],
        #     outputs=[
        #         artifact_repo_and_buildspec
        #     ],
        #     lambda_ = lambda_add_buildspec,
        #     user_parameters={
        #         "Buildspec" : {
        #             "Bucket" : self.bucket_buildspec.bucket_name,
        #             "Key" : "buildspec.yaml"
        #         }
        #     },
        # )
        
        # cdk synth
        
        build_project_cdk_synth = aws_codebuild.PipelineProject(self, "CdkSynth",
          build_spec = aws_codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "install": {
                    "on-failure": "ABORT",
                    "commands": [
                      "npm install -g typescript",
                      "npm install -g ts-node",
                      "npm install -g aws-cdk",
                      "npm install",
                      "cdk --version"
                      
                    ]
                },
                "build": {
                    "on-failure": "ABORT",
                    "commands": [
                      "ls",
                      "cdk synth",
                    ]
                }
            },
            "artifacts": {
              "files": [
                "cdk.out/*"
              ],
              "discard-paths":"no",
              "enable-symlinks":"yes"
            }
          })
        )

        artifact_synthed = aws_codepipeline.Artifact()

        action_build = aws_codepipeline_actions.CodeBuildAction(
            action_name = "CodeBuild",
            project = build_project_cdk_synth,
            input = artifact_source,
            outputs = [
                artifact_synthed
            ],
        )
        
        # eval engine
        
        lambda_eval_engine_wrapper = aws_lambda.Function(self, "EvalEngineWrapper",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 1024,
            code=aws_lambda.Code.from_asset("./supplementary_files/lambdas/eval-engine-wrapper")
        )
        
        lambda_eval_engine_wrapper.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:PutObject",
            ],
            resources=[
                f'{self.bucket_synthed_templates.bucket_arn}/*'
            ]
        ))
        
        lambda_eval_engine_wrapper.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "states:StartSyncExecution",
            ],
            resources=[
                self.sfn_outer_eval_engine.attr_arn,
                f'{self.sfn_outer_eval_engine.attr_arn}*'
            ]
        ))
        
        action_eval_engine = aws_codepipeline_actions.LambdaInvokeAction(
            action_name="EvalEngine",
            inputs=[
                artifact_synthed
            ],
            lambda_ = lambda_eval_engine_wrapper,
            user_parameters={
                "SynthedTemplatesBucket" : self.bucket_synthed_templates.bucket_name,
                "EvalEngineSfnArn" : self.sfn_outer_eval_engine.attr_arn
            },
        )
        
        # provision
        
        stack_name = "control-broker-simple-provision"
        change_set_name = stack_name
        
        action_create_changeset = aws_codepipeline_actions.CloudFormationCreateReplaceChangeSetAction(
            action_name="PrepareChanges",
            stack_name=stack_name,
            change_set_name=change_set_name,
            admin_permissions=True,
            template_path=artifact_synthed.at_path("ControlBrokerEvalEngineExampleAppStackSQS.template.json"), # FIXME
            run_order=1
        )
        
        action_execute_changeset = aws_codepipeline_actions.CloudFormationExecuteChangeSetAction(
            action_name="ExecuteChanges",
            stack_name=stack_name,
            change_set_name=change_set_name,
            run_order=3
        )
        
        # pipeline

        root_pipeline = aws_codepipeline.Pipeline(self,"ControlBrokerEvalEngine",
            artifact_bucket=aws_s3.Bucket(self, "RootPipelineArtifactBucket",
                removal_policy= RemovalPolicy.DESTROY,
                auto_delete_objects = True
            ),
            stages = [
                aws_codepipeline.StageProps(
                    stage_name = "Source",
                    actions = [
                        action_source
                    ]
                ),
                # aws_codepipeline.StageProps(
                #     stage_name = "AddBuildspec",
                #     actions = [
                #         action_add_buildspec
                #     ]
                # ),
                aws_codepipeline.StageProps(
                    stage_name = "CdkSynth",
                    actions = [
                        action_build
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name = "EvalEngine",
                    actions = [
                        action_eval_engine
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name = "Provision",
                    actions = [
                        action_create_changeset,
                        action_execute_changeset
                    ]
                )
            ]
        )