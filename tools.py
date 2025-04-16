import os
from datetime import datetime, timedelta
from itertools import product
import geopandas as gpd
import numpy as np
import pandas as pd

def get_start_end_in_seconds(start_end_in_string):
    t_second_start=[int(_) for _ in start_end_in_string[0].split(":")]
    t_second_end=[int(_) for _ in start_end_in_string[1].split(":")]
    return [t_second_start[0]*60*60+t_second_start[1]*60+t_second_start[2],t_second_end[0]*60*60+t_second_end[1]*60+t_second_end[2]]

def get_time_from_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)  # Get hours and remaining seconds
    minutes, seconds = divmod(remainder, 60)  # Get minutes and remaining seconds
    return [int(hours),int(minutes),int(seconds)], f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'

def getTimeInSecFromHms(time_hms):
    a=time_hms.split(":")
    return int(a[0])*60*60+int(a[1])*60+int(a[2])


def get_lastFile(pathDir,initFile):
    files =os.listdir(pathDir)
    v,ff=-1,None
    for file in files:
        if file.startswith(initFile):
            # try:
            a = int(file.replace(initFile,"")[:2])
            if a > v :
                v,ff=a,file
            # except ValueError : return
    return ff

def get_list_period_day(period_day):
    start_date = datetime.strptime(period_day[0], "%d/%m/%Y")
    end_date = datetime.strptime(period_day[1], "%d/%m/%Y")
    return[(start_date + timedelta(days=i)).strftime("%d/%m/%Y") for i in range((end_date - start_date).days + 1)]

def get_list_period_hh(period_hh):
    start_date_hh = datetime.strptime(period_hh[0], "%H:%M")
    end_date_hh = datetime.strptime(period_hh[1], "%H:%M")
    return [(start_date_hh + timedelta(hours=i)).strftime("%H:%M") for i in range((end_date_hh - start_date_hh).seconds // 3600 + 1)]

def get_format_day(input_day,type_in="dd/mm/yyyy",type_out="ddmmyyyy"):
    if type_in=="dd/mm/yyyy":
        if type_out=="ddmmyyyy":
            return input_day.replace("/","")
        if type_out=="yyyymmdd":
            l=input_day.split('/')
            return "{}{}{}".format(l[2],l[1],l[0])
        else:print("type out not defined")
    else: print ("type in not defined")


def get_list_period_day_hh(period_day,period_hh):
    return [f"{day} {hour}" for day, hour in product(get_list_period_day(period_day), get_list_period_hh(period_hh))]

def get_df_compare_values_are_same(df,list_colum_search=["trip"],column_merge=['id']):
    df_base = df[df.sim == "base"]
    df_no_base = df[df.sim != "base"]
    df1 = df_no_base.merge(df_base, on=column_merge, suffixes=("_sc", "_bs"))
    for ind_pos in range(len(list_colum_search)):
        ind = list_colum_search[ind_pos]
        df1[ind+"_inTrip"] = df1.apply(lambda row: row['trip_bs'] == row['trip_sc'], axis=1)
    return df1

def get_df_compare_values_in_list_are_in_column(df,list_val,column,name_new_col):
    df1=df.copy()
    # df1["val_inCol"] = df1.apply(lambda row: str(row[val]) in row[column], axis=1)
    df1[name_new_col] = df1[column].astype(str).apply(lambda x: any(val in x for val in list_val))
    return df1

# def get_df_compare_string_in_list(df,list_colum_search=["trip"],column_to_search=['id']):
#     df_base = df[df.sim == "base"]
#     df_no_base = df[df.sim != "base"]
#     df1 = df_no_base.merge(df_base, on=column_to_search, suffixes=("_sc", "_bs"))
#     for ind_pos in range(len(list_colum_search)):
#         ind = list_colum_search[ind_pos]
#         df1[ind+"_inTrip"] = df1.apply(lambda row: str(row['id']) in row['trip_sc'], axis=1)
#     return df1

def get_df_compare_values(df,list_ind,diff_ind=["res","del","per"],id=['ID']):
    df_base = df[df.sim == "base"]
    df_no_base = df[df.sim != "base"]
    df1 = df_no_base.merge(df_base, on=id+[ "hh", "zone"], suffixes=("_sc", "_bs"))
    # Get delta and res
    for ind_pos in range(len(list_ind)):
        ind = list_ind[ind_pos]
        if "res" in diff_ind:
            df1[ind + "_res"] = df1[ind + "_sc"] / df1[ind + "_bs"]
            df1[ind + "_res"] = df1[ind + "_res"].fillna(0)
        if "del" in diff_ind:
            df1[ind + "_del"] = df1[ind + "_sc"] - df1[ind + "_bs"]
            df1[ind + "_del"] = df1[ind + "_del"].fillna(0)
        if "per" in diff_ind:
            df1[ind + "_per"] = (df1[ind + "_sc"] - df1[ind + "_bs"])/df1[ind + "_bs"]*100
            df1[ind + "_per"] = df1[ind + "_per"].fillna(0)
    return df1

def get_df_norm_stdDev (df,listInd_norm):
    df1=df.copy()
    for ind in listInd_norm: df1[ind+"_stDv"]=  (df1[ind] - df1[ind].mean()) / df1[ind].std()
    return df1

def add_value_to_new_row(df,list_vals_0,list_vals_1,list_ind,val=0.0):
    df1=df.copy()
    base_rows = []
    for hh_value in list_vals_0:
        for z in list_vals_1:
            base_row = {'zone': z,'hh': hh_value,'sim_sc': 'base'}
            base_row.update({key: val for key in list_ind })
            base_rows.append(base_row)

    # Convert to DataFrame and append
    base_df = pd.DataFrame(base_rows)
    df1 = pd.concat([df1, base_df], ignore_index=False)
    return df1

def get_random_value_table(   df_links,sim,  n_sensors_per_street = 10,hh_values = [6, 7, 8],lim_vals_L_aeq = [40, 80],lim_vals_L_max = [70, 120],type_random='randint'):
    df_expanded = df_links.loc[df_links.index.repeat(len(hh_values))].reset_index(drop=True)
    df_expanded["hh"] = np.tile(hh_values, len(df_links))
    total_repeats = n_sensors_per_street * len(hh_values)
    df_expanded = df_links.loc[df_links.index.repeat(total_repeats)].reset_index(drop=True)
    df_expanded["hh"] = np.tile(hh_values * n_sensors_per_street, len(df_links))
    df_expanded_02 = df_expanded.loc[df_expanded.index.repeat(len(sim))].reset_index(drop=True)
    df_expanded_02["sim"] = np.tile(sim, len(df_expanded))

    np.random.seed(1)
    if type_random=="randint":
        df_expanded_02["l_aeq"] = np.random.randint(lim_vals_L_aeq[0], lim_vals_L_aeq[1], size=len(df_expanded_02))
        df_expanded_02["l_max"] = np.random.randint(lim_vals_L_max[0], lim_vals_L_max[1], size=len(df_expanded_02))
    elif type_random=='powerlaw':
        power_law_samples = np.random.pareto(2, len(df_expanded_02))  # Shift to start from 1
        df_expanded_02["l_aeq"] = (lim_vals_L_aeq[0] + (power_law_samples - power_law_samples.min()) * (
                lim_vals_L_aeq[1] - lim_vals_L_aeq[0]) / (power_law_samples.max() - power_law_samples.min()))

        power_law_samples = np.random.pareto(2, len(df_expanded_02))  # Shift to start from 1
        df_expanded_02["l_max"] = (lim_vals_L_max[0] + (power_law_samples - power_law_samples.min()) * (
                lim_vals_L_max[1] - lim_vals_L_max[0]) / (power_law_samples.max() - power_law_samples.min()))

    df_expanded_02["ID_sen"] = range(1, len(df_expanded_02) + 1)
    return df_expanded_02