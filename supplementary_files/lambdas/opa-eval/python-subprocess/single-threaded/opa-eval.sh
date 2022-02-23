EVAL=$(/tmp/opa eval --explain full --disable-early-exit --format raw \
    -d /tmp/opa-policies/ \
    -i /tmp/input.json \
    "data")
echo $EVAL