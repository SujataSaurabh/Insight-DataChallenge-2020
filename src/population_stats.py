#!/usr/bin/env python3
# population_stats.py
# Author: Sujata Goswami
"""Program to generate report on population stats from census data.

This module generates report containing population stats grouped by CBSA data.
Example input data: http://www2.census.gov/programs-surveys/decennial/tables/time-series/tract-change-00-10/censustract-00-10.xlsx
Source of data layout: https://www2.census.gov/programs-surveys/metro-micro/technical-documentation/file-layout/tract-change-00-10/censustract-00-10-layout.doc

    Typical usage example:
        Provide following command line args:
            first arg: Input filepath
            second arg: Output filepath
        cmd> python3.7 population_stats.py path/to/input.csv path/to/output.csv
"""
import sys
import csv
import bears as br

_MISSING_CBSA_PLACEHOLDER_VALUE = -1
_CBSA09_COL_NAME = 'CBSA09'
_CBSA_TITLE_COL_NAME = 'CBSA_T'
_TRACT_COL_NAME = 'GEOID'
_POPULATION_2000_COL_NAME = 'POP00'
_POPULATION_2010_COL_NAME = 'POP10'
_POP_CHANGE_PERCENT_COL_NAME = 'POP_CHANGE_PERCENT'

def _get_avg_population_change_by_cbsa(data_table: br.DataTable) -> dict:
    """Calculates population percent change from 2000 to 2010 from census data.

    Calculates population percent change from 2000 to 2010 given the census data
    in the form of a DataTable, stores it within the DataTable as a separate
    column, and calculates the average grouped by cbsa, and return it as
    dictionary. The population change percentage is float rounded to 2-digits.

    Args:
        data_table: An br.DataTable instance containing census data. Columns
            containing population data must be int type.

    Returns:
        A dict mapping cbsa to the average population change percentage. For
        example:

        {28540: -4.41,
         46900: -10.25}

        Returned values are of type float, rounded up to to 2 decimal points.
    """
    population_2000 = data_table[_POPULATION_2000_COL_NAME]
    population_2010 = data_table[_POPULATION_2010_COL_NAME]
    population_percent_change = []
    for pop_2000, pop_2010 in zip(population_2000, population_2010):
        if pop_2000 == 0:
            population_percent_change.append(0)
            continue
        population_percent_change.append((pop_2010-pop_2000)*100/pop_2000)
    data_table[_POP_CHANGE_PERCENT_COL_NAME] = population_percent_change
    return data_table.avg(col_name=_POP_CHANGE_PERCENT_COL_NAME, group_by=_CBSA09_COL_NAME)

def _get_cbsa_title_by_cbsa(data_table: br.DataTable) -> dict:
    """Retrieves CBSA titles for each CBSA from census data.

    Retrieves the CBSA titles for each CBSA from the input census data by
    reading the CBSA ids and title columns from the DataTable, and then
    map the CBSA ids with titles, and stores them in a dictionary, and then
    return it.

    Args:
        data_table: An br.DataTable instance containing census data.

    Returns:
        A dict mapping CBSA id to the CBSA title. For example:

        {28540: "Ketchikan, AK",
         46900: "Vernon, TX"}
    """
    cbsa_ids = data_table[_CBSA09_COL_NAME]
    cbsa_titles = data_table[_CBSA_TITLE_COL_NAME]
    return {k: v for k, v in zip(cbsa_ids, cbsa_titles)}

def _read_data_table(in_file: str) -> br.DataTable:
    """Reads input csv file containing census data into a DataTable.

    Reads input csv file containing census data into instance of br.DataTable.
    It also converts the relevant columns (population, CBSA code, etc.) into int
    datatypes, to allow aggregation operations.
    Missing CBSA code will be replaced by placeholder value to allow conversion
    to int value, and to potentially exclude the rows.

    Args:
        in_file: Input file containing census data in csv format.

    Returns:
        An instance of br.DataTable representing data in input file.

    Raises:
        IOError: An error reading file.
    """
    data_table = br.read_csv(in_file)

    def cbsa_to_int(value: str) -> int:
        return _MISSING_CBSA_PLACEHOLDER_VALUE if value == '' else int(value)

    data_table.map(col_name=_CBSA09_COL_NAME, func=cbsa_to_int)
    data_table.map(col_name=_POPULATION_2000_COL_NAME, func=int)
    data_table.map(col_name=_POPULATION_2010_COL_NAME, func=int)
    return data_table

def _get_unique_sorted_cbsa(data_table: br.DataTable) -> list:
    """ Returns valid unique sorted CBSA values from input DataTable.

    Retrieves all CBSA values from the input data, finds out unique CBSA values,
    removes invalid values, and then sort them in increasing order in a list.

    Args:
        data_table: An instance of br.DataTable representing data.

    Returns:
        list of unique valid CBSA values sorted numerically.
    """
    cbsa_ids = data_table[_CBSA09_COL_NAME]
    unique_cbsa_ids = set(cbsa_ids)
    if _MISSING_CBSA_PLACEHOLDER_VALUE in unique_cbsa_ids:
        unique_cbsa_ids.remove(_MISSING_CBSA_PLACEHOLDER_VALUE)
    unique_cbsa_ids = list(unique_cbsa_ids)
    unique_cbsa_ids.sort()
    return unique_cbsa_ids

def generate_population_stats_report(in_file: str, out_file: str):
    """Generates report on population stats by reading census data.

    Computes population stats grouped by CBSA, by reading input census data file
    and persist them into an output report file.
    Output report file contains data in csv format, where each row contains
    following fields in order:
        - Core Based Statstical Area Code (i.e., CBSA09)
        - Core Based Statistical Area Code Title (i.e., CBSA_T)
        - total number of census tracts
        - total population in the CBSA in 2000
        - total population in the CBSA in 2010
        - average population percent change for census tracts in this CBSA.

    Args:
        in_file: Input file in csv format, containing census data.
        out_file: Report containing population stats, grouped by CBSA.
    """
    data_table = _read_data_table(in_file)

    sorted_cbsa_ids = _get_unique_sorted_cbsa(data_table)
    cbsa_title_by_cbsa = _get_cbsa_title_by_cbsa(data_table)
    census_tract_by_cbsa = data_table.count(group_by=_CBSA09_COL_NAME)
    population_2000_by_cbsa = data_table.sum(col_name=_POPULATION_2000_COL_NAME,
                                             group_by=_CBSA09_COL_NAME)
    population_2010_by_cbsa = data_table.sum(col_name=_POPULATION_2010_COL_NAME,
                                             group_by=_CBSA09_COL_NAME)
    avg_population_change_by_cbsa = _get_avg_population_change_by_cbsa(data_table)

    with open(out_file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        for cbsa_id in sorted_cbsa_ids:
            row = [cbsa_id,
                   cbsa_title_by_cbsa[cbsa_id],
                   census_tract_by_cbsa[cbsa_id],
                   population_2000_by_cbsa[cbsa_id],
                   population_2010_by_cbsa[cbsa_id],
                   round(avg_population_change_by_cbsa[cbsa_id], 2)
                  ]
            csvwriter.writerow(row)

if __name__ == '__main__':
    args_count = len(sys.argv) - 1
    if args_count != 2:
        raise ValueError("Expected two arguments first to specify input file,"
                         " and second to specify output file, but found {}: {}."
                         .format(args_count, sys.argv[1:])
                        )

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_population_stats_report(input_file, output_file)
    