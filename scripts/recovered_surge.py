"""Recovered MLP surge definitions, copied without algorithm changes.

Only the class and pure function are retained; no production entrypoint runs.
Source: ML4PDevLab/MLP-data-intro at fea13989b8ee6803d1ed82f091097730ae04f727
License: MIT, Copyright (c) 2025 Machine Learning for Peace.
Full notice: ../licenses/MLP-data-intro-MIT.txt
"""

import math
import numpy as np
from scipy.stats import boxcox, zscore
from scipy.stats.mstats import winsorize

class PeakDetector:
    def __init__(self, lookaround, std_dev, normalize, alpha, beta):
        self.lookaround = lookaround
        self.std_dev = std_dev
        self.normalise = normalize
        self.alpha = alpha
        self.beta = beta
        
    @staticmethod
    def equalize_lists(lst1, lst2):
        len1, len2 = len(lst1), len(lst2)
        difference = abs(len1 - len2)
        if len1 < len2:
            lst1 = np.concatenate((lst1, [0] * difference))
        elif len2 < len1:
            lst2 = np.concatenate((lst2, [0] * difference))
        return lst1, lst2

    @staticmethod
    def apply_transformation(values, method, limits=0.05):
        if method == 'log':
            return [np.log(v) if v > 0 else 0 for v in values]
        elif method == 'boxcox':
            return boxcox(values)[0]
        elif method == 'sqrt':
            return [np.sqrt(v) if v >= 0 else -np.sqrt(-v) for v in values]
        elif method == 'winsorize':
            if limits == 0:
                return values
            return winsorize(values, limits=limits)
        return values

    def peakiness(self, left, post_value, right, pre_value):
        w_left = [math.exp(-j * self.beta) for j in range(1, 13)]
        w_right = [1 - self.alpha * j for j in range(1, 13)]
        w_left = [w / sum(w_left) for w in w_left]
        w_right = [w / sum(w_right) for w in w_right]

        left, weights_left = self.equalize_lists(left, w_left)
        right, weights_right = self.equalize_lists(right, w_right)

        left_mean = np.dot(weights_left, left)
        right_mean = np.dot(weights_right, right)
        left_std = math.sqrt(np.dot(weights_left, (left - left_mean) ** 2))
        right_std = math.sqrt(np.dot(weights_right, (right - right_mean) ** 2))

        left_score = (pre_value - left_mean) / left_std if left_std != 0 else 0
        right_score = (pre_value - right_mean) / right_std if right_std != 0 else 0

        return left_score, right_score

    def peakiness_conservative(self, left, post_value, right, pre_value):
        # right, weights = self.equalize_lists(right, weights)

        w_left = [round(math.exp(-j * self.beta),2) for j in range(1,13)]
        w_right = [round(1-self.alpha*j,2) for j in range(1,13)]
        w_left_sum = sum(w_left)
        w_left = [weight/w_left_sum for weight in w_left]
        w_right_sum = sum(w_right)
        w_right = [weight/w_right_sum for weight in w_right]
        left, weights_left = self.equalize_lists(left, w_left)
        right, weights_right = self.equalize_lists(right, w_right)
        reverse_weights = list(reversed(weights_left))

        result_left = [(a * ((post_value - b) ** 2)) for a, b in zip(reverse_weights, left)]
        left_weighted_std_squared = np.sum(result_left) if  len(left) > 0 else 0
        left_weighted_std = left_weighted_std_squared ** 0.5

        result_right = [(a * ((post_value - b) ** 2)) for a, b in zip(weights_right, right)]
        right_weighted_std_squared = np.sum(result_right) if len(right)>0 else 0
        right_weighted_std = right_weighted_std_squared ** 0.5

        left_mean_list = [a * b for a, b in zip(reverse_weights, left)]
        left_mean = np.sum(left_mean_list) if  len(left) > 0 else 0

        right_mean_list = [a * b for a, b in zip(weights_right, right)]
        right_mean = np.sum(right_mean_list) if  len(right) > 0 else 0

        left_total = (left_weighted_std * self.std_dev) + left_mean
        right_total = (right_weighted_std * self.std_dev) + right_mean

        average_total = (left_total + right_total) / 2

        return pre_value > max(left_total, right_total)

    def peak_detection(self, series):
        pre_values = series.tolist()
        z_scores = zscore(pre_values)
        num_outliers = np.sum(np.abs(z_scores) > 2)

        winsorizing_proportion = min(math.ceil(num_outliers / len(pre_values)), 0.1)
        
        
        method = ['none', 'winsorize', 'sqrt'][self.normalise]
        values = self.apply_transformation(series, method, winsorizing_proportion)

        peak_scores = [self.peakiness(values[max(0, i - self.lookaround): i],
                                      values[i],
                                      values[i + 1: i + self.lookaround + 1],
                                      pre_values[i]) for i in range(len(values))]
        return peak_scores


    def peak_detection_conservative(self, series):
        pre_values = series.tolist()
        z_scores = zscore(pre_values)
        num_outliers = np.sum(np.abs(z_scores) > 2)

        winsorizing_proportion = min(math.ceil(num_outliers / len(pre_values)), 0.1)
        method = ['none', 'winsorize', 'sqrt'][self.normalise]
        values = self.apply_transformation(series, method, winsorizing_proportion)

        peak_scores = [self.peakiness_conservative(values[max(0, i - self.lookaround): i],
                                      values[i],
                                      values[i + 1: i + self.lookaround + 1],
                                      pre_values[i]) for i in range(len(values))]
        return peak_scores
    
    
    def refine_peaks(Y, peaks):
        # Ensure top 3 spikes are always included
        top_three_peaks = np.argsort(-np.abs(Y[peaks]))[:3]
        peaks = np.union1d(peaks, top_three_peaks)

        # Label adjacent points
        new_peaks = []
        for peak in peaks:
            new_peaks.append(peak)
            if peak > 0 and Y[peak - 1] > Y[peak]:
                new_peaks.append(peak - 1)
            if peak < len(Y) - 1 and Y[peak + 1] > Y[peak]:
                new_peaks.append(peak + 1)

        # Remove duplicates
        new_peaks = np.unique(new_peaks)

        # Remove peaks if both neighbors are larger
        final_peaks = []
        for peak in new_peaks:
            if (peak > 0 and Y[peak - 1] > Y[peak]) and (peak < len(Y) - 1 and Y[peak + 1] > Y[peak]):
                continue
            final_peaks.append(peak)

        return np.array(final_peaks)

def convert_to_training_data_2(Y, country, event, peak_detector, loaded_model=None):
    X_values = peak_detector.peak_detection(Y)
    X_values = np.nan_to_num(np.array(X_values))
    X_values = X_values.reshape(-1, 2)

    if loaded_model is None:
        binary_predictions_NN = [0] * len(X_values)
    else:
        predictions = loaded_model.predict(X_values)
        predictions = predictions['dense_5']
        binary_predictions_NN = (predictions > 0.5).astype(int)
        binary_predictions_NN = [item for sublist in binary_predictions_NN for item in sublist]

    binary_predictions_algorithm = peak_detector.peak_detection_conservative(Y)
    binary_predictions_algorithm = [int(v) for v in binary_predictions_algorithm]

    # OR of NN + conservative algorithm
    new_list = [1 if x or y else 0 for x, y in zip(binary_predictions_NN, binary_predictions_algorithm)]

    # force top-3 magnitude spikes on
    top_3_indices = sorted(range(len(Y)), key=lambda i: abs(Y[i]), reverse=True)[:3]
    for idx in top_3_indices:
        new_list[idx] = 1

    # neighborhood cleanup: drop pits & allow neighbor switch
    for i in range(1, len(Y) - 1):
        if new_list[i] == 1:
            left = Y[i-1] if i > 0 else float('-inf')
            right = Y[i+1] if i < len(Y) - 1 else float('-inf')
            if left > Y[i] and right > Y[i]:
                new_list[i] = 0
            else:
                if left > Y[i]:
                    new_list[i-1] = 1
                if right > Y[i]:
                    new_list[i+1] = 1

    return X_values, binary_predictions_algorithm, new_list
