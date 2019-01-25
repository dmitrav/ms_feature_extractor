
import numpy
from src.constants import allowed_ppm_error


def extract_mz_region(spectrum, mz_interval):
    """ Method extracts spectrum region based on m/z interval specified. """

    mz_values = []
    intensities = []

    for i in range(len(spectrum['m/z array'])):

        if mz_interval[0] <= spectrum['m/z array'][i] <= mz_interval[1]:
            mz_values.append(spectrum['m/z array'][i])
            intensities.append(spectrum['intensity array'][i])

        elif spectrum['m/z array'][i] > mz_interval[1]:
            break

    return numpy.array(mz_values), numpy.array(intensities)


def find_closest_centroids(mz_spectrum, centroids_indexes, expected_peaks_list):
    """ This method looks for all the expected peaks in the list of centroids. """

    # actual peaks out of expected ones
    actual_peaks = []

    for i in range(len(expected_peaks_list)):

        closest_peak_index, ppm = find_closest_peak_index(mz_spectrum, centroids_indexes, expected_peaks_list[i])

        if closest_peak_index < 0:
            another_peak = {'present': False, 'mz': None, 'ppm': None, 'index': None}
        else:
            another_peak = {'present': True,
                            'mz': mz_spectrum[closest_peak_index],
                            'ppm': ppm,
                            'index': closest_peak_index}

        actual_peaks.append(another_peak)

    return actual_peaks


def find_closest_peak_index(mz_spectrum, peaks_indexes, expected_peak_mz):
    """ This method finds the closest peak to the expected one within centroids list.
        If in the vicinity of allowed ppm there is no peak, the peak is considered to be missing. """

    closest_index = 0
    while mz_spectrum[peaks_indexes[closest_index]] < expected_peak_mz:
        closest_index += 1

    previous_peak_ppm = abs(mz_spectrum[peaks_indexes[closest_index-1]] - expected_peak_mz) / expected_peak_mz * 10 ** 6
    next_peak_ppm = abs(mz_spectrum[peaks_indexes[closest_index]] - expected_peak_mz) / expected_peak_mz * 10 ** 6

    if previous_peak_ppm <= next_peak_ppm and previous_peak_ppm <= allowed_ppm_error:
        return closest_index-1, previous_peak_ppm

    elif previous_peak_ppm > next_peak_ppm and next_peak_ppm <= allowed_ppm_error:
        return closest_index, next_peak_ppm

    else:
        return -1, None


def locate_annotated_peak(mz_region, spectrum):
    """ This method finds the accurate m/z and intensity values
    for visually chosen peaks and hardcoded m/z region for them. """

    local_max_intensity = -1

    for i in range(len(spectrum['m/z array'])):

        if mz_region[0] <= spectrum['m/z array'][i] <= mz_region[1]:

            if local_max_intensity <= spectrum['intensity array'][i]:
                local_max_intensity = spectrum['intensity array'][i]
            else:
                pass

        elif spectrum['m/z array'][i] > mz_region[1]:
            break

    if local_max_intensity < 0:
        raise ValueError

    accurate_intensity_value = local_max_intensity
    accurate_mz_value = spectrum['m/z array'][list(spectrum['intensity array']).index(local_max_intensity)]

    return accurate_mz_value, accurate_intensity_value


def get_peak_fitting_region(spectrum, index):
    """ This method extract the peak region (peak with tails) for a peak of the given index. """

    left_border = -1

    step = 0
    while left_border < 0:

        if spectrum['intensity array'][index-step-1] <= spectrum['intensity array'][index-step]:
            step += 1
        else:
            left_border = index-step

    right_border = -1

    step = 0
    while right_border < 0:

        if spectrum['intensity array'][index+step] >= spectrum['intensity array'][index+step+1]:
            step += 1
        else:
            right_border = index+step

    return [left_border, right_border]
