from random import getrandbits

def lambda_handler(event,context):
    print(f'event\n{event}\ncontext:\n{context}')
    return {
        "EvalEngineLambdalith": {
            "Evaluation": {
                "IsAllowed":bool(getrandbits(1))
            }
        }
    }