import streamlit as st
import requests
import pandas as pd
import time
import json
import os

st.title("DOJ Legal Fraud Research Agent")

# Use BACKEND_URL from environment or default to Docker Compose service name
backend_url = os.environ.get("BACKEND_URL", "http://backend:8000")

# --- Analysis controls ---
query = st.text_input("Search Topic")
fraud_type = st.selectbox(
    "Fraud Type",
    ["Any", "financial_fraud", "health_care_fraud", "disaster_fraud", "consumer_protection", "cybercrime", "false_claims_act", "public_corruption", "tax", "immigration", "intellectual_property"]
)
max_pages = st.slider("Max Pages", 1, 1000, 10)
max_cases = st.slider("Max Cases", 1, 10000, 100)

# --- Session state for results ---
if 'results' not in st.session_state:
    st.session_state['results'] = []

if st.button("Run Analysis"):
    payload = {
        "query": query,
        "max_pages": max_pages,
        "max_cases": max_cases,
        "fraud_type": None if fraud_type == "Any" else fraud_type
    }
    try:
        res = requests.post(f"{backend_url}/analyze/", json=payload, timeout=10)
        res.raise_for_status()
        job_id = res.json().get("job_id")
        if not job_id:
            st.error("No job_id returned from backend.")
        else:
            with st.spinner("Running analysis (async)..."):
                status = "pending"
                error = None
                poll_count = 0
                while status not in ("done", "error") and poll_count < 120:
                    poll_count += 1
                    time.sleep(2)
                    job_res = requests.get(f"{backend_url}/job/{job_id}", timeout=10)
                    job_data = job_res.json()
                    status = job_data.get("status")
                    error = job_data.get("error")
                if status == "done":
                    st.session_state['results'] = job_data.get("result", [])
                    st.success("Analysis complete. Results below.")
                elif status == "error":
                    st.error(f"Job failed: {error}")
                else:
                    st.error("Job timed out or unknown status.")
    except Exception as e:
        st.error(f"Error: {e}")

results = st.session_state['results']

# Debug: Show raw results for inspection
st.write('Raw results:', results)

# --- Summary statistics and results display ---
if not results:
    st.info("No cases found.")
else:
    # --- Summary statistics ---
    df = pd.DataFrame(results)
    def get_fraud_flag(row):
        # Prefer GPT-4o fraud flag if present
        if isinstance(row.get("gpt4o"), dict):
            return row["gpt4o"].get("fraud_flag", False)
        # Fallback to classic
        if isinstance(row.get("fraud_info"), dict):
            return row["fraud_info"].get("is_fraud", False)
        return False
    df["fraud_flag"] = df.apply(get_fraud_flag, axis=1)
    total_cases = len(df)
    # Unique fraud cases by URL
    fraud_case_urls = set()
    for _, row in df.iterrows():
        if row["fraud_flag"]:
            url = row.get("url")
            if url:
                fraud_case_urls.add(url)
    unique_fraud_cases = len(fraud_case_urls)
    all_charges = df["charges"].explode().dropna()
    top_charges = all_charges.value_counts().head(10)
    st.header("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", total_cases)
    col2.metric("Fraud Cases (unique by URL)", unique_fraud_cases)
    col3.metric("Fraud Cases (raw sum)", int(df["fraud_flag"].sum()))
    st.subheader("Top Charges")
    if not top_charges.empty:
        st.table(top_charges.reset_index().rename(columns={"index": "Charge", "charges": "Count"}))
    else:
        st.write("No charges found.")
    st.markdown("---")
    # --- Case results ---
    for case in results:
        st.write(f"### {case.get('title', 'No Title')}")
        st.markdown(f"**Date**: {case.get('date', 'N/A')}")
        st.markdown(f"**URL**: [{case.get('url', 'N/A')}]({case.get('url', '')})")
        st.markdown(f"**Charges**: {', '.join(case.get('charges', []))}")
        st.markdown(f"**Categories**: {', '.join(case.get('charge_categories', []))}")
        fraud_flag = None
        reasoning = None
        category = None
        # Prefer GPT-4o fraud info if present
        gpt4o = case.get('gpt4o')
        if isinstance(gpt4o, dict):
            fraud_flag = gpt4o.get('fraud_flag')
            reasoning = gpt4o.get('fraud_rationale')
            category = gpt4o.get('fraud_type')
        else:
            fraud_info = case.get('fraud_info')
            if fraud_info:
                fraud_flag = fraud_info.get('is_fraud')
                reasoning = fraud_info.get('evidence')
                category = ', '.join([c for c in fraud_info.get('charge_categories', [])])
        st.markdown(f"**Fraud Flag**: {fraud_flag}")
        st.markdown(f"**Fraud Category**: {category}")
        st.markdown(f"**Reasoning**: {reasoning}")
        st.markdown("---") 