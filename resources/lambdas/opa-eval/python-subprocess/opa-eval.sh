EVAL=$(/tmp/opa eval --fail --explain full --disable-early-exit --format raw \
    -d /tmp/policy.rego \
    -i /tmp/cfn.json \
    "data")
echo $EVAL