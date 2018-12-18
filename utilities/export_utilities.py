def export_summary_to_text(pressure_taps, calculate_mode):

    result_summary = '# label position-x/y/z mean std kurtosis skewness min max cev_mean aev_mean'
    if calculate_mode:
        result_summary += ' cev_mode aev_mode'
    result_summary += '\n'

    for pressure_tap in pressure_taps:

        # identifier information
        result_summary += pressure_tap['label'] + ' '
        result_summary += '[' + ', '.join(map(str, [round(coordinate, 3)
                                                    for coordinate in pressure_tap['position']])) + '] '

        # general statistics
        result_summary += str(round(pressure_tap['statistics']
                                    ['cp']['general']['mean'], 3)) + ' '
        result_summary += str(round(pressure_tap['statistics']
                                    ['cp']['general']['std'], 3)) + ' '
        result_summary += str(round(pressure_tap['statistics']
                                    ['cp']['general']['kurtosis'], 3)) + ' '
        result_summary += str(round(pressure_tap['statistics']
                                    ['cp']['general']['skewness'], 3)) + ' '
        result_summary += str(round(pressure_tap['statistics']
                                    ['cp']['general']['min'], 3)) + ' '
        result_summary += str(round(pressure_tap['statistics']
                                    ['cp']['general']['max'], 3)) + ' '

        # extreme value statistics
        result_summary += str(round(pressure_tap['statistics']['cp']
                                    ['extreme_value']['classical']['statistics']['mean'], 3)) + ' '
        result_summary += str(round(pressure_tap['statistics']['cp']
                                    ['extreme_value']['alternative']['statistics']['mean'], 3)) + ' '

        if calculate_mode:
            result_summary += str(round(pressure_tap['statistics']['cp']
                                        ['extreme_value']['classical']['statistics']['mode'], 3)) + ' '
            result_summary += str(round(pressure_tap['statistics']['cp']
                                        ['extreme_value']['alternative']['statistics']['mode'], 3)) + ' '

        result_summary += '\n'

    return result_summary
