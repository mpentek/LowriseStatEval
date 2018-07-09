# -*- coding: utf-8 -*-
"""
Module contains the main evaluation of pressure tap results

The variable 'results' will be initially populated with the raw results
This dictionary will be enhanced with the statistic evaluation
Check the proposed structure of the dictionary in the read.me

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de
"""

import json
import sys
from os import path as os_path

from argparse import ArgumentParser, ArgumentTypeError
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from utilities.file_utilities import initialize_point_data
from utilities.other_utilities import get_ramp_up_index, get_cp_series
from utilities.statistic_utilities import get_general_statistics, get_extreme_values_statistics
from utilities.plot_utilities import plot_ref_point_pressure_results, plot_pressure_tap_cp_results, plot_pressure_taps_general_statistics, plot_pressure_taps_extreme_values


#----------------------------------------------------------------
# system arguments which can be passed and default values
parser = ArgumentParser()

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')

# add more options if you like
parser.add_argument('-tv','--run_test', dest='run_test', type=str2bool, default=True,
                    help='bool: is_test to evaluate on very few files for testing, will speed up computation if True')
parser.add_argument('-cm','--calculate_mode', dest='calculate_mode', type=str2bool, default=False,
                    help='bool: calculate_mode when calling statistics, will slow down computation if True')
parser.add_argument('-nb','--nr_of_blocks', dest='nr_of_blocks', type=int, default=6,
                    help='int: number of blocks for Block-axima')

args = parser.parse_args()
print("## Considered arguments: ", args)

if args.calculate_mode:
    print("## Mode calculation on, will take longer")

if args.run_test:
    results_overview = 'ResultsOverviewTest.json'
    report_case_ending = 'Test.pdf'
    print("## In testing mode, will take less time")
else:
    results_overview = 'ResultsOverview.json'
    report_case_ending = '.pdf'
    print("## In all evaluation mode, will take quite some time")

#----------------------------------------------------------------
# hardcoded parameters

# subfolders where the input data is and where reports should be generated
input_data_folder = 'input_data'
reports_folder = 'reports'

#----------------------------------------------------------------
# load results parameters
with open(os_path.join(input_data_folder, results_overview)) as f:
    results = json.load(f)['results']

#----------------------------------------------------------------
# evaluate results

for result in results:

    with PdfPages(os_path.join(reports_folder, 'LowriseReport_' + result['case'] + report_case_ending)) as report_pdf:

        # load reference data results, update existing dictionary
        # NOTE: for now only one reference point, later more could be added
        ref_point_file = os_path.join(input_data_folder, os_path.normpath(result['reference_points'][0]['file_name']))
        result['reference_points'][0].update(initialize_point_data(ref_point_file, result['case']))
        # NOTE: assuming that reference point data and tap data have the same time step
        # which should be the case as we are taking both from the same simulation
        result['reference_points'][0]['post_ramp_up_index'] = get_ramp_up_index(result['reference_points'][0]['series']['time'], result['ramp_up_time'])

        # evaluating statistical quantities
        result['reference_points'][0]['statistics'] = {}
        result['reference_points'][0]['statistics']['pressure'] = {}
        result['reference_points'][0]['statistics']['pressure']['general'] = get_general_statistics(result['reference_points'][0]['series']['pressure'],
                                                                    args.calculate_mode)

        # plotting reference point data
        plot_ref_point_pressure_results(result['reference_points'][0], report_pdf)

        tap_counter = 0
        for pressure_tap in result['pressure_taps']:

            tap_counter += 1
            pressure_tap['label'] = str(tap_counter)
            # load tap data results, update existing dictionary
            pressure_tap_file = os_path.join(input_data_folder, os_path.normpath(pressure_tap['file_name']))
            pressure_tap.update(initialize_point_data(pressure_tap_file, result['case']))
            pressure_tap['post_ramp_up_index'] = get_ramp_up_index(pressure_tap['series']['time'], result['ramp_up_time'])

            pressure_tap['series']['cp'] = get_cp_series(pressure_tap['series']['pressure'],
                                                        result['reference_points'][0]['series'],
                                                        result['density'])

            # evaluating statistical quantities (only after ramp-up time)
            pressure_tap['statistics'] = {}
            pressure_tap['statistics']['cp'] = {}
            pressure_tap['statistics']['cp']['general'] = get_general_statistics(pressure_tap['series']['cp'][pressure_tap['post_ramp_up_index']:],
                                                args.calculate_mode)
            pressure_tap['statistics']['cp']['extreme_value'] = get_extreme_values_statistics(pressure_tap['series']['cp'][pressure_tap['post_ramp_up_index']:],
                                                pressure_tap['post_ramp_up_index'],
                                                args.nr_of_blocks,
                                                args.calculate_mode)

            # plotting tap data
            plot_pressure_tap_cp_results(pressure_tap, args.calculate_mode, report_pdf)

            print('## Plot for result case ' + result['case'] + ' and tap label ' + pressure_tap['label'] + ' ready')

        # general statistics for all taps
        plot_pressure_taps_general_statistics(result['pressure_taps'], report_pdf)

        # extreme value statistics for all taps
        plot_pressure_taps_extreme_values(result['pressure_taps'], args.calculate_mode, report_pdf)

        print('## All plots for result case ' + result['case'] + ' finished')
        # "clearing" dictionary value to reduce memory consumption
        result = {}
