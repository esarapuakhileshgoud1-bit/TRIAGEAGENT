import glob
import os
import sys
import pandas as pd


def main():
    data_dir = os.path.join(os.getcwd(), 'data')
    pattern = os.path.join(data_dir, 'tickets_*.parquet')
    files = sorted(glob.glob(pattern))
    if not files:
        print('NO_TICKET_FILES_FOUND')
        return 2

    latest = files[-1]
    try:
        df = pd.read_parquet(latest)
    except Exception as e:
        print('FAILED_TO_READ_PARQUET', e)
        return 3

    # Defensive: ensure assigned_engineer exists
    if 'assigned_engineer' not in df.columns:
        print('NO_ASSIGNED_ENGINEER_COLUMN')
        return 4

    counts = df['assigned_engineer'].fillna('Unassigned').astype(str).value_counts(dropna=False)
    print('FILE:', latest)
    for name, cnt in counts.items():
        print(f'{name}: {cnt}')

    unassigned = int(counts.get('Unassigned', 0))
    if unassigned > 0:
        print('UNASSIGNED_PRESENT')
        return 1
    else:
        print('ALL_ASSIGNED')
        return 0


if __name__ == '__main__':
    sys.exit(main())
