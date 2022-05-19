package cross_cloud_demo

rule_applicable {
    data.InputType == "SomeCrossCloudInput"
}

default allow = false

allow = null {
    not rule_applicable
} else {
    input.Something.Encrypted
}

