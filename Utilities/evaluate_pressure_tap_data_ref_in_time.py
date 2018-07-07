import numpy as np
import os
import re
from scipy.stats import tmean, tstd, skew, kurtosis

class TimeHistoryData:

    def __init__(self, file_name, ramp_up_time):

        this_file = file_name

        # read in quantities
        with open(this_file, 'r') as f:
            #jump to the beginning of the file
            f.seek(0)
            first_line = f.readline()
            second_line = f.readline()

        self.position = [float(item) for item in (re.findall(r"[-+]?\d*\.\d+|\d+",first_line))]
        variable_names = re.findall('\w+',second_line)

        self.variable_results_raw = {}
        # for variable in range(len(variable_names)):
        #     self.variable_results_raw[variable_names[variable]] = np.genfromtxt(this_file, skip_header=2, skip_footer=0, usecols = (variable,))

        print("this_file: ",this_file)

        self.variable_results_raw["time"] = np.loadtxt(this_file, usecols = (0,))
        self.variable_results_raw["PRESSURE"] = np.loadtxt(this_file, usecols = (1,))
        try:
            self.variable_results_raw["velocity_x"] =  np.loadtxt(this_file, usecols = (2,))
        except:
            print("no velocity data")

class PressureCoefficientData:

    def __init__(self, position, raw_data, ref_data, ramp_up_time, density):

        self.position = position

        ramp_up_index = np.where(raw_data['time']>= ramp_up_time + ramp_up_time/5)[0]

        self.raw_data = {}
        self.raw_data['PRESSURE'] = raw_data['PRESSURE'][ramp_up_index[0]:]
        self.raw_data['time'] = raw_data['time'][ramp_up_index[0]:]

        self.ref_data = {}
        self.ref_data['PRESSURE'] = ref_data["pressure"][ramp_up_index[0]:]
        reference_velocity = tmean(ref_data["velocity_x"][ramp_up_index[0]:])

        # print("pres ref avg ", tmean(self.ref_data['PRESSURE']))
        # print("vel ref ", reference_velocity)

        # print("len pre raw: " + str(len(self.raw_data['PRESSURE'])))
        # print("len pre ref: " + str(len(self.ref_data['PRESSURE'])))

        self.pressure_coefficient_time_history = self.CalculatePressureCoefficient(reference_velocity, density)

        # print("len coef hist: " + str(len(self.pressure_coefficient_time_history)))

        self.statistic_results = CalculateStatistics(self.pressure_coefficient_time_history)


    def CalculatePressureCoefficient(self, reference_velocity, density):
        return [(pressure_value - reference_pressure)/(0.5 * density * reference_velocity**2)
            for pressure_value, reference_pressure
            in zip(self.raw_data['PRESSURE'], self.ref_data['PRESSURE'])]

def CalculateStatistics(time_history_data):
    statistic_results = {}
    statistic_results['mean'] = tmean(time_history_data)
    statistic_results['std'] = tstd(time_history_data)
    statistic_results['skewness'] = skew(time_history_data)
    #one can choose between Fisher's and Pearson's definition
    statistic_results['kurtosis'] = kurtosis(time_history_data, fisher = True)

    # new additions
    statistic_results['min'] = min(time_history_data)
    statistic_results['max'] = max(time_history_data)

    return statistic_results