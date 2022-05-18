import streamlit as st
import pandas as pd
from predict_page import facies_prediction, make_bar_charts, well_info


st.title("Prediction of Facies")
log_info = st.file_uploader('Upload well logs as a csv file', type = ['csv']) 
if log_info is not None:
    log_info = pd.read_csv(log_info)
    logs = pd.DataFrame(log_info) 
col3, col4, col5 = st.columns([1,.6,.4])
with col3:
    predict = st.button('Predict Facies')
with col4:
    chart = st.button('Charts')   
with col5:
    weell_info = st.button('Well info') 

if predict:
    col1, col2 = st.columns([1,1])
    with col1:
        min_depth = st.number_input('Min Depth', help = 'enter a minimum depth',
        value = logs.Depth.min())
    with col2:
        max_depth = st.number_input('Max Depth', help = 'enter a maximum depth',
        value = logs.Depth.max())
    facies_prediction(logs, min_depth, max_depth)
if chart:
    col1, col2 = st.columns([1,1])
    with col1:
        min_depth = st.number_input('Min Depth', help = 'enter a minimum depth',
        value = logs.Depth.min())
    with col2:
        max_depth = st.number_input('Max Depth', help = 'enter a maximum depth',
        value = logs.Depth.max())
    make_bar_charts(logs, min_depth, max_depth)
if weell_info:
    well_info(logs)
