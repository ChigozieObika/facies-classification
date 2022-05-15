import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
from scipy.stats import chi2_contingency
from scipy.stats import chi2
import joblib

import config

class UniAnalysis():
    '''
    A class for creating histograms and boxplots for the dataframe
    '''
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
        sns.boxplot(y=self.df[feature], x=self.df[label], palette=config.FACIES_COLORS, ax=ax[1])
        ax[1].set_ylabel(f'{feature}', fontsize = 12, fontweight ='bold')
        ax[1].set_xlabel(f'{label}', fontsize = 12, fontweight ='bold')
        ax[1].set_title(f'{feature} vs {label} Boxplot', fontsize = 14, fontweight = 'bold')
        plt.show()

def make_facies_log_plot(logs, facies_colors):
    '''
    A function that plots the log information of a well. Takes the logs in the form of a dataframe and the facies colors that 
    maps a color to each label in the dataset as arguments. Reproduces the log information in a log plot
    '''
    logs = logs.sort_values(by='Depth') #sorts the dataframe by depth
    cmap_facies = colors.ListedColormap(
            facies_colors[0:len(facies_colors)], 'indexed') #make color map from a list of colors
    
    ztop=logs.Depth.min(); zbot=logs.Depth.max() #defines the range of the log
    
    cluster=np.repeat(np.expand_dims(logs['Facies'].values,1), 100, 1) #cluster for the color map plot
    
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
    #sets and inverts limit on y axis
    for i in range(len(ax)-1):
        ax[i].set_ylim(ztop,zbot)
        ax[i].invert_yaxis()
        ax[i].grid()
        ax[i].locator_params(axis='x', nbins=3)
    #sets labels and limits on the x axis
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
    #sets labels for x and y ticks
    ax[1].set_yticklabels([]); ax[2].set_yticklabels([]); ax[3].set_yticklabels([])
    ax[4].set_yticklabels([]); ax[5].set_yticklabels([])
    ax[5].set_xticklabels([])
    f.suptitle('Well Logs and Facies for %s'%logs.iloc[0]['Well Name'], fontsize=14, fontweight = 'bold', y=0.9)
    plt.show()

def unskew(df):
    '''
    Applies the boxcox function from scipy stats to reduce the skewedness of selected columns in the dataframe
    '''
    df['GR'] = stats.boxcox(df['GR'])[0]
    df['PHIND'] = stats.boxcox(df['PHIND'])[0]
    df['PE'] = stats.boxcox(df['PE'])[0]
    return df

def select_categorical_feature(data, feature, label):
    '''
    Uses the chi2 value to establish correlation of categorical features with the target label
    '''
    cross_tab_result=pd.crosstab(index=data[feature],columns=data[label])
    stat, _, dof, _ = chi2_contingency(cross_tab_result)
    prob = 0.95
    critical = chi2.ppf(prob, dof)
    if abs(stat) >= critical:
        result = f'{feature} is dependent of {label}, reject H0'
    else:
        result = f'{feature} ia independent of {label}, fail to reject H0'
    return result

def train_test_split_by_well(df, train_size):
    '''
    Splits the dataframe into train and test sets while ensuring values from a well only found in either train or test set
    and not in both
    '''
    grouped_by_well = df.groupby(['Well Name'])['Facies'].count()
    grouped_by_well = pd.DataFrame(grouped_by_well)
    grouped_by_well.rename(columns = {'Facies':'count'}, inplace=True)
    grouped_by_well.reset_index(inplace=True)
    grouped_by_well.sort_values(by = 'count', ascending = False, inplace=True)
    total_count = grouped_by_well['count'].sum()
    add_count = 0
    train_wells = []
    for i, count in enumerate(grouped_by_well['count']):
        if (train_size*total_count-add_count)>count: #checks if the next well can be included in the train wells
            add_count+=count
            train_wells.append(grouped_by_well['Well Name'][i])
        else:
            continue
    #creates train and test sets
    train = df.loc[df['Well Name'].isin(train_wells)]
    test = df.loc[~df['Well Name'].isin(train_wells)]
    return train,test

def drop_columns(well_df):
    '''
    drop columns that are not required in the model training stage
    '''
    processed_df = well_df.drop(['Well Name', 'Formation', 'Depth'], axis =1)
    return processed_df

def train_test_plot(df, train_df, test_df):
    '''
    plot to show that the split by well is correctly applied. Takes the dataframe, the test and the test sets as arguments
    '''
    well_counts = df.value_counts('Well Name').to_frame('count').reset_index()
    categories = {'Train Set': train_df['Well Name'].unique(),
                'Test Set': test_df['Well Name'].unique()}
    plt.rcParams['figure.figsize'] = (7,5)
    theme_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    category_colors = {category: color for category, color in zip(categories, theme_colors)}
    display_names = {}
    value_to_category = {display_names.get(value,value):category 
                        for category, values in categories.items()
                        for value in values}
    colors = [category_colors[value_to_category[value]] 
            for value in well_counts['Well Name']]
    plt.bar(x = well_counts['Well Name'], height = well_counts['count'], color = colors)
    handles = [plt.Rectangle((0,0), 1, 1, color=color) for color in category_colors.values()]
    plt.legend(handles, categories)
    plt.title('Train_set Wells and Test_set', fontweight = 'bold')
    plt.xticks([])
    plt.ylabel('Count', fontweight = 'bold')
    plt.xlabel('Wells', fontweight = 'bold')
    plt.show()

def plot_predictions(well, model_filename):
    '''
    produces a plot of the logs of a well and its predicted classes. takes the logs and the filename of the model as arguemnts.
    loads the model from the filename, uses the loaded model to make predictions.
    '''
    model = joblib.load(model_filename)
    well_predictions = model.predict(well)
    well['Facies'] = well_predictions
    make_facies_log_plot(well, config.FACIES_COLORS)
