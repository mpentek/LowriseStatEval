# -*- coding: utf-8 -*-
"""
Module contains statistic evaluations functions

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de, michael.andre@tum.de
"""


import matplotlib.mlab as mlab
import numpy as np
from scipy.stats import gaussian_kde, tmean, tstd, skew, kurtosis  # , mode
# from scipy.stats.mstats import mode


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

    if len(data_series) > 1:
        kde = gaussian_kde(data_series)
        results['x'] = np.linspace(data_series_min, data_series_max, 1000)
        results['y'] = kde(results['x'])
    elif len(data_series) == 0:
        print("Data series has 1 element")
        print("Fallback solution")
        results['x'] = [0.0]
        results['y'] = data_series[0]
    else:
        print("Data series has no elements")
        print("Fallback solution")
        results['x'] = []
        results['y'] = []

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
    data_series_std = np.std(data_series)
    data_series_mean = np.mean(data_series)
    data_series_min = np.min(data_series)
    data_series_step = (data_series_max - data_series_min) / 1000

    if data_series_std == 0.0:
        results['x'] = np.zeros(len(data_series))
        results['y'] = np.zeros(len(data_series))

    else:
        data_series_pdf = mlab.normpdf(np.arange(data_series_min, data_series_max + data_series_step, data_series_step),
                                       data_series_mean,
                                       data_series_std)
        results['x'] = np.arange(
            data_series_min, data_series_max + data_series_step, data_series_step)
        results['y'] = data_series_pdf

    return results


def get_pdf(data_series, case='KDE'):

    if case == 'KDE':
        return get_pdf_kde(data_series)

    elif case == 'Normal':
        return get_pdf_normal(data_series)

    else:
        raise Exception(
            "PDF type not implemented, choose either KDE or Normal")


def get_general_statistics(data_series, calculate_mode):

    results = {}

    results['mean'] = tmean(data_series)
    try:
        results['std'] = tstd(data_series)
    except:
        print("Probably not enough data in data series to calculate std, length of array: ", str(
            len(data_series)))
        print("Fallback solution: returning std = 0.")
        results['std'] = 0.0

    results['skewness'] = skew(data_series)
    # one can choose between Fisher's and Pearson's definition
    results['kurtosis'] = kurtosis(data_series, fisher=True)
    # new additions
    results['min'] = min(data_series)
    results['max'] = max(data_series)

    results['pdf'] = get_pdf(data_series)

    # NOTE: mode is time-consuming
    if calculate_mode:
        # version 1
        # scipy.stats.mode seems to have a problem and deliver bad results
        # r esults['mode'] = mode(data_series)[0][0]

        # version 2
        # alternative would be scipy.stats.mstat.mode as new_mode
        # which seems to deliver more correct results than versiom 1
        # and be the most robust
        # it also seems to be a lot faster than version 1
        # results['mode'] = mode(data_series)[0][0]

        # version 3
        # note: as PDF is anyway calculated, taking mode from there as the max
        # value in the PDF
        '''
        Assuming unimodal functions:
        A mode of a continuous probability distribution is a value at which the
        probability density function (pdf) attains its maximum value
        '''
        if (len(results['pdf']['y']) > 1):
            results['mode'] = results['pdf']['x'][np.argmax(
                results['pdf']['y'])]
        else:
            print("y component of pdf has no values")
            print("Fallback solution taking mode = 0.")
            results['mode'] = 0.

    return results


def get_extreme_values_statistics(data_series, ramp_up_idx, block_size, calculate_mode, case='BM'):

    if case == 'BM':
        print('## Evaluating BM - Block-Maxima')
        return get_block_maxima(data_series, ramp_up_idx, block_size, calculate_mode)

    elif case == 'POT':
        print('## Evaluating POT - Peak-Over-Threshol')
        raise Exception("POT not implemented, choose BM")

    else:
        raise Exception(
            "Extreme value evaluation not implemented, choose either BM or POT")


def get_block_maxima(data_series, ramp_up_idx,  nr_of_blocks, calculate_mode):

    block_size = np.round(len(data_series) / nr_of_blocks)
    nr_of_sections = int(np.round(len(data_series) / block_size))
    series_sections = np.array_split(data_series, nr_of_sections)
    global_idx_adjustment = ramp_up_idx

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
        classical_extreme_idx.append(np.where(section == max_val)[
                                     0][0] + global_idx_adjustment)

        if np.sign(max_val) != np.sign(min_val):
            alternative_extremes_val.append(min_val)
            alternative_extremes_idx.append(np.where(section == min_val)[
                                            0][0] + global_idx_adjustment)

        global_idx_adjustment += len(section)

    block_start_idx.append(global_idx_adjustment - 1)

    classical_extremes_stat = get_general_statistics(
        classical_extremes_val, calculate_mode)

    if alternative_extremes_val:
        alternative_extremes_stat = get_general_statistics(
            alternative_extremes_val, calculate_mode)

    else:
        print("## No alternative extremes found, using 0.0 as dummy statistic values not to break plotting")
        alternative_extremes_val.append(0.0)
        alternative_extremes_idx.append(0)

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


def get_velocity_and_pressure_autocorrelation(time_series, velocity_series, pressure_series, target_lux=[80.0, 100.0, 120.0]):
    '''
    Spectral length for target autocorrelation
    specified by default
    '''

    t = time_series
    # time shift to start from 0 the autocorrelation results
    t = t - t[0]

    u = velocity_series
    p = pressure_series

    umean = np.mean(u)
    u = u - umean
    nx = len(u)
    ur = np.array([u[i] for i in range(nx - 1, -1, -1)])
    u = np.hstack((u, u[:-1]))
    # it is the correlation of velocity with itself - so autocorrelation
    r_uu = np.convolve(ur, u, mode='valid') / nx
    # r/r[0] represents the normalized autocorrelation of velocity
    r_uu = r_uu / r_uu[0]

    pmean = np.mean(p)
    p = p - pmean
    nx = len(p)
    pr = np.array([p[i] for i in range(nx - 1, -1, -1)])
    # it is the correlation of pressure with itself - so autocorrelation
    p = np.hstack((p, p[:-1]))
    r_pp = np.convolve(pr, p, mode='valid') / nx
    # r/r[0] represents the normalized autocorrelation of pressure
    r_pp = r_pp / r_pp[0]

    results = {}
    results['time'] = t
    results['velocity'] = r_uu
    results['pressure'] = r_pp
    results['target'] = {}

    for tl in target_lux:
        f1 = np.exp(-0.822 * (umean * t / tl)**0.77)
        target_autocorr = 0.5 * (f1 + f1**2)

        results['target']["ESDU Lux={:5.1f}".format(tl)] = target_autocorr

    return results


def get_velocity_spectra(time_series, velocity_series, z=25.0, z0=0.06):
    '''
    Default values for z and z0 hardcoded - here for the gable_roof_wind_2.h5
    All results should be based upon this generated wind
    '''
    def Fu_exact(k1z): return 52.5 * k1z / (1. + 33. * k1z)**(5. / 3.)

    kxz_fit = np.array([0.00198943678865, 0.00296803190755, 0.00442799361834, 0.00660610400926, 0.00985561722592,
                        0.0147035515589, 0.021936163255, 0.0327264645157, 0.0488244670342, 0.0728410054812,
                        0.108671172505, 0.162126039523, 0.241875118171, 0.360852414347, 0.538354113993,
                        0.8031681112, 1.19824293728, 1.78765331532, 2.66699204005, 3.9788735773])
    Fu_fit = np.array([0.105791883098, 0.146072921739, 0.197712237681, 0.260742123281, 0.332502406069,
                       0.406558248946, 0.47290167654, 0.520191810197, 0.539347512083, 0.526518073323,
                       0.484089036307, 0.420301445225, 0.347791585792, 0.278950554163, 0.220213310142,
                       0.172281158258, 0.133847652859, 0.103416441602, 0.0795951241049, 0.0611154974287])

    u = velocity_series
    umean = np.mean(velocity_series)
    # calculate the respective length measure
    # based upon length of time series and the mean velocity
    lx = (time_series[-1] - time_series[0]) * umean

    utau = 0.41 * umean / np.log(z / z0)

    nx = len(u)
    Fu = np.zeros(int(nx / 2) + 1)

    kx = np.array([2.0 * np.pi * i / lx for i in range(int(nx / 2) + 1)])
    kxz = kx * z / (2.0 * np.pi)

    Fu = Fu + kx * abs(np.fft.fft(u)[:int(nx / 2) + 1]
                       )**2 * lx / nx**2 / (2.0 * np.pi) / utau**2

    results = {}
    results['kxz'] = kxz
    results['Fu'] = Fu
    results['kxz_fit'] = kxz_fit
    results['Fu_fit'] = Fu_fit
    results['Fu_exact'] = Fu_exact(kxz)

    return results
