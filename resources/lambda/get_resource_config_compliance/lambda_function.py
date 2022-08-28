import json
import boto3
import os
from botocore.exceptions import ClientError

config = boto3.client('config')

class NoMatchingEvaluationResults(Exception):
    print('NoMatchingEvaluationResults')
    pass

def get_resource_config_compliance_by_resource(*,resource_type,resource_id, config_rule_name):
    
    print('begin get_resource_config_compliance_by_resource')
    
    try:
        r = config.get_compliance_details_by_resource(
            ResourceType=resource_type,
            ResourceId=resource_id,
            ComplianceTypes=[
                'COMPLIANT',
                'NON_COMPLIANT',
                # 'NOT_APPLICABLE',
                # 'INSUFFICIENT_DATA',
            ],
        )
    except ClientError as e:
        print(f"ClientError\n{e}")
        raise
    else:
        print(r)
        
        evaluation_results = r['EvaluationResults']
        
        print(f'evaluation_results\n{evaluation_results}')
        
        evaluation_results = [i['ComplianceType'] for i in evaluation_results if i['EvaluationResultIdentifier']['EvaluationResultQualifier']['ConfigRuleName'] == config_rule_name]
        
        try:
            
            evaluation_result = evaluation_results[0]
        
        except IndexError:
            
            print('NoMatchingEvaluationResults')
            return None
            # raise NoMatchingEvaluationResults
        
        else:
            
            print(f'evaluation_result:\n{evaluation_result}')
    
            return evaluation_result == 'COMPLIANT'

# def get_resource_config_compliance_by_rule(*,resource_id, config_rule_name):
    
#     print('begin get_resource_config_compliance_by_rule')
    
#     try:
#         r = config.get_compliance_details_by_config_rule(
#             ConfigRuleName = config_rule_name,
#             ComplianceTypes=[
#                 'COMPLIANT',
#                 'NON_COMPLIANT',
#                 'NOT_APPLICABLE'
#             ],
#             Limit = 100 #Max
#         )
#     except ClientError as e:
#         print(f"ClientError\n{e}")
#         raise
#     else:
#         print(r)
        
#         evaluation_results = r['EvaluationResults']
        
#         print(f'evaluation_results\n{evaluation_results}')
        
#         evaluation_results = [i['ComplianceType'] for i in evaluation_results if i['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'] == resource_id]
        
#         try:
            
#             evaluation_result = evaluation_results[0]
        
#         except IndexError:
            
#             print('NoMatchingEvaluationResults')
#             return None
#             # raise NoMatchingEvaluationResults
        
#         else:
            
#             print(f'evaluation_result:\n{evaluation_result}')
    
#             return evaluation_result == 'COMPLIANT'


def lambda_handler(event, context):

    # class ConfigComplianceStatusIsNotAsExpectedException(Exception):
    #     pass

    print(event)
    
    config_event = event['ConfigEvent']
    
    invoking_event = json.loads(config_event["invokingEvent"])
    
    resource_id = invoking_event['configurationItem']['resourceId']
    
    resource_type = invoking_event['configurationItem']['resourceType']
    
    config_rule_name = config_event['configRuleName']
    
    compliance =  get_resource_config_compliance_by_resource(
        resource_type = resource_type,
        resource_id = resource_id,
        config_rule_name = config_rule_name,
    )
    
    print(f'compliance:\n{compliance}')
    
    # get_resource_config_compliance_by_rule(resource_id = resource_id,config_rule_name = config_rule_name)
    
    expected_compliance_status = event['ExpectedComplianceStatus']
    
    print(f'expected_compliance_status:\n{expected_compliance_status}')
    
    if expected_compliance_status is None:
        
        return compliance
    
    else:
        return {
            "ComplianceIsAsExpected": expected_compliance_status == compliance
        }