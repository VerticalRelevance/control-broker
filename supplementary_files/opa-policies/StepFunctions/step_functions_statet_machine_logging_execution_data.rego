package step_functions_statet_machine_logging_execution_data

import input 

type = "AWS::StepFunctions::StateMachine"

default allow = false

allow {
    count(infraction) == 0
}

infraction[r] {
    some offending_resource
    offending_resources[offending_resource]
    r := {
        "resource": offending_resource,
        "allow": false,
        "reason": "LoggingConfiguration.IncludeExecutionData is misconfigured"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.LoggingConfiguration.IncludeExecutionData == true
    #properties.LoggingConfiguration.IncludeExecutionData == false
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}