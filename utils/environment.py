import os

def is_pipeline_synth():
    return "PIPELINE_SYNTH" in os.environ
