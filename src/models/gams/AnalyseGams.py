import pandas as pd
import numpy as np
import statistics
import pickle

F_GROUPS = ["Pro", "Pico", "Cocco", "Diazo", "Diatom", "Dino", "Zoo"]


def get_predictions(path, *prediction_sets):
    p_sets = []
    for predictons in prediction_sets:
        with open(f"{path}/{predictons}.pkl", "rb") as handle:
            predictons_set = pickle.load(handle)
        p_sets.append(predictons_set)
    return [p_sets[i] for i in range(len(p_sets))]


def get_targets(path, *darwin_true_values):
    darwin_targets = []
    for target in darwin_true_values:
        with open(f"{path}/{target}.pkl", "rb") as handle:
            target_set = pickle.load(handle)
        darwin_targets.append(target_set)
    return [darwin_targets[i] for i in range(len(darwin_targets))]


def pres_abs_summary(gams, darwin, cutoff):
    gams_present, darwin_present, total = [], [], len(darwin["Pro"])
    gams_absent, darwin_absent, either_below_cutoff = [], [], []
    for group in F_GROUPS:
        gams_present.append(
            gams[group][(gams[group] >= cutoff) & (darwin[group] >= cutoff)]
        )
        darwin_present.append(
            darwin[group][(darwin[group] >= cutoff) & (gams[group] >= cutoff)]
        )
        gams_absent.append(gams[group][(gams[group] < cutoff)])
        darwin_absent.append(darwin[group][(darwin[group] < cutoff)])

    [
        either_below_cutoff.append(total - len(gams_present[i]))
        for i in range(len(F_GROUPS))
    ]

    pres_abs_summary = cutoff_summary(
        gams_absent, darwin_absent, either_below_cutoff, total
    )
    return gams_present, darwin_present, pres_abs_summary


def cutoff_summary(gams_abs, darwin_abs, either_below, total):
    cutoff_summary = pd.DataFrame(
        {"Darwin < cutoff": [0], "GAMs < cutoff": [0], "Either < cutoff": [0]},
        index=F_GROUPS,
    )
    for i in range(len(F_GROUPS)):
        cutoff_summary["Darwin < cutoff"][i] = len(darwin_abs[i])
        cutoff_summary["GAMs < cutoff"][i] = len(gams_abs[i])
        cutoff_summary["Either < cutoff"][i] = either_below[i]

    cutoff_summary["Presence Fraction"] = 1 - (
        round(cutoff_summary["Either < cutoff"] / (total), 2)
    )
    return cutoff_summary


def mean_and_median(predictions):
    mean_arr, med_arr = [], []
    for f_group in predictions:
        mean_arr.append(np.mean(f_group))
        med_arr.append(np.median(f_group))
    return mean_arr, med_arr


def calc_ratios(mean_gams, med_gams, mean_darwin, med_darwin):
    mean_ratios, med_ratios = [], []
    for i in range(len(med_gams)):
        mean_r = round((mean_gams[i] - mean_darwin[i]) / mean_darwin[i], 2)
        med_r = round((med_gams[i] - med_darwin[i]) / med_darwin[i], 2)
        mean_ratios.append(mean_r)
        med_ratios.append(med_r)
    return mean_ratios, med_ratios


def r_squared(darwin_target, gams_predictions):
    rsq = []
    for i in range(len(darwin_target)):
        rsq.append(calc_rsq(darwin_target[i], gams_predictions[i]))
    return rsq


def calc_rsq(darwin, predictions):
    residuals = calc_residuals(darwin, predictions)
    data_var = calc_variance(darwin)
    residuals_var = calc_variance(residuals)
    return 1 - (residuals_var) / (data_var)


def calc_residuals(darwin, predictions):
    return darwin - predictions


def calc_variance(data):
    sq_diff = (data - data.mean()) ** 2
    return sq_diff.mean()


def return_summary(cutoffs_df, means_ratios, meds_ratios, rsq, total):
    cols = ["Darwin < cutoff", "GAMs < cutoff"]
    summary_df = round((cutoffs_df[cols] / total), 2)
    summary_df["Both > cutoff"] = round(1 - (cutoffs_df["Either < cutoff"] / total), 2)
    summary_df["Means Ratios"] = means_ratios
    summary_df["Medians Ratios"] = meds_ratios
    summary_df["r-squared"] = [round(r, 2) for r in rsq]
    return summary_df


def return_combined_df(dfs):
    return pd.concat(
        [df.rename(columns=lambda x: x.zfill(4)) for df in dfs],
        keys=[
            "Obvs. (1987-2008)",
            "Rand. (1987-2008)",
            "Obvs. (2079-2100)",
            "Rand. (2079-2100)",
        ],
        axis=0,
    )
