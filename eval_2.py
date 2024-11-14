from src.bigstick import LoadedModel as lm
import src.config as c
from src.report import ReportBasics, JobReport, QueryReport
from string import ascii_uppercase as ABC
import sys
from datetime import datetime
from httpx import ReadTimeout
import json
import math
import random

trials = 10
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

for trial in range(1, trials + 1):
    interest, query_data = gen_data()

    query = f"""
        Find any anomalies in this data: {query_data}
        Respond only with JSON containing the following keys and values:
            - "rank": <the rank you assigned to the anomaly>,
            - "line": <the line number of the data>,
            - "data": <the relevant data>,
            - "explanation: <the explanation for your choice>
            
        """

    start_time = datetime.now()
    try:
        resp = lm(json_mode=True, base_url=f"http://{c.GPU_NODE}:11434").Simple(
            query=query
        )

        try:
            result = json.loads(resp.model_dump_json())["text"].strip("\n")
            report = {"resp_error": False, "resp_raw": result, "query_error": False}

        except ValueError as e:
            report = {
                "resp_error": True,
                "resp_raw": resp.model_dump_json(),
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
        "query_notes": f"Trial {trial}/{trials}",
    }

    qr = QueryReport(**{**header, **report})
    qr.submit()

job_report.end_time = datetime.now()
job_report.submit()
