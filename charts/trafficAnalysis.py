import sys

class TrafficAnalysis:
    def __init__    (self, logger,parameters):
        self.__logger = logger
        self.__logger.logSep(cl=self, method=sys._getframe(), message="init charts traffic")
        if parameters!=None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters

    def get_df_groupby_ts(self,run,df,groupby,indicators):
        if run:
            df=df[indicators]
            self.__logger.log(cl=self, method=sys._getframe(),message="get df grouped by ts. Compute average speed and density")
            df_groupby_ts = df.groupby(by=groupby).sum().reset_index()[indicators]
            df_groupby_ts[ "av_sp_mps"] = df_groupby_ts.td / df_groupby_ts.tt
            df_groupby_ts["av_sp_kpm"] = df_groupby_ts.td / df_groupby_ts.tt*3.6
            df_groupby_ts_density = df.groupby(by=groupby).mean().reset_index()[groupby+["density"]]
            df_groupby_ts = df_groupby_ts.merge(df_groupby_ts_density, on=groupby,suffixes=("_x",""))

            return df_groupby_ts





