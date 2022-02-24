package sns_walk

# A purposely non-performant policy to help test how poorly performing Rego policies affect overall Control Broker performance

allow {
    not some_bad_thing
    not some_other_bad_thing
}

some_bad_thing {
    path := walk(input)
    path[1] == 'EvilInputThatWillNeverExist'
}

some_other_bad_thing {
    path := walk(input.Resources)
    path[1] == 'EvilInputThatWillNeverExist'
}