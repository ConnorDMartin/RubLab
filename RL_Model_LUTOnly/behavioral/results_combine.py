import pandas as pd

hw_df = pd.read_csv('./../results/summary/performance_results.csv')
error_df = pd.read_csv('./../results/summary/error_report.csv')
new_df = hw_df.merge(error_df[["Design","Error_Prob", "Average_abs_error", "Average_error", "Average_relative_error", "Average_absolute_relative_error"]], on="Design", how="left")
print(new_df)

new_df.to_csv('./../results/summary/results_combined_4.csv', index=False, na_rep=" ")
