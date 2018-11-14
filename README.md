# Data Journalism exercise with Python loading Excel and CSV in Google Fusion after finding Geocoordinates using MapQuest.

This repo is Python code to:
- Read a Excel file.
- Perform an operation on it, remove dissolved countries in Stranieri a Roma 2016 Excel
- Split numbers of residents of dissolved countries in their present day ones.
- For each country fetch geocoordinates from MapQuest
- Save the resulting Excel in a new Excel file and a CSV one.
- Load CSV into Google Fusion Table

For the Data Journalism exercise at Sapienza, the resulting map is in: https://www.google.com/fusiontables/DataSource?docid=19cHImENsTkRAz4F0Kz54ICEJo5IDVQlQ6UkiyKMd

# How to run the scripts

## Set up prerequisites
1. Download and install Python locally for your Operating System.
2. Install `virtualenvwrapper` via the `Python package manager - pip`.
3. Create an environment with: `$ mkvirtualenv data_journalism`.
4. Run: `workon data_journalism`.
5. In the folder with all the files run: `pip install -r requirements.txt`.
6. Modify the `./service_credentials` file in the root folder to contain your keys (register here: https://console.cloud.google.com/ for Drive, Fusion API and here: https://developer.mapquest.com/ for the Geocoordinates API, click on get your free API key). To get a `service_credentials.json` file follow this guide here: https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount, then copy the values in the `./service_credentials.json` file of this repo.
7. Having put the correct credentials in `./service_credentials_example.json` file, rename it to `./service_credentials.json` so the script can find it.

## Run the cleaner
1. Run `$ python clean_data_countries.py` will load the `unclean....xlsx` file from the `data` folder
2. Get `longitude` and `latitude` for each country from MapQuest API.
3. Script then applies transformations defined in `config_data.json`
4. Saves result in a `XLSX` and `CSV` files.

## Run the Google Fusion table loader
1. Run `$ python google_fusion_api.py` to load the `CSV` previously obtained in Google Fusion table. The config information used will be from `./service_credentials.json` and `./config_data.json`.
2. The resulting Fusion Table has public permission and the resulting links are printed at the end of the script.
3. The generated URL for the exercise of creating a map of `stranieri residenti a Roma nel 2016` is: `https://www.google.com/fusiontables/DataSource?docid=19cHImENsTkRAz4F0Kz54ICEJo5IDVQlQ6UkiyKMd`
