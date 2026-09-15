"""Explicit normalization for this reviewed Lisbon case, not a general feed adapter."""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

def normalize(feed):
    result = deepcopy(feed)
    zone = ZoneInfo('Europe/Lisbon')
    for event in result['events']:
        for record in [event, *event['sources']]:
            value = datetime.fromisoformat(record['starts_at'])
            if value.tzinfo is not None:
                raise ValueError('This case expects the original local timestamps without offsets.')
            if value.date().isoformat() not in {'2026-09-19', '2026-09-27'}:
                raise ValueError('This normalization was reviewed only for the case-study dates.')
            record['starts_at'] = value.replace(tzinfo=zone).isoformat()
    return result

if __name__ == '__main__':
    source = Path(__file__).with_name('collected-local-times.json')
    print(json.dumps(normalize(json.loads(source.read_text(encoding='utf-8'))), ensure_ascii=False, indent=2))
