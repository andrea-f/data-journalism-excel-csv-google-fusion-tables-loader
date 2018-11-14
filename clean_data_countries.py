import pandas
import json
import urllib2
import urllib
import pprint

CONFIG_FILE = "./config_data.json"
CREDENTIALS_FILE = "./service_credentials.json"


class DataCleaner(object):
    """
    Perform operations on the data.
    """


    def __init__(self):
        """
        Starts up class variables.
        """
        self.excel_file = None
        self.excel_data = None

    
    def read_excel_file(self, file_name):
        """
        Reads XLSX, Excel file and load it in the instance.
        
        :param file_name:
            Contains local location of Excel file, string.

        Returns loaded file.
        """
        print "Reading Excel file {}...".format(file_name)
        df = pandas.read_excel(file_name)
        return df


    def read_config_file(self, file_name=None):
        """
        Reads the config file to apply the translations.
        
        :param file_name:
            Contains local location of config file, string.
            
        Returns loaded translations file.
        """
        if not file_name:
            file_name = CONFIG_FILE
        print "Reading operations data file {}...".format(file_name)
        with open(file_name, 'r') as fn:
            return json.loads(fn.read())


    def replace_dissolved_countries(self, operations_data, excel_original_data):
        """
        Applies the translations in the config file to the Excel data.

        :param operations_data:
            Loaded data to clean the Excel info, dict.
        :param excel_data:
            Loaded data from the Excel file, dict.
        
        Returns the modified Excel data.
        """
        print "Applying transformations..."
        column_name = operations_data["replace"]["column_name"]
        excel_data = excel_original_data.copy()
        countries = excel_data[column_name].values
        api_key = self.read_config_file(CREDENTIALS_FILE)["mapquest_api_key"]
        countries_geocoded = [None] * len(countries)
        removed_count = 0
        for key_clean, value in operations_data["replace"]["data"].iteritems():
            print "Replacing {}".format(key_clean)
            for c in xrange(len(countries)):
                current_country = countries[c]
                if key_clean in current_country:
                    if isinstance(value, unicode):
                        # Geocode countries
                        countries_geocoded[c] = self.geocode_address(
                            current_country, api_key)
                        excel_data[column_name] = excel_data[column_name].replace({key_clean: value})
                    elif isinstance(value, list) and operations_data["replace"]["split_data_keys_in_list"]:
                        # Value of list after key has been matched in the Excel file.
                        for column_sum in operations_data["replace"]["sum_column_names_in_list"]:
                            # Which number of Male and Female to add to each substituting country total
                            # Assuming the dissolved countries are split into equal numbers of new countries
                            totals = excel_data[column_sum][c] / len(value)
                            # List of countries to substitute dissolved with
                            for v_clean in value:
                                position = -1
                                for compensate in xrange(len(countries)):
                                    if v_clean.upper() in countries[compensate]:
                                        # Find the index of a specific country in the Male and Female columns
                                        position = compensate
                                        break
                                # Add to each country M or F number to subdivide the others
                                if position != -1:
                                    if isinstance(excel_data[column_sum][position], int):
                                        excel_data.loc[position,
                                                       column_sum] += totals
                                else:
                                    print "{} not found in Excel file.".format(v_clean)
                        try:
                            # Removing key which got split in other keys
                            removed_count += 1
                            excel_data.drop([c], inplace=True)
                        except:
                            print "{} not found in Excel data".format(key_clean)
                    break
                else:
                    # Geocode unmodified countries
                    countries_geocoded[c] = self.geocode_address(
                        current_country, api_key)

        geocolumn = operations_data["replace"]["geocode_column"]
        excel_data[geocolumn] = pandas.Series(countries_geocoded)
        # Raise error if there is a mismatch between the geocoded column length
        # And the initial countries list.
        if len(excel_data[geocolumn]) != (len(countries) - removed_count):
            raise Exception("Mismatch between {}({}) and {}({})".format(
                geocolumn, len(excel_data[geocolumn]), column_name, len(countries)))
        return excel_data


    def geocode_address(self, address, api_key):
        """
        Converts an address to geocordinates using Google Geocode API.
        
        :param address:
            Contains name of location, string.

        :param api_key:
            MapQuest API key, string.

        Return string with "longitude latitude"
        """
        query_url = "http://www.mapquestapi.com/geocoding/v1/address?location={}&key={}".format(
            address.replace("'", " ").replace(" ", "+"),
            api_key
        )
        request = urllib2.Request(query_url)
        request_open = urllib2.urlopen(request)
        try:
            location = json.loads(request_open.read())
            location = location['results'][0]['locations'][0]['latLng']
            geocoded = "{} {}".format(location['lat'], location['lng'])
        except Exception as e:
            print "Geocoding error", e
            # No geocode found
            geocoded = "0 0"
        return geocoded
        

    def save_file(self, excel_file, output_file_name):
        """
        Saves the cleaned Excel file locally.

        :param excel_file:
            Loaded data from the Excel file, dict.

        :param output_file_name:
            Contains location of where to save file and which name to use, string.
        """
        writer = pandas.ExcelWriter(output_file_name)
        excel_file.to_excel(writer, 'Sheet1')
        writer.save()
        excel_file.to_csv(output_file_name.replace("xlsx","csv"), sep=',', encoding='utf-8')
        print "Saved {} also CSV file, with {} columns.".format(output_file_name, len(excel_file.keys()))


    def run(self, excel_file=None):
        """
        Performs file loading, applies translations and saves output.

        :param excel_file:
            Location where the original Excel file is, string.
        """
        operations_data = self.read_config_file()
        if not excel_file:
            excel_file = operations_data["replace"]["input_file_name"]
        if not self.excel_file:
            self.excel_file = excel_file
        excel_data = self.read_excel_file(excel_file)
        modified_excel_file = self.replace_dissolved_countries(
            operations_data, excel_data)
        self.save_file(modified_excel_file,
                       operations_data["replace"]["output_file_name"])


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.run()

    
    
