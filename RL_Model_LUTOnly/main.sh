#!/bin/sh

##### Variables to set for specifying data size
size=8

current_dir=$PWD
cd $current_dir

## Uncomment if need to create directories
# . create_directories.sh   

numRunsInParallel=1
totalRunsCntr=0
runCntr=0

# INIT1=6666666688888888
# INIT2=666606608888F880
# INIT3=666606668888F880

python testbench.py


# version_array=("v1" "v2" "v3")
# version_array=("v1" "v2")
# current_version='v1'

# for element in "${version_array[@]}"; do
new_version="${element}"

# . update_version.sh $current_version $new_version #updates the Python files

declare -a temp_configs

#python ./behavioral/top.py &> ./run_results/behav_out.txt &
python ./behavioral/top_lut_new.py

source ./behavioral/testConfigs.sh

for config in ${arr_configs[@]}; do

   config=`echo $config | sed 's/\\r//g'` # to remove \r from string

   config=`echo $config | sed 's/ *$//g'` # remove spaces at the end
   config=`echo $config | sed 's/^ *//g'` # remove spaces at the front

  #  temp_configs+=" $config" # assign values to temp array

    echo "Configuration: $config"
    mult=adder_"${config}".vhd
    echo $mult


    mkdir -p ./results/performance/$new_version/$config
    mkdir -p ./results/behavioral/$new_version/$config
    mkdir -p ./run_results/designs/$new_version/$config
    mkdir -p ./results/designs/$new_version/$config

    yes | cp -rf ./top.vhd ./results/designs/$new_version/$config/
    yes | cp -rf ./top_tb.vhd ./results/designs/$new_version/$config/
    yes | cp -rf -r ./data_"${size}" ./run_results/designs/$new_version/$config/

    echo "Beginning Vivado Run"
    /tools/Xilinx/Vivado/2020.2/bin/vivado -mode batch -nojournal -nolog -source ./main_tcl.tcl -tclargs $mult $config $new_version $size  &> ./run_results/designs/$new_version/$config/out &
    echo "Vivado Run Ended"


    # runCntr=`expr ${runCntr} + 1`
    totalRunsCntr=`expr ${totalRunsCntr} + 1`
    echo "Total Runs: ${totalRunsCntr}"

    if [[ ( ${runCntr} = ${numRunsInParallel} ) ]]; then

      echo "Started all parallel runs"
      wait < <(jobs -p)
      runCntr=0

      echo "Comparison of generated results"
      for temp in ${temp_configs[@]}; do

      python ./behavioral/error_values_computation_new.py -f=$temp -p="4" -d="3" -v="$new_version"
 #     python ./behavioral/compare_output.py -c=$temp
      # python3 ./behavioral/csv_combine_from_shell.py -f=$temp -v="$new_version"
      python ./behavioral/results_combine.py -f=$temp -v="$new_version"

      rm -r ./run_results/designs/$new_version/$temp/data_"${size}"
      rm -r ./run_results/designs/$new_version/$temp/Vivado_Project.*
      done

      # unset temp_configs

      # declare -a temp_configs



    fi

done

wait < <(jobs -p)
echo "Comparison of generated results in outer loop"
# for temp in ${temp_configs[@]}; do
  python ./behavioral/error_values_computation_new.py -f=$temp -p="4" -d="3" -v="$new_version"
#  python ./behavioral/compare_output.py -c=$temp
  python ./behavioral/csv_combine_from_shell.py -f=$temp -v="$new_version"

  rm -r ./run_results/designs/$new_version/$temp/data_"${size}"
  rm -r ./run_results/designs/$new_version/$temp/Vivado_Project.*

# done

# unset temp_configs
# echo "declaring a new temp array"
# declare -a temp_configs

grep -rnw './run_results/' -e 'ERROR:' > failed_configs_"$new_version".txts

# current_version="${element}"
# done

# . update_version.sh $current_version 'v1' #updates the Python files
