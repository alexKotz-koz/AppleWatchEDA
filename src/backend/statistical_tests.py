import pandas as pd
from scipy.stats import spearmanr, pearsonr
import os

class StatisticalTest:
    def __init__(self,heartRateFile=None, restingHeartRate=None, stepsFile=None, gaitFile=None, spo2File=None) -> None:
        self.heartRateFile = heartRateFile
        self.restingHeartRateFile = restingHeartRate
        self.stepsFile = stepsFile
        self.gaitFile = gaitFile
        self.spo2File = spo2File
        if not os.path.exists("../data/descriptive_statistics"):
            os.makedirs("../data/descriptive_statistics")


    def mean_heart_rate_three_days(self, df):
        dfCopy = df.copy()
        dfCopy['hour'] = pd.to_datetime(dfCopy['time'], format='%H:%M:%S').dt.hour

        # Calculate mean heart rate per hour in the copy
        mean_heart_rate = dfCopy.groupby(['date', 'hour'])['heartRate'].mean().reset_index()
        mean_heart_rate.columns = ['date', 'hour', 'meanHeartRate']

        # Merge mean_heart_rate with the original df
        df = pd.merge(df, mean_heart_rate, how='left', left_on=['date', pd.to_datetime(df['time'], format='%H:%M:%S').dt.hour], right_on=['date', 'hour'])
        
        return df

    def mean_steps_three_days(self, df):
        dfCopy = df.copy()
        dfCopy['hour'] = pd.to_datetime(dfCopy['startTime'], format='%H:%M:%S').dt.hour
        meanSteps = dfCopy.groupby(['date', 'hour'])['steps'].mean().reset_index()
        meanSteps.columns = ['date', 'hour', 'meanSteps']
        df = pd.merge(df, meanSteps, how='left', left_on=['date', pd.to_datetime(df['startTime'], format='%H:%M:%S').dt.hour], right_on=['date', 'hour'])

        return df

    def mean_gait_three_days(self, df):
        dfCopy = df.copy()
        dfCopy['hour'] = pd.to_datetime(dfCopy['startTime'], format="%H:%M:%S").dt.hour
        meanGaitLength = dfCopy.groupby(['date', 'hour'])['gaitLength'].mean().reset_index()
        meanGaitLength.columns = ['date', 'hour', 'meanGaitLength']
        df = pd.merge(df, meanGaitLength, how='left', left_on=['date', pd.to_datetime(df['startTime'], format='%H:%M:%S').dt.hour], right_on=['date', 'hour'])
        return df

    def mean_spo2_three_days(self, df):
        dfCopy = df.copy()
        dfCopy['hour'] = pd.to_datetime(dfCopy['startTime'], format='%H:%M:%S').dt.hour
        meanSpo2 = dfCopy.groupby(['date', 'hour'])['SpO2'].mean().reset_index()
        meanSpo2.columns = ['date','hour','meanSpo2']
        df = pd.merge(df, meanSpo2, how='left', left_on=['date', pd.to_datetime(df['startTime'], format='%H:%M:%S').dt.hour], right_on=['date', 'hour'])
        return df

    def standard_deviation(self, df, columnName):
        return df[columnName].std()

    def nonparametric_wrapper(self, dataset1, dataset2):
        # Assuming your DataFrame is named df
        groupedDF1 = dataset1.groupby(['date', 'hour'])['meanSteps'].mean().reset_index()
        groupedDF2 = dataset2.groupby(['date', 'hour'])['meanHeartRate'].mean().reset_index()
        mergedDf = pd.merge(groupedDF1, groupedDF2, on=['date', 'hour'], how='inner')
        df1New = mergedDf[['date', 'hour', 'meanSteps']]
        df2New = mergedDf[['date', 'hour', 'meanHeartRate']]
        
        # Get mean datatype per hour
        # Write mean datatype per hour value to a nparray
        # return nparray
        return df1New, df2New

    def spearman(self,dataset1, dataset2):
        df1New, df2New = self.nonparametric_wrapper(dataset1, dataset2)
        #calculate Spearman Rank correlation and corresponding p-value
        rho, p = spearmanr(df1New['meanSteps'], df2New['meanHeartRate'])

        if rho < 0:
            print(f"There is a negative correlation between the two variables @: {rho}")
        else:
            print(f"There is a positive correlation between the two variables @: {rho}")
        
        if p < 0.05:
            print(f"The correlation is not statistically significant. p-val = {p}")
        else:
            print(f"The correlation is statistically significant. p-val = {p}")


    def descriptive_statistics(self):
        
        heartRateDF = pd.read_csv(self.heartRateFile, index_col=0)
        meanHeartRate = self.mean_heart_rate_three_days(heartRateDF)
        sd = self.standard_deviation(heartRateDF,'heartRate')
        meanHeartRate['SD'] = sd
        meanHeartRate.to_csv("../data/descriptive_statistics/mean_heart_rate_three_days.csv", index=False)

        stepsDF = pd.read_csv(self.stepsFile, index_col=0)
        meanSteps = self.mean_steps_three_days(stepsDF)
        meanSteps.to_csv("../data/descriptive_statistics/mean_steps_three_days.csv", index=False)

        gaitDF = pd.read_csv(self.gaitFile,index_col=0)
        meanGaitLength = self.mean_gait_three_days(gaitDF)
        meanGaitLength.to_csv('../data/descriptive_statistics/mean_gait_length_three_days.csv', index=False)

        spo2DF = pd.read_csv(self.spo2File, index_col=0)
        meanSpo2 = self.mean_spo2_three_days(spo2DF)
        meanSpo2.to_csv("../data/descriptive_statistics/mean_spo2_three_days.csv", index=False)

        # uncomment to run spearmans on mean heart rate and mean steps
        #self.spearman(meanSteps, meanHeartRate)

        return heartRateDF, stepsDF, meanGaitLength