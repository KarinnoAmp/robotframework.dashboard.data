import mysql.connector
import os, yaml, uuid


DATABASE_NAME: str = "robot_tests"


class databaseConnector:
    def __init__(
        self, host: str, user: str, password: str, database: str = None
    ) -> None:
        self.my_database = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )

    def cursor(self):
        self.my_cursor = self.my_database.cursor()

    def createDatabase(self, database_name):
        self.my_cursor.execute(f"CREATE DATABASE {database_name}")

    def createTable(self, create_query):
        self.my_cursor.execute(create_query)

    def queryLocalized(self) -> dict:
        localized_data: dict = dict()
        sql = str("SELECT country_code, id FROM localized")
        self.my_cursor.execute(sql)
        data = self.my_cursor.fetchall()
        for index in data:
            localized_data[index[0]] = index[1]
        return localized_data

    def queryTestSite(self) -> dict:
        test_site_data: dict = dict()
        sql = str("SELECT label, id FROM test_site")
        self.my_cursor.execute(sql)
        data = self.my_cursor.fetchall()
        for index in data:
            test_site_data[index[0]] = index[1]
        return test_site_data

    def insertTestSite_id(self, test_site: list):
        data = dict()
        for index in test_site:
            data[index] = {"label": index.upper(), "id": str(uuid.uuid4())}
        for label in data:
            sql = str("INSERT INTO test_site (label, id) VALUES (%(label)s, %(id)s)")
            self.my_cursor.execute(sql, data[label])
            self.my_database.commit()

    def insertLocalized_id(self, language: list):
        data = dict()
        for index in language:
            data[index] = {"country_code": index.upper(), "id": str(uuid.uuid4())}
        for country_code in data:
            sql = str(
                "INSERT INTO localized (country_code, id) VALUES (%(country_code)s, %(id)s)"
            )
            self.my_cursor.execute(sql, data[country_code])
            self.my_database.commit()

    def insertTestSite(self, data: dict):
        for country_code in data:
            sql = str("INSERT INTO test_site (label, id) VALUES (%(label)s, %(id)s)")
            self.my_cursor.execute(sql, data[country_code])
            self.my_database.commit()

    def insertTestRunsToDatabase(self, data: dict):
        sql = str(
            "INSERT INTO test_runs (id, started_at, imported_at, hash, test_site_id, localized_id, build_id) VALUES (%(id)s, %(started_at)s, %(imported_at)s, %(hash)s, %(test_site_id)s, %(localized_id)s, %(build_id)s)"
        )
        self.my_cursor.execute(sql, data)
        self.my_database.commit()
        print("Dumping Test run data success!!")

    def insertTestRunsStatusToDatabase(self, data: dict):
        sql = str(
            "INSERT INTO test_run_status (id, test_run_id, name, elapsed, failed, passed) VALUES (%(id)s, %(test_run_id)s, %(name)s, %(elapsed)s, %(failed)s, %(passed)s)"
        )
        self.my_cursor.execute(sql, data)
        self.my_database.commit()
        print("Dumping Test run status success!!")

    def insertSuiteData(self, data: list):
        for index in data:
            sql = "INSERT INTO suites (id, suite_id, xml_id, name, doc) VALUES (%(id)s, %(suite_id)s, %(xml_id)s, %(name)s, %(doc)s)"
            self.my_cursor.execute(sql, index)
            self.my_database.commit()
        print("Dumping Suite data success!!")

    def insertSuiteStatus(self, data: list):
        for index in data:
            sql = "INSERT INTO suite_status (id, test_run_id, suite_id, elapsed, failed, passed, status) VALUES (%(id)s, %(test_run_id)s, %(suite_id)s, %(elapsed)s, %(failed)s, %(passed)s, %(status)s)"
            self.my_cursor.execute(sql, index)
            self.my_database.commit()
        print("Dumping Suite status success!!")

    def insertTestData(self, data: list):
        for index in data:
            sql = "INSERT INTO test_cases (id, suite_id, xml_id, name, timeout, doc) VALUES (%(id)s, %(suite_id)s, %(xml_id)s, %(name)s, %(timeout)s, %(doc)s)"
            self.my_cursor.execute(sql, index)
            self.my_database.commit()
        print("Dumping Test cases data success!!")

    def insertTestCasesStatus(self, data: list):
        for index in data:
            sql = "INSERT INTO test_cases_status (id, test_case_id, test_run_id, status, elapsed, message) VALUES (%(id)s, %(test_case_id)s, %(test_run_id)s, %(status)s, %(elapsed)s, %(message)s)"
            self.my_cursor.execute(sql, index)
            self.my_database.commit()
        print("Dumping Test cases status success!!")

    def insertBuildNumber(self, data: dict):
        sql = "INSERT INTO build (id, build_number, timestamp) VALUES (%(id)s, %(build_number)s, %(timestamp)s)"
        self.my_cursor.execute(sql, data)
        self.my_database.commit()
        print("Dumping Build number success!!")

    def deleteAllData(self):
        test_case_status = [
            "DELETE FROM test_cases_status",
            "DELETE FROM test_cases",
            "DELETE FROM suite_status",
            "DELETE FROM suites",
            "DELETE FROM test_run_status",
            "DELETE FROM test_runs",
            "DELETE FROM build"
        ]
        for sql in test_case_status:
            self.my_cursor.execute(sql)
            self.my_database.commit()


if __name__ == "__main__":
    with open(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "Config", "DB-Config.yaml"
        ),
        encoding="UTF-8",
    ) as yaml_file:
        config_data = yaml.full_load(yaml_file)
    db = databaseConnector(
        host=config_data["service"]["host"],
        user=config_data["service"]["username"],
        password=config_data["service"]["password"],
        database=DATABASE_NAME,
    )
    db.cursor()
    db.deleteAllData()
    # localized = db.queryTestSite()
    # print(localized)
