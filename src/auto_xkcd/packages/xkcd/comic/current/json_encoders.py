import typing as t
from datetime import datetime
import pendulum
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, pendulum.DateTime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
