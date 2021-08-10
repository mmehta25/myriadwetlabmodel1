import datetime
import statistics
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd


def convert_date(datestr):
    return datetime.strptime(datestr[:19], '%Y-%m-%d %H:%M:%S')

def convert_to_minutes(x):
	return x.seconds / 60

def process_instrument(dfs, an):
    an_num = dfs[an]

    c = an_num.loc[an_num['STATE']=='CREATED']
    d = an_num[an_num['STATE']=='DONE']
    cd = c.merge(d,on='TIMESTAMP', how='inner', suffixes=('_cr', '_do'))

    r = an_num[an_num['STATE']=='RUNNING']
    rd = r.merge(d, on='TIMESTAMP', how='inner', suffixes=('_ru', '_do'))

    cd['Created to Done'] = cd['STATE_CHANGED_AT_do'] - cd['STATE_CHANGED_AT_cr']
    cd['Running to Done'] = rd['STATE_CHANGED_AT_do'] - rd['STATE_CHANGED_AT_ru']

    done_created = an_num.loc[(an_num['STATE'] == 'CREATED') | (an_num['STATE'] == 'DONE')].iloc[1: , :]
    done_created['Idle'] = done_created['STATE_CHANGED_AT'] - done_created['STATE_CHANGED_AT'].shift(-1)

    done_created = done_created.drop(columns={'ASSET_NUMBER', 'STATUS', 'METHOD_NAME', 'STATE', 'TIMESTAMP'})
    done_created = done_created.rename(columns={'STATE_CHANGED_AT': 'STATE_CHANGED_AT_do'})
    merged = done_created.merge(cd, on='STATE_CHANGED_AT_do', how='inner')
    merged['Offset']= merged['Created to Done'] / (merged['Running to Done'] + merged['Idle'])
    merged['Offset'] = merged['Offset'].apply(lambda x: x + 1)
    final = merged[['METHOD_NAME_do', 'STATE_CHANGED_AT_do', 'ASSET_NUMBER_do', 'TIMESTAMP', 'Idle', 'Created to Done', 'Running to Done', 'Offset']].copy()

    todrop = []
    unique_days = final['TIMESTAMP'].apply(lambda x: x.date()).unique()
    unique_days
    final['day'] = final['TIMESTAMP'].apply(lambda x: x.date())
    for day in unique_days:
        bydate = final.loc[final['day'] == day]
        bydate = bydate.reset_index() 
        if len(bydate) > 1:
            todrop.append(bydate.iloc[len(bydate)-1]['TIMESTAMP'])
            
    final = final[~final['TIMESTAMP'].isin(todrop)]

    return final

def process_dataframe(df):
	df['STATE_CHANGED_AT'] = df['STATE_CHANGED_AT'].apply(lambda x: str(x))
	df['STATE_CHANGED_AT'] = df['STATE_CHANGED_AT'].apply(convert_date)
	df = df.sort_values(by='TIMESTAMP')
	df = df.sort_values(by='STATE_CHANGED_AT')
	
	errored_timestamps = set(df.loc[df['STATE'] == 'ERRORED']['TIMESTAMP'].unique())
	df_clean = df[~df['TIMESTAMP'].isin(errored_timestamps)]

	retested_timestamps = set(df_clean.loc[df['STATE'] == 'FORCE_RETEST']['TIMESTAMP'].unique())
	df_clean = df_clean[~df_clean['TIMESTAMP'].isin(retested_timestamps)]

	terminated_timestamps = set(df_clean.loc[df_clean['STATE'] == 'TERMINATED']['TIMESTAMP'].unique())
	df_clean = df_clean[~df_clean['TIMESTAMP'].isin(terminated_timestamps)]

	#Create different dataframes for each instrument (by asset number)
	an_list = df_clean.ASSET_NUMBER.unique()
	
	dfs = {}
	for an in an_list:
	    dfs[an] = df_clean.loc[df_clean['ASSET_NUMBER']==an]

	#Number of unique timestamps before and after removing failed/force_reset/terminated states
	removed_datapoints = {}
	for an in an_list:
	    df_an = df.loc[df['ASSET_NUMBER'] == an]
	    new_counts = dfs[an].pivot_table(index='METHOD_NAME', values='TIMESTAMP', aggfunc= lambda x: x.nunique())
	    old_counts = df_an.pivot_table(index='METHOD_NAME', values='TIMESTAMP', aggfunc= lambda x: x.nunique())
	    n = old_counts.merge(new_counts, on='METHOD_NAME', how='inner', suffixes=('_old_' + an, '_new_' + an))
	    n['rem'] = n['TIMESTAMP_old_'+an] - n['TIMESTAMP_new_'+an]
	    removed_points = sum(np.array(n['rem']))
	    removed_datapoints[an] = removed_points

	dfs2 = {}
	for an in an_list:
	    final_df = process_instrument(dfs, an)
	    dfs2[an] = final_df

	return {"dfs":dfs2}
