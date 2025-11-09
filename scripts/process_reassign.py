import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from mock_data import MockDataGenerator
from ai_triage import AITriageAgent
from engineer_assignment import EngineerAssignmentEngine
from data_storage import DataStorage

# load config
with open('config/sample_config.json') as f:
    cfg = json.load(f)
engineers = cfg.get('engineers', [])

triage_agent = AITriageAgent(use_openai=False)
assignment_engine = EngineerAssignmentEngine(engineers)
storage = DataStorage(cfg.get('data_storage', {}))

# load latest tickets
p = Path('data').glob('tickets_*.parquet')
files = sorted(p)
if not files:
    print('No tickets')
    raise SystemExit(0)
latest = files[-1]
df = pd.read_parquet(latest)
records = df.to_dict(orient='records')

triaged = triage_agent.batch_triage(records)
assigned = assignment_engine.assign_tickets(triaged, reset_workload=True)
from collections import Counter
print('Assigned counts after processing:', Counter([t['assigned_engineer'] for t in assigned]))

# Save
storage.save_tickets(assigned)
print('Saved re-assigned tickets')
# Now try allowing overflow so all tickets get assigned
assignment_engine.reset_workload()
assigned_overflow = assignment_engine.assign_tickets(triaged, reset_workload=True, allow_overflow=True)
print('Assigned counts with overflow enabled:', Counter([t['assigned_engineer'] for t in assigned_overflow]))
storage.save_tickets(assigned_overflow, filename='tickets_overflow_test')
print('Saved overflow-assigned tickets')
