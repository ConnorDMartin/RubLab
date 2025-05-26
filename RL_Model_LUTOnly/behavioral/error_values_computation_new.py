from argparse import ArgumentParser
import sys
import numpy as np
from itertools import combinations
import os
import pandas as pd
from pathlib import Path


def error_compute(degree, coef_used, config, version):

	current_dir = Path(__file__).parent.absolute()
	os.chdir(str(current_dir))
	temp_location = './../run_results/designs/{}'.format(version)
	config_bin = format(int(config), '05b')

	if os.path.isfile('{}/{}/add_results_{}_{}.csv'.format(temp_location, config, config,version)) == False:
		file_status1 = open("./../results/summary/status_error_file.txt","a+")
		file_status1.write('\n {}_{}.'.format(config, version))
		file_status1.close()
		sys.exit(0)

	else:

		df = pd.read_csv('{}/{}/add_results_{}_{}.csv'.format(temp_location, config, config,version))
		# print(df)
		# df.drop(df.index[[0,1]],inplace=True)
		# df.reset_index(drop=True, inplace=True)
		# print(df)

		acc_result = df['acc'].values
		app_result = df['approx'].values


		df['error'] = acc_result - app_result # difference between accurate and approximate result

		average_error = np.sum(acc_result-app_result)/len(df.index) # average error of accurate and approximate results


		average_absolute_error = np.sum(np.absolute(acc_result-app_result))/len(df.index) # average error of accurate and approximate results

		acutal_max_error = np.max(acc_result-app_result)

		actual_min_error = np.min(acc_result-app_result)

		relative_error = np.zeros(acc_result.shape)

		counter = 0 # to count number of rows with accurate answer not equal to zero
		counter_prob_approx = 0 # to find error probability of approximate result

		for i in range(len(acc_result)):
			if acc_result[i] != 0:

				relative_error[i] = (acc_result[i] - app_result[i])/acc_result[i]
				counter = counter + 1



		for i in range(len(acc_result)):
			if acc_result[i] != app_result[i]:
				counter_prob_approx = counter_prob_approx + 1


		error_prob_approx = (counter_prob_approx/len(acc_result))*100

		average_relative_error = np.sum(relative_error)/counter
		average_absolute_relative_error = np.sum(np.absolute(relative_error))/counter

		if os.path.isfile('./../results/summary/error_values_{}.csv'.format(version)) == False:
			data_to_store = [[config, average_error, average_absolute_error, average_relative_error,	average_absolute_relative_error,
			acutal_max_error, actual_min_error, error_prob_approx]]
			header = ['config', 'average_error', 'average_absolute_error', 'average_relative_error', 'average_absolute_relative_error',
			'acutal_max_error', 'actual_min_error', 'error_prob_approx']
			error_df = pd.DataFrame(data_to_store, columns=header)
			error_df.to_csv('./../results/summary/error_values_{}.csv'.format(version), index=False, na_rep=" ")

		else:

			error_df = pd.read_csv('./../results/summary/error_values_{}.csv'.format(version))
			total_records = len(error_df.index)
			error_df.loc[total_records] = [config, average_error, average_absolute_error, average_relative_error,
			average_absolute_relative_error, acutal_max_error, actual_min_error, error_prob_approx]
			error_df.to_csv('./../results/summary/error_values_{}.csv'.format(version), index=False, na_rep=" ")


def main():
	parser = ArgumentParser(description='Computes the approximate result using linear regression models')

	parser.add_argument("-f", type = str, help="provide csv file name ")
	parser.add_argument("-d", type = int, help="provide degree of the regression model ")
	parser.add_argument("-p", type = int, help="provide number of used coefficients ")
	parser.add_argument("-v", type = str, help="provide version ")
	args = parser.parse_args()


##Extract operands

	file_name_from_shell = args.f
	degree = args.d
	coef_used = args.p
	version = args.v
	# print('file name from shell: ', file_name_from_shell)

	error_compute(degree, coef_used, file_name_from_shell, version)

if __name__ == '__main__':
	main()
