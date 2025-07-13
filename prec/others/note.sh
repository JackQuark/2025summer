    # # return null globbing rather than origin pattern (from gpt :D
    # shopt -s nullglob
	# # check if there are existing HSt42_xx directories
    # hst_dirs=("$output_dir/HSt42_${L}"*)
    # if [ ${#hst_dirs[@]} -gt 0 ]; then
	# 	# todo: declare the target directory instead of using glob
	# 	# perhaps add user defined suffix after $L
    #     echo "Warning: Found existing directory matching HSt42_${L}*:"
    #     for dir in "${hst_dirs[@]}"; do
    #         echo " - $dir"
    #     done