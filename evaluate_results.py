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

import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from utilities.file_utilities import initialize_point_data
from utilities.other_utilities import get_custom_parser_settings, get_ramp_up_index, get_cp_series
from utilities.statistic_utilities import get_general_statistics, get_extreme_values_statistics, get_velocity_spectra, get_velocity_and_pressure_autocorrelation
from utilities.plot_utilities import plot_ref_point_pressure_results, plot_ref_point_velocity_spectra, plot_ref_point_velocity_and_pressure_autocorrelation, plot_pressure_tap_cp_results, plot_pressure_taps_general_statistics, plot_pressure_taps_extreme_values
from utilities.export_utilities import export_summary_to_text

#----------------------------------------------------------------
# parsing of command line arguments for user specified settings
# or default ones
# sample usage: testing mode -> off, calculate mode -> on, cp_mode -> traditional
# python3 evaluate_results.py -rt 'false' -cm 'true' -cpm 'trad'

args = get_custom_parser_settings().parse_args()
print("## Considered command-line arguments: ", args)

if args.calculate_mode:
    print("## Mode calculation on, will take longer")

if args.run_test:
    results_overview = 'ResultsOverviewTest.json'
    report_ending = '_Test.pdf'
    result_summary_ending = '_Test.dat'
    print("## In testing mode, will take less time")
else:
    results_overview = 'ResultsOverview.json'
    report_ending = '.pdf'
    result_summary_ending = '.dat'
    print("## In all evaluation mode, will take quite some time")

if args.cp_mode == 'trad':
    result_cp = '_Trad'
else:
    result_cp = '_New'


#----------------------------------------------------------------
# hardcoded parameters

# subfolders where the input data is and where reports should be generated
input_data_folder = 'input_data'
reports_folder = 'reports'
summaries_folder = 'summaries'

#----------------------------------------------------------------
# load results parameters
with open(os_path.join(input_data_folder, results_overview)) as f:
    results = json.load(f)['results']

#----------------------------------------------------------------
# evaluate results


for result in results:

    with PdfPages(os_path.join(reports_folder, 'LowriseReport_' + result['case'] + result_cp + report_ending)) as report_pdf:

        # load reference data results, update existing dictionary
        # NOTE: for now only one reference point, later more could be added
        ref_point_file = os_path.join(input_data_folder, os_path.normpath(
            result['reference_points'][0]['file_name']))
        result['reference_points'][0].update(
            initialize_point_data(ref_point_file, result['case']))
        # NOTE: assuming that reference point data and tap data have the same time step
        # which should be the case as we are taking both from the same
        # simulation
        result['reference_points'][0]['post_ramp_up_index'] = get_ramp_up_index(
            result['reference_points'][0]['series']['time'], result['ramp_up_time'])

        # evaluating statistical quantities
        result['reference_points'][0]['statistics'] = {}
        result['reference_points'][0]['statistics']['pressure'] = {}
        result['reference_points'][0]['statistics']['pressure']['general'] = get_general_statistics(result['reference_points'][0]['series']['pressure'],
                                                                                                    args.calculate_mode)

        result['reference_points'][0]['velocity_spectra'] = get_velocity_spectra(result['reference_points'][0]['series']['time'][result['reference_points'][0]['post_ramp_up_index']:],
                                                                                 result['reference_points'][0]['series']['velocity_x'][result['reference_points'][0]['post_ramp_up_index']:])

        result['reference_points'][0]['autocorrelation'] = get_velocity_and_pressure_autocorrelation(result['reference_points'][0]['series']['time'][result['reference_points'][0]['post_ramp_up_index']:],
                                                                                                     result['reference_points'][0]['series']['velocity_x'][result['reference_points']
                                                                                                                                                           [0]['post_ramp_up_index']:],
                                                                                                     result['reference_points'][0]['series']['pressure'][result['reference_points'][0]['post_ramp_up_index']:])

        # plotting reference point data
        plot_ref_point_pressure_results(
            result['reference_points'][0], report_pdf)
        plot_ref_point_velocity_spectra(
            result['reference_points'][0], report_pdf)
        plot_ref_point_velocity_and_pressure_autocorrelation(
            result['reference_points'][0], report_pdf)

        tap_counter = 0
        for pressure_tap in result['pressure_taps']:
            tap_counter += 1
            pressure_tap['label'] = str(tap_counter)

            # load tap data results, update existing dictionary
            pressure_tap_file = os_path.join(
                input_data_folder, os_path.normpath(pressure_tap['file_name']))
            pressure_tap.update(initialize_point_data(
                pressure_tap_file, result['case']))
            pressure_tap['post_ramp_up_index'] = get_ramp_up_index(
                pressure_tap['series']['time'], result['ramp_up_time'])

            pressure_tap['series']['cp'] = get_cp_series(pressure_tap['series']['pressure'],
                                                         result['reference_points'][0]['series'],
                                                         result['density'],
                                                         args.cp_mode)

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
            plot_pressure_tap_cp_results(
                pressure_tap, args.calculate_mode, report_pdf)

            print('## Plot for result case ' +
                  result['case'] + ' and tap label ' + pressure_tap['label'] + ' ready')

        # general statistics for all taps
        plot_pressure_taps_general_statistics(
            result['pressure_taps'], report_pdf)

        # extreme value statistics for all taps
        plot_pressure_taps_extreme_values(
            result['pressure_taps'], args.calculate_mode, report_pdf)

        # export main data summary to text format
        with open(os_path.join(
                summaries_folder, 'LowriseSummary_' + result['case'] + result_cp + result_summary_ending), 'w') as result_summary:
            result_summary.write(export_summary_to_text(
                result['pressure_taps'], args.calculate_mode))
            result_summary.close()

        print('## All plots for result case ' + result['case'] + ' finished')
        # "clearing" dictionary value to reduce memory consumption
        result = {}
