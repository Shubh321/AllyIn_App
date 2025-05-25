import streamlit as st
st.set_page_config(page_title="AllyIn AI Agent")  
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import json
from datetime import datetime
import time
import altair as alt

from tools.router_agent import agent
from tools.logger import log_feedback
import dashboards.metrics

st.title("🤖 AllyIn AI Assistant")
st.markdown("Ask a question based on the documents. The AI will try to respond using SQL, vector search, or graph tools.")

question = st.text_input("Enter your question")

if question:
    with st.spinner("Thinking..."):
        start_time = time.time()

        try:
            response = agent.run(question)
            duration = round(time.time() - start_time, 2)
            tool_used = "Unknown"  # Replace with dynamic tracking if available

            st.success("✅ Answer:")
            st.write(response)

            st.session_state.last_question = question
            st.session_state.last_response = response
            st.session_state.last_tool = tool_used
            st.session_state.last_duration = duration

        except Exception as e:
            st.error(f"❌ Error: {e}")
            response = None

if "last_response" in st.session_state:
    st.markdown("---")
    st.subheader("📣 Was this answer helpful?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Yes"):
            log_feedback(
                st.session_state.last_question,
                st.session_state.last_response,
                "positive",
                tool=st.session_state.get("last_tool", "Unknown"),
                duration=st.session_state.get("last_duration", None)
            )
            st.success("Thanks for your feedback!")

    with col2:
        if st.button("👎 No"):
            correction = st.text_input("Suggest a better answer (optional):", key="correction")
            if st.button("Submit Correction"):
                log_feedback(
                    st.session_state.last_question,
                    st.session_state.last_response,
                    "negative",
                    correction,
                    tool=st.session_state.get("last_tool", "Unknown"),
                    duration=st.session_state.get("last_duration", None)
                )
                st.info("We'll review your feedback.")

st.sidebar.title("📊 Metrics Dashboard")

feedback_file = "feedback_log.jsonl"
if os.path.exists(feedback_file):
    with open(feedback_file, "r", encoding="utf-8") as f:
        feedback_data = []
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    if "feedback" in entry:
                        if "timestamp" not in entry:
                            entry["timestamp"] = datetime.now().isoformat()
                        feedback_data.append(entry)
                except json.JSONDecodeError:
                    continue

    if feedback_data:
        df = pd.DataFrame(feedback_data)
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date

        st.sidebar.metric("Total Queries", len(df))

        if "duration" in df.columns:
            avg_duration = round(df["duration"].dropna().astype(float).mean(), 2)
            st.sidebar.metric("Avg Query Duration (s)", avg_duration)
        else:
            st.sidebar.metric("Avg Query Duration (s)", "N/A")

        st.sidebar.subheader("Queries Per Day")
        st.sidebar.bar_chart(df["date"].value_counts().sort_index())

        st.sidebar.subheader("Tool Usage Breakdown")
        if "tool" in df.columns:
            st.sidebar.bar_chart(df["tool"].value_counts())

        st.sidebar.subheader("Query Duration by Tool")
        if "duration" in df.columns and "tool" in df.columns:
            df_chart = df[["timestamp", "duration", "tool"]].dropna()
            df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"])

            chart = alt.Chart(df_chart).mark_bar().encode(
                x=alt.X("timestamp:T", title="Query Time"),
                y=alt.Y("duration:Q", title="Duration (s)"),
                color=alt.Color("tool:N", title="Tool Used"),
                tooltip=["timestamp", "duration", "tool"]
            ).properties(
                title="Query Duration by Tool"
            )

            st.sidebar.altair_chart(chart, use_container_width=True)

    else:
        st.sidebar.info("No valid feedback entries logged yet.")
else:
    st.sidebar.info("Feedback log file not found.")

