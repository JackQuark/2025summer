#!/bin/bash
# author: Quark
# edit: 2025-07-13
# script for HSt42 long run
# ==============================
# user settings
output_dir="/home/Quark/Moist_Dycore/IdealizeSpetral/exp/HSt42"

L=20 # latent heat
suffix="" # e.g. "_quack" 
warmstart_file="None"

start_day=0
final_day=10
space_day=2
# ============================== move to output directory
# output dir check
if [ -d "$output_dir" ]; then
    echo "Output directory $output_dir exists."
	cd $output_dir

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

# main loop
for i in `seq $start_day $space_day $final_day`; do	
	if [ $i -lt $final_day ]; then
		echo "Running from day $i to day $((i+space_day-1))"
		echo "Warmstart file: $(cat firstday_file.txt)"
		/home/Quark/julia-1.8.5/bin/julia /home/Quark/Moist_Dycore/IdealizeSpetral/exp/HSt42/Run_HS.jl
		# move 'all' file to data
		# warmstart file will be left in the exp directory
		mv "all_L"$L".dat" "data/RH80_L"$L"_"$final_day"day_startfrom_"$i"day.dat"
		
		# change warmstart file to default after first run (final of previous run)
		if [ $i = 0 ]; then 
			echo "test"
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