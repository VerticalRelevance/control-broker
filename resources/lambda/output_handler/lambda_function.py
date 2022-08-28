import json
            
def lambda_handler(event, context):
    
    print(event)
    
    results=event.get('CfnGuardValidateResults')
    
    rules_compliant=[i['compliant'] for i in results if i['compliant']]
    print(f'rules_compliant:\n{rules_compliant}')
    
    rules_not_compliant=[i['not_compliant'] for i in results if i['not_compliant']]
    print(f'rules_not_compliant:\n{rules_not_compliant}')
    
    compliance_decision= not bool(rules_not_compliant)
    
    print(f'compliance_decision:\n{compliance_decision}')

    return {
        "IsCompliant":compliance_decision
    }