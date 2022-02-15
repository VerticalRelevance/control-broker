package sns_subscription_protocol

import input 

type = "AWS::SNS::Subscription"

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
        "reason": "Protocol must be queue"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.Protocol  == "queue"
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}