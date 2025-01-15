import src.config as c
from src.report import ReportBasics, JobReport, QueryReport
import sys
from datetime import datetime
from httpx import ReadTimeout
import json
import math
import random
from langchain_ollama import ChatOllama

trials = 1000
job_name = "smalldim_varlength"

replacement = "/../../../etc/shadow"
input_data = []
[
    input_data.append(f"{k},{v}")
    for k, v in enumerate(
        [
            x.split(" ")[6]
            for x in open(
                f"{c.DATA_PATH}/generated-logs/generated.log", "r"
            ).readlines()
        ]
    )
]


def gen_data():
    # Calculate a random number within range.
    ran_replace = random.choice(range(len(input_data)))

    # Replacement
    input_data[ran_replace] = f"{ran_replace},{replacement}"

    return (ran_replace, input_data)


job_uid = ReportBasics.uid
job_report = JobReport(
    uid=job_uid,
    job_name=job_name,
    replacement=replacement,
    description="Testing very small 1 dimensional array with variable data length",
    notes="N/A",
)
job_report.submit()

llm = ChatOllama(
    model="bigstick:simple",
    format="json",
    base_url="http://localhost:11434",
    cache=False,
    repeat_last_n=0,
)

for trial in range(1, trials + 1):
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
                "query_notes": f"Trial {trial}/{trials}",
                **result,
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
            "query_note": f"Timeout error received during {trial}",
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
        "query_interest": interest,
        "query_size_bytes": sys.getsizeof(query),
    }

    qr = QueryReport(**{**header, **report, "job_uid": job_uid})
    if response_metadata:
        qr.resp_metadata = str(response_metadata)
    qr.submit()

job_report.end_time = datetime.now()
job_report.submit()
