EVAL=$(/tmp/opa eval --explain full --disable-early-exit --format raw \
    -d /tmp/pac_policies/ \
    -d /tmp/evaluation_context.json \
    -d /tmp/approved_context.json \
    -d /tmp/input_type.json \
    -i /tmp/input_to_be_evaluated_object.json \
    "data")
echo $EVAL