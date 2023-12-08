# Generate command line iterator for a script
#  $1 script to be executed
#  $2 year to start
#  $3 month to start
#  $4 first day
#  $5 last day

# Example:
# $. make_script_iterator.sh offgridtech_195W_victron.sh 2023 12 10 17

echo "#Pipe into 'bash' to generate command lines"
echo "seq $4 $5 | $(echo "awk '{print \".\", \"$1\", strftime(\"%Y-%m-%d\",mktime(\"$2 $3 \" \$1 \" 00 00 00\"))}'")"
