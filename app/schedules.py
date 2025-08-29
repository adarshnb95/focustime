from dateutil.rrule import rrulestr
from datetime import datetime

def occurrences_between(rrule_str: str, start: datetime, end: datetime):
    rule = rrulestr(rrule_str, dtstart=start)
    for dt in rule.between(start, end, inc=True):
        yield dt