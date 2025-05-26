# Retrieve Project Parameters
# change top name, testbench name and FPGA-Board accordingly
if {[catch {current_project} result ]} {
puts "No project is open"
} else {
puts "$result is already open. It will be closed"
close_project
}
puts "The version of Vivado Design Suite is [version -short]"

#puts [llength $argv]
#foreach i $argv {puts $i}
set first_arg [lindex $argv 0]
set second_arg [lindex $argv 1]
set third_arg [lindex $argv 2]

set fourth_arg [lindex $argv 3]

puts $first_arg

#set extension "vhd"
#set first_arg [format %s.%s $first_arg_temp $extension]
#puts $first_arg
puts $second_arg

set inst_name_for_csv $second_arg

set version $third_arg

set parent_directory [ pwd]
set vhdl_directory_temp [ pwd]
set vhdl_directory "$vhdl_directory_temp/results/designs/$version/$second_arg"

#set check_path [exec pwd]
#puts "$check_path"

set TOP top    ; #top
set TB top_tb  ; #testbench
set PART xc7v585tffg1157-3; #FPGA-Board

# Exploration Parameters
set time_const 7.0 ;    # Time Constraint
set ach_critical_path 20.0 ;   # Achieved Critical Path Delay
set delay_from_succ 30.0;   # critical path delay from sucessfull run
set LUTs 0 ;    # LUT amount
set p 0.0 ;     # power in µwatt
set slack 8.0 ; # current slack
set tmptlog 0 ; # temp logic delay
set tlog 0 ;    # logic delay from sucessfull run
set tmptsig 0 ; # temp signal delay
set tsig 0 ;    # signal delay from sucessfull run
set run 2 ;    # maximum number of runs
set aggressive 0 ; # aggressive optimization using post_place_opt flag, only true or false
set aggrs 0 ;   # save aggressive state

set output_files_location_temp [ pwd]
set output_files_location $output_files_location_temp/run_results/designs/$version/$second_arg
cd $output_files_location

create_project -part $PART -force Vivado_Project
cd $vhdl_directory
# read vhdl files, you have to change those!
read_vhdl -library xil_defaultlib {
  top.vhd
  top_tb.vhd
}

read_vhdl -library xil_defaultlib $first_arg

cd $output_files_location
#cd ./../../../run_results/designs/$second_arg
#set output_files_location [ pwd]

#cd ./../implementation
update_compile_order -fileset sources_1
# set project properties for the top file and testbench
set_property USED_IN_SYNTHESIS 0 [get_files $TB.vhd]
set_property top $TOP [current_fileset]
set_property top_file $TOP.vhd [current_fileset]

# -----------------------------------------------------------------------------
# Run Synthesis with 4 threads
synth_design -top $TOP -part $PART

# -----------------------------------------------------------------------------

# create empty output textfile
set outfile [open RESULT_$inst_name_for_csv.txt w]
puts $outfile "Implementation results for $fourth_arg $inst_name_for_csv adder"
puts $outfile "The version of Vivado Design Suite is [version -short]"
puts $outfile "-------------------------------------------------------------"
close $outfile

# while loop, updating Clock
# stop when the difference of positive slack and time to test is less than 1%
while {$run != 0} {
  set error_message "Slack values matched."
  # create new clock each run
  create_clock -period $time_const -name clock -add [get_ports -filter {NAME =~  "*clk*" && DIRECTION == "IN" }]

  # -----------------------------------------------------------------------------
  # Place & Route
  if { $aggressive == 1} {
    place_design -post_place_opt
    phys_opt_design
    route_design
  } else {
    opt_design -directive Explore
    place_design -directive Explore
    phys_opt_design -directive Explore
    route_design -directive Explore
  }

  # -----------------------------------------------------------------------------
  # Report timing

  report_drc
  #report_timing -setup -hold -max_paths 32 -nworst 3 -input_pins -sort_by group -file  $TOP.twr
  report_timing -setup -hold -max_paths 32 -input_pins -sort_by group -file  $TOP.twr
  #report_timing_summary -delay_type min_max -path_type full_clock_expanded -report_unconstrained -check_timing_verbose -max_paths 3 -nworst 3 -significant_digits 3 -input_pins -file $TOP.twr
  report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 32 -input_pins -file $TOP.twr

  # -----------------------------------------------------------------------------
  # find maximum Data Path Delay and Slack
  
  ############### the following four lines can be deleted. It is for debugging only
  set twr_directory [ pwd]
  set outfile [open RESULT_$inst_name_for_csv.txt a]
  puts $outfile "TWR values read from: $twr_directory"
  close $outfile
  ############################################
  
  set f [open $TOP.twr r]
  set file_data [read $f]
  close $f
  if {[regexp { +Data Path Delay: +(\d+\.\d+)} $file_data -> value]} {
    set ach_critical_path $value
  }
  if {[regexp { +Data Path Delay: +\d+\.\d+[ns]+ +[(]+logic +(\d+\.\d+)} $file_data -> value]} {
    set tmptlog $value
  }
  if {[regexp { +Data Path Delay: +\d+\.\d+[ns]+ +[(]+logic +\d+\.\d+[ns]+ +[(]+\d+\.\d+[%)]+ +route +(\d+\.\d+)} $file_data -> value]} {
    set tmptsig $value
  }
  # Registered version
  if {[regexp {clock +([-]?\d+\.\d+) +} $file_data -> slack]} {
    puts ------------
    puts $slack
    puts $time_const
    puts ------------
  }

set slack_test_setup [get_property SLACK [get_timing_paths]]
set slack_test_hold [get_property SLACK [get_timing_paths -hold]]
set pw_test [report_pulse_width -all_violators]
# Default value of error message


  # -----------------------------------------------------------------------------
  # check if timing is met

  # save constraint for later printing
  set ttmp $time_const
  set run [expr { $run -1}]

# if slack value does not match. End iterations.
  if {$slack_test_setup != $slack } {
#    set run 0

    set error_message "Slack value does not match."
    puts " ***** slack values does not match "
  }
  if {$slack_test_setup < 0 || $slack_test_hold < 0 || $pw_test != ""} {
    # Timing constraints didn't pass.

    if {$slack_test_setup < 0 } {
      puts " slack_test_setup < 0 ****"
    set ttn [expr { $time_const - $slack }]
  } elseif {$slack_test_hold < 0 } {
  set ttn [expr { $time_const - $slack_test_hold }]
  puts " slack_test_hold < 0 ****"
  } elseif {$pw_test != ""} {
      set pw_test "pulse width problem"
      puts "******* pulse width problem *****"
      set ttn [expr { $time_const + 1 }]
      }
    set time_const $ttn
  } elseif { $slack >= 0.1 } {
    #sucessfull run
    if { $ach_critical_path < $delay_from_succ } {
      #new critical path delay is smaller than from previous, save the values
      puts "achieved critical path delay salim: $ach_critical_path"
      set aggrs $aggressive
      set aggressive 0
      set ts $time_const
      set delay_from_succ $ach_critical_path
      set tlog $tmptlog
      set tsig $tmptsig
# find new clock.
      set ttn [expr { $time_const - $slack}]
      set time_const $ttn
    } else {

      #new critical path delay is larger than previous succesful run delay_from_succ. Do not modify delay_from_succ.
      #since slack is still large enough just start a new run

      set ttn [expr { $time_const - $slack}]
      set time_const $ttn
    }


  } elseif { $slack >= 0 && $slack < 0.1 } {
    #still a sucessful run but slack is very small
    if { $ach_critical_path < $delay_from_succ } {
      #new critical path delay is smaller than from previous, save the values, since the slack is already very small try aggressive optimization
      set aggrs $aggressive
      set aggressive 1
      set ts $time_const
      set delay_from_succ $ach_critical_path
      set tlog $tmptlog
      set tsig $tmptsig
      set ttn [expr { $time_const - $slack }]
      set time_const $ttn
    } elseif { $aggressive == 0 } {
      #new critical path delay is larger than previous succesful run delay_from_succ, since the slack is already very small try aggressive optimization
      set aggressive 1
    } else {
      #new critical path delay is larger than previous, aggressive optimization is already tried, stop here
      set run 0
    }
  } else {
    #unsucessfull run, slack is negative
    set ttn [expr { $time_const - $slack }]
    set time_const $ttn
  }

  # write the outputs of the actual run to save the progress
  set outfile [open RESULT_$inst_name_for_csv.txt a]
  puts $outfile "Constraint: $ttmp,   Total Current Delay: $ach_critical_path,   Logic Delay: $tmptlog,   Signal Delay: $tmptsig,   Slack_hendrik: $slack,  Slack_setup: $slack_test_setup   Iteration: $run,   Aggressive: $aggressive,    Pulse_width: $pw_test,  Slack_hold: $slack_test_hold,   Message: $error_message, slack_test_setup: $slack_test_setup, slack: $slack"
  close $outfile
}
# end of while loop
############ Error message for checking slack values
#set outfile [open RESULT.txt a]
#puts $outfile "$error_message"
#close $outfile
###############################################
# create new clock each run
create_clock -period $ts -name clock -add [get_ports -filter {NAME =~  "*clk*" && DIRECTION == "IN" }]

# -----------------------------------------------------------------------------
# Place & Route
if { $aggrs == 1} {
  place_design -post_place_opt
  phys_opt_design
  route_design
} else {
  opt_design -directive Explore
  place_design -directive Explore
  phys_opt_design -directive Explore
  route_design -directive Explore
}

# -----------------------------------------------------------------------------
# substitute the delay time of the testbench with the fastest result

set f [open $vhdl_directory/$TB.vhd r+]
set file_data [read $f]
set newf [open $vhdl_directory/test.vhd w]

#regsub -all {clock <= clock xor running after \d+\.*\d* ns;} $file_data "clock <= clock xor running after $delay_from_succ ns;" chg
###### wait time and result file location is automated.
regsub -all {constant clk_period : time := \d+\.*\d* ns;} $file_data "constant clk_period : time := $delay_from_succ ns;" chg
puts $newf $chg
close $f
close $newf
file rename -force $vhdl_directory/test.vhd $vhdl_directory/top_tb.vhd

set f [open $vhdl_directory/$TB.vhd r+]
set file_data [read $f]
set newf [open $vhdl_directory/test.vhd w]
set file_data_tmp [regsub -all {total_clocks_(\S+).txt} $file_data $output_files_location/total_clocks_$inst_name_for_csv.txt]
set inst_name_for_csv_updated "${inst_name_for_csv}_${version}"
set file_data_tmp1 [regsub -all {add_results_(\S+).csv} $file_data_tmp $output_files_location/add_results_$inst_name_for_csv_updated.csv]
set file_data_tmp2 [regsub -all {tb_in_a0.txt} $file_data_tmp1 $output_files_location/data_$fourth_arg/tb_in_a0.txt]
set file_data_tmp3 [regsub -all {tb_in_b0.txt} $file_data_tmp2 $output_files_location/data_$fourth_arg/tb_in_b0.txt]


puts $newf $file_data_tmp3
close $f
close $newf
file rename -force $vhdl_directory/test.vhd $vhdl_directory/top_tb.vhd


# set testbench top
set_property top $TB [get_filesets sim_1]

# set saif and testbench settings, your top in the testbench must be instantiated as DUT
set_property -name {xsim.simulate.runtime} -value {-all} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.saif_scope} -value {DUT} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.saif} -value {power.saif} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.saif_all_signals} -value {true} -objects [get_filesets sim_1]

# set power report unit
set_units -power uW

# write netlist
write_vhdl -force -mode funcsim $TOP\_netlist.vhd

# prepare testbench input files

  set i 0
  set f [open $vhdl_directory/$TB.vhd r+]
  set file_data [read $f]
  set newf [open $vhdl_directory/$TB.$i w]
  regsub -all "tb_in_a[0-9]" $file_data tb_in_a$i chgA
  regsub -all "tb_in_b[0-9]" $chgA tb_in_b$i chgB
# multiple result files are generated

  puts $newf $chgB
  close $f
  close $newf
  file rename -force $vhdl_directory/$TB.$i $vhdl_directory/$TB.vhd

  # start simulation
  launch_simulation -simset sim_1 -mode post-implementation -type functional

  close_sim

  # report utilization
  report_utilization -hierarchical

  # report power with saif file
  read_saif Vivado_Project.sim/sim_1/impl/func/xsim/power.saif
  report_power -file power_$inst_name_for_csv.pwr -hier all

  # -----------------------------------------------------------------------------
  # Use mutliple simulations for averaging
  
  ############### the following four lines can be deleted. It is for debugging only
  set pwr_directory [ pwd]
  set outfile [open RESULT_$inst_name_for_csv.txt a]
  puts $outfile "Power values read from: $pwr_directory"
  close $outfile
######################################################
  set v [open power_$inst_name_for_csv.pwr r]
  set file_data [read $v]
  close $v
  if {[regexp -all {\| +add +\| +\d+\.\d+ +\| +\d+ +\| +\d+\.\d+ +\| +\d+ +\| +\d+.\d+ +\| +\d+ +\| +(\d+\.\d+)} $file_data -> power]} {
     set sp$i $power
  } else {
    set sp$i 0
  }
  if {[regexp -all {\| +add +\| +\d+\.\d+ +\| +\d+ +\| +\d+\.\d+ +\| +\d+ +\| +\d+.\d+ +\| +\d+ +\| +\d+.\d+ +\| +\d+ +\| +(\d+\.\d+)} $file_data -> power]} {
     set lp$i $power
  } else {
    set lp$i 0
  }

  if {[regexp -all {\| +top +\| +\d+\.\d+ +\| +\d+ +\| +\d+\.\d+ +\| +\d+ +\| +\d+.\d+ +\| +\d+ +\| +(\d+\.\d+)} $file_data -> power]} {
     set sp_top$i $power
  } else {
    set sp_top$i 0
  }
  if {[regexp -all {\| +top +\| +\d+\.\d+ +\| +\d+ +\| +\d+\.\d+ +\| +\d+ +\| +\d+.\d+ +\| +\d+ +\| +\d+.\d+ +\| +\d+ +\| +(\d+\.\d+)} $file_data -> power]} {
     set lp_top$i $power
  } else {
    set lp_top$i 0
  }


close_project

# extract LUT and Carry Chain count together with the power consumption of the module
# and write it all back including succesful timing in a file named RESULT
set v [open power_$inst_name_for_csv.pwr r]
set file_data [read $v]
close $v
if {[regexp -all {\| +LUT as Logic +\| +\d+\.\d+ +\| +(\d+)} $file_data -> LUTsize]} {
  set LUTs $LUTsize
} else {
  set LUTs 0
}
if {[regexp -all {\| +CARRY4 +\| +\d+\.\d+ +\| +(\d+)} $file_data -> CARRYsize]} {
  set CCs $CARRYsize
} else {
  set CCs 0
}

if {[regexp -all {\| +Overall confidence level +\| +([A-Z]+[a-z]+)} $file_data -> confidence]} {
   set con $confidence
} else {
  set con 0
}
set total_power [ expr { $sp0 + $lp0 }]
set total_power_top [ expr { $sp_top0 + $lp_top0 }]
set outfile [open $parent_directory/results/performance/$version/$second_arg/RESULT_$version.csv w]

puts $outfile "$inst_name_for_csv, $ts, $delay_from_succ, $tlog, $tsig, $LUTs, $CCs, $sp0, $lp0, $total_power, $sp_top0, $lp_top0, $total_power_top, $con"

close $outfile
