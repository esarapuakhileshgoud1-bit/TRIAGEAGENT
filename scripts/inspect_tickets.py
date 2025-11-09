import pandas as pd
import sys
from pathlib import Path
p = Path('data').glob('tickets_*.parquet')
files = sorted(p)
if not files:
    print('No files')
    sys.exit(1)
latest = files[-1]
print('Reading', latest)
df = pd.read_parquet(latest)
print('Columns:', df.columns.tolist())
print(df.head(10).to_dict(orient='records'))
