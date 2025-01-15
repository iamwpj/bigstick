import src.config as c
import json
import inspect
from _io import TextIOWrapper
from os import path


def _load(location) -> tuple[TextIOWrapper, dict]:
    """Local load dict of statefile

    Returns:
        tuple[TextIOWrapper, dict]: File handle of state file, full state dict.
    """

    if path.isfile(location):
        f = open(location, "r")
        try:
            data = json.loads(f)

        except TypeError:
            data = {}

        f.close

    else:
        data = {}

    fh = open(location, "w+")

    return (fh, data)


class state:
    """State Saving Function
    This will create a object storage for state-specific running.
    Essentially I act as a cache layer for settings and runtime
    posistions. Some of these will be recalled in future functions.

    We re-inspect the stack at every function since it changes.
    """

    def __init__(self, location=f"{c.DATA_PATH}/.state"):
        self.location = location
        self.fileh, self.stated = _load(location=location)

    def get(self, key: str, sub: str = None) -> str | bool | dict:
        stack = inspect.stack()

        if not sub:
            sub = f"{stack[1].filename}:{stack[1].function}"

        if sub in self.stated.keys():
            try:
                return self.stated[sub][key]
            except TypeError:
                raise Exception(f"Key not found in {json.dumps(self.stated[sub])}")
        else:
            raise Exception(f"Sub state entry not found in {self.location}")

    def save(self, item: dict, sub: str = None) -> dict:
        """Save

        Args:
            item (dict): Entry into state file.
            sub (str, optional): Provide the necessary key (sub-state). Defaults to None.

        Returns:
            dict: Returns entire state file from sub state, with added entry.
        """
        stack = inspect.stack()

        if not sub:
            sub = f"{stack[1].filename}:{stack[1].function}"

        if sub in self.stated.keys():
            sub_stated = self.stated[sub]
        else:
            self.stated[sub] = {}
            sub_stated = self.stated[sub]

        self.stated[sub] = {**sub_stated, **item}
        json.dump(self.stated, self.fileh)
        
        return self.stated[sub]

    def clear(self):
        json.dump({}, self.fileh)
