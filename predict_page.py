import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import joblib
import streamlit as st
import warnings
warnings.filterwarnings('ignore')


def make_predictions(logs):
    loaded_model = joblib.load('facies_classification_model.joblib')
    well_predictions = loaded_model.predict(logs)
    logs['Facies'] = well_predictions
    return logs


def facies_prediction(logs, min_depth, max_depth):
    logs = make_predictions(logs)
    facies_colors = ['#F4D03F', '#F5B041', '#DC7633', '#6E2C00',
                     '#1B4F72', '#2E86C1', '#AED6F1', '#A569BD', '#196F3D']
    facies_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    logs = logs.sort_values(by='Depth')  # sorts the dataframe by depth
    cmap_facies = colors.ListedColormap(facies_colors[0:len(
        facies_colors)], 'indexed')  # make color map from a list of colors
    ztop = min_depth
    zbot = max_depth
    if ztop < logs.Depth.min() or zbot > logs.Depth.max():
        st.subheader('The depth is out of range')
        return
    cluster = np.repeat(
        np.expand_dims(
            logs['Facies'].values,
            1),
        100,
        1)  # cluster for the color map plot
    f, ax = plt.subplots(nrows=1, ncols=6, figsize=(8, 12))
    ax[0].plot(logs.GR, logs.Depth, '-g')
    ax[1].plot(logs.ILD_log10, logs.Depth, '-')
    ax[2].plot(logs.DeltaPHI, logs.Depth, '-', color='0.5')
    ax[3].plot(logs.PHIND, logs.Depth, '-', color='r')
    ax[4].plot(logs.PE, logs.Depth, '-', color='black')
    im = ax[5].imshow(cluster, interpolation='none', aspect='auto',
                      cmap=cmap_facies, vmin=1, vmax=9)

    divider = make_axes_locatable(ax[5])
    cax = divider.append_axes("right", size="20%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label((21 * ' ').join(str(item) for item in facies_labels))
    cbar.set_ticks(range(0, 1))
    cbar.set_ticklabels('')
    # sets and inverts limit on y axis
    for i in range(len(ax) - 1):
        ax[i].set_ylim(ztop, zbot)
        ax[i].invert_yaxis()
        ax[i].grid()
        ax[i].locator_params(axis='x', nbins=3)
    # sets labels and limits on the x axis
    ax[0].set_xlabel("GR")
    ax[0].set_xlim(logs.GR.min(), logs.GR.max())
    ax[1].set_xlabel("ILD_log10")
    ax[1].set_xlim(logs.ILD_log10.min(), logs.ILD_log10.max())
    ax[2].set_xlabel("DeltaPHI")
    ax[2].set_xlim(logs.DeltaPHI.min(), logs.DeltaPHI.max())
    ax[3].set_xlabel("PHIND")
    ax[3].set_xlim(logs.PHIND.min(), logs.PHIND.max())
    ax[4].set_xlabel("PE")
    ax[4].set_xlim(logs.PE.min(), logs.PE.max())
    ax[5].set_xlabel('Facies')
    # sets labels for x and y ticks
    ax[1].set_yticklabels([])
    ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    ax[5].set_yticklabels([])
    ax[5].set_xticklabels([])
    f.suptitle(
        'Well Logs and Facies for %s' %
        logs.iloc[0]['Well Name'],
        fontsize=14,
        fontweight='bold',
        y=0.9)
    st.pyplot(f)


def make_bar_charts(logs, min_depth, max_depth):
    logs = make_predictions(logs)
    min = min_depth
    max = max_depth
    if min < logs.Depth.min() or max > logs.Depth.max():
        st.subheader('The depth is out of range')
        return
    data = logs[logs['Depth'].between(min, max)]
    f, ax = plt.subplots(nrows=2, ncols=1, figsize=(6, 14), dpi=100)
    facies_colors_map = {1: '#F4D03F', 2: '#F5B041', 3: '#DC7633',
                         4: '#6E2C00', 5: '#1B4F72', 6: '#2E86C1',
                         7: '#AED6F1', 8: '#A569BD', 9: '#196F3D'}
    data_chart = data['Facies'].value_counts().to_frame().reset_index()
    data_chart.rename(
        columns={
            'index': 'Facies',
            'Facies': 'Counts'},
        inplace=True)
    labels = data_chart.Facies
    data_colors = [facies_colors_map[key] for key in labels]
    sns.barplot(
        x='Facies', y='Counts', data=data_chart,
        hue='Facies', palette=facies_colors_map,
        ax=ax[0])
    ax[0].legend(title='Facies', loc=2, bbox_to_anchor=(1, 1))
    ax[0].set_title('Counts of Facies', fontweight='bold')

    ax[1].pie(
        data_chart.Counts,
        colors=data_colors,
        labels=labels,
        autopct='%1.1f%%',
        pctdistance=0.85,
    )
    ax[1].set_title('Percentage Occurrence of Facies', fontweight='bold')
    ax[1].legend(title='Facies', loc=2, bbox_to_anchor=(1, 1))
    circle = plt.Circle((0, 0), 0.7, color='white')
    p = plt.gcf()
    p.gca().add_artist(circle)
    f.suptitle(
        'Charts for %s' %
        logs.iloc[0]['Well Name'],
        fontsize=14,
        fontweight='bold',
        y=0.95)
    st.pyplot(f)


def well_stats(logs):
    logs = make_predictions(logs)
    max_depth = logs.Depth.max()
    facies_classes = [x for x in logs.Facies.unique()]
    facies_count = logs.Facies.value_counts().to_frame()
    facies_count_max = facies_count.index[0]
    formation = [x for x in logs.Formation.unique()]
    st.subheader('Well Information')
    st.write('Well Name: %s' % logs.iloc[0]['Well Name'])
    st.write(f'Maximum depth of well: {max_depth}m')
    st.write(
        f'Facies present in well: {len(facies_count)} facies - {facies_classes}')
    st.write('Most occurring facies in well: %s' % facies_count_max)
    st.write(
        f'Formations present in well: {len(formation)} formations - {formation}')
