package sqs_queue_dedup

type = "aws_sqs_queue"

resources := [ resource | r := input.configuration.root_module.resources[_]
    r.type == type
    resource := r
]