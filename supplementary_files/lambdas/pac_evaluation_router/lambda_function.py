import json
import os

import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
cfn = boto3.client('cloudformation')
cloudcontrol = boto3.client('cloudcontrol')

def get_object(*,bucket,key):
    
    try:
        r = s3.get_object(
            Bucket = bucket,
            Key = key
        )
    except ClientError as e:
        print(f'ClientError:\nbucket:\n{bucket}\nkey:\n{key}\n{e}')
        raise
    else:
        print(f'no ClientError get_object:\nbucket:\n{bucket}\nkey:\n{key}')
        body = r['Body']
        content = json.loads(body.read().decode('utf-8'))
        return content
        
def put_object(*,bucket,key,object_:dict):
    
    print(f'begin put_object\nbucket:\n{bucket}\nkey:\n{key}')
    
    try:
        r = s3.put_object(
            Bucket = bucket,
            Key = key,
            Body = json.dumps(object_)
        )
    except ClientError as e:
        print(f'ClientError:\nbucket:\n{bucket}\nkey:\n{key}\n{e}')
        raise
    else:
        print(f'no ClientError put_object:\nbucket:\n{bucket}\nkey:\n{key}')
        return True

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


class ConfigEventToCloudFormationConverter():
    
    def __init__(
        self,
        event:dict
    ):
        
        self.event = event
        
        self.config_event_s3_path = {
            "Bucket":self.event['ControlBrokerConsumerInputs']['Bucket'],
            "Key":self.event['ControlBrokerConsumerInputKey']
        }
        
        self.config_event = get_object(
            bucket = self.config_event_s3_path['Bucket'],
            key = self.config_event_s3_path['Key']
        )
        
    def parse_config_event(self):
        
        print(f'config_event:\n{self.config_event}')
    
        invoking_event = json.loads(self.config_event["invokingEvent"])
        print(f'invoking_event:\n{invoking_event}')
        
        rule_parameters = self.config_event.get("ruleParameters")
        if rule_parameters:
            rule_parameters = json.loads(rule_parameters)
            print(f'rule_parameters:\n{rule_parameters}')
        
        configuration_item = invoking_event["configurationItem"]
        print(f'configuration_item:\n{configuration_item}')
        
        item_status = configuration_item["configurationItemStatus"]
        print(f'item_status:\n{item_status}')
        
        self.resource_type = configuration_item['resource_type']
        print(f'resource_type:\n{self.resource_type}')
        
        resource_configuration = configuration_item['configuration']
        print(f'resource_configuration:\n{resource_configuration}')
        
        if resource_configuration:
            resource_configuration_keys = list(resource_configuration.keys())
            print(f'resource_configuration_keys:\n{resource_configuration_keys}')
        
        self.resource_id = configuration_item['resourceId']
        print(f'resource_id:\n{self.resource_type}')
    
    def get_converted_cloudformation(self):
        
        c = CloudControl(type_name=self.resource_type,identifier=self.resource_id)
    
        self.cfn = c.get_cfn()
        
        return cfn
        
    def put_converted_cloudformation(self):
        
        self.converted_s3_path = {
            'Bucket' : os.environ['ConvertedInputsBucket'],
            'Key' : self.config_event_s3_path['Key'],
        }
        
        put_object(
            bucket = self.converted_s3_path['Bucket'],
            key = self.converted_s3_path['Key'],
            object_ = self.cfn
        )
    
    def get_converted_s3_path(self):
        
        self.parse_config_event()
        self.get_converted_cloudformation()
        self.put_converted_cloudformation()
        
        return self.converted_s3_path

class PacEvaluationRouter():
    def __init__(
        self,
        event:dict,
    ):
        self.event = event

    
    def convert_config_event_to_cfn(self,original_consumer_input_s3_path):
        
        c = ConfigEventToCloudFormationConverter(original_consumer_input_s3_path)
        
        modified_input_s3_path = c.get_converted_s3_path()
        
        return modified_input_s3_path
    
    def get_pac_bucket(self,*,pac_framework):
        
        pac_bucket_routing = json.loads(os.environ['PaCBucketRouting'])
        
        pac_bucket = pac_bucket_routing[pac_framework]
        
        return {
            "Bucket": pac_bucket
        }
    
    def get_modified_input_s3_path(self,*,input_conversion_object):
        
        original_consumer_input_s3_path = {
            "Bucket":self.event['ControlBrokerConsumerInputs']['Bucket'],
            "Key":self.event['ControlBrokerConsumerInputKey']
        }
        
        if not input_conversion_object:
            
            # pass-through original input - no modification needed
            
            return original_consumer_input_s3_path
        
        else:
            
            modified_input_s3_path = input_conversion_object(self.event)
            
            return modified_input_s3_path
        
    def get_invoking_sfn_next_state(self,*,input_type,pac_framework):
        
        return f'Evaluate{input_type}By{pac_framework}'
    
        
    # def get_invoking_sfn_next_state(self,*,RoutingConfig):
        
    #     return f'Evaluate{RoutingConfig["InputType"]}By{RoutingConfig["PaCFramework"]}'
        
    # def format_routing_decision(self,routing_config):
        
    #     routing_decision = {
    #         "InvokingSfnNextState" : self.get_invoking_sfn_next_state(
    #             routing_config = routing_config
    #         ),
    #         "PaC": self.get_pac_bucket(
    #             pac_framework = routing_config['PaCFramework']
    #         ),
    #         "ModifiedInput": self.get_modified_input_s3_path(
    #             input_conversion_object = routing_config['InputConversionObject']
    #         )
    #     }
        
    #     return routing_decision
    
    # def get_routing_decision(self):
    
    #     control_broker_consumer_inputs = self.event['ControlBrokerConsumerInputs']
        
    #     control_broker_consumer_input_key = self.event['ControlBrokerConsumerInputKey']
        
    #     input_type = control_broker_consumer_inputs['InputType']
        
    #     routing_decision_matrix = {
    #         "CloudFormationTemplate": {
    #             "InputType": "CloudFormationTemplate",
    #             "PaCFramework": "OPA",
    #             "InputConversionObject":None
    #         },
    #         "ConfigEvent": {
    #             "InputType": "ConfigEvent",
    #             "PaCFramework": "OPA",
    #             "InputConversionObject":self.convert_config_event_to_cfn
    #         }
    #     }
        
    #     routing_decision = self.format_routing_decision(routing_decision_matrix[input_type])
    
    #     return routing_decision
    
    
    def get_routing_decision(self):
    
        control_broker_consumer_inputs = self.event['ControlBrokerConsumerInputs']
        
        control_broker_consumer_input_key = self.event['ControlBrokerConsumerInputKey']
        
        input_type = control_broker_consumer_inputs['InputType']
        
        if input_type == 'CloudFormationTemplate':
            
            pac_framework = "OPA"
            
            routing_decision = {
                "PaC": self.get_pac_bucket(
                    pac_framework = pac_framework
                ),
                "ModifiedInput": self.get_modified_input_s3_path(
                    input_conversion_object = None
                ),
                "InvokingSfnNextState": self.get_invoking_sfn_next_state(
                    input_type = input_type,
                    pac_framework = pac_framework,
                )
            }
        
        if input_type == 'ConfigEvent':
            
            pac_framework = "OPA"
            
            routing_decision = {
                "PaC": self.get_pac_bucket(
                    pac_framework = pac_framework
                ),
                "ModifiedInput": self.get_modified_input_s3_path(
                    input_conversion_object = self.convert_config_event_to_cfn
                ),
                "InvokingSfnNextState": self.get_invoking_sfn_next_state(
                    input_type = "CloudFormationTemplate", # ConvertedTo
                    pac_framework = pac_framework,
                )
            }
            
    
        return routing_decision
        

def lambda_handler(event, context):

    print(event)
    
    p = PacEvaluationRouter(
        event = event,
    )
    
    routing_decision = p.get_routing_decision()
    
    routing = {
        "Routing": routing_decision,
    }
    
    print(f"routing:\n{routing}")
    
    return routing