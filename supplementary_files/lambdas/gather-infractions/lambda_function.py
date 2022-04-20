def lambda_handler(event, context):
    
    print(event)
    
    opa_eval_results = event
    
    infractions = [ {i:opa_eval_results[i]}for i in opa_eval_results if not opa_eval_results[i].get('allow')]

    print(f'infractions:\n{infractions}\n{type(infractions)}')
    
    return infractions
