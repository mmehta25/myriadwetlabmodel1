import pandas as pd
import numpy as np
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import statistics

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
	#df['TIMESTAMP'] = df['TIMESTAMP'].apply(lambda x: str(x))

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

	# median_timedeltas1 = {}
	# median_timedeltas2 = {}
	# median_timedeltas3 = {}
	# median_timedeltas4 = {}

	# for an in an_list:
	#     median_timedeltas1[an] = dfs2[an].pivot_table(index='METHOD_NAME_do', values='Created to Done', aggfunc=statistics.median)
	#     median_timedeltas2[an] = dfs2[an].pivot_table(index='METHOD_NAME_do', values='Running to Done', aggfunc=statistics.median)
	#     median_timedeltas3[an] = dfs2[an].pivot_table(index='METHOD_NAME_do', values='Offset', aggfunc=statistics.median)
	#     median_timedeltas4[an] = dfs2[an].pivot_table(index='METHOD_NAME_do', values='Idle', aggfunc=statistics.median)

	# a1 = median_timedeltas1['AN-50075'].merge(median_timedeltas1['AN-50105'], on='METHOD_NAME_do', how='inner', suffixes=('_50075', '_50105'))
	# b1 = median_timedeltas1['AN-1834'].merge(median_timedeltas1['AN-1835'], on='METHOD_NAME_do', how='inner', suffixes=('_1834', '_1835'))
	# c1 = a1.merge(b1, on='METHOD_NAME_do', how='inner')

	# a2 = median_timedeltas2['AN-50075'].merge(median_timedeltas2['AN-50105'], on='METHOD_NAME_do', how='inner', suffixes=('_50075', '_50105'))
	# b2 = median_timedeltas2['AN-1834'].merge(median_timedeltas2['AN-1835'], on='METHOD_NAME_do', how='inner', suffixes=('_1834', '_1835'))
	# c2 = a2.merge(b2, on='METHOD_NAME_do', how='inner')

	# a3 = median_timedeltas3['AN-50075'].merge(median_timedeltas3['AN-50105'], on='METHOD_NAME_do', how='inner', suffixes=('_50075', '_50105'))
	# b3 = median_timedeltas3['AN-1834'].merge(median_timedeltas3['AN-1835'], on='METHOD_NAME_do', how='inner', suffixes=('_1834', '_1835'))
	# c3 = a3.merge(b3, on='METHOD_NAME_do', how='inner')

	# a4 = median_timedeltas4['AN-50075'].merge(median_timedeltas4['AN-50105'], on='METHOD_NAME_do', how='inner', suffixes=('_50075', '_50105'))
	# b4 = median_timedeltas4['AN-1834'].merge(median_timedeltas4['AN-1835'], on='METHOD_NAME_do', how='inner', suffixes=('_1834', '_1835'))
	# c4 = a4.merge(b4, on='METHOD_NAME_do', how='inner')

	# for col in c4.columns:
	# 	c4[col] = c4[col].apply(convert_to_minutes)
	# for col in c1.columns:
	#     c1[col] = c1[col].apply(convert_to_minutes)
	# for col in c2.columns:
	#     c2[col] = c2[col].apply(convert_to_minutes)

	return {"dfs":dfs2}
