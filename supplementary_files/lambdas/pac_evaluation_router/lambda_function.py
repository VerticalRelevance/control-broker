# class PacEvaluationRouter():
#     def __init__(
#         self,
#         input_type
#     ):
#         self.input_type = input_type

#     def convert_config_to_cfn(self):
#         pass
    
    
#     def main(self):
#         # convert : {
#         #     "ConfigEvent":self.convert_config_to_cfn,
#         #     # "SAM": convert_sam_to_cfn#TODO
#         #     # "HelmChart": #TODO
#         #     # "Terraform": #TODO
#         # }
#         pass

def lambda_handler(event, context):

    print(event)
    
    # p = PacEvaluationRouter(
    #     input_type = event['input_type']
    # )
    
    # p.main()
    
    routing = {
        "Routing": "InputTypeCloudFormationPaCFrameworkOPA"
    }
    
    return routing