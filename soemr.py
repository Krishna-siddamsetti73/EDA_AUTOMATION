import pandas as pd
import ydata_profiling as yp
def profiling(fp):
    df=pd.read_csv(fp)
    profile = yp.ProfileReport(df)
    profile.to_notebook_iframe()
    profile.to_file('eda_report.html')
    return profile
