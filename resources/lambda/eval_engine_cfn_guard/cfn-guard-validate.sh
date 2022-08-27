PATH=${PATH}:~/.guard/bin
r=$(/tmp/.guard/bin/cfn-guard validate \
    --output-format json \
    --data /tmp/input_to_be_analyzed.json \
    --rules /tmp/rule.guard
)
echo $r