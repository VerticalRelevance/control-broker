package sqs_queue_dedup

import future.keywords.in
import future.keywords.every

type = "aws_sqs_queue"

# input.configuration.root_module.resources is an array

infractions := [ infraction | o := offending_resources[_]
    infraction := {
        "resource": o,
        "allow": false,
        "reason": "ContentBasedDeduplication property is misconfigured"
    }
]

offending_resources := [ resource | r := input.configuration.root_module.resources[_]
    r.type == type
    r.expressions.content_based_deduplication.constant_value != true
    resource := r
]

# bad = all - good model, cf. previous client's structure where input.Resources was a dict

# WIP

# offending_resources = resources - obedient_resources

# obedient_resources := [ resource | r := input.configuration.root_module.resources[_]
#     r.type == type
#     r.expressions.content_based_deduplication.constant_value
#     resource := r
# ]

# resources := [ resource | r := input.configuration.root_module.resources[_]
#     r.type == type
#     resource := r
# ]

# resources[resource] := def {
#     some resource
#     r := input.configuration.root_module.resources[_][resource]
#     r.type == type
#     # resource := r
#     def := r
# }