#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("rust_loc_results_with_summary.csv")
df = df[df['repo']!="TOTAL SUMMARY"]

# --- Histogram of eLOC per CFP ---
plt.hist(df['eLOC_per_CFP'].dropna(), bins=20, color='skyblue')
plt.title("Histogram: eLOC per CFP")
plt.xlabel("eLOC per CFP")
plt.ylabel("Frequency")
plt.savefig("hist_eloc_per_cfp.png")
plt.close()

# --- Scatter plot eLOC vs CFP ---
plt.scatter(df['CFP'], df['rust_code'], alpha=0.6)
plt.xlabel("CFP")
plt.ylabel("eLOC")
plt.title("eLOC vs CFP")
plt.savefig("scatter_eloc_vs_cfp.png")
plt.close()

# --- Boxplot ---
plt.boxplot(df['eLOC_per_CFP'].dropna())
plt.title("Boxplot of eLOC per CFP")
plt.savefig("box_by_type.png")
plt.close()
