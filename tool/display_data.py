import pandas as pd


def run():
    df = get_data()
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 1000)
    pd.set_option('display.width', 1000)
    df.style.set_properties(**{'background-color': 'black',
                               'color': 'lawngreen',
                               'border-color': 'white'})
    print(df)


def get_data():
    df = pd.read_csv('../log_error.csv')
    return df
