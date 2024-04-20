from datetime import datetime
from validateJSON import validateJSONSchema
from connectDB import databaseConnector
import json, yaml
import pytz
import hashlib, uuid, os
import unittest


with open(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "Config", "DB-Config.yaml"
    ),
    encoding="UTF-8",
) as yaml_file:
    CONFIG = yaml.full_load(yaml_file)


class readingJSONOutput:
    def __init__(self, json_file_path) -> None:
        with open(json_file_path) as json_file:
            self.json_data = json.load(json_file)
            self.file_name = json_file_path
        validateJSONSchema().validateJSON(self.json_data)
        MY_DATABASE = databaseConnector(
            host=CONFIG["service"]["host"],
            user=CONFIG["service"]["username"],
            password=CONFIG["service"]["password"],
            database=CONFIG["service"]["database"],
        )
        MY_DATABASE.cursor()
        self.localized = MY_DATABASE.queryLocalized()
        self.test_site = MY_DATABASE.queryTestSite()

    def getTestRunsData(self, localized: str, test_site: str):
        test_run_data: dict = {
            "id": str(uuid.uuid4()),
            "started_at": self.getTestRunStartTime(),
            "imported_at": self.getCurrentImportTime(),
            "hash": self.hash_file(),
            "test_site_id": self.test_site[str(test_site).upper()],
        }
        if str(localized).upper() != "NONE":
            test_run_data["localized_id"] = self.localized[str(localized).upper()]
        self.test_run_id = test_run_data["id"]
        return test_run_data

    def getCurrentImportTime(self) -> datetime:
        current_datetime: datetime = datetime.now()
        current_datetime: datetime = current_datetime.astimezone(pytz.utc)
        return current_datetime

    def getTestRunStartTime(self) -> datetime:
        run_start_time_str: str = self.json_data["start_time"]
        run_start_time_str: list = run_start_time_str.split(".")
        run_start_time_datetime: datetime = datetime.strptime(
            run_start_time_str[0], "%Y-%m-%dT%H:%M:%S"
        )
        run_start_time_datetime: datetime = run_start_time_datetime.astimezone(pytz.utc)
        return run_start_time_datetime

    def hash_file(self):
        # make a hash object with sha1
        h = hashlib.sha1()
        # open file for reading in binary mode
        with open(self.file_name, "rb") as file:
            # loop till the end of the file
            chunk = 0
            while chunk != b"":
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)
        # return the hex representation of digest
        return h.hexdigest()

    def getTestRunStatus(self) -> dict:
        test_status_count: dict = self.getTestRunStatusCount()
        test_run_status: dict = {
            "id": str(uuid.uuid4()),
            "test_run_id": self.test_run_id,
            "name": self.json_data["name"],
            "elapsed": self.json_data["elapsed_time"],
            "failed": test_status_count["failed"],
            "passed": test_status_count["passed"],
        }
        self.test_run_status_id = test_run_status["id"]
        return test_run_status

    def getTestRunStatusCount(self) -> dict:
        passed = 0
        failed = 0
        for suite1 in self.json_data["suites"]:
            for suite2 in suite1["suites"]:
                for test in suite2["tests"]:
                    if test["status"] == "PASS":
                        passed += 1
                    elif test["status"] == "FAIL":
                        failed += 1
        return dict({"passed": passed, "failed": failed})

    """<--<--<--<--<--<--Get all test suite-->-->-->-->-->-->"""

    def getSuitesData(self):
        suite_id: dict = dict()

        """<--<--<--1st for test suites-->-->-->"""
        start_suite_data: dict = {
            "id": str(uuid.uuid4()),
            "suite_id": None,
            "xml_id": self.hash_file(),
            "name": self.json_data["name"],
            "doc": "",
        }
        list_suite_data: list = list()
        list_suite_data.append(start_suite_data)
        """<--<--<--1st for test suites-->-->-->"""

        """<--<--<--2nd for test suites-->-->-->"""
        for suite1_data in self.json_data["suites"]:
            suite1_data_formatted: dict = {
                "id": str(uuid.uuid4()),
                "suite_id": start_suite_data["id"],
                "xml_id": self.hash_file(),
                "name": suite1_data["name"],
                "doc": "",
            }
            list_suite_data.append(suite1_data_formatted)
            for suite2_data in suite1_data["suites"]:
                suite_data: dict = {
                    "id": str(uuid.uuid4()),
                    "suite_id": suite1_data_formatted["id"],
                    "xml_id": self.hash_file(),
                    "name": suite2_data["name"],
                    "doc": "",
                }
                suite_id[suite2_data["name"]] = suite_data["id"]
                list_suite_data.append(suite_data)
        """<--<--<--2nd for test suites-->-->-->"""

        self.suite_id: dict = suite_id
        return list_suite_data

    """<--<--<--<--<--<--Get all test suite-->-->-->-->-->-->"""

    def getSuiteStatus(self):
        list_suite_status: list = list()
        for suite1 in self.json_data["suites"]:
            for suite2 in suite1["suites"]:
                suite_status_count: dict = self.getSuiteStatusCount(suite2["tests"])
                suite_data: dict = {
                    "id": str(uuid.uuid4()),
                    "test_run_id": self.test_run_id,
                    "suite_id": self.suite_id[suite2["name"]],
                    "elapsed": suite2["elapsed_time"],
                    "failed": suite_status_count["failed"],
                    "passed": suite_status_count["passed"],
                    "status": suite2["status"],
                }
                list_suite_status.append(suite_data)
        return list_suite_status

    def getSuiteStatusCount(self, test_suite: list) -> dict:
        passed = 0
        failed = 0
        for test in test_suite:
            if test["status"] == "PASS":
                passed += 1
            elif test["status"] == "FAIL":
                failed += 1
        suite_status_count: dict = {"passed": passed, "failed": failed}
        return suite_status_count

    def getTestCaseData(self) -> list:
        list_test_case_data: list = list()
        dict_test_case_id: dict = dict()
        for suite1 in self.json_data["suites"]:
            for suite2 in suite1["suites"]:
                for test in suite2["tests"]:
                    test_cases_data: dict = {
                        "id": str(uuid.uuid4()),
                        "suite_id": self.suite_id[suite2["name"]],
                        "xml_id": self.hash_file(),
                        "name": test["name"],
                        "timeout": None,
                        "doc": None,
                    }
                    list_test_case_data.append(test_cases_data)
                    dict_test_case_id[test_cases_data["name"]] = test_cases_data["id"]
        self.dict_test_case_id = dict_test_case_id
        return list_test_case_data

    def getTestCasesStatus(self) -> list:
        list_test_cases_status: list = list()
        for suite1 in self.json_data["suites"]:
            for suite2 in suite1["suites"]:
                for test in suite2["tests"]:
                    test_cases_status: dict = {
                        "id": str(uuid.uuid4()),
                        "test_case_id": self.dict_test_case_id[test["name"]],
                        "test_run_id": self.test_run_id,
                        "status": test["status"],
                        "elapsed": test["elapsed_time"],
                        "message": self.getTestMessage(test),
                    }
                    list_test_cases_status.append(test_cases_status)
        return list_test_cases_status

    def getTestMessage(self, test_case_data: dict) -> str:
        if "message" in test_case_data:
            message: str = test_case_data["message"]
        else:
            message: str = str()
        return message


class unittest_readingJSONOutput(unittest.TestCase):
    def setUp(self) -> None:
        json_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "unittestData",
            "sample_data.json",
        )
        self.readingJSONOutput = readingJSONOutput(json_path)
        self.idRegex = (
            "^([a-z0-9]{8})-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-([a-z0-9]{12})$"
        )

    def test_jsonValidation(self):
        json_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "unittestData",
            "sample_data.json",
        )
        self.assertNoLogs(readingJSONOutput(json_path))

    def test_jsonValidation_wrongSchema(self):
        json_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "unittestData",
            "wrongSchema_sample_data.json",
        )
        with self.assertRaises(ValueError, msg="JSON data is invalid."):
            readingJSONOutput(json_path)

    def test_getTestRunsData(self):
        localized = "th"
        test_site = "dev"
        expected_result: dict = {
            "id": "e179a726-aec2-46ad-a6e3-e889016770a4",
            "started_at": None,
            "imported_at": None,
            "hash": "f9ef4451e758ffe09e009928dc9ad43659277ca1",
            "test_site_id": "a060c146-e740-415a-94c7-49b0e90de13f",
            "localized_id": "ad3052e7-e05e-4436-b002-7796e181ba54",
        }
        actual_result = self.readingJSONOutput.getTestRunsData(localized, test_site)
        self.assertEqual(actual_result.keys(), expected_result.keys())
        self.assertEqual(type(actual_result["id"]), str)
        self.assertEqual(type(actual_result["started_at"]), datetime)
        self.assertEqual(type(actual_result["imported_at"]), datetime)
        self.assertEqual(type(actual_result["hash"]), str)
        self.assertEqual(type(actual_result["test_site_id"]), str)
        self.assertEqual(type(actual_result["localized_id"]), str)

    def test_getCurrentImportTime(self):
        self.assertEqual(type(self.readingJSONOutput.getCurrentImportTime()), datetime)

    def test_getTestRunStartTime(self):
        self.assertEqual(type(self.readingJSONOutput.getTestRunStartTime()), datetime)

    def test_getTestRunData_noLocalized(self):
        test_site = None
        localized = None
        with self.assertRaises(KeyError):
            self.readingJSONOutput.getTestRunsData(localized, test_site)

    def test_getTestRunStatus(self):
        localized = "th"
        test_site = "dev"
        expected_result: dict = {
            "id": "8eb8acb3-bd8d-4c33-8487-71b74da594e2",
            "test_run_id": "dc6f5e33-a88c-46a6-ac48-c88a554a26dc",
            "name": "TestSuites",
            "elapsed": 1227.093,
            "failed": 0,
            "passed": 45,
        }
        self.readingJSONOutput.getTestRunsData(localized, test_site)
        actual_result: dict = self.readingJSONOutput.getTestRunStatus()
        self.assertEqual(actual_result.keys(), expected_result.keys())
        self.assertEqual(type(actual_result["id"]), str)
        self.assertEqual(type(actual_result["test_run_id"]), str)
        self.assertEqual(actual_result["name"], expected_result["name"])
        self.assertEqual(actual_result["elapsed"], expected_result["elapsed"])
        self.assertEqual(actual_result["failed"], expected_result["failed"])
        self.assertEqual(actual_result["passed"], expected_result["passed"])

    def test_getTestRunStatusCount(self):
        expected_result: dict = {"passed": 45, "failed": 0}
        actual_result: dict = self.readingJSONOutput.getTestRunStatusCount()
        self.assertDictEqual(actual_result, expected_result)

    def test_getSuiteData(self):
        actual_result: list = self.readingJSONOutput.getSuitesData()
        self.assertEqual(type(actual_result), list)
        expected_result: dict = {
            "id": "",
            "suite_id": "",
            "xml_id": "",
            "name": "",
            "doc": "",
        }
        for index in actual_result:
            self.assertEqual(index.keys(), expected_result.keys())
            self.assertRegex(index["id"], self.idRegex)
            if index["suite_id"] == None:
                self.assertEqual(type(index["suite_id"]), type(None))
            else:
                self.assertRegex(str(index["suite_id"]), self.idRegex)
            self.assertEqual(type(index["xml_id"]), str)
            self.assertEqual(type(index["name"]), str)
            self.assertEqual(type(index["doc"]), str)

    def test_getSuiteStatus(self):
        localized = "th"
        test_site = "dev"
        self.readingJSONOutput.getTestRunsData(localized, test_site)
        self.readingJSONOutput.getSuitesData()
        expected_result: dict = {
            "id": "",
            "test_run_id": "",
            "suite_id": "",
            "elapsed": "",
            "failed": "",
            "passed": "",
            "status": "",
        }
        actual_result: list = self.readingJSONOutput.getSuiteStatus()
        self.assertEqual(type(actual_result), list)
        for index in actual_result:
            self.assertEqual(index.keys(), expected_result.keys())
            self.assertRegex(index["id"], self.idRegex)
            self.assertRegex(index["test_run_id"], self.idRegex)
            self.assertRegex(index["suite_id"], self.idRegex)
            self.assertEqual(type(index["elapsed"]), float)
            self.assertEqual(type(index["failed"]), int)
            self.assertEqual(type(index["passed"]), int)
            self.assertEqual(type(index["status"]), str)

    def test_getSuiteStatusCount(self):
        fake_suite: list = [
            {"status": "PASS"},
            {"status": "FAIL"},
        ]
        expected_result: dict = {"passed": 1, "failed": 1}
        actual_result: dict = self.readingJSONOutput.getSuiteStatusCount(fake_suite)
        self.assertDictEqual(actual_result, expected_result)

    def test_getTestCaseData(self):
        localized = "th"
        test_site = "dev"
        self.readingJSONOutput.getTestRunsData(localized, test_site)
        self.readingJSONOutput.getSuitesData()
        expected_result: dict = {
            "id": "",
            "suite_id": "",
            "xml_id": "",
            "name": "",
            "timeout": "",
            "doc": "",
        }
        actual_result: list = self.readingJSONOutput.getTestCaseData()
        self.assertEqual(type(actual_result), list)
        for index in actual_result:
            self.assertEqual(index.keys(), expected_result.keys())
            self.assertRegex(index["id"], self.idRegex)
            self.assertRegex(index["suite_id"], self.idRegex)
            self.assertEqual(type(index["xml_id"]), str)
            self.assertEqual(type(index["name"]), str)
            self.assertEqual(type(index["timeout"]), type(None))
            self.assertEqual(type(index["doc"]), type(None))

    def test_getTestCasesStatus(self):
        localized = "th"
        test_site = "dev"
        self.readingJSONOutput.getTestRunsData(localized, test_site)
        self.readingJSONOutput.getSuitesData()
        self.readingJSONOutput.getTestCaseData()
        expected_result: dict = {
            "id": "",
            "test_case_id": "",
            "test_run_id": "",
            "status": "",
            "elapsed": "",
            "message": "",
        }
        actual_result: list = self.readingJSONOutput.getTestCasesStatus()
        self.assertEqual(type(actual_result), list)
        for index in actual_result:
            self.assertEqual(index.keys(), expected_result.keys())
            self.assertRegex(index["id"], self.idRegex)
            self.assertRegex(index["test_case_id"], self.idRegex)
            self.assertRegex(index["test_run_id"], self.idRegex)
            self.assertEqual(type(index["status"]), str)
            self.assertEqual(type(index["elapsed"]), float)
            self.assertEqual(type(index["message"]), str)


if __name__ == "__main__":
    unittest.main()
    # current_dir = os.path.join(
    #     os.path.dirname(os.path.realpath(__file__)), "2024-04-19-EN.json"
    # )
    # json_data = readingJSONOutput(current_dir)
    # json_data.getTestRunsData("EN", "Dev")
    # json_data.getTestRunStatus()
    # json_data.getSuitesData()
    # json_data.getSuiteStatus()
    # json_data.getTestCaseData()
    # data = json_data.getTestCasesStatus()
    # print(data)
    # print(json_data.getTestRunsData())
    # print(json_data.getTestRunStatus())
    # print(json_data.getSuitesData())
    # print(json_data.getSuiteStatus())
