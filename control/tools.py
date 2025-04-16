import pandas as pd

def test_package(a): print ("handfiles: packages has been imported\nrun run from toolbox.handlefiles import tools")

def storeDataframe(logger,pathStore,df):
    logger.log(cl=None,method=None,message="Store dataframe in:{}".format(pathStore))
    df.to_csv(pathStore, sep=';')

def storeGeoDataframe(logger,pathStore,df):
    logger.log(cl=None,method=None,message="Store geo-dataframe in:{}".format(pathStore))
    df.to_file(pathStore)

def dropValColumns(columns,listValToDrop):
    for i in listValToDrop:        columns.pop(columns.index(i))
    return columns
def dropColumns(logger, columns, df ):
    df1=df
    for c in columns:
        try             : df1= df1.drop(columns=[c])
        except KeyError : logger.warning(cl=None,method=None,message="key not founded: {}".format(c),doQuit=False)
    return df1

def mergeDfSns(df_mat,df_sym,mat_col,sym_col,quantile,resetIndex,nameColumn,minQuant):
    df1=pd.DataFrame(df_mat[["time",mat_col]])
    df2=pd.DataFrame(df_sym[["time",sym_col]])
    if quantile != None:
        if minQuant:
            limit=min(df1[mat_col].quantile(quantile),df2[sym_col].quantile(quantile))
            df1=df1[df1[mat_col]<limit]
            df2=df2[df2[sym_col]<limit]
        df1=df1[df1[mat_col]<df1[mat_col].quantile(quantile)]
        df2=df2[df2[sym_col]<df2[sym_col].quantile(quantile)]
    df1["model"]="MATSim"
    try:df1=df1.rename(columns={mat_col:nameColumn,"time":"p_range"})
    except KeyError:     logger.warning(cl=None,method=None,message="error in cast columns",doQuit=False)


    df2["model"]="Symuvia"
    df2=df2.rename(columns={sym_col:nameColumn})
    df3=pd.concat([df1,df2])
    if resetIndex:    df3=df3.reset_index()
    return df3

def saveFig(fig,logger, pathSave):
    logger.log(cl=None,method=None,message="store figure at:{}".format(pathSave))
    fig.savefig(pathSave, bbox_inches="tight")

def get_second(time_hms):
    split=time_hms.split(":")
    if len(split)==3:   return 60*60*int(split[0])+60*int(split[1])+int(split[2])
    elif len(split)==2: return 60*60*int(split[0])+60*int(split[1])


def getListColumnsAsType(df,type):
    c =[]
    for i in df.columns:
        if df[i].dtype==type : c.append(i)

    return [i for i in df.columns if df[i].dtype==type  ]