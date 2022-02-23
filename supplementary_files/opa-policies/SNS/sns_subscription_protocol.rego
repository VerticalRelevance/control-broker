package sns_subscription_protocol

import input 

type = "AWS::SNS::Subscription"

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
        "reason": "Subscription must use protocol of queue"
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