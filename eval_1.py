from src.report import ReportBasics, JobReport, QueryReport
from string import ascii_uppercase as ABC
import sys
from datetime import datetime
from httpx import ReadTimeout
import json
import math
from langchain_ollama import ChatOllama

trials = 1000
job_name = "small_dim_array"

# Generate a sample
sample = {}
for letter in ABC:
    sample[letter] = 0

sample["F"] = 1

job_uid = ReportBasics.uid
job_report = JobReport(
    uid=job_uid,
    job_name=job_name,
    replacement="'F':1",
    description="Testing very small 1 dimensional array.",
    notes="N/A",
)
# job_report.submit()

llm = ChatOllama(
    model="bigstick:simple",
    format="json",
    base_url="http://localhost:11434",
    cache=False,
    repeat_last_n=0,
    client_kwargs={"timeout": 3.0},
)

for trial in range(1, trials + 1):
    interest = list(sample.keys()).index("F")
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
    {json.dumps(sample,indent=2)}
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
                "query_notes": f"Trial {trial}/{trials}",
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
    }

    qr = QueryReport(**{**header, **report, "job_uid": job_uid})
    if response_metadata:
        qr.resp_metadata = str(response_metadata)
    # qr.submit()
    print(qr.query_duration_microseconds / 1_000_000, qr.query_notes, qr.query_error)

job_report.end_time = datetime.now()
# job_report.submit()
