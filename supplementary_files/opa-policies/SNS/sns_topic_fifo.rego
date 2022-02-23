package sns_topic_fifo

import input 

type = "AWS::SNS::Topic"

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
        "reason": "Topic must be Fifo"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.FifoTopic == true
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}