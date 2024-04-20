from connectDB import databaseConnector
import yaml
import os


"""<--<--<--<--<--<--<--<--<--Loading config file -->-->-->-->-->-->-->-->-->"""
with open(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "Config", "DB-Config.yaml"
    ),
    encoding="UTF-8",
) as yaml_file:
    CONFIG = yaml.full_load(yaml_file)
"""<--<--<--<--<--<--<--<--<--Loading config file -->-->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<-- Create robot_test database -->-->-->-->-->-->-->-->"""
MY_DATABASE = databaseConnector(
    host=CONFIG["service"]["host"],
    user=CONFIG["service"]["username"],
    password=CONFIG["service"]["password"],
)
MY_DATABASE.cursor()
MY_DATABASE.createDatabase(CONFIG["service"]["database"])
"""<--<--<--<--<--<--<--<-- Create robot_test database -->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<-- Connect robot_tests database -->-->-->-->-->-->-->"""
MY_DATABASE = databaseConnector(
    host=CONFIG["service"]["host"],
    user=CONFIG["service"]["username"],
    password=CONFIG["service"]["password"],
    database=CONFIG["service"]["database"],
)
MY_DATABASE.cursor()
"""<--<--<--<--<--<--<-- Connect robot_tests database -->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<-- Create table test site -->-->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE TABLE test_site (
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        label TEXT
    )
    """
)
MY_DATABASE.insertTestSite_id(CONFIG["testSite"])
"""<--<--<--<--<--<--<--<-- Create table test site -->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<-- Create table localized -->-->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE TABLE localized (
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        country_code TEXT
    )
    """
)
MY_DATABASE.insertLocalized_id(CONFIG["localized"])
"""<--<--<--<--<--<--<--<-- Create table localized -->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<-- Create table test_runs -->-->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE TABLE test_runs (
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        source_file TEXT,
        started_at DATETIME,
        finished_at DATETIME,
        imported_at DATETIME NOT NULL,
        localized_id TEXT,
        test_site_id VARCHAR(255),
        hash VARCHAR(255) NOT NULL UNIQUE,
        FOREIGN KEY (test_site_id) REFERENCES test_site (id)
    )
    """
)
"""<--<--<--<--<--<--<--<-- Create table test_runs -->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<-- Create table test_runs_status -->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE TABLE test_run_status (
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        test_run_id VARCHAR(255) NOT NULL,
        name TEXT NOT NULL,
        elapsed INT,
        failed INT NOT NULL,
        passed INT NOT NULL,
        FOREIGN KEY (test_run_id) REFERENCES test_runs (id)
    )
    """
)
"""<--<--<--<--<--<--<-- Create table test_runs_status -->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<--<-- Create table suites -->-->-->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE Table suites(
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        suite_id VARCHAR(255),
        xml_id TEXT NOT NULL,
        name TEXT,
        source TEXT,
        doc TEXT NOT NULL
    )
    """
)
"""<--<--<--<--<--<--<--<--<-- Create table suites -->-->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<-- Create table suites_status -->-->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE Table suite_status(
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        test_run_id VARCHAR(255),
        suite_id VARCHAR(255),
        elapsed INT NOT NULL,
        failed INT NOT NULL,
        passed INT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (test_run_id) REFERENCES test_runs (id),
        FOREIGN KEY (suite_id) REFERENCES suites (id)
    )
    """
)
"""<--<--<--<--<--<--<--<-- Create table suites_status -->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<--<-- Create table test_cases -->-->-->-->-->-->-->-->-->"""
MY_DATABASE.createTable(
    """
    CREATE Table test_cases(
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        suite_id VARCHAR(255),
        xml_id TEXT NOT NULL,
        name TEXT NOT NULL,
        timeout TEXT,
        doc TEXT,
        FOREIGN KEY (suite_id) REFERENCES suites (id)
    )
    """
)
"""<--<--<--<--<--<--<--<--<-- Create table test_cases -->-->-->-->-->-->-->-->-->"""


"""<--<--<--<--<--<--<--<-- Create table test_cases_status -->-->-->-->-->-->-->-->"""

MY_DATABASE.createTable(
    """
    CREATE Table test_cases_status(
        id VARCHAR(255) PRIMARY KEY NOT NULL,
        test_case_id VARCHAR(255) NOT NULL,
        test_run_id VARCHAR(255) NOT NULL,
        status TEXT NOT NULL,
        elapsed INT NOT NULL,
        message TEXT,
        FOREIGN KEY (test_case_id) REFERENCES test_cases (id),
        FOREIGN KEY (test_run_id) REFERENCES test_runs (id)
    )
    """
)
"""<--<--<--<--<--<--<--<-- Create table test_cases_status -->-->-->-->-->-->-->-->"""
