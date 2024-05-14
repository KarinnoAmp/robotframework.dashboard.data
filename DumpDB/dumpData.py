import sys, os

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
    )
)

from connectDB import databaseConnector
from readJSON import readingJSONOutput
import yaml, argparse


with open(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "Config", "DB-Config.yaml"
    )
) as yaml_file:
    CONFIG: dict = yaml.full_load(yaml_file)


def gettingArgument() -> None:
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument(
        "-l",
        "--language",
        help="Language of the running automated `EN`",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="JSON file of automated output `output.json`",
        default="output.json",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-e",
        "--environment",
        help="Environment of running automated `DEV`, `SIT`",
        default="DEV",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-b",
        "--build",
        help="Build number of deployment e.g. `Commit number`, or other",
        default=None,
        type=str,
    )
    # Parse the arguments
    args = parser.parse_args()
    return args


"""<--<--<--<--<--<--<--<-- Connecting to database -->-->-->-->-->-->-->-->"""
arguments = gettingArgument()
MY_DATABASE = databaseConnector(
    host=CONFIG["service"]["host"],
    user=CONFIG["service"]["username"],
    password=CONFIG["service"]["password"],
    database=CONFIG["service"]["database"],
)
MY_DATABASE.cursor()
"""<--<--<--<--<--<--<--<-- Connecting to database -->-->-->-->-->-->-->-->"""

# MY_DATABASE.deleteAllData()

current_dir = os.path.join(os.getcwd(), arguments.file)
json_data = readingJSONOutput(current_dir)
try:
    run_language = str(arguments.language).upper()
except KeyError:
    run_language = None
build_number = json_data.getBuildNumber(str(arguments.build))
test_run_data = json_data.getTestRunsData(
    run_language, str(arguments.environment).upper()
)
test_run_status_data = json_data.getTestRunStatus()
suites_data = json_data.getSuitesData()
suite_status = json_data.getSuiteStatus()
test_cases_data = json_data.getTestCaseData()
test_case_status = json_data.getTestCasesStatus()
if arguments.build != None:
    MY_DATABASE.insertBuildNumber(build_number)
MY_DATABASE.insertTestRunsToDatabase(test_run_data)
MY_DATABASE.insertTestRunsStatusToDatabase(test_run_status_data)
MY_DATABASE.insertSuiteData(suites_data)
MY_DATABASE.insertSuiteStatus(suite_status)
MY_DATABASE.insertTestData(test_cases_data)
MY_DATABASE.insertTestCasesStatus(test_case_status)
