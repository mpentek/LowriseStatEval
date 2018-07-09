# -*- coding: utf-8 -*-
"""
Module contains some generic functions

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de
"""


import numpy as np
from scipy.stats import tmean


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