import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

cfn = boto3.client('cloudformation')
cloudcontrol = boto3.client('cloudcontrol')

class CloudControl():
    
    def __init__(self,type_name,identifier):
        self.type_name = type_name
        self.identifier = identifier
    
    def get_resource_schema(self,*,resource_type):
        try:
            r = cfn.describe_type(
                Type = 'RESOURCE',
                type_name = resource_type,
            )
        except cfn.exceptions.TypeNotFoundException:
            print(f'TypeNotFoundException: {resource_type}')
            return None
        except ClientError as e:
            raise
        else:
            schema = json.loads(r['Schema'])
            print(schema)
            return schema
    
    def cloudcontrol_get(self,*,type_name,identifier):   
        try:
            r = cloudcontrol.get_resource(
                type_name = type_name,
                identifier = identifier
            )
        except ClientError as e:
            print(f'ClientError\n{e}')
            raise
        else:
            properties = json.loads(r['ResourceDescription']['Properties'])
            print(f'cloudcontrol.get_resource properties\ntype_name:\n{type_name}\nidentifier:\n{identifier}\nProperties:\n{properties}')
            return properties

    def get_cfn(self):
        
        cloudcontrol_properties = self.cloudcontrol_get(type_name=self.type_name,identifier=self.identifier)
        
        resource_schema = self.get_resource_schema(resource_type=self.type_name)
        print(f'resource_schema:\n{resource_schema}')
        
        schema_properties = resource_schema['properties']
        
        read_only_properties = [i.split('/properties/')[1] for i in resource_schema['readOnlyProperties']]
        for read_only_property in read_only_properties:
            cloudcontrol_properties.pop(read_only_property,None)
        
        cfn = {
            "Resources" : {
              "ConfigEventResource" : {
                "Type" : self.type_name,
                "Properties" : cloudcontrol_properties,
              }
            }
        }
        print(f'cfn:\n{cfn}')
        return cfn

def lambda_handler(event, context):
    """
    translate existing resource to a reconfiguration-event-tracked-resource.cfn.template.json
    file that would create an identical resource
    
    """
    
    print(event)
    
    invoking_event = json.loads(event["invokingEvent"])
    print(f'invoking_event:\n{invoking_event}')
    
    rule_parameters = event.get("ruleParameters")
    if rule_parameters:
        rule_parameters = json.loads(rule_parameters)
        print(f'rule_parameters:\n{rule_parameters}')
    
    configuration_item = invoking_event["configurationItem"]
    print(f'configuration_item:\n{configuration_item}')
    
    item_status = configuration_item["configurationItemStatus"]
    print(f'item_status:\n{item_status}')
    
    resource_type = configuration_item['resource_type']
    print(f'resource_type:\n{resource_type}')
    
    resource_configuration = configuration_item['configuration']
    print(f'resource_configuration:\n{resource_configuration}')
    
    if resource_configuration:
        resource_configuration_keys = list(resource_configuration.keys())
        print(f'resource_configuration_keys:\n{resource_configuration_keys}')
    
    resource_id = configuration_item['resourceId']

    # only 506/874 resources can use CloudControl, by a recent count of NON_PROVISIONABLE status

    c = CloudControl(type_name=resource_type,identifier=resource_id)
    
    cfn = c.get_cfn()
    
    return {
        "Cfn": cfn
    }