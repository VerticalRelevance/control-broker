import json
with open('/home/ec2-user/environment/cschneider-utils/sfn/input.topic.json','r') as f:
    event = json.loads(f.read())
from pprintpp import pprint as pp
from urllib.parse import quote
# local
########################################################

import json

import requests

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
boto3_session = boto3.session.Session()
boto3_region = boto3_session.region_name

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

cfn = boto3.client('cloudformation', config=config)


class AwsResource():
    def __init__(self,resource_type,resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        self.api_calls = {
            "AWS::SNS::Topic": {
                "FifoTopic": {
                    "Request": f"https://sns.{boto3_region}.amazonaws.com/?Action=GetTopicAttributes&TopicArn={quote(self.resource_id,safe='')}&Version=2010-03-31&AUTHPARAMS"
                }
            }
        }
    
    def main(self):
        
        a = self.api_calls[self.resource_type]
        
        pp(a)


class DescribeType():
    def __init__(self,type_name,resource_configuration,resource_id):
        self.type_name = type_name
        self.resource_configuration = resource_configuration
        self.resource_id = resource_id
    
    def get_resource_schema(self,*,type_name):
    
        try:
            r = cfn.describe_type(
                Type = 'RESOURCE',
                type_name = type_name,
            )
        except cfn.exceptions.TypeNotFoundException:
            print(f'\nTypeNotFoundException: {type_name}')
            return None
        except ClientError as e:
            raise
        else:
            schema = json.loads(r['Schema'])
            # print(schema)
            return schema

    def get_cfn(self):
        
        def format_to_cfn(Input):
            
            if Input.isdigit():
                return int(Input)
            elif Input == 'true':
                return True
            elif Input == 'false':
                return False
            else:
                return Input
                
        resource_schema = self.get_resource_schema(type_name=self.type_name)
        print(f'\nresource_schema:\n')
        pp(resource_schema)
        
        schema_properties = resource_schema['properties']
        
        read_only_properties = [i.split('/properties/')[1] for i in resource_schema['readOnlyProperties']]
        print(f'\nread_only_properties:\n')
        pp(read_only_properties)
        
        for read_only_property in read_only_properties:
            schema_properties.pop(read_only_property,None)
        
        print(f'\nschema_properties:\n')
        pp(schema_properties)
        
        resource_configuration_keys = list(self.resource_configuration.keys())
        print(f'\nresource_configuration_keys:\n')
        pp(resource_configuration_keys)
        
        properties_keys = list(schema_properties.keys())
        print(f'\nproperties_keys:\n')
        pp(properties_keys)
        
        keys_in_properties_and_config = list( set(properties_keys) & set(resource_configuration_keys) )
        keys_in_properties_and_config = sorted(keys_in_properties_and_config)
        print(f'\nkeys_in_properties_and_config:\n')
        pp(keys_in_properties_and_config)
        
        keys_in_properties_not_config = list ( set(properties_keys) - set(resource_configuration_keys))
        keys_in_properties_not_config = sorted(keys_in_properties_not_config)
        print(f'\nkeys_in_properties_not_config:\n')
        pp(keys_in_properties_not_config)
        
        for key in keys_in_properties_not_config:
            print(key)
            # get_api_call_to_get_existing_resource_configuration_value_for_that_key(key)
        
        keys_in_config_not_properties = list ( set(resource_configuration_keys) - set(properties_keys))
        keys_in_config_not_properties = sorted(keys_in_config_not_properties)
        print(f'\nkeys_in_config_not_properties:\n')
        pp(keys_in_config_not_properties)
        
        cfn_properties = {}
        
        for key in keys_in_properties_and_config:
            cfn_properties[key] = format_to_cfn(self.resource_configuration.get(key))
            
        cfn = {
            "Resources" : {
              "ConfigEventResource" : {
                "Type" : self.type_name,
                "Properties" : cfn_properties,
                "UpdateReplacePolicy" : "Delete",
                "DeletionPolicy" : "Delete",
              }
            }
        }
        # print(f'\ncfn:\n{cfn)
        return cfn

    
def lambda_handler(event, context):
    """
    translate existing resource to a reconfiguration-event-tracked-resource.cfn.template.json
    file that would create an identical resource
    
    TODO: handle nested properties (using recursion to parse resource_schema)
    
    """
    
    print(event)
    
    invoking_event = json.loads(event["invokingEvent"])
    print(f'\ninvoking_event:\n')
    pp(invoking_event)
    
    rule_parameters = json.loads(event["ruleParameters"])
    print(f'\nrule_parameters:\n')
    pp(rule_parameters)
    
    configuration_item = invoking_event["configurationItem"]
    print(f'\nconfiguration_item:\n')
    pp(configuration_item)
    
    item_status = configuration_item["configurationItemStatus"]
    print(f'\nitem_status:\n')
    pp(item_status)
    
    resource_configuration = configuration_item['configuration']
    print(f'\nresource_configuration:\n')
    pp(resource_configuration)
    
    resource_configuration_keys = list(resource_configuration.keys())
    print(f'\nresource_configuration_keys:\n')
    pp(resource_configuration_keys)
    
    resource_type = configuration_item['resource_type']
    resource_id = configuration_item['resource_id']

    # only 506/874 resources can use CloudControl, by a recent count of NON_PROVISIONABLE status
    
    # d = DescribeType(type_name=resource_type,resource_configuration=resource_configuration,resource_id=resource_id)
    
    # cfn = d.get_cfn()
    
    # print(f'\ncfn:\n')
    # pp(cfn)
    
    # return {
    #     "Cfn": cfn
    # }

    a = AwsResource(resource_type=resource_type,resource_id=resource_id)
    a.main()

########################################################
# local
if __name__ == '__main__':
    lambda_handler(event,{})