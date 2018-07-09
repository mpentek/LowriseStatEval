# -*- coding: utf-8 -*-
"""
Module contains some generic functions

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de
"""


import numpy as np
from scipy.stats import tmean
from argparse import ArgumentParser, ArgumentTypeError


def get_custom_parser_settings():

    # system arguments which can be passed and default values
    parser = ArgumentParser()

    # needed custom function definition to get a bool value from a string
    # when command line argument is passed
    def str2bool(input_string):
        if input_string.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif input_string.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise ArgumentTypeError('Boolean value expected.')

    # add more options if you like
    parser.add_argument('-rt','--run_test', dest='run_test', type=str2bool, default=True,
                        help='bool: is_test to evaluate on very few files for testing, will speed up computation if True')
    parser.add_argument('-cm','--calculate_mode', dest='calculate_mode', type=str2bool, default=False,
                        help='bool: calculate_mode when calling statistics, will slow down computation if True')
    parser.add_argument('-nb','--nr_of_blocks', dest='nr_of_blocks', type=int, default=6,
                        help='int: number of blocks for Block-axima')

    return parser


def get_ramp_up_index(times_series, ramp_up_time):

    return np.where(times_series >= ramp_up_time + ramp_up_time/5)[0][0]

def get_cp_series(tap_pressure_series, reference_data_series, density):
    # this is the cp calculation using the "cleaning"
    # so substracting the reference pressure
    # for each time instance
    reference_velocity = tmean(reference_data_series['velocity_x'])
    mutiplication_factor = 1 /(0.5 * density * reference_velocity**2)

    return np.multiply(np.subtract(tap_pressure_series, reference_data_series['pressure']),
        mutiplication_factor)