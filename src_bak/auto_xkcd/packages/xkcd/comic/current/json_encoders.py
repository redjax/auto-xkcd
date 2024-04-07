from __future__ import annotations

from datetime import datetime
import json
import typing as t

import pendulum

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, pendulum.DateTime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
