package s3_bucket_block_public_acls

type = "AWS::S3::Bucket"

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
        "reason": "BlockPublicAccessConfiguration.BlockPublicAcls is misconfigured"
    }
}

offending_resources = { r | resources[r]} - obedient_resources

obedient_resources[resource] {
    some resource
    properties := resources[resource]
    properties.BlockPublicAccessConfiguration.BlockPublicAcls  == true
    #properties.BlockPublicAccessConfiguration.BlockPublicAcls  == false
}

resources[resource] = def {
    some resource
    input.Resources[resource].Type == type
    def := input.Resources[resource].Properties
}