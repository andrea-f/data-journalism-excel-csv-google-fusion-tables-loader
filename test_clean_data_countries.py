import unittest
from clean_data_countries import DataCleaner

class TestDataCleaner(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_can_load_excel_file(self):
        """
        Test that Excel file can be loaded.
        """
        test_file = "./data/unclean_stranieri_roma_2016.xlsx"
        cleaner = DataCleaner()
        read_file = cleaner.read_excel_file(test_file)
        self.assertTrue(len(read_file) > 0)

    def test_can_apply_transformations(self):
        """
        Test that transformations can be applied on the Excel file.
        """
        test_file = "./data/unclean_stranieri_roma_2016.xlsx"
        cleaner = DataCleaner()
        excel_data = cleaner.read_excel_file(test_file)
        operations_data = cleaner.read_data_operations_file()
        cleaned_data = cleaner.apply_translations(operations_data, excel_data)
        if "EX JUGOSLAVIA" in cleaned_data["Cittadinanza"].values:
            self.fail("EX JUGOSLAVIA")
        if "EX SERBIA E MONTENEGRO" in cleaned_data["Cittadinanza"].values:
            self.fail("EX SERBIA E MONTENEGRO")
        if "EX CECOSLOVACCHIA" in cleaned_data["Cittadinanza"].values:
            self.fail("EX CECOSLOVACCHIA")
        self.assertIn("PALESTINA", cleaned_data["Cittadinanza"].values)
        self.assertTrue(cleaned_data["M"][30] > 1077)
        cleaner.save_file(cleaned_data,
                          operations_data["replace"]["output_file_name"])

        

