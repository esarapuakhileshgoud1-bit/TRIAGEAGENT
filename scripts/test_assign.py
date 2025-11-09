from pathlib import Path
import pandas as pd
import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
from engineer_assignment import EngineerAssignmentEngine
import json

# load config engineers
with open('config/sample_config.json') as f:
    cfg = json.load(f)
engineers = cfg.get('engineers', [])
engine = EngineerAssignmentEngine(engineers)

# load tickets
p = Path('data').glob('tickets_*.parquet')
files = sorted(p)
if not files:
    print('No tickets')
    raise SystemExit(0)
latest = files[-1]
df = pd.read_parquet(latest)
records = df.to_dict(orient='records')

assigned = engine.assign_tickets(records, reset_workload=True)
from collections import Counter
print('Assigned counts:', Counter([t['assigned_engineer'] for t in assigned]))
print('Sample assigned:', assigned[:5])
