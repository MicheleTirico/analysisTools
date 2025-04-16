import sys
import matplotlib.pyplot as plt
import seaborn as sns
import toolbox.control.tools
import pandas as pd

class StatisticalCharts:
    def __init__(self, logger, parameters=None):
        self.__logger = logger
        self.__logger.logSep(cl=self, method=sys._getframe(), message="init get statistical charts")
        if parameters != None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters

    def getChart_ts(self,run,df,listPathOut,indicator,label):
        if run :
            self.__logger.log(cl=self, method=sys._getframe(), message="get statistical charts, indicator: {}".format(indicator))
            df['datetime'] = pd.to_datetime(df['ts'], unit='s').dt.strftime('%H:%M')

            fig, ax = plt.subplots()
            ax.set(xlabel='time [hh:mm]', ylabel=label)
            ax.tick_params(axis='x', rotation=45)
            g=sns.lineplot(data=df, x="datetime", y=indicator, linestyle='-', marker="o",markersize=5,hue="sim")
            g.legend_.set_title(None)
            toolbox.control.tools.saveFig(logger=self.__logger,fig=fig,pathSave=listPathOut[0])
            plt.close()

    def getChart_residual_vs_indipendent_variable(self,run, df, r0, r1, indVar):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get statistical charts. Residual (ratio between vals r0: {} and r1: {}), as a function of idnVar: {}".format(r0,r1,indVar))
            print (df)

    def getChart_scatter_residuals_two_variables(self, run, df, r0, r1):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get statistical charts. Residual (ratio between vals): r0=: {}, r1: {}".format(r0,r1))
            df["r0"]=df[r0[0]]/df[r0[1]]
            df["r1"]=df[r1[0]]/df[r1[1]]

            plt.figure(figsize=(5, 5))

            # custom_palette = {0: 'red', 1: 'blue', 2: 'green',3:"grey"}

            sns.scatterplot(data=df, x="r0",y="r1", hue="zone",
                            # palette=custom_palette,
                            markers=".",
                            s=20)
            plt.show()
            plt.close()



    def getChart_groupZones_ts(self, run, df, listPathOut, indicator, label):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get statistical charts, plot zones, indicator: {}".format(indicator))
            df['datetime'] = pd.to_datetime(df['ts'], unit='s').dt.strftime('%H:%M')

            fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(8, 6))
            sns.lineplot(data=df[df.zone==0], x="datetime", y=indicator, linestyle='-', marker="o", markersize=5, hue="sim",ax=ax[0],legend=True)
            sns.lineplot(data=df[df.zone==1], x="datetime", y=indicator, linestyle='-', marker="o", markersize=5, hue="sim", ax=ax[1],legend=False)
            sns.lineplot(data=df[df.zone==2], x="datetime", y=indicator, linestyle='-', marker="o", markersize=5, hue="sim", ax=ax[2],legend=False)
            # legend
            handles, labels = ax[0].get_legend_handles_labels()
            fig.legend(handles, labels, loc="upper right", title=None)
            ax[0].legend_.remove()
            # axes
            plt.tight_layout(rect=[0, 0, 0.75, 1])
            fig.supylabel(label, fontsize=12)
            fig.supxlabel('time [hh:mm]', fontsize=12)
            for a in ax:
                a.set_xlabel('')  # Remove y-label
                a.set_ylabel('')  # Remove y-label
                a.tick_params(axis='x', labelsize=8)  # Change x-tick font size
                a.tick_params(axis='y', labelsize=8)  # Change x-tick font size
                a.tick_params(axis='x', rotation=45)

            toolbox.control.tools.saveFig(logger=self.__logger, fig=fig, pathSave=listPathOut[0])
            plt.close()
