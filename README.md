# robotframework.dashboard.data
RobotFramework result dashboard on Grafana

# Requirements
- robotframework >= 7.0
- Python >= 3.11
- MySQL database or any other with same syntax

# How to dump the data?
 1. Edit your database config in the `Config/DB-Config.yaml`.
 2. Use `python3` command with `createDB.py` file.
    ```bash
    python3 createDB.py
    ```
 3. After create the database now you can dump the robotframework result to your database. You can use `python3` command with `dumpData.py` file for dumping the data.
    ```bash
    python3 dumpData.py -f <output.json> -l <language> -e <environment>
    ```
    - `-f` or `--file` is `output.json` file.
    - `-l` or `--language` is a result of language for that running.
    - `-e` or `--environment` is a result of environment or test site for that running.

    *Note:* Before running `dumpData.py` please convert `output.xml` to `output.json` file via `rebot` command.
    ```bash
    rebot -l None -r None -o <output.xml> output.xml
    ```
# How to use Docker compose for this repo?
You can use the docker for try to create the dashboard on Grafana by these command.
### Start all service at 1st time
```bash
docker-compose up -d
```
*Note:* `-d` for detach to not show the logs
### Start all service
```bash
docker-compose start
```
### Stop all service
```bash
docker-compose stop
```
### Stop all service and delete the container
```bash
docker-compose down
```