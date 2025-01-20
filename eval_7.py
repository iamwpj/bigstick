from src.report import ReportBasics, JobReport, QueryReport
import src.config as c
from langchain_ollama import ChatOllama
from datetime import datetime
from httpx import ReadTimeout
import json
import sys
import math
import random

trials = 1000
job_name = "query_growth"
description = "Adding to the query size to test response time."
replacement = "$"
input_data = open(f"{c.DATA_PATH}/words.txt", "r").read().split("\n")

job_uid = ReportBasics.uid
job_report = JobReport(
    uid=job_uid,
    job_name=job_name,
    replacement=replacement,
    description=description,
    notes="N/A",
)
job_report.submit()

llm = ChatOllama(
    model="bigstick:simple",
    format="json",
    base_url="http://localhost:11434",
    num_keep=900,
    client_kwargs={"timeout": 600.0},
    run_id=job_uid,
    num_ctx=25_000,
    mirostat=2,
)


def gen_data(wordcount=100):
    # Calculate a random number within range.
    ran_replace = random.choice(range(wordcount))

    # Return words
    sample = random.sample(input_data, wordcount)
    # Swap the data:
    sample[ran_replace] = replacement
    return (ran_replace, sample)


for trial in range(trials + 1):
    report = {}
    response_metadata = None

    interest, data = gen_data(wordcount=(trial + 1) * 10)

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
            (datetime.now() - start_time).total_seconds() * 1_000_000
        ),
        "query_raw": "N/A",
        "query_interest": interest,
        "query_size_bytes": sys.getsizeof(query),
        "query_notes": f"Trial {trial+1}/{trials}",
    }

    qr = QueryReport(**{**header, **report, "job_uid": job_uid})
    if response_metadata:
        qr.resp_metadata = str(response_metadata)
    qr.submit()


job_report.end_time = datetime.now()
job_report.submit()
