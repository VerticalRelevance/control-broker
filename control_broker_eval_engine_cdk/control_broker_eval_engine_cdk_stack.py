import os
import json

from aws_cdk import (
    Duration,
    Stack,
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
)
from constructs import Construct

class ControlBrokerEvalEngineCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ##################################################################
        #                       Required Existing Resources
        ##################################################################

        repo_app_team_cdk = aws_codecommit.Repository.from_repository_name(self,"AppTeamCdk",
            repository_name = 'opa-eval-serverless-cdk-source'
        )
        
        repo_branch_app_team_cdk = "master"

        ##################################################################
        #                            misc
        ##################################################################
        
        # eval results
        
        table_eval_results = aws_dynamodb.Table(self,"EvalResults",
            partition_key = aws_dynamodb.Attribute(name="pk", type=aws_dynamodb.AttributeType.STRING),
            sort_key = aws_dynamodb.Attribute(name="sk", type=aws_dynamodb.AttributeType.STRING),
            billing_mode = aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        
        bucket_synthed_templates = aws_s3.Bucket(self, "SynthedTemplates",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL
        )
      
        # buildspec
        
        bucket_buildspec = aws_s3.Bucket(self, "Buildspec",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL
        )
        
        aws_s3_deployment.BucketDeployment(self, "Buildspec.yaml",
            sources=[aws_s3_deployment.Source.asset("./resources/buildspec")],
            destination_bucket=bucket_buildspec,
        )
        
        # opa policies
        
        bucket_opa_policies = aws_s3.Bucket(self,"OpaPolicies",
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL
        )
        
        aws_s3_deployment.BucketDeployment(self, "OpaPoliciesByService",
            sources=[aws_s3_deployment.Source.asset("./resources/opa-policies")],
            destination_bucket=bucket_opa_policies,
        )
        
        ##################################################################
        #                     lambdas in sfn
        ##################################################################
        
        # parse active services
        
        lambda_parse_active_services = aws_lambda.Function(self, "ParseActiveServices",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 1024,
            code=aws_lambda.Code.from_asset("./resources/lambdas/parse-active-services")
        )
        lambda_parse_active_services.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:HeadObject",
                "s3:GetObject"
            ],
            resources=[
                f'{bucket_synthed_templates.bucket_arn}/*'
            ]
        ))
        
        # opa eval - python subprocess
        
        lambda_opa_eval_python_subprocess = aws_lambda.Function(self, "OpaEvalPythonSubprocess",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 1024,
            code=aws_lambda.Code.from_asset("./resources/lambdas/opa-eval/python-subprocess")
        )
        
        lambda_opa_eval_python_subprocess.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:HeadObject",
                "s3:GetObject"
            ],
            resources=[
                f'{bucket_opa_policies.bucket_arn}/*',
                f'{bucket_synthed_templates.bucket_arn}/*'
            ]
        ))
        
        # infractions feedback
        
        lambda_infractions_feedback_git_codecommit = aws_lambda.Function(self, "InfractionsFeedbackGitCodeCommit",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 1024,
            environment = {
              "AppTeamCdkRepo"       : repo_app_team_cdk.repository_name,
              "AppTeamCdkRepoBranch" : repo_branch_app_team_cdk
            },
            code=aws_lambda.Code.from_asset("./resources/lambdas/infractions-feedback/git/codecommit")
        )
        
        lambda_infractions_feedback_git_codecommit.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:HeadObject",
                "s3:GetObject"
            ],
            resources=[
                f'{bucket_synthed_templates.bucket_arn}/*'
            ]
        ))
        lambda_infractions_feedback_git_codecommit.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "dynamodb:Query",
            ],
            resources=[
                table_eval_results.table_arn,
                f'{table_eval_results.table_arn}/*'
            ]
        ))
        lambda_infractions_feedback_git_codecommit.role.add_to_policy(aws_iam.PolicyStatement(
            not_actions=[
                "codecommit:Delete*",
            ],
            resources=[
                repo_app_team_cdk.repository_arn,
                f'{repo_app_team_cdk.repository_arn}/*'
            ]
        ))
        
        ##################################################################
        #                       inner sfn
        ##################################################################
        
        log_group_inner_eval_engine_sfn = aws_logs.LogGroup(self,"InnerEvalEngineSfnLogs")
        
        role_inner_eval_engine_sfn = aws_iam.Role(self, "InnerEvalEngineSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )
        
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "logs:*"
            ],
            resources=[
                "*",
                log_group_inner_eval_engine_sfn.log_group_arn
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "lambda:InvokeFunction"
            ],
            resources=[
                lambda_parse_active_services.function_arn,
                lambda_opa_eval_python_subprocess.function_arn,
                lambda_infractions_feedback_git_codecommit.function_arn,
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "dynamodb:UpdateItem",
            ],
            resources=[
                table_eval_results.table_arn,
                f'{table_eval_results.table_arn}/*'
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:ListBucket",
            ],
            resources=[
                bucket_opa_policies.bucket_arn
            ]
        ))
        role_inner_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:ListObjectsV2",
                "s3:HeadObject",
                "s3:GetObject",
            ],
            resources=[
                f'{bucket_opa_policies.bucket_arn}/*'
            ]
        ))
        
        sfn_inner_eval_engine = aws_stepfunctions.CfnStateMachine(self, "InnerEvalEngine",
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
                "StartAt" : "CFN",
                "States" : {
                  "CFN" : {
                    "Type" : "Pass",
                    "Next" : "ParseActiveServices",
                    "Parameters" : {
                      "CFN" : {
                        "Bucket.$" : "$.Template.Bucket",
                        "Key.$"    : "$.Template.Key",
                      }
                    },
                    "ResultPath" : "$"
                  },
                  "ParseActiveServices" : {
                    "Type" : "Task",
                    "Next" : "ForEachActiveSerive",
                    "ResultPath" : "$.ParseActiveServices",
                    "Resource" : "arn:aws:states:::lambda:invoke",
                    "Parameters" : {
                      "FunctionName" : lambda_parse_active_services.function_name,
                      "Payload.$" : "$.CFN"
                    },
                    "ResultSelector" : {
                      "Payload.$" : "$.Payload"
                    }
                  },
                  "ForEachActiveSerive" : {
                    "Type" : "Map",
                    "Next" : "InfractionsFeedback",
                    "ResultPath" : "$.ForEachActiveSerive",
                    "ItemsPath" : "$.ParseActiveServices.Payload.ActiveServices",
                    "Parameters" : {
                      "ActiveService.$" : "$$.Map.Item.Value",
                      "CFN.$" : "$.CFN"
                    },
                    "Iterator" : {
                      "StartAt" : "ListPoliciesByService",
                      "States" : {
                        "ListPoliciesByService" : {
                          "Type" : "Task",
                          "Next" : "ChoicePoliciesExist",
                          "ResultPath" : "$.ListPoliciesByService",
                          "Resource" : "arn:aws:states:::aws-sdk:s3:listObjectsV2",
                          "Parameters" : {
                            "Bucket" : bucket_opa_policies.bucket_name,
                            "Prefix.$" : "$.ActiveService"
                          },
                        },
                        "ChoicePoliciesExist" : {
                          "Type" : "Choice",
                          "Default" : "NoPolicies",
                          "Choices" : [
                            {
                              "Variable" : "$.ListPoliciesByService.Contents",
                              "IsPresent" : True,
                              "Next" : "ForEachPolicy"
                            }
                          ]
                        },
                        "NoPolicies" : {
                          "Type" : "Pass",
                          "End" : True
                        },
                        "ForEachPolicy" : {
                          "Type" : "Map",
                          "End" : True,
                          "ResultPath" : "$.ForEachPolicy",
                          "ItemsPath" : "$.ListPoliciesByService.Contents",
                          "Parameters" : {
                            "Policies" : {
                              "Bucket" : bucket_opa_policies.bucket_name,
                              "Key.$" : "$$.Map.Item.Value.Key",
                            },
                            "CFN.$" : "$.CFN"
                          },
                          "Iterator" : {
                            "StartAt" : "OPAEvalPythonSubprocess",
                            "States" : {
                              "OPAEvalPythonSubprocess" : {
                                "Type" : "Task",
                                "Next" : "ChoiceOPAEvalIsAllowed",
                                "ResultPath" : "$.OPAEvalPythonSubprocess",
                                "Resource" : "arn:aws:states:::lambda:invoke",
                                "Parameters" : {
                                  "FunctionName" : lambda_opa_eval_python_subprocess.function_name,
                                  "Payload" : {
                                    "Policies.$" : "$.Policies",
                                    "CFN.$" : "$.CFN",
                                  }
                                },
                                "ResultSelector" : {
                                  "Payload.$" : "$.Payload"
                                }
                              },
                              "ChoiceOPAEvalIsAllowed" : {
                                "Type" : "Choice",
                                "Default" : "Deny",
                                "Choices" : [
                                  {
                                    "Variable" : "$.OPAEvalPythonSubprocess.Payload.OPAEvalDenyResult",
                                    "StringEquals" : "False",
                                    "Next" : "Allow"
                                  }
                                ]
                              },
                              "Allow" : {
                                "Type" : "Pass",
                                "End" : True
                              },
                              "Deny" : {
                                "Type" : "Pass",
                                "Next" : "ForEachInfraction"
                              },
                              "ForEachInfraction" : {
                                "Type" : "Map",
                                "End" : True,
                                "ResultPath" : "$.ForEachInfraction",
                                "ItemsPath" : "$.OPAEvalPythonSubprocess.Payload.Infractions",
                                "Parameters" : {
                                  "Infraction.$" : "$$.Map.Item.Value",
                                  "Policies.$" : "$.Policies",
                                  "CFN.$" : "$.CFN"
                                },
                                "Iterator" : {
                                  "StartAt" : "WriteInfractionToDDB",
                                  "States" : {
                                    "WriteInfractionToDDB" : {
                                      "Type" : "Task",
                                      "End" : True,
                                      "ResultPath" : "$.WriteEvalResultToDDB",
                                      "Resource" : "arn:aws:states:::dynamodb:updateItem",
                                      "ResultSelector" : {
                                        "HttpStatusCode.$" : "$.SdkHttpMetadata.HttpStatusCode"
                                      },
                                      "Parameters" : {
                                        "TableName" : table_eval_results.table_name,
                                        "Key" : {
                                          "pk" : {
                                            "S.$" : "$$.Execution.Id"
                                          },
                                          "sk" : {
                                            "S.$" : "States.Format('{}#{}', $.CFN.Key, $.Policies.Key)"
                                          }
                                        },
                                        "ExpressionAttributeNames" : {
                                          "#allowed" : "AllowedStringBoolean",
                                          "#infractions" : "Infractions"
                                        },
                                        "ExpressionAttributeValues" : {
                                          ":allowed" : {
                                            "S" : "False"
                                          },
                                          ":infractions" : {
                                            "S.$" : "States.JsonToString($.Infraction)"
                                          },
                                        },
                                        "UpdateExpression" : "SET #allowed=:allowed, #infractions=:infractions"
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  },
                  "InfractionsFeedback" : {
                    "Type" : "Task",
                    "Next" : "ChoicePipelineIsHalted",
                    "ResultPath" : "$.InfractionsFeedback",
                    "Resource" : "arn:aws:states:::lambda:invoke",
                    "Parameters" : {
                      "FunctionName" : lambda_infractions_feedback_git_codecommit.function_name,
                      "Payload" : {
                        "CFN.$" : "$.CFN",
                        "DynamoDB" : {
                          "Table" : table_eval_results.table_name,
                          "Pk.$" : "$$.Execution.Id"
                        }
                      }
                    },
                    "ResultSelector" : {
                      "Payload.$" : "$.Payload"
                    }
                  },
                  "ChoicePipelineIsHalted" : {
                    "Type" : "Choice",
                    "Default" : "PipelineIsHalted",
                    "Choices" : [
                      {
                        "Variable" : "$.InfractionsFeedback.Payload.InfractionsExist",
                        "BooleanEquals" : False,
                        "Next" : "PipelineProceeds"
                      }
                    ]
                  },
                  "PipelineProceeds" : {
                    "Type" : "Succeed",
                  },
                  "PipelineIsHalted" : {
                    "Type" : "Fail",
                    "Cause" : "InfractionsExist"
                  },
                }
            }),
            
        )
        
        ##################################################################
        #                       outer sfn
        ##################################################################
        
        log_group_outer_eval_engine_sfn = aws_logs.LogGroup(self,"OuterEvalEngineSfnLogs")
        
        role_outer_eval_engine_sfn = aws_iam.Role(self, "OuterEvalEngineSfn",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
        )
        
        role_outer_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "logs:*"
            ],
            resources=[
                "*",
                log_group_outer_eval_engine_sfn.log_group_arn

            ]
        ))
        role_outer_eval_engine_sfn.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "states:StartExecution",
                "states:StartSyncExecution",
            ],
            resources=[
                sfn_inner_eval_engine.attr_arn
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
        
        sfn_outer_eval_engine = aws_stepfunctions.CfnStateMachine(self, "OuterEvalEngine",
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
                            "StateMachineArn" : sfn_inner_eval_engine.attr_arn,
                            "Input" : {
                              "Template.$" : "$.Template"
                            },
                          },
                        }
                      }
                    }
            
                  }
                }
            }),
            
        )
   
   
        ##################################################################
        #                       root pipeline
        ##################################################################
        
        # source
        
        artifact_source = aws_codepipeline.Artifact()
        
        action_source = aws_codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo_app_team_cdk,
            output=artifact_source
        )
        
        # add buildspec
        
        lambda_add_buildspec = aws_lambda.Function(self, "AddBuildspec",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            timeout = Duration.seconds(60),
            memory_size = 1024,
            code=aws_lambda.Code.from_asset("./resources/lambdas/add-buildspec")
        )
        
        lambda_add_buildspec.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:HeadObject",
                "s3:GetObject"
            ],
            resources=[
                f'{bucket_buildspec.bucket_arn}/*'
            ]
        ))
        
        artifact_repo_and_buildspec = aws_codepipeline.Artifact()
        
        action_add_buildspec = aws_codepipeline_actions.LambdaInvokeAction(
            action_name="AddBuildspec",
            inputs=[
                artifact_source
            ],
            outputs=[
                artifact_repo_and_buildspec
            ],
            lambda_ = lambda_add_buildspec,
            user_parameters={
                "Buildspec" : {
                    "Bucket" : bucket_buildspec.bucket_name,
                    "Key" : "buildspec.yaml"
                }
            },
        )
        
        # cdk synth
        
        build_project_cdk_synth = aws_codebuild.PipelineProject(self, "CdkSynth")

        artifact_synthed = aws_codepipeline.Artifact()

        action_build = aws_codepipeline_actions.CodeBuildAction(
            action_name = "CodeBuild",
            project = build_project_cdk_synth,
            input = artifact_repo_and_buildspec,
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
            code=aws_lambda.Code.from_asset("./resources/lambdas/eval-engine-wrapper")
        )
        
        lambda_eval_engine_wrapper.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "s3:PutObject",
            ],
            resources=[
                f'{bucket_synthed_templates.bucket_arn}/*'
            ]
        ))
        
        lambda_eval_engine_wrapper.role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "states:StartSyncExecution",
            ],
            resources=[
                sfn_outer_eval_engine.attr_arn,
                f'{sfn_outer_eval_engine.attr_arn}*'
            ]
        ))
        
        action_eval_engine = aws_codepipeline_actions.LambdaInvokeAction(
            action_name="EvalEngine",
            inputs=[
                artifact_synthed
            ],
            lambda_ = lambda_eval_engine_wrapper,
            user_parameters={
                "SynthedTemplatesBucket" : bucket_synthed_templates.bucket_name,
                "EvalEngineSfnArn" : sfn_outer_eval_engine.attr_arn
            },
        )
        
        # pipeline

        root_pipeline = aws_codepipeline.Pipeline(self,"ControlBrokerEvalEngine",
            stages = [
                aws_codepipeline.StageProps(
                    stage_name = "Source",
                    actions = [
                        action_source
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name = "AddBuildspec",
                    actions = [
                        action_add_buildspec
                    ]
                ),
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
                )
            ]
        )