package sam_serverless_function_runtime

type = "AWS::Serverless::Function"

rule_applicable {
    data.ApprovedContext.EnvironmentEvaluation == "Prod"
    data.InputType == "SAM"
}

default allow = false

allow = null {
    not rule_applicable
} else {
    count(infraction) == 0
}

infraction[r] {
    rule_applicable # return empty set if rule not applicable
    some offending_resource
    offending_resources[offending_resource]
    r := {
        "resource": offending_resource,
        "allow": false,
        "reason": "Runtime property is misconfigured"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.Runtime == "python3.9"
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}
