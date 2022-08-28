import json
            
def lambda_handler(event, context):
    
    print(event)
    
    results=event.get('CfnGuardValidateResults')
    
    rules_compliant=[i['compliant'] for i in results]
    
    rules_not_compliant=[i['not_compliant'] for i in results]
    
    compliance_decision= bool(rules_not_compliant)
    
    print(f'compliance_decision:\n{compliance_decision}')

    return compliance_decision