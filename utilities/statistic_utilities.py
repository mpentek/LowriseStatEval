# -*- coding: utf-8 -*-
"""
Module contains statistic evaluations functions

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de
"""


import matplotlib.mlab as mlab
import numpy as np #import max,min,std,mean,abs,floor,fft
from scipy.stats import gaussian_kde, tmean, tstd, skew, kurtosis, mode
from scipy.stats.mstats import mode as new_mode


def get_pdf_kde(data_series):
    '''
    Evaluates the probability distribution function (pdf)
    of the samples by using a non-parametric estimation technique called Kernal Desnity
    Estimation (KDE). More details can be found at
    https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.stats.gaussian_kde.html.
    '''
    results = {}

    data_series_max = np.max(data_series)
    data_series_min = np.min(data_series)
    kde = gaussian_kde(data_series)
    results['x'] = np.linspace(data_series_min, data_series_max, 1000)
    results['y'] = kde(results['x'])

    return results

def get_pdf_normal(data_series):
    '''
    Estimates the normal pdf of the signal from the mean
    and standard deviation of the samples. Recall the fact that a Normal distribution
    can be entirely defined by two parameters, namely the mean and standard deviation.
    More details about the function mlab.normpdf can be found at
    https://matplotlib.org/api/mlab_api.html.
    '''

    results = {}

    data_series_max = np.max(data_series)
    data_series_std= np.std(data_series)
    data_series_mean = np.mean(data_series)
    data_series_min = np.min(data_series)
    data_series_step = (data_series_max - data_series_min)/ 1000

    if data_series_std ==0.0:
        results['x'] = np.zeros(len(data_series))
        results['y']  = np.zeros(len(data_series))

    else:
        data_series_pdf = mlab.normpdf(np.arange(data_series_min, data_series_max + data_series_step, data_series_step),
                                        data_series_mean,
                                        data_series_std)
        results['x']  = np.arange(data_series_min, data_series_max + data_series_step, data_series_step)
        results['y']  = data_series_pdf

    return results

def get_pdf(data_series, case='KDE'):

    if case == 'KDE':
        return get_pdf_kde(data_series)

    elif case == 'Normal':
        return get_pdf_normal(data_series)

    else:
        raise Exception("PDF type not implemented, choose either KDE or Normal")

def get_general_statistics(data_series, calculate_mode):

    results = {}

    results['mean'] = tmean(data_series)
    results['std'] = tstd(data_series)
    results['skewness'] = skew(data_series)
    #one can choose between Fisher's and Pearson's definition
    results['kurtosis'] = kurtosis(data_series, fisher = True)
    # new additions
    results['min'] = min(data_series)
    results['max'] = max(data_series)

    results['pdf'] = get_pdf(data_series)

    # NOTE: mode is time-consuming
    if calculate_mode:
        # scipy.stats.mode seems to have a problem and deliver bad results
        #results['mode'] = mode(data_series)[0][0]

        # alternative would be scipy.stats.mstat.mode as new_mode
        # which seems to deliver correct results
        # and be the most robust
        results['mode'] = new_mode(data_series)[0][0]

        # Note: as PDF is anyway calculated, taking mode from there as the max value in the PDF
        # '''
        # Assuming unimodal functions:
        # A mode of a continuous probability distribution is a value at which the
        # probability density function (pdf) attains its maximum value
        # '''
        # results['mode'] = results['pdf']['x'][np.argmax(results['pdf']['y'])]

    return results

def get_extreme_values_statistics(data_series, ramp_up_idx, block_size, calculate_mode, case='BM'):

    if case == 'BM':
        print('Evaluating BM - Block-Maxima')
        return get_block_maxima(data_series, ramp_up_idx, block_size, calculate_mode)

    elif case == 'POT':
        print('Evaluating POT - Peak-Over-Threshol')
        raise Exception("POT not implemented, choose BM")

    else:
        raise Exception("Extreme value evaluation not implemented, choose either BM or POT")

def get_block_maxima(data_series, ramp_up_idx,  nr_of_blocks, calculate_mode):

    block_size = np.round(len(data_series)/nr_of_blocks)
    nr_of_sections = int(np.round(len(data_series)/block_size))
    series_sections = np.array_split(data_series, nr_of_sections)
    global_idx_adjustment = ramp_up_idx;

    classical_extremes_val = []
    classical_extreme_idx = []
    alternative_extremes_val = []
    alternative_extremes_idx = []
    block_start_idx = []

    for section in series_sections:
        block_start_idx.append(global_idx_adjustment)

        # sign of mean_val and max_val has to coincide by definition
        mean_val = np.mean(section)

        if mean_val >= 0.0:
            min_val = np.min(section)
            max_val = np.max(section)

        else:
            max_val = np.min(section)
            min_val = np.max(section)

        classical_extremes_val.append(max_val)
        classical_extreme_idx.append(np.where(section == max_val)[0][0] + global_idx_adjustment)

        if np.sign(max_val) != np.sign(min_val):
            alternative_extremes_val.append(min_val)
            alternative_extremes_idx.append(np.where(section == min_val)[0][0] + global_idx_adjustment)

        global_idx_adjustment += len(section)

    block_start_idx.append(global_idx_adjustment - 1)

    classical_extremes_stat = get_general_statistics(classical_extremes_val, calculate_mode)

    if alternative_extremes_val:
        alternative_extremes_stat = get_general_statistics(alternative_extremes_val, calculate_mode)

    else:
        print("## No alternative extremes found, using 0.0 as dummy statistic values not to break plotting")
        alternative_extremes_stat = {}
        alternative_extremes_stat['mean'] = 0.0
        alternative_extremes_stat['std'] = 0.0
        alternative_extremes_stat['kurtosis'] = 0.0
        alternative_extremes_stat['skewness'] = 0.0
        alternative_extremes_stat['min'] = 0.0
        alternative_extremes_stat['max'] = 0.0

        if calculate_mode:
            alternative_extremes_stat['mode'] = 0.0

        alternative_extremes_stat['pdf'] = {}
        alternative_extremes_stat['pdf']['x'] = np.asarray([])
        alternative_extremes_stat['pdf']['y'] = np.asarray([])

    results = {}
    results['block_start_idx'] = np.asarray(block_start_idx)
    results['classical'] = {}
    results['classical']['val'] = np.asarray(classical_extremes_val)
    results['classical']['idx'] = np.asarray(classical_extreme_idx)
    results['classical']['statistics'] = classical_extremes_stat
    results['alternative'] = {}
    results['alternative']['val'] = np.asarray(alternative_extremes_val)
    results['alternative']['idx'] = np.asarray(alternative_extremes_idx)
    results['alternative']['statistics'] = alternative_extremes_stat

    return results