from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer, PowerTransformer, FunctionTransformer

from xgboost import XGBClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

FACIES_COLORS = ['#F4D03F', '#F5B041','#DC7633','#6E2C00',
                '#1B4F72','#2E86C1', '#AED6F1', '#A569BD', '#196F3D']

FACIES_LABELS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

TRAIN_SIZE = 0.8

MODELS = [
     LogisticRegression(), ExtraTreesClassifier(), XGBClassifier(), DecisionTreeClassifier()
]
PREPROCESSORS = [Normalizer(), MinMaxScaler(), StandardScaler(), PowerTransformer()]

def drop_columns(well_df):
    '''
    drop columns that are not required in the model training stage
    '''
    processed_df = well_df.drop(['Well Name', 'Formation', 'Depth'], axis =1)
    return processed_df
DROP_COLUMNS = FunctionTransformer(drop_columns)