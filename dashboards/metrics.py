import os
import json
from collections import defaultdict
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

TOOL_LOG_PATH = os.path.join("logs", "tool_metrics_log.jsonl")

query_counts = defaultdict(int)
tool_usage = defaultdict(int)
timings = []

if os.path.exists(TOOL_LOG_PATH):
    with open(TOOL_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            date = data["timestamp"].split("T")[0]
            query_counts[date] += 1
            tool_usage[data["tool"]] += 1
            timings.append(data.get("duration", 0))

st.sidebar.title("📊 Metrics Dashboard")

total_queries = sum(query_counts.values())
st.sidebar.metric("Total Queries", total_queries)

st.sidebar.subheader("Queries Per Day")
st.sidebar.bar_chart(pd.Series(query_counts))

st.sidebar.subheader("Tool Usage Breakdown")
st.sidebar.bar_chart(pd.Series(tool_usage))

avg_time = round(sum(timings) / len(timings), 2) if timings else 0
st.sidebar.metric("Avg. Query Duration (s)", avg_time)
