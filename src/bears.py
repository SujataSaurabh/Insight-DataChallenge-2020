""" Module provides datastructures for tabular data, and function for reading csv files.
"""
from collections import defaultdict
import csv
import numbers

class DataTable:
    """ Two-dimensional, potentially heterogeneous tabular data.

    Can be thought of as a dict-like container for List objects, where the key
    represents the column name and value is of type list, with each element in
    list holding data for each row for that column.

    Data representation:
        For example, for input tabular data:
        --------------
        A,B,C,D
        1,'x', 5.0, 3
        2,'y', 8.2, 4
        --------------
        can be represented as follows:
        {
            'A': [1, 2],
            'B': ['x', 'y'],
            'C': [5.0, 8.2],
            'D': [3, 4]
        }

    Attributes:
        data_table: A dictionary holding tabular data.
    """

    def __init__(self, data_table: dict):
        """ Creates an instance of Datatable..

        Given a dictionary, with keys as column names, and values as list with
        each element in list as row value for that column.

        Args:
            data_table: Dictionary containing data to be stored in this data table.
        """
        self.data_table = data_table

    def __getitem__(self, col_name: str) -> list:
        """ Gets column data as list for the input column name.

        Validates input column name to ensure it exists in the data and returns the
        corresponding row values as list.

        Args:
            col_name: Name of the column for which data values need to be returned.

        Returns:
            A list containing row values for the input column. For example:

            ['A', 'B', 'C']

        Raises:
            ValueError: If the column name does not exist in this DataTable.
        """
        self._validate_col_name(col_name)
        return self.data_table[col_name]

    def __setitem__(self, col_name: str, values: list):
        """ Sets column data given a column name and list with row values.

        Args:
            col_name: Name of the column for which data values need to be saved.
            values: Row values for the column.

        Returns:
        """
        self.data_table[col_name] = values

    def _validate_col_name(self, col_name: str):
        """ Validates input column name.

        Args:
            col_name: Name of the column to be validated.

        Raises:
            ValueError: If the column name does not exist in this DataTable.
        """
        if col_name not in self.data_table:
            raise ValueError("Invalid column name: {}, valid values are: {}"
                             .format(col_name, self.data_table.keys()))

    def count(self, group_by: str) -> dict:
        """ Counts the number of rows for each value in a given column.

        Args:
            group_by: Name of the column by which the rows must be grouped.

        Returns:
            A dict mapping group_by column value to the number of rows with it.
            example:

            {'A': 2, 'B': 3}

        Raises:
            ValueError: If the column name does not exist in this DataTable.
        """
        self._validate_col_name(group_by)
        result = defaultdict(int)
        group_by_values = self.data_table[group_by]
        for group_by_value in group_by_values:
            result[group_by_value] += 1
        return result

    def sum(self, col_name: str, group_by: str) -> dict:
        """ Calculates sum of values in a column, grouped by another column.

        Args:
            col_name: Name of the column for which values must be added.
            group_by: Name of the column by which the rows must be grouped.

        Returns:
            A dict mapping group_by column value to the sum of values from another column.
            example:

            {'A': 45, 'B': 36}

        Raises:
            ValueError: If the column name does not exist in this DataTable.
        """
        self._validate_col_name(col_name)
        self._validate_col_name(group_by)

        result = defaultdict(int)
        col_values = self.data_table[col_name]
        group_by_values = self.data_table[group_by]
        for col_value, group_by_value in zip(col_values, group_by_values):
            if not isinstance(col_value, numbers.Number):
                raise TypeError("Column data must be of numeric type, but found: {}."
                                .format(type(col_value))
                                )
            result[group_by_value] += col_value
        return result

    def avg(self, col_name: str, group_by: str) -> dict:
        """ Calculates average of values in a column, grouped by another column.

        Args:
            col_name: Name of the column for which values must be averaged.
            group_by: Name of the column by which the rows must be grouped.

        Returns:
            A dict mapping group_by column value to the average of values from another column.
            example:

            {'A': 45.3, 'B': 36.2}

        Raises:
            ValueError: If the column name does not exist in this DataTable.
        """
        self._validate_col_name(col_name)
        self._validate_col_name(group_by)

        sum = self.sum(col_name, group_by)
        count = self.count(group_by)
        return {k: sum[k]/count[k] for k in sum.keys()}

    def map(self, col_name: str, func):
        """ Maps each value in a given column with the mapping function.

        Args:
            col_name: Name of the column for which values must be added.
            func: Mapping function that takes one argument, and maps the intput
                row values.

        Raises:
            ValueError: If the column name does not exist in this DataTable.
        """
        self._validate_col_name(col_name)
        self.data_table[col_name] = [func(x) for x in self.data_table[col_name]]


def read_csv(filepath: str) -> DataTable:
    """ Reads input file in CSV format, with header in first line.

    Args:
        filepath: Input file path that should be read.

    Returns:
        An instance of DataTable containing data from the input file. For
        example, for input file:
        --------------
        A,B,C,D
        1,'x', 5.0, 3
        2,'y', 8.2, 4
        --------------
        will create instance of DataTable using following dict:
        {
            'A': ['1', '2'],
            'B': ['x', 'y'],
            'C': ['5.0', '8.2'],
            'D': ['3', '4']
        }
        The dictionary used for creating DataTable will contain all row values
        as str data-type.

    Raises:
        ValueError: If the column count is not consistent in all rows, including
            header.
    """
    col_names = {}
    data = {}
    row_num = 1
    with open(filepath, 'r') as file:
        for row_values in csv.reader(file):
            if row_num == 1:
                for idx, col_name in enumerate(row_values):
                    col_names[idx] = col_name
                    data[idx] = []
            else:
                if len(row_values) != len(col_names):
                    raise ValueError("Mismatch found in column count:{} and row values count:{}, row: {}."
                                     .format(len(col_names), len(row_values), row_values))
                for idx, col_value in enumerate(row_values):
                    data[idx].append(col_value)
            row_num += 1
    data_with_header = {col_names[idx]: data[idx] for idx in range(len(col_names))}
    return DataTable(data_with_header)
