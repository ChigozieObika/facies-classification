import streamlit as st
import pandas as pd
from predict_page import facies_prediction, make_bar_charts, well_stats


st.title("Prediction of Facies")
log_info = st.file_uploader('Upload well logs as a csv file', type=['csv'])
if log_info is not None:
    log_info = pd.read_csv(log_info)
    logs = pd.DataFrame(log_info)
try:
    col1, col2 = st.columns([1, 1])
    with col1:
        min_depth = st.number_input('Min Depth', help='enter a minimum depth',
                                    value=logs.Depth.min())
    with col2:
        max_depth = st.number_input('Max Depth', help='enter a maximum depth',
                                    value=logs.Depth.max())
except NameError:
    st.write('Upload the well logs in the section above.')
    st.write('For well information click "Well Info".')
    st.write('For a plot of predicted facies click "Predicted Facies"')
    st.write('Click "Charts" for a visualization of the predicted facies distribution')

col3, col4, col5 = st.columns([1, 1, 1])
with col3:
    well_info = st.button('Well Info')
with col4:
    predict = st.button('Predict Facies')
with col5:
    chart = st.button('Charts')

if predict:
    facies_prediction(logs, min_depth, max_depth)
if chart:
    make_bar_charts(logs, min_depth, max_depth)
if well_info:
    well_stats(logs)
