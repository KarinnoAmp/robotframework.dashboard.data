# robotframework.dashboard.data
RobotFramework result dashboard on Grafana

# Requirements
- robotframework >= 7.0
- Python >= 3.11
- MySQL database or any other with same syntax

# How to dump the data
 1. Edit your database config in the `Config/DB-Config.yaml`.
 2. Use `python3` command with `createDB.py` file.
    ```bash
    python3 createDB.py
    ```
 3. After create the database now you can dump the robotframework result to your database. You can use `python3` command with `dumpData.py` file for dumping the data.
    ```bash
    python3 dumpData.py -f <output.json> -l <localized> -e <environment>
    ```
    *Note:* Before running `dumpData.py` please convert `output.xml` to `.json` file via `rebot` command.
    ```bash
    rebot -l None -r None -o <output.xml> output.xml
    ```