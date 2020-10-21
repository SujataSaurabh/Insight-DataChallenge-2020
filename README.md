# Approach
1. We read the csv file in memory.
2. Aggregated data by CBSA column. We created the a python module to read the csv file and store in DataTable.
3. DataTable is a custom class similar to DataFrame
in pandas library. This class allows reuse of groupby logic to perform the mathematical operations.
4. Ran the program on small input dataset to match with provided results.
5. Ran it on the full dataset which was downloaded from the census.gov website.
6. Adapted code to handle missing values for CBSA.

# Run instructions
Use command line to run this program.

cmd>`./run.sh`