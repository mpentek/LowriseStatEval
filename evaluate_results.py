import json
from os import path as os_path

import re
import numpy as np

from pprint import pprint

from utilities.evaluate_pressure_tap_data_ref_in_time import TimeHistoryData, PressureCoefficientData

with open(os_path.normpath('input_data/ResultsOverview.json')) as f:
    results = json.load(f)['results']

nr_of_blocks = 6
ramp_up_time = 30
density = 1.2

for result in results:

    # load reference data results
    ref_point_file = os_path.join("input_data", os_path.normpath(result['reference_points'][0]['file_name']))

    with open(ref_point_file, 'r') as f:
        #jump to the beginning of the file
        f.seek(0)
        first_line = f.readline()

    ref_data = {}
    if 'Kratos' in result['case']:
        ref_data['position'] = [float(item) for item in (re.findall(r"[-+]?\d*\.\d+|\d+",first_line))]
    elif 'FeFlo' in result['case']:
        ref_data['position'] = [float(item) for item in first_line.rstrip('\n').split('  ')[-3:]]
    ref_data["time"] = np.loadtxt(ref_point_file, usecols = (0,))
    ref_data["pressure"] = np.loadtxt(ref_point_file, usecols = (1,))
    ref_data["velocity_x"] =  np.loadtxt(ref_point_file, usecols = (2,))

    for pressure_tap in result['pressure_taps']:
        pressure_tap_file = os_path.join("InputData", os_path.normpath(pressure_tap['file_name']))

        pressure_data = TimeHistoryData(pressure_tap_file, ramp_up_time)

        cp_data = PressureCoefficientData(pressure_data.position,
                                        pressure_data.variable_results_raw,
                                        ref_data,
                                        ramp_up_time,
                                        density)

        pprint(cp_data.statistic_results)
        break
