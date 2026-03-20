import numpy as np
import pandas as pd
from scipy.stats import norm
import yaml
import sys
import os

config = yaml.safe_load(open(sys.argv[1]))

outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

OR = config["odds_ratio"]
p0 = config["p_control"]
alpha = config["alpha"]
n_cases_base = config["n_cases_base"]
n_total_fixed = config["n_total_fixed"]
max_ratio = config["max_ratio"]
n_points = config["n_points"]

zcrit = norm.ppf(1 - alpha / 2)

def p_case(OR, p0):
    return (OR * p0) / (1 - p0 + OR * p0)

def var_log_or(n1, n0):
    p1 = p_case(OR, p0)
    return (
        1 / (n1 * p1) +
        1 / (n1 * (1 - p1)) +
        1 / (n0 * p0) +
        1 / (n0 * (1 - p0))
    )

def power(n1, n0):
    v = var_log_or(n1, n0)
    z = np.log(OR) / np.sqrt(v)
    return norm.cdf(z - zcrit) + norm.cdf(-z - zcrit)

def ci_width(n1, n0):
    v = var_log_or(n1, n0)
    return 2 * zcrit * np.sqrt(v)

ratios = np.linspace(1, max_ratio, n_points)

def build_df(n1_func, n0_func):
    rows = []
    for r in ratios:
        n1 = n1_func(r)
        n0 = n0_func(r)
        rows.append({
            "ratio": r,
            "power": power(n1, n0),
            "ci_width": ci_width(n1, n0)
        })
    return pd.DataFrame(rows)

# Generate datasets
df_controls = build_df(
    lambda r: n_cases_base,
    lambda r: n_cases_base * r
)

df_balanced = build_df(
    lambda r: n_cases_base * r,
    lambda r: n_cases_base * r
)

df_fixedN = build_df(
    lambda r: n_total_fixed / (1 + r),
    lambda r: n_total_fixed * r / (1 + r)
)

# Write CSVs
df_controls.to_csv(f"{outdir}/power_controls.csv", index=False)
df_balanced.to_csv(f"{outdir}/power_balanced.csv", index=False)
df_fixedN.to_csv(f"{outdir}/power_fixedN.csv", index=False)
