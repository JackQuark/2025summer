#!/bin/bash
# author: Quark
# edit: 2025-07-13
# script for HSt42 long run experiment
# ==============================
# user settings
# output_dir="/home/Quark/Moist_Dycore/IdealizeSpetral/exp"
output_dir="/data92/Quark/LRFws"

L=20 # latent heat
suffix="_ws500d_gLRF" # e.g. "_quack" 
warmstart_file="/data92/Quark/ctrl_2000d/startfrom_475day_final.dat"

start_day=500
final_day=1500
space_day=25
# ============================== move to output directory
# output dir check
if [ -d "$output_dir" ]; then
    echo "Output directory $output_dir exists."
	cd $output_dir # script will work in the output directory

	exp_dir="$output_dir/HSt42_${L}$suffix"

	if [ -d "$exp_dir" ]; then
		echo "Warning: Output directory $exp_dir already exists."
        read -p "Overwrite existing output directory? [y/N]: " confirm
        confirm=${confirm,,} # convert to lowercase
        if [[ "$confirm" = "y" ]]; then 
			echo "Overwriting existing output directory."
			rm -rf "$exp_dir"
			mkdir "$exp_dir"
		else
            echo "Aborting to avoid overwrite."
            exit 1
        fi
    else
        mkdir "$exp_dir"
    fi
else
    echo "Output directory $output_dir does not exist."
    exit 1
fi
# ============================== move to exp directory
# init exp
cd $exp_dir
mkdir "data" # for .dat files
echo -n $space_day > "day_interval.txt"
echo -n $L > "Latent_heat.txt"
# check if init warmstart file 
if [ "$warmstart_file" != "None" ]; then 
	if [ -f "$warmstart_file" ]; then
		echo "Using warmstart file: $warmstart_file as init field"
		echo -n $warmstart_file > "firstday_file.txt"
	else
		echo "Warmstart file $warmstart_file does not exist."
		exit 1
	fi
else
	echo -n "None" > "firstday_file.txt"
fi

first_iter=1
# main loop
for i in `seq $start_day $space_day $final_day`; do	
	if [ $i -lt $final_day ]; then
		echo "Running from day $i to day $((i+space_day-1))"
		echo "Warmstart file: $(cat firstday_file.txt)"
		/home/Quark/julia-1.8.5/bin/julia /home/Quark/Moist_Dycore/IdealizeSpetral/exp/HSt42/Run_HS_Q.jl
		# move 'all' file to data
		# warmstart file will be left in the exp directory
		mv "all_L"$L".dat" "data/RH80_L"$L"_"$final_day"day_startfrom_"$i"day.dat"
		
		# change warmstart file to default after first run (final of previous run)
		if [ "$first_iter" -eq 1 ]; then
			first_iter=0
			echo -n "warmstart_${L}.dat" > "firstday_file.txt"
		fi

	elif [ $i -eq $final_day ]; then
		echo "All files have completed!!!"
	fi
done

# for test
# if [ -d "$exp_dir.bak" ]; then
#     echo "Removing existing $exp_dir.bak"
#     rm -rf "$exp_dir.bak"
# fi
# mv "$exp_dir" "$exp_dir.bak"