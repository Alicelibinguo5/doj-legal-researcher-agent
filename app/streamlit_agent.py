import streamlit as st
import requests
import pandas as pd
import time
import json
import os

st.title("DOJ Legal Fraud Research Agent")

# --- Analysis controls ---
fraud_type = st.selectbox(
    "Fraud Type",
    ["Any", "financial_fraud", "health_care_fraud", "disaster_fraud", "consumer_protection", "cybercrime", "false_claims_act", "public_corruption", "tax", "immigration", "intellectual_property"]
)
max_pages = st.slider("Max Pages", 1, 1000, 2)
max_cases = st.slider("Max Cases", 1, 10000, 10)

# --- Session state for results ---
if 'results' not in st.session_state:
    st.session_state['results'] = []

if st.button("Run Analysis"):
    payload = {
        "max_pages": max_pages,
        "max_cases": max_cases,
        "fraud_type": None if fraud_type == "Any" else fraud_type
    }
    try:
        BASE_URL  =os.environ.get("BACKEND_URL", "http://localhost:8000")
        # os.environ.get("BACKEND_URL", "http://backend:8000")

        res = requests.post(f"{BASE_URL}/analyze/", json=payload, timeout=10)
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
                    job_res = requests.get(f"{BASE_URL}/job/{job_id}", timeout=10)
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
# st.write('Raw results:', results)

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
    # Unique money laundering cases by URL
    def get_money_laundering_flag(row):
        gpt4o = row.get("gpt4o")
        if isinstance(gpt4o, dict):
            return gpt4o.get("money_laundering_flag", False)
        return row.get("money_laundering_flag", False)
    df["money_laundering_flag"] = df.apply(get_money_laundering_flag, axis=1)
    laundering_case_urls = set()
    for _, row in df.iterrows():
        if row["money_laundering_flag"]:
            url = row.get("url")
            if url:
                laundering_case_urls.add(url)
    unique_laundering_cases = len(laundering_case_urls)
    # Both fraud and money laundering flag
    df["fraud_and_laundering"] = df["fraud_flag"] & df["money_laundering_flag"]
    both_case_urls = set()
    for _, row in df.iterrows():
        if row["fraud_and_laundering"]:
            url = row.get("url")
            if url:
                both_case_urls.add(url)
    unique_both_cases = len(both_case_urls)
    all_charges = df["charges"].explode().dropna()
    top_charges = all_charges.value_counts().head(10)
    st.header("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cases", total_cases)
    col2.metric("Fraud Cases (unique by URL)", unique_fraud_cases)
    col3.metric("Money Laundering Cases (unique by URL)", unique_laundering_cases)
    col4.metric("Fraud & Money Laundering (unique by URL)", unique_both_cases)
    st.markdown("---")
    st.subheader("Top Charges")
    if not top_charges.empty:
        st.bar_chart(top_charges)
        st.dataframe(top_charges.reset_index().rename(columns={"index": "Charge", "charges": "Count"}), use_container_width=True)
    else:
        st.write("No charges found.")
    st.markdown("---")
    # --- Case results ---
    st.subheader("Case Results Table")
    display_rows = []
    for case in results:
        gpt4o = case.get('gpt4o')
        if isinstance(gpt4o, dict):
            fraud_flag = gpt4o.get('fraud_flag')
            reasoning = gpt4o.get('fraud_rationale')
            category = gpt4o.get('fraud_type')
            money_laundering_flag = gpt4o.get('money_laundering_flag', None)
            money_laundering_evidence = gpt4o.get('money_laundering_evidence', None)
        else:
            fraud_info = case.get('fraud_info')
            if fraud_info:
                fraud_flag = fraud_info.get('is_fraud')
                reasoning = fraud_info.get('evidence')
                category = ', '.join([c for c in fraud_info.get('charge_categories', [])])
            else:
                fraud_flag = None
                reasoning = None
                category = None
            money_laundering_flag = case.get('money_laundering_flag', None)
            money_laundering_evidence = case.get('money_laundering_evidence', None)
        both_flag = bool(fraud_flag) and bool(money_laundering_flag)
        display_rows.append({
            'Title': case.get('title', 'No Title'),
            'Date': case.get('date', 'N/A'),
            'URL': case.get('url', ''),
            'Charges': ', '.join(case.get('charges', [])),
            'Categories': ', '.join(case.get('charge_categories', [])),
            'Fraud Flag': fraud_flag,
            'Fraud Category': category,
            'Reasoning': reasoning,
            'Money Laundering Flag': money_laundering_flag,
            'Money Laundering Evidence': money_laundering_evidence,
            'Fraud & Money Laundering': both_flag
        })
    case_df = pd.DataFrame(display_rows)
    # Color highlighting for flags
    def highlight_flags(val):
        if val is True:
            return 'background-color: #ffcccc; color: #b30000; font-weight: bold;'
        elif val is False:
            return 'background-color: #e6ffe6; color: #006600;'
        return ''
    # Make URLs clickable with a short label
    def make_clickable(val):
        if isinstance(val, str) and val.startswith('http'):
            return f'<a href="{val}" target="_blank">Open</a>'
        return val
    if not case_df.empty:
        case_df_display = case_df.copy()
        case_df_display['URL'] = case_df_display['URL'].apply(make_clickable)
        # Use to_html and st.markdown to render HTML links
        st.markdown(case_df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown("<small>Tip: Click 'Open' in the URL column to open the press release.</small>", unsafe_allow_html=True)
    else:
        st.info("No case results to display.") 