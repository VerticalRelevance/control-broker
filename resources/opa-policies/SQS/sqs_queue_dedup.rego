package sqs_queue_dedup

import input 

type = "AWS::SQS::Queue"

default deny = true

deny {
    count(infraction) > 0
}

infraction[r] {
    some offending_resource
    offending_resources[offending_resource]
    r := {
        "resource": offending_resource,
        "deny": true,
        "reason": "Queue must use ContentBasedDeduplication"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.ContentBasedDeduplication == true
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}