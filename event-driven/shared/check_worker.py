import time
from pathlib import Path

heartbeat = Path('/tmp/worker-heartbeat')
assert heartbeat.exists() and time.time() - float(heartbeat.read_text()) < 30
