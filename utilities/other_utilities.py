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
    parser.add_argument('-rt', '--run_test', dest='run_test', type=str2bool, default=True,
                        help='bool: is_test to evaluate on very few files for testing, will speed up computation if True')
    parser.add_argument('-cm', '--calculate_mode', dest='calculate_mode', type=str2bool, default=False,
                        help='bool: calculate_mode when calling statistics, will slow down computation if True')
    parser.add_argument('-nb', '--nr_of_blocks', dest='nr_of_blocks', type=int, default=6,
                        help='int: number of blocks for Block-axima')
    # the way how to calculate the cp
    # trad = traditional = reference values is not subtracted for each time step,
    # but an arithmetic mean is used for p0 and v_ref
    # new = reference values is subtracted for each time instance,
    # using p0(t) and v_ref
    parser.add_argument('-cpm', '--cp_mode', dest='cp_mode', type=str, default='new',
                        help='str: selecting the way how to calculate the cp ')

    return parser


def get_ramp_up_index(times_series, ramp_up_time):
    return np.where(times_series >= ramp_up_time + ramp_up_time / 5)[0][0]


def get_cp_series(tap_pressure_series, reference_data_series, density, cp_mode):
    if cp_mode == 'trad':
        return get_cp_series_traditional(tap_pressure_series, reference_data_series, density)
    elif cp_mode == 'new':
        return get_cp_series_new(tap_pressure_series, reference_data_series, density)
    else:
        raise ArgumentTypeError('cp_mode not implemented.')


def get_cp_series_traditional(tap_pressure_series, reference_data_series, density):
    # this is the cp calculation using the "traditional" way
    # so using the arithmetic mean of pressure and reference streamwise
    # velocity
    reference_velocity = tmean(reference_data_series['velocity_x'])
    refernce_pressure = tmean(reference_data_series['pressure'])
    mutiplication_factor = 1 / (0.5 * density * reference_velocity**2)

    return np.multiply(tap_pressure_series - refernce_pressure, mutiplication_factor)


def get_cp_series_new(tap_pressure_series, reference_data_series, density):
    # this is the cp calculation using the "new/cleaning"
    # so substracting the reference pressure
    # for each time instance
    reference_velocity = tmean(reference_data_series['velocity_x'])
    mutiplication_factor = 1 / (0.5 * density * reference_velocity**2)

    return np.multiply(np.subtract(tap_pressure_series, reference_data_series['pressure']),
                       mutiplication_factor)
