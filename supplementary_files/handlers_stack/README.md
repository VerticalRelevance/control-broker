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

```
-i /tmp/input_analyzed_object.json \
```

Consumer sends S3 path to `input_analyzed_object` in the request body sent to the Control Broker outer APIGW endpoint.

