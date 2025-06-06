import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.set_page_config(page_title="Clinical Trial Dashboard", layout="wide")
st.title("🏥 Clinical Trial Risk-Based Monitoring Dashboard")

# Load data
conn = sqlite3.connect('data/clinical_data.db')
demographics = pd.read_sql('SELECT * FROM demographics', conn)
adverse_events = pd.read_sql('SELECT * FROM adverse_events', conn)
conn.close()

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Subjects", len(demographics))
with col2:
    st.metric("Total AEs", len(adverse_events))
with col3:
    active_count = len(demographics[demographics['treatment_arm'] == 'Active'])
    st.metric("Active Arm", active_count)
with col4:
    st.metric("Sites", demographics['site_id'].nunique())

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Enrollment by Site")
    site_data = demographics.groupby('site_id').size().reset_index(name='count')
    fig1 = px.bar(site_data, x='site_id', y='count', title="Subjects per Site")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("⚠️ AE Severity Distribution")
    ae_severity = adverse_events.groupby('severity').size().reset_index(name='count')
    fig2 = px.pie(ae_severity, values='count', names='severity', title="Adverse Events by Severity")
    st.plotly_chart(fig2, use_container_width=True)

# Data tables
st.subheader("📋 Subject Demographics")
st.dataframe(demographics)

st.subheader("📋 Adverse Events")
st.dataframe(adverse_events)
