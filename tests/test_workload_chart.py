import pandas as pd
import triage_ai


def test_display_workload_chart_handles_missing_and_counts(monkeypatch):
    # Prepare a small DataFrame with various assigned_engineer values
    df = pd.DataFrame({
        'assigned_engineer': ['Alice', 'Bob', 'Alice', None, '']
    })

    # Monkeypatch Streamlit plotting/dataframe functions used by display_workload_chart
    monkeypatch.setattr(triage_ai.st, 'plotly_chart', lambda *args, **kwargs: None)
    monkeypatch.setattr(triage_ai.st, 'dataframe', lambda *args, **kwargs: None)
    monkeypatch.setattr(triage_ai.st, 'info', lambda *args, **kwargs: None)

    # Should not raise
    triage_ai.display_workload_chart(df)
