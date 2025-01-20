import src.config as c
from src.report import ReportBasics, JobReport, QueryReport
from langchain_ollama import ChatOllama
import random
import sys
from datetime import datetime
from httpx import ReadTimeout
import math
import json

lines = 100
job_name = "large_random_longrun"
trials = 1000

# This file is from Elasticsearch
# https://github.com/elastic/examples/blob/master/Common%20Data%20Formats/apache_logs/apache_logs
input_data = open(f"{c.DATA_PATH}/apache_logs/1.txt", "r").readlines()[: lines - 1]

# Replacement data of interest
replacement = '93.164.60.142 - - [17/May/2015:12:05:31 +0000] "GET /../../../etc/shadow HTTP/1.1" 200 32 "-" "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36"'

# Create an output report
# Job entry, we will submit this, and then again
job_uid = ReportBasics.uid
job_report = JobReport(
    uid=job_uid,
    job_name=job_name,
    replacement=replacement,
    description=f"This is an iterative test of random replacing one line within a sample of {lines} lines. The query will be tried {trials} times.",
    notes="N/A",
)
job_report.submit()

llm = ChatOllama(
    model="bigstick:simple",
    format="json",
    base_url="http://localhost:11434",
    cache=False,
    repeat_last_n=0,
    num_ctx=11_000,
)


def gen_data():
    # Calculate a random number within range.
    ran_replace = random.choice(range(len(input_data)))

    # Swap the data:
    input_data[ran_replace] = f"{replacement}"
    return (ran_replace, input_data)


# We like to start at one OK.
for trial in range(trials + 1):
    interest, query_data = gen_data()
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
            {query_data}
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
            (datetime.now() - start_time).total_seconds() * 1_000_000
        ),
        "query_raw": "N/A",
        "query_interest": interest,
        "query_size_bytes": sys.getsizeof(query),
        "query_notes": f"Trial {trial}/{trials}",
    }

    qr = QueryReport(**{**header, **report, "job_uid": job_uid})
    if response_metadata:
        qr.resp_metadata = str(response_metadata)
    qr.submit()

job_report.end_time = datetime.now()
job_report.submit()
