package sqs_queue_dedup

type = "AWS::SQS::Queue"

default allow = false

allow {
    count(infraction) == 0
}

# make "allow":null if this policy is not applicable

# policy determines if it is itself applicable, based on value of ApprovedContext


infraction[r] {
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