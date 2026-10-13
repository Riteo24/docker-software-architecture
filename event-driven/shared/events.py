from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
from jsonschema import Draft202012Validator, FormatChecker

SCHEMAS = Path(__file__).resolve().parents[1] / 'schemas'

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def event(type: str, **payload):
    return {'type':type, 'eventId':str(uuid4()), **payload, 'ts':timestamp()}

def validate_event(value):
    type = value.get('type')
    if type not in {'OrderCreated','PaymentCaptured','EmailSent'}:
        raise ValueError('unknown event type')
    schema = json.loads((SCHEMAS / (type+'.json')).read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
