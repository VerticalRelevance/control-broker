import os
import re

class PacEvaluationRouter():
    def __init__(
        self,
        event:dict,
    ):
        self.event = event

    def get_pac_bucket(self,*,input_type):
        pac_bucket = os.environ['PaCBucketRouting'][input_type]
        
        return {
            "Bucket": pac_bucket
        }
    
    def get_modified_input_s3_path(self,*,input_conversion_object):
        
        if not input_conversion_object:
            
            modified_input_s3_path = {
                # pass-through original input unmodified
                "Bucket":self.event['ControlBrokerConsumerInputs']['Bucket'],
                "Key":self.event['ControlBrokerConsumerInputKey']
            }
        
        return modified_input_s3_path
        
    def get_invoking_sfn_next_state(self,*,RoutingConfig):
        
        return f'Evaluate{RoutingConfig["InputType"]}By{RoutingConfig["PaCFramework"]}'
        
    def format_routing_decision(self,RoutingConfig):
        
        routing_decision = {
            "InvokingSfnNextState" : self.get_invoking_sfn_next_state(
                RoutingConfig = RoutingConfig
            ),
            "PaC": self.get_pac_bucket(
                input_type = RoutingConfig['InputType']
            ),
            "ModifiedInput": self.get_modified_input_s3_path(
                input_conversion_object = RoutingConfig['InputConversionObject']
            )
        }
        
        return routing_decision
    
    def get_routing_decision(self):
    
        control_broker_consumer_inputs = self.event['ControlBrokerConsumerInputs']
        
        control_broker_consumer_input_key = self.event['ControlBrokerConsumerInputKey']
        
        input_type = control_broker_consumer_inputs['InputType']
        
        routing_decision_matrix = {
            "CloudFormationTemplate": {
                "InputType": "CloudFormationTemplate",
                "PaCFramework": "OPA",
                "InputConversionObject":None
            },
            # "ConfigEvent": {}
        }
        
        routing_decision = self.format_routing_decision(routing_decision_matrix[input_type])
    
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