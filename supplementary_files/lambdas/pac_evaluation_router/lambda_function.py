class PacEvaluationRouter():
    def __init__(
        self,
        input_type
    ):
        self.input_type = input_type

    def get_routing_decision(self):
    
        routing_decision_matrix = {
            "CloudFormationTemplate":"InputTypeCloudFormationPaCFrameworkOPA"
        }
    
        return routing_decision_matrix[self.input_type]
        

def lambda_handler(event, context):

    print(event)
    
    control_broker_consumer_inputs = event['ControlBrokerConsumerInputs']
    
    print(f"control_broker_consumer_inputs:\n{control_broker_consumer_inputs}")
    
    input_type = control_broker_consumer_inputs['InputType']

    p = PacEvaluationRouter(
        input_type = input_type
    )
    
    routing_decision = p.get_routing_decision()
    
    routing = {
        "Routing": routing_decision
    }
    
    return routing