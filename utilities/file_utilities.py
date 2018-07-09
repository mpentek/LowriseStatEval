# -*- coding: utf-8 -*-
"""
Module contains file io functions, some specific implementations for
the various formats from Kratos, FeFlow, OpenFoam

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de
"""


import re
import numpy as np


def get_position_from_header(file, result_case):
    with open(file, 'r') as f:
        #jump to the beginning of the file
        f.seek(0)
        first_line = f.readline()

    if 'Kratos' in result_case:
        position = [np.around(float(item),2) for item in (re.findall(r"[-+]?\d*\.\d+|\d+",first_line))]
    elif 'FeFlo' in result_case:
        position = [np.around(float(item),2) for item in first_line.rstrip('\n').split('  ')[-3:]]
    else:
        raise Exception('Result case: ' + result_case + ' not supported.')

    return position

def get_tabular_data(file):
    # assumed column structure - time, pressure, velocity_x
    # NOTE: np.loadtxt() already casts to np.asarray() where possible
    time_series = np.loadtxt(file, usecols = (0,))
    pressure_series = np.loadtxt(file, usecols = (1,))
    try:
        velocity_x_series =  np.loadtxt(file, usecols = (2,))
    except:
        print("No velocity_x_series in " + file)
        velocity_x_series = np.asarray([])

    return time_series, pressure_series, velocity_x_series

def initialize_point_data(ref_file, result_case):
    point_data = {}
    point_data['position'] = get_position_from_header(ref_file, result_case)
    point_data['series'] = {}
    [point_data['series']['time'], point_data['series']['pressure'], point_data['series']['velocity_x']]= get_tabular_data(ref_file)
    return point_data