EVAL=$(/tmp/opa eval --explain full --disable-early-exit --format raw \
    -d /tmp/pac_policies/ \
    -d /tmp/evaluation_context.json \
    -d /tmp/approved_context.json \
    -i /tmp/input_analyzed_object.json \
    "data")
echo $EVAL