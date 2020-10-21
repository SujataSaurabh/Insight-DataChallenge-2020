import unittest
import sys
sys.path.append('../../src/')
import bears as br

class DataTableTest(unittest.TestCase):

    def test_empty_data_table(self):
        data_table = br.DataTable({})

    def test_get_item(self):
        data_table = br.DataTable({'A': [1, 2]})
        self.assertEqual(data_table['A'], [1, 2])

    def test_set_item(self):
        data_table = br.DataTable({})
        data_table['A'] = [1, 2]
        self.assertEqual(data_table['A'], [1, 2])

    def test_count(self):
        data_table = br.DataTable({'A': [1, 2, 3, 4, 5], 'B': ['x', 'y', 'x','z', 'z']})
        count_by_B = data_table.count(group_by='B')
        self.assertEqual(count_by_B, {'x' : 2, 'y' : 1, 'z' : 2})

    def test_count_invalid_col_name(self):
        data_table = br.DataTable({})
        with self.assertRaises(ValueError):
            data_table.count(group_by='B')

    def test_sum(self):
        data_table = br.DataTable({'A': [1, 2, 3, 4, 5], 'B': ['x', 'y', 'x','z', 'z']})
        count_by_B = data_table.sum(col_name='A', group_by='B')
        self.assertEqual(count_by_B, {'x' : 4, 'y' : 2, 'z' : 9})

    def test_sum_invalid_col_name(self):
        data_table = br.DataTable({})
        with self.assertRaises(ValueError):
            data_table.sum(col_name='A', group_by='B')

    def test_sum_non_numeric_data(self):
        data_table = br.DataTable({'A': [1, 2, '3', 4, 5], 'B': ['x', 'y', 'x','z', 'z']})
        with self.assertRaises(TypeError):
            data_table.sum(col_name='A', group_by='B')

    def test_avg(self):
        data_table = br.DataTable({'A': [1, 2, 3, 4, 5], 'B': ['x', 'y', 'x','z', 'z']})
        count_by_B = data_table.avg(col_name='A', group_by='B')
        self.assertEqual(count_by_B, {'x' : 2.0, 'y' : 2.0, 'z' : 4.5})

    def test_avg_invalid_col_name(self):
        data_table = br.DataTable({})
        with self.assertRaises(ValueError):
            data_table.avg(col_name='A', group_by='B')

    def test_avg_non_numeric_data(self):
        data_table = br.DataTable({'A': [1, 2, '3', 4, 5], 'B': ['x', 'y', 'x','z', 'z']})
        with self.assertRaises(TypeError):
            data_table.avg(col_name='A', group_by='B')

    def test_map(self):
        data_table = br.DataTable({'A': [1, 2, 3, 4, 5]})
        data_table.map(col_name='A', func=lambda x: x*x)
        self.assertEqual(data_table['A'], [1, 4, 9, 16, 25])

    def test_map_invalid_col_name(self):
        data_table = br.DataTable({})
        with self.assertRaises(ValueError):
            data_table.map(col_name='A', func=lambda x: x*x)

    def test_map_lambda_throws_exception(self):
        data_table = br.DataTable({'A': [1, 2, 3, 4, 5]})
        with self.assertRaises(Exception):
            data_table.map(col_name='A', func=lambda x: exec('raise(Exception(x))')
)

if __name__ == '__main__':
    unittest.main()
