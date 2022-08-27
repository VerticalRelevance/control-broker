PATH=${PATH}:~/.guard/bin
#/tmp/.guard/bin/cfn-guard --version
/tmp/.guard/bin/cfn-guard validate --data /tmp/input_to_be_analyzed.json --rules /tmp/rules -o json > /tmp/result.json