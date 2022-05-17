# Eval Engine Lambdalith

## `opa eval`


### policies

```
-d /tmp/pac_policies/ `
```

All PaC Policies are hosted in a bucket that is deployed to with the contents of this [directory](./supplementary_files/handlers_stack/pac_frameworks) 

Note the `OPA` prefix used to find the appropriact PaCFramework is set in [cdk.json](./cdk.json):

```
"control-broker/pac-framework":"OPA"
```

### ConsumerMetadata

```
-d /tmp/consumer_metadata.json \
```

Passed by the Consumer in the request body sent to the Control Broker outer APIGW endpoint.

### EvaluationContext

```
-d /tmp/evaluation_context.json \
```


Hosted in a bucket that is deployed to with the contents of this [directory](./supplementary_files/handlers_stack/evaluation_context)


### ApprovedContext

```
-d /tmp/approved_context.json \
```

handler implements custom approval process. For now:

```
get_approved_context(*,consumer_requested_context,authorization_header):
    
    # some Authz call
    
    return consumer_requested_context # auto-approve for now, pending full implementation
```

### Input Analyzed Object

the object passed by the Consumer's request that is subject to PaC analysis

```
-i /tmp/input_analyzed_object.json \
```

Consumer sends S3 path to `input_analyzed_object` in the request body sent to the Control Broker outer APIGW endpoint.

