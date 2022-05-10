package sqs_queue_dedup

type = "AWS::SQS::Queue"

# allow:null if this policy is not applicable

# not applicable if ApprovedContext != "Prod"

# this Policy only applies to Prod

# if not applicable, do not return any infractions

# allow:true if this policy is applicable and no violations

# allow:false if this policy is applicable and yes violations

rule_applicable {
    data.ApprovedContext.EnvironmentEvaluation == "Prod"
    # data.InputType == "CloudFormation"
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
        "reason": "ContentBasedDeduplication property is misconfigured"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.ContentBasedDeduplication == data.EvaluationContext.Allowed.SQS.Queue.ContentBasedDeduplication
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}
