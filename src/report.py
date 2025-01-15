from dataclasses import dataclass, fields
from datetime import datetime
import src.db as database
from string import ascii_uppercase
from random import choice
from typing import Any

"""
Each job will create an entry in a table with all of it's 
details.

The run of queries for a job is another table entirely --
this one is a line-by-line listing of query responses.

Once you instantiate the dataclass object it will insert
or update the row.
"""

@dataclass
class ReportBasics:
    uid: str = "".join(choice(ascii_uppercase) for i in range(12))

@dataclass
class JobReport:
    # You typically won't pick the UID.
    uid: str
    job_name: str
    replacement: str
    description: str
    notes: str

    start_time: datetime = datetime.now()
    end_time: datetime = None

    def __post_init__(self):
        # Build the schema:
        params = []
        for i in [f.name for f in fields(JobReport)]:
            if i != "uid":
                params.append(f"[{i}] STRING")
            else:
                params.append(f"[{i}] STRING PRIMARY KEY")

        q = f"""
            CREATE TABLE IF NOT EXISTS jobs
            (
                {','.join(map(str,params))}
            )
            """
        database.submit(conn=database.establish(), query=q)

    def submit(self):
        data = {}
        data[str(self.job_name)] = {x: str(self.__dict__[x]) for x in self.__dict__}

        ins_count = 0
        for i in data:
            column = ",".join(f"{x}" for x in data[i])
            row = ",".join(
                f"""
                    '{str(data[i][x]).replace("'",'"')}'
                """
                for x in data[i]
            )
            q = f"INSERT OR REPLACE INTO jobs({column}) VALUES({row})"

            insert = database.submit(
                conn=database.establish(), query=q
            )

            if int(insert) > ins_count:
                ins_count += insert
            else:
                print(
                    f"An insert error has occured. Review your SQL query for jobs submission.\n{q}"
                )


@dataclass
class QueryReport:
    uid: int  # This is likely the iteration count.
    job_name: str
    job_uid: str
    query_notes: str
    query_interest: int
    query_error: bool
    query_duration_microseconds: str
    query_size_bytes: str
    query_raw: str

    # All of these are strings since I can't rely
    # on the LLM response to get it right.
    # Only the raw is required, the rest can be updated
    # later.

    resp_error: bool
    resp_raw: str
    resp_note: str = None
    resp_metadata: str = None
    rank: Any = None
    line: Any = None
    data: Any = None
    explanation: Any = None

    def __post_init__(self):
        # Build the schema:
        params = []
        for i in [f.name for f in fields(QueryReport)]:
            if i != "uid":
                params.append(f"[{i}] STRING")
            else:
                params.append(f"[{i}] STRING PRIMARY KEY")

        q = f"""
            CREATE TABLE IF NOT EXISTS {self.job_name}
            (
                {','.join(map(str,params))}
            )
            """
        database.submit(conn=database.establish(), query=q)

    def submit(self):
        data = {}
        data[str(self.job_name)] = {x: str(self.__dict__[x]) for x in self.__dict__}

        ins_count = 0
        for i in data:
            column = ",".join(f"{x}" for x in data[i])
            row = ",".join(
                f"""
                    '{str(data[i][x]).replace("'",'"')}'
                """
                for x in data[i]
            )
            q = f"INSERT OR REPLACE INTO {self.job_name}({column}) VALUES({row})"

            insert = database.submit(conn=database.establish(), query=q)

            if int(insert) > ins_count:
                ins_count += insert
            else:
                print(
                    f"An insert error has occured. Review your SQL query for query submission.\n{q}"
                )
