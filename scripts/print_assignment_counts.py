import pandas as pd
from pathlib import Path
p = Path('data').glob('tickets_*.parquet')
files = sorted(p)
if not files:
    print('No files found')
    raise SystemExit(0)
latest = files[-1]
print('Reading', latest)
df = pd.read_parquet(latest)
print('\nassigned_engineer value counts:')
print(df['assigned_engineer'].value_counts(dropna=False))
print('\nSample rows:')
print(df[['assigned_engineer','ai_skills','ai_category']].head(20).to_string())
