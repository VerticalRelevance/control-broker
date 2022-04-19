import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

cfn = boto3.client('cloudformation')
cloudcontrol = boto3.client('cloudcontrol')

class CloudControl():
    
    def __init__(self,TypeName,Identifier):
        self.type_name = TypeName
        self.identifier = Identifier
    
    def get_resource_schema(self,*,ResourceType):
        try:
            r = cfn.describe_type(
                Type = 'RESOURCE',
                TypeName = ResourceType,
            )
        except cfn.exceptions.TypeNotFoundException:
            print(f'TypeNotFoundException: {ResourceType}')
            return None
        except ClientError as e:
            raise
        else:
            schema = json.loads(r['Schema'])
            print(schema)
            return schema
    
    def cloudcontrol_get(self,*,TypeName,Identifier):   
        try:
            r = cloudcontrol.get_resource(
                TypeName = TypeName,
                Identifier = Identifier
            )
        except ClientError as e:
            print(f'ClientError\n{e}')
            raise
        else:
            properties = json.loads(r['ResourceDescription']['Properties'])
            print(f'cloudcontrol.get_resource properties\nTypeName:\n{TypeName}\nIdentifier:\n{Identifier}\nProperties:\n{properties}')
            return properties

    def get_cfn(self):
        
        cloudcontrol_properties = self.cloudcontrol_get(TypeName=self.type_name,Identifier=self.identifier)
        
        resource_schema = self.get_resource_schema(ResourceType=self.type_name)
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
    
    resource_type = configuration_item['resourceType']
    print(f'resource_type:\n{resource_type}')
    
    resource_configuration = configuration_item['configuration']
    print(f'resource_configuration:\n{resource_configuration}')
    
    if resource_configuration:
        resource_configuration_keys = list(resource_configuration.keys())
        print(f'resource_configuration_keys:\n{resource_configuration_keys}')
    
    resource_id = configuration_item['resourceId']

    # only 506/874 resources can use CloudControl, by a recent count of NON_PROVISIONABLE status

    c = CloudControl(TypeName=resource_type,Identifier=resource_id)
    
    cfn = c.get_cfn()
    
    return {
        "Cfn": cfn
    }