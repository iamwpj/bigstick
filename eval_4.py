from src.report import ReportBasics, JobReport, QueryReport
import json
import random
import string
import sys
from datetime import datetime
import math
from httpx import ReadTimeout
from langchain_ollama import ChatOllama

job_name = "sliding_context_window"
maximum = 128_000
step = 1_000
description = f"Test the effect of increasing data and increasing context window on query time and accuracy. We will scale from {step} to {maximum} by increasing {step}"
replacement = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))

# Create an output report
# Job entry, we will submit this, and then again
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
    cache=False,
    repeat_last_n=0,
    run_id=job_uid,
    num_ctx=step,
)


def gen_data(line_count=step):
    fill = "f" * 16
    result = [f"{x}={fill}" for x in range(line_count)]
    ran_replace = random.choice(range(line_count))

    result[ran_replace] = f"{ran_replace}={replacement}"
    return (ran_replace, result)


# Start at the first increment (step)
for trial in range(step, maximum, step):
    llm.num_ctx = trial

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
            (datetime.now() - start_time).total_seconds() * 100_000
        ),
        "query_raw": "N/A",
        "query_interest": str([interest, replacement]),
        "query_size_bytes": sys.getsizeof(query),
        "query_notes": f"Trial {trial}/{maximum}",
    }

    qr = QueryReport(**{**header, **report, "job_uid": job_uid})
    if response_metadata:
        qr.resp_metadata = str(response_metadata)
    qr.submit()


job_report.end_time = datetime.now()
job_report.submit()
