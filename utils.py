import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
from scipy.stats import chi2_contingency
from scipy.stats import chi2

import config

class UniAnalysis():
    def __init__(self, df):
        self.df = df
    
    def describe_feature(self, feature):
        return self.df[feature].describe()
    
    def create_histplot(self, feature, bins):
        plt.rcParams.update({'figure.figsize':(5,3), 'figure.dpi':100})
        sns.histplot(self.df[feature],bins=bins,kde=True)
        plt.ylabel('Count', fontsize = 12, fontweight ='bold')
        plt.xlabel(f'{feature}', fontsize = 12, fontweight ='bold')
        plt.title('Frequency Distribution of {}'.format(feature), fontsize = 14, fontweight = 'bold')
        plt.show()
    
    def create_boxplot(self, feature, label):
        _, ax = plt.subplots(nrows=1, ncols=2, sharey=True,figsize=(10,4), gridspec_kw = {'width_ratios':[0.3, 0.8]}, dpi=100)
        sns.boxplot(y=self.df[feature],ax=ax[0])
        ax[0].set_ylabel(f'{feature}', fontsize = 12, fontweight ='bold')
        ax[0].set_title('{} Distribution(Boxplot)'.format(feature), fontsize = 14, fontweight = 'bold')
        sns.boxplot(y=self.df[feature], x=self.df[label], ax=ax[1])
        ax[1].set_ylabel(f'{feature}', fontsize = 12, fontweight ='bold')
        ax[1].set_xlabel(f'{label}', fontsize = 12, fontweight ='bold')
        ax[1].set_title(f'{feature} vs {label} Boxplot', fontsize = 14, fontweight = 'bold')
        plt.show()

def make_facies_log_plot(logs, facies_colors):
    logs = logs.sort_values(by='Depth')
    cmap_facies = colors.ListedColormap(
            facies_colors[0:len(facies_colors)], 'indexed')
    
    ztop=logs.Depth.min(); zbot=logs.Depth.max()
    
    cluster=np.repeat(np.expand_dims(logs['Facies'].values,1), 100, 1)
    
    f, ax = plt.subplots(nrows=1, ncols=6, figsize=(8, 12))
    ax[0].plot(logs.GR, logs.Depth, '-g')
    ax[1].plot(logs.ILD_log10, logs.Depth, '-')
    ax[2].plot(logs.DeltaPHI, logs.Depth, '-', color='0.5')
    ax[3].plot(logs.PHIND, logs.Depth, '-', color='r')
    ax[4].plot(logs.PE, logs.Depth, '-', color='black')
    im=ax[5].imshow(cluster, interpolation='none', aspect='auto',
                    cmap=cmap_facies,vmin=1,vmax=9)
    
    divider = make_axes_locatable(ax[5])
    cax = divider.append_axes("right", size="20%", pad=0.05)
    cbar=plt.colorbar(im, cax=cax)
    cbar.set_label((21*' ').join(str(item) for item in config.FACIES_LABELS))
    cbar.set_ticks(range(0,1)); cbar.set_ticklabels('')
    
    for i in range(len(ax)-1):
        ax[i].set_ylim(ztop,zbot)
        ax[i].invert_yaxis()
        ax[i].grid()
        ax[i].locator_params(axis='x', nbins=3)
    
    ax[0].set_xlabel("GR")
    ax[0].set_xlim(logs.GR.min(),logs.GR.max())
    ax[1].set_xlabel("ILD_log10")
    ax[1].set_xlim(logs.ILD_log10.min(),logs.ILD_log10.max())
    ax[2].set_xlabel("DeltaPHI")
    ax[2].set_xlim(logs.DeltaPHI.min(),logs.DeltaPHI.max())
    ax[3].set_xlabel("PHIND")
    ax[3].set_xlim(logs.PHIND.min(),logs.PHIND.max())
    ax[4].set_xlabel("PE")
    ax[4].set_xlim(logs.PE.min(),logs.PE.max())
    ax[5].set_xlabel('Facies')
    
    ax[1].set_yticklabels([]); ax[2].set_yticklabels([]); ax[3].set_yticklabels([])
    ax[4].set_yticklabels([]); ax[5].set_yticklabels([])
    ax[5].set_xticklabels([])
    f.suptitle('Well Logs and Facies for %s'%logs.iloc[0]['Well Name'], fontsize=14, fontweight = 'bold', y=0.9)
    plt.show()

def unskew(df):
    df['GR'] = stats.boxcox(df['GR'])[0]
    df['PHIND'] = stats.boxcox(df['PHIND'])[0]
    df['Depth'] = stats.boxcox(df['Depth'])[0]
    df['PE'] = stats.boxcox(df['PE'])[0]
    df['DeltaPHI'] = np.log(df['DeltaPHI'])
    return df

def select_categorical_feature(data, feature, label):
    cross_tab_result=pd.crosstab(index=data[feature],columns=data[label])
    stat, _, dof, _ = chi2_contingency(cross_tab_result)
    prob = 0.95
    critical = chi2.ppf(prob, dof)
    if abs(stat) >= critical:
        result = f'{feature} is dependent of {label}, reject H0'
    else:
        result = f'{feature} ia independent of {label}, fail to reject H0'
    return result

