package sqs_queue_dedup

type = "aws_sqs_queue"

obedient_resources := [ resource | r := input.configuration.root_module.resources[_]
    r.type == type
    r.expressions.content_based_deduplication.constant_value
    resource := r
]

resources := [ resource | r := input.configuration.root_module.resources[_]
    r.type == type
    resource := r
]