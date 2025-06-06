import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.title("Clinical Trial Dashboard")

# Load data
conn = sqlite3.connect('data/clinical_data.db')
demographics = pd.read_sql('SELECT * FROM demographics', conn)
adverse_events = pd.read_sql('SELECT * FROM adverse_events', conn)
conn.close()

# Show metrics
st.metric("Total Subjects", len(demographics))
st.metric("Total AEs", len(adverse_events))

# Show data
st.subheader("Demographics")
st.dataframe(demographics.head())

st.subheader("Adverse Events")
st.dataframe(adverse_events.head())
