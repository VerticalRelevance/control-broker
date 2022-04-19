import pathlib

__THIS_FILE_DIR = pathlib.Path(__file__).parent

REPO_ROOT = __THIS_FILE_DIR.parent

LAMBDA_FUNCTIONS = REPO_ROOT / "supplementary_files/lambdas"
