from src.report import ReportBasics, JobReport, QueryReport
import src.config as c
from langchain_ollama import ChatOllama
from datetime import datetime
from httpx import ReadTimeout
import json
import sys
import math

trials = 100
job_name = "multi_source"
description = "Two log sources have been combined and anomalous data added."
replacement = [
    "[IPTABLES INPUT] REJECT . . . 93.164.60.142",
    '93.164.60.142 - - [17/May/2015:12:05:31 +0000] "GET /../../../etc/shadow HTTP/1.1" . . .',
]

job_uid = ReportBasics.uid
job_report = JobReport(
    uid=job_uid,
    job_name=job_name,
    replacement=','.join(replacement),
    description=description,
    notes="N/A",
)
job_report.submit()

llm = ChatOllama(
    model="bigstick:simple",
    format="json",
    base_url="http://localhost:11434",
    num_keep=900,
    cache=False,
    client_kwargs={"timeout": 600.0},
    run_id=job_uid,
    num_ctx=25000,
    mirostat=2,
)
data = open(f"{c.DATA_PATH}/iptables_logs/suss.txt", "r").readlines()
interest = "1-16,139"

for trial in range(trials + 1):
    report = {}
    response_metadata = None

    query = f"""
        Read all of the data, identify the purpose of each item, and compare them to decipher any anomalous data. Some data that appears normal might only be considered anomalous when combined with other data.
        Respond only with JSON containing the following keys and values:
            - "rank": <the rank you assigned to the anomaly>,
            - "line": <the line number of the data>/<the total number of lines in the file>,
            - "data": <the relevant data>,
            - "explanation: <the explanation for your choice>
        Respond in JSON only.

        Input:
        {data}
        """

    start_time = datetime.now()

    try:
        resp = llm.invoke(query)
        try:
            result = json.loads(resp.content)
            report = {
                "resp_error": False,
                "resp_raw": str(result),
                "query_error": False,
                "rank": result["rank"] if "rank" in result.keys() else None,
                "line": result["line"] if "line" in result.keys() else None,
                "data": result["data"] if "data" in result.keys() else None,
                "explanation": result["explanation"]
                if "explanation" in result.keys()
                else None,
            }
            response_metadata = str(resp.response_metadata) + str(resp.usage_metadata)

        except ValueError as e:
            report = {
                "resp_error": True,
                "resp_raw": str(resp.content),
                "resp_note": e,
                "query_error": False,
            }

    except ReadTimeout or TimeoutError as e:
        report = {
            "query_error": True,
            "query_notes": f"Timeout error received during {trial}",
            "resp_raw": e,
            "resp_error": True,
        }

    header = {
        "uid": trial,
        "job_name": job_name,
        "query_duration_microseconds": math.floor(
            (datetime.now() - start_time).total_seconds() * 100_000
        ),
        "query_raw": "N/A",
        "query_interest": str([interest, replacement]),
        "query_size_bytes": sys.getsizeof(query),
        "query_notes": f"Trial {trial}/{trials}",
    }

    qr = QueryReport(**{**header, **report, "job_uid": job_uid})
    if response_metadata:
        qr.resp_metadata = str(response_metadata)
    qr.submit()


job_report.end_time = datetime.now()
job_report.submit()
