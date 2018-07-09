# -*- coding: utf-8 -*-
"""
Module contains plot functions

Created on 08.07.2018

@author: mate.pentek@tum.de, anoop.kodakkal@tum.de
"""


import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec


# print to check all available predefined plot styles
#print(plt.style.available)
# for example choose the popular ggplot
#plt.style.use('ggplot')

# custom plot definitions
# return cm from inch
def cm2inch(value):
    return value / 2.54

# paper size for a4 landscape
width = cm2inch(29.7)
height = cm2inch(21)

# custom rectangle size for figure layout
cust_rect = [0, 0.025, 1, 0.95]

# direct input
plt.rcParams['text.latex.preamble'] = [r"\usepackage{lmodern}"]

# options
# for customizing check https://matplotlib.org/users/customizing.html
params = {'text.usetex': True,
          'font.size': 10,
          'font.family': 'lmodern',
          'text.latex.unicode': True,
          'figure.titlesize': 14,
          'figure.titleweight': 'bold',
          'figure.figsize': (width, height),
          'figure.dpi': 300,
          'figure.constrained_layout.use' : True,
          'figure.subplot.wspace'  : 0.25,
          'figure.subplot.hspace'  : 0.25,
          'axes.titlesize': 12,
          'axes.titlepad' : 12,
          'axes.labelsize': 10,
          'axes.labelpad': 10,
          'axes.grid': 'True',
          'axes.grid.which': 'both',
          'axes.xmargin': 0.05,
          'axes.ymargin': 0.05,
          'lines.linewidth': 1.0,
          'lines.markersize': 5,
          'xtick.labelsize': 10,
          'ytick.labelsize': 10,
          'ytick.minor.visible': False,
          'xtick.minor.visible': False,
          'grid.linestyle': '-',
          'grid.linewidth': 0.5,
          'grid.alpha': 0.3,
          'legend.fontsize': 10,
          'savefig.dpi': 300,
          'savefig.format': 'pdf',
          'savefig.bbox': 'tight'
          }
plt.rcParams.update(params)


def plot_pressure_tap_cp_results(pressure_tap, calculate_mode, report_pdf):

    # main figure
    fig = plt.figure()
    fig.suptitle('Results for tap "' + pressure_tap['label'] + '" at: ' + ', '.join(map(str, pressure_tap['position'])))
    gs = gridspec.GridSpec(2, 3)

    # subplot 1
    ax1 = fig.add_subplot(gs[0,:])

    # main plot
    ax1.plot(pressure_tap['series']['time'],
        pressure_tap['series']['cp'])

    # mean
    ax1.axhline(pressure_tap['statistics']['cp']['general']['mean'],
        color='r',
        linestyle='-',
        label = 'Mean')

    ax1.text(0.95,0.5,
        'Mean %.3f' % pressure_tap['statistics']['cp']['general']['mean'],
        transform = ax1.transAxes)

    # scatter for extreme values
    ax1.scatter(pressure_tap['series']['time'][pressure_tap['statistics']['cp']['extreme_value']['classical']['idx']],
            pressure_tap['series']['cp'][pressure_tap['statistics']['cp']['extreme_value']['classical']['idx']],
            marker ='s',
            c='r',
            label = 'Clas. Extr.')

    ax1.scatter(pressure_tap['series']['time'][pressure_tap['statistics']['cp']['extreme_value']['alternative']['idx']],
            pressure_tap['series']['cp'][pressure_tap['statistics']['cp']['extreme_value']['alternative']['idx']],
            marker = 'D',
            c='g',
            label = 'Alter. Extr.')

    for idx in pressure_tap['statistics']['cp']['extreme_value']['block_start_idx']:
        ax1.axvline(x=pressure_tap['series']['time'][idx], color='k',linestyle='--')

    ax1.set_title('Time history')
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Pressure coefficient [-]')

    ax1.legend()
    ax1.grid(True)

    # subplot 2
    ax2 = fig.add_subplot(gs[1,0])

    # main plot
    ax2.plot(pressure_tap['statistics']['cp']['general']['pdf']['x'],
        pressure_tap['statistics']['cp']['general']['pdf']['y'])

    # mean
    ax2.axvline(pressure_tap['statistics']['cp']['general']['mean'],
            color='r',
            label='Mean')

    text_msg = 'Mean %.3f' % (pressure_tap['statistics']['cp']['general']['mean'])

    # mode
    if calculate_mode:
        ax2.axvline(pressure_tap['statistics']['cp']['general']['mode'],
            color = 'g',
            label = 'Mode')

        text_msg = 'Mean %.3f \n Mode %.3f' % (pressure_tap['statistics']['cp']['general']['mean'],
                                               pressure_tap['statistics']['cp']['general']['mode'])

    ax2.text(0.1,0.9, text_msg, transform = ax2.transAxes)

    ax2.set_title('PDF of time history')
    ax2.set_xlabel('Pressure coefficient [-]')
    ax2.set_ylabel('Probability density')
    ax2.grid(True)

    # subplot 3
    ax3 = fig.add_subplot(gs[1,1])

    # main plot
    ax3.plot(pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['pdf']['x'],
        pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['pdf']['y'])

    # mean
    ax3.axvline(pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mean'],
        color='r',
        label='Mean')

    text_msg = 'Mean %.3f' % (pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mean'])

    if calculate_mode:
        ax3.axvline(pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mode'],
            color='g',
            label='Mode')

        text_msg = 'Mean %.3f \n Mode %.3f' % (pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mean'],
                                               pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mode'])

    ax3.text(0.1,0.9, text_msg, transform = ax3.transAxes)

    ax3.set_title('PDF of Classical Extrema')
    ax3.set_xlabel('Pressure coefficient [-]')
    ax3.grid(True)

    # subplot 4
    ax4 = fig.add_subplot(gs[1,2])

    if pressure_tap['statistics']['cp']['extreme_value']['alternative']:
        # list not empty

        # main plot
        ax4.plot(pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['pdf']['x'],
            pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['pdf']['y'])

        ax4.axvline(pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mean'],
            color='r',
            label = 'Mean')

        text_msg = 'Mean %.3f' % (pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mean'])

        if calculate_mode:
            ax4.axvline(pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mode'],
                color='g',
                label = 'Mode')

            text_msg = 'Mean %.3f \n Mode %.3f' % (pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mean'],
                                                   pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mode'])

        ax4.text(0.1,0.9, text_msg, transform = ax4.transAxes)

    else:
        print("pressure_tap['statistics']['cp']['extreme_value']['alternative'] list empty for tap " + pressure_tap['label'])

    ax4.set_title('PDF of Alternative Extrema')
    ax4.set_xlabel('Pressure coefficient [-]')
    ax4.grid(True)
    ax4.legend(bbox_to_anchor=(0.9, 0.9),bbox_transform=ax4.transAxes)

    #fig.tight_layout()

    # resizing the internal rectangle so that the sup title is not overlayed
    # workaround for overlapping elements
    gs.tight_layout(fig, rect=cust_rect)

    report_pdf.savefig()

    # plot window needs to be closed to avoid error and memory problem
    # due to too many opened
    plt.close()

def plot_ref_point_pressure_results(ref_point, report_pdf):

    # main figure
    fig = plt.figure()
    fig.suptitle('Results for tap "' + ref_point['label'] + '" at: ' + ', '.join(map(str, ref_point['position'])))
    gs = gridspec.GridSpec(1, 1)

    # subplot 1
    ax1 = fig.add_subplot(gs[0,0])

    # main plot
    ax1.plot(ref_point['series']['time'],
        ref_point['series']['pressure'])

    # mean
    ax1.axhline(ref_point['statistics']['pressure']['general']['mean'],
        color='r',
        label = 'mean')

    # mean + std
    ax1.axhline(ref_point['statistics']['pressure']['general']['mean'] + ref_point['statistics']['pressure']['general']['std'],
        color='r',
        linestyle='--',
        label = 'mean+std')

    # mean - std
    ax1.axhline(ref_point['statistics']['pressure']['general']['mean'] - ref_point['statistics']['pressure']['general']['std'],
        color='r',
        linestyle='--',
        label = 'mean-std')

    ax1.text(0.95,0.5,
        'Mean %.3f\n Mean+std%.3f\n Mean-std %.3f' % (ref_point['statistics']['pressure']['general']['mean'],
        ref_point['statistics']['pressure']['general']['mean'] + ref_point['statistics']['pressure']['general']['std'],
        ref_point['statistics']['pressure']['general']['mean'] - ref_point['statistics']['pressure']['general']['std']),
        transform = ax1.transAxes)

    ax1.axvline(x=ref_point['series']['time'][ref_point['post_ramp_up_index']], color='k',linestyle='--')

    ax1.set_title('Time history')
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel(r'Pressure [$N/{m}^2$]')

    ax1.legend()
    ax1.grid(True)

    #fig.tight_layout()

    # resizing the internal rectangle so that the sup title is not overlayed
    # workaround for overlapping elements
    gs.tight_layout(fig, rect=cust_rect)

    report_pdf.savefig()

    # plot window needs to be closed to avoid error and memory problem
    # due to too many opened
    plt.close()

def plot_pressure_taps_general_statistics(pressure_taps, report_pdf):
    barwidth = 0.33

    custom_tick_labels = []
    mean = []
    std = []
    kurt = []
    skew = []
    min_val = []
    max_val = []

    nr_of_bars = len(pressure_taps)

    for pressure_tap in pressure_taps:

        custom_tick_labels.append(pressure_tap['label'])

        mean.append(pressure_tap['statistics']['cp']['general']['mean'])
        std.append(pressure_tap['statistics']['cp']['general']['std'])
        kurt.append(pressure_tap['statistics']['cp']['general']['kurtosis'])
        skew.append(pressure_tap['statistics']['cp']['general']['skewness'])
        min_val.append(pressure_tap['statistics']['cp']['general']['min'])
        max_val.append(pressure_tap['statistics']['cp']['general']['max'])

    # part 1
    # main figure
    fig = plt.figure()
    fig.suptitle('General statistics - part 1')
    gs = gridspec.GridSpec(3, 1)

    # subplot 1
    ax1 = fig.add_subplot(gs[0,0])
    ax1.bar(np.arange(nr_of_bars), mean, barwidth, color='r')
    ax1.set_title('Mean')
    ax1.set_ylabel('Pressure coefficient [-]')
    ax1.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax1.grid(True)

    # subplot 2
    ax2 = fig.add_subplot(gs[1,0])
    ax2.bar(np.arange(nr_of_bars), std, barwidth, color='g')
    ax2.set_title('Std')
    ax2.set_ylabel('Pressure coefficient [-]')
    ax2.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax2.grid(True)

    # subplot 3
    ax3 = fig.add_subplot(gs[2,0])
    ax3.bar(np.arange(nr_of_bars), kurt, barwidth, color='b')
    ax3.set_title('Kurtosis')
    ax3.set_ylabel('Pressure coefficient [-]')
    ax3.set_xlabel('Tap label')
    ax3.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax3.grid(True)

    #fig.tight_layout()

    # resizing the internal rectangle so that the sup title is not overlayed
    # workaround for overlapping elements
    gs.tight_layout(fig, rect=cust_rect)

    report_pdf.savefig()

    # plot window needs to be closed to avoid error and memory problem
    # due to too many opened
    plt.close()

    # part 2
    # main figure
    fig = plt.figure()
    fig.suptitle('General statistics - part 2')
    gs = gridspec.GridSpec(3, 1)

    # subplot 1
    ax1 = fig.add_subplot(gs[0,0])
    ax1.bar(np.arange(nr_of_bars), skew, barwidth, color='r')
    ax1.set_title('Skewness')
    ax1.set_ylabel('Pressure coefficient [-]')
    ax1.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax1.grid(True)

    # subplot 2
    ax2 = fig.add_subplot(gs[1,0])
    ax2.bar(np.arange(nr_of_bars), min_val, barwidth, color='g')
    ax2.set_title('Min')
    ax2.set_ylabel('Pressure coefficient [-]')
    ax2.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax2.grid(True)

    # subplot 3
    ax3 = fig.add_subplot(gs[2,0])
    ax3.bar(np.arange(nr_of_bars), max_val, barwidth, color='b')
    ax3.set_title('Max')
    ax3.set_ylabel('Pressure coefficient [-]')
    ax3.set_xlabel('Tap label')
    ax3.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax3.grid(True)

    #fig.tight_layout()

    # resizing the internal rectangle so that the sup title is not overlayed
    # workaround for overlapping elements
    gs.tight_layout(fig, rect=cust_rect)

    report_pdf.savefig()

    # plot window needs to be closed to avoid error and memory problem
    # due to too many opened
    plt.close()

def plot_pressure_taps_extreme_values(pressure_taps, calculate_mode, report_pdf):
    barwidth = 0.33

    custom_tick_labels = []
    mean_CEV = []
    mean_AEV = []

    if calculate_mode:
        mode_CEV = []
        mode_AEV = []

    for pressure_tap in pressure_taps:

        custom_tick_labels.append(pressure_tap['label'])

        mean_CEV.append(pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mean'])
        mean_AEV.append(pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mean'])

        if calculate_mode:
            mode_CEV.append(pressure_tap['statistics']['cp']['extreme_value']['classical']['statistics']['mode'])
            mode_AEV.append(pressure_tap['statistics']['cp']['extreme_value']['alternative']['statistics']['mode'])

    nr_of_bars = len(pressure_taps)

    # main figure
    fig = plt.figure()
    fig.suptitle('Extreme value statistics')
    gs = gridspec.GridSpec(2, 1)

    # subplot 1
    ax1 = fig.add_subplot(gs[0,0])

    if calculate_mode:
        ax1.bar(np.arange(nr_of_bars)-barwidth/2, mean_CEV, barwidth, color='r', label = 'Mean')
        ax1.bar(np.arange(nr_of_bars)+barwidth/2, mode_CEV, barwidth, color='g', label = 'Mode')

    else:
        ax1.bar(np.arange(nr_of_bars), mean_CEV, barwidth, color='r', label = 'Mean')

    ax1.set_title('Classical Extrema')
    ax1.set_ylabel('Pressure coefficient [-]')
    ax1.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax1.grid(True)

    # subplot 2
    ax2 = fig.add_subplot(gs[1,0])

    if calculate_mode:
        ax2.bar(np.arange(nr_of_bars)-barwidth/2, mean_AEV, barwidth, color='r', label = 'Mean')
        ax2.bar(np.arange(nr_of_bars)+barwidth/2, mode_AEV, barwidth, color='g', label = 'Mode')

    else:
        ax2.bar(np.arange(nr_of_bars), mean_AEV, barwidth, color='r', label = 'Mean')

    ax2.set_title('Alternative Extrema')
    ax2.set_ylabel('Pressure coefficient [-]')
    ax2.set_xlabel('Tap Label')
    ax2.set_xticks(np.arange(nr_of_bars), custom_tick_labels)
    ax2.grid(True)
    ax2.legend()

    #fig.tight_layout()

    # resizing the internal rectangle so that the sup title is not overlayed
    # workaround for overlapping elements
    gs.tight_layout(fig, rect=cust_rect)

    report_pdf.savefig()

    # plot window needs to be closed to avoid error and memory problem
    # due to too many opened
    plt.close()
