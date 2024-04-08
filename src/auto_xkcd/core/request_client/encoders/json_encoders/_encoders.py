from __future__ import annotations

from datetime import datetime
import json
import typing as t

import pendulum


class DateTimeEncoder(json.JSONEncoder):
    """Handle encoding a `datetime.datetime` or `pendulum.DateTime` as an ISO-formatted string."""

    def default(self, o) -> str | json.Any:
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, pendulum.DateTime):
            return o.isoformat()

        return json.JSONEncoder.default(self=self, o=o)
