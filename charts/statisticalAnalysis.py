import sys
import math
import numpy as np
from scipy.stats import *

class StatisticalAnalysis:
    def __init__    (self, logger):
        self.__logger = logger
        self.__logger.logSep(cl=self, method=sys._getframe(), message="get statistical analysis")

    def get_fractional_bias(self,run,df,ind,hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get fractional bias indicator")
            key=list(hue.keys())[0]
            values=hue.get(key)

            df1=df[df[key]==values[0]]
            df2=df[df[key]==values[1]]

            v0_mean=df1[ind].mean()
            v1_mean=df2[ind].mean()
            return (v0_mean - v1_mean)/(0.5 * (v0_mean + v1_mean))
        else: return None


    def get_spearman_correlation(self,run,df,ind,hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get the spearman correlation coefficient")
            key = list(hue.keys())[0]
            values = hue.get(key)

            v0 = np.array(list(df[df[key] == values[0]][ind]))
            v1 = np.array(list(df[df[key] == values[1]][ind]))
            rho, p_value = spearmanr(v0, v1)

            return rho

    def get_kendall_correlation(self,run,df,ind,hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get the Kendall correlation coefficient")
            key = list(hue.keys())[0]
            values = hue.get(key)
            v0 = np.array(list(df[df[key] == values[0]][ind]))
            v1 = np.array(list(df[df[key] == values[1]][ind]))
            tau, p_value = kendalltau(v0, v1)
            return tau

    def get_geometric_mean_bias(self,run,df,ind,hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get geometric mean bias indicator")
            key=list(hue.keys())[0]
            values=hue.get(key)

            df1=df[df[key]==values[0]]
            df2=df[df[key]==values[1]]

            v0 = math.log(df1[ind].mean())
            v1 = math.log(df2[ind].mean())

            return math.exp(v0-v1)
        else: return None

    def get_geometric_variance(self, run, df, ind, hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get geometric variance indicator: ind: {}".format(ind))
            key = list(hue.keys())[0]
            values = hue.get(key)


            v0=np.array(list(df[df[key] == values[0]][ind]))
            v1=np.array(list(df[df[key] == values[1]][ind]))


            if len(v0) != len(v1):
                raise ValueError("Both datasets must have the same number of elements.")

                # Ensure all values are positive

            if np.any(v0 <= 0) :
                self.__logger.warning(cl=self, method=sys._getframe(), message="All values in both datasets must be positive for geometric variance computation",doQuit=False)

                positions = [index for index, value in enumerate(v0) if value <= 0]
                v0 =np.array( [value for index, value in enumerate(v0) if index not in positions])
                v1 = np.array([value for index, value in enumerate(v1) if index not in positions])

                # quit()
                # quit()
                # raise ValueError("All values in both datasets must be positive for geometric variance computation.")
                # return -1000
                # Compute the squared differences of logarithms

            if np.any(v1 <= 0):
                self.__logger.warning(cl=self, method=sys._getframe(),
                                      message="All values in both datasets must be positive for geometric variance computation",
                                      doQuit=False)

                positions = [index for index, value in enumerate(v1) if value <= 0]
                v1 = np.array([value for index, value in enumerate(v1) if index not in positions])
                v0 =np.array( [value for index, value in enumerate(v0) if index not in positions])

            log_diff_squared = (np.log(v0) - np.log(v1)) ** 2

            # Compute geometric variance
            VG = np.exp(np.mean(log_diff_squared))

            return VG

    def get_indipendent_t_test(self, run, df, ind, hue):
        """
        The independent t-test compares the means of two independent groups to determine if they are significantly different.
        Interpretation:
            t-value	Interpretation
                ~ 0	Very little difference between groups
                > 2 or < -2	Moderate to strong difference
                > 3 or < -3	Strong difference
            p-value interpretation :
                p-value < 0.05 → The means are significantly different.
                p-value ≥ 0.05 → No significant difference.
        """
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get indipendent T-test")
            key = list(hue.keys())[0]
            values = hue.get(key)

            v0 = np.array(list(df[df[key] == values[0]][ind]))
            v1 = np.array(list(df[df[key] == values[1]][ind]))
            t_stat, p_value = ttest_ind(v0, v1)

            return t_stat
    def get_coefficient_variation(self, run, df, ind, hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get coefficient of variation")
            key = list(hue.keys())[0]
            values = hue.get(key)

            v0 = np.array(list(df[df[key] == values[0]][ind]))
            v1 = np.array(list(df[df[key] == values[1]][ind]))
            return np.std(v0) / np.mean(v1)


    def get_correlation_coefficient (self, run, df, ind, hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get correlation coefficient")
            key = list(hue.keys())[0]
            values = hue.get(key)

            v0=np.array(list(df[df[key] == values[0]][ind]))
            v1=np.array(list(df[df[key] == values[1]][ind]))
            if len(v0) != len(v1):
                raise ValueError("Both datasets must have the same number of elements.")

            # Compute Pearson correlation coefficient
            r = np.corrcoef(v0, v1)[0, 1]

            return r

    def get_fraction_within_factor_of_two(self, run, df, ind, hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get fraction within factor of two")
            key = list(hue.keys())[0]
            values = hue.get(key)
            v0=np.array(list(df[df[key] == values[0]][ind]))
            v1=np.array(list(df[df[key] == values[1]][ind]))
            
            if len(v0) != len(v1):
                raise ValueError("Both datasets must have the same number of elements.")
    
            # Compute the ratio P/O
            ratio = v1 / v0
    
            # Count values that fall within the range [0.5, 2]
            within_factor_of_two = np.sum((ratio >= 0.5) & (ratio <= 2))
    
            # Compute the fraction
            fac2 = within_factor_of_two / len(v0)
    
            return fac2
    
    def get_normalized_mean_square_error(self, run, df, ind, hue):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get normalized mean square error indicator")
            key = list(hue.keys())[0]
            values = hue.get(key)

            v0=np.array(list(df[df[key] == values[0]][ind]))
            v1=np.array(list(df[df[key] == values[1]][ind]))

            # Compute Mean Squared Error (MSE)
            mse = np.mean((v0 - v1) ** 2)

            # Compute Variance of the true values
            variance = np.var(v1)

            # Compute Normalized Mean Squared Error (NMSE)
            return mse / variance
        else:
            return None

