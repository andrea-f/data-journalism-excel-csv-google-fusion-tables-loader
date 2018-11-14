#!/usr/bin/python
#
# Copyright (C) 2011 Google Inc.
# Modified by Jack Reed @mejackreed November 2012
# Modified by Jack Reed @mejackreed March 2013

"""
Fusion Tables OAuth Helper.
Retrieve OAuth 2.0 access and refresh tokens for Fusion Tables.
"""

import pprint
import urllib2, urllib, json
import apiclient


from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.client import GoogleCredentials
from googleapiclient.http import MediaFileUpload


CREDENTIALS_FILE = "./service_credentials.json"
CONFIG_FILE = "./config_data.json"

class GoogleFusionTablesOAuth(object):
    """
    Publishes a CSV file to Google Fusion Table.
    """


    def __init__(self):
        self.access_token = None


    def read_config_file(self, config_file= CREDENTIALS_FILE):
        """
        Reads Google Fusion Tables credentials file.
        """
        with open(config_file, 'r') as fn:
            #return fn.read()
            return json.loads(fn.read())


    def retrieve_tokens(self):
        """
        Retrieves tokes to use in subsequent requests.
        """
        credentials = self.read_config_file()['web']
        client_id = credentials['client_id']
        redirect_uri = credentials['redirect_uris'][0]
        client_secret = credentials['client_secret']
        token_uri = credentials['token_uri']
        auth_uri = credentials['auth_uri']
        print '%s?client_id=%s&redirect_uri=%s&scope=%s&access_type=offline&response_type=code' % \
            (auth_uri, 
            client_id,
            redirect_uri,
            'https://www.googleapis.com/auth/fusiontables') 

        auth_code = raw_input('Enter authorization code ("code" parameter of URL): ')
        
        data = urllib.urlencode({
            'code': auth_code, 
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code' 
        })
        request = urllib2.Request(
            url=token_uri,
            data=data)
        request_open = urllib2.urlopen(request)
        response = request_open.read()
        #print response
        tokens = json.loads(response)
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        return access_token, refresh_token


    def get_access_token(self):
        """
        Retrieves the access and refresh tokens in the instance.
        Otherwise generates new ones.
        """
        if not self.access_token:
            self.access_token, self.refresh_token = self.retrieve_tokens()
        return self.access_token, self.refresh_token


    def upload_excel_to_google_fusion_table(self, file_name, table_name):
        """
        Uploads an Excel file to Google Fusion Table.
        """
        excel_file = apiclient.http.MediaFileUpload(file_name, mimetype='application/octet-stream')
        request = apiclient.discovery.service.table().importRows(tableId=table_name, media_body=excel_file,
                                            startLine=1, encoding='utf-8')
        response = request.execute()
        return response
        

    def create_table(self, name, description, columns, file_name, data=None, make_public=False):
        """
        Creates table in Google Fusion.
        """
        scopes = ['https://www.googleapis.com/auth/fusiontables',
                'https://www.googleapis.com/auth/drive']
        credentials = GoogleCredentials.from_stream(
            CREDENTIALS_FILE).create_scoped(scopes=scopes)
        http_auth = credentials.authorize(Http())
        ft_service = build(
            serviceName='fusiontables', version='v2', http=http_auth)
        drive_service = build(
            serviceName='drive', version='v3', http=http_auth)
        body = dict(name=name, description=description, columns=columns, isExportable=True)
        table = ft_service.table()
        result = table.insert(body=body).execute()
        permissions = drive_service.permissions()
        permissions.create(fileId=result["tableId"], body={"emailAddress": "mailandreafassina@gmail.com","type": "user", "role": "writer"}, sendNotificationEmail=False).execute()
        if make_public:
            public_permission = {'type': 'anyone', 'role': 'reader'}
            permissions.insert(
                fileId=result["tableId"], body=public_permission).execute()
        media_body = MediaFileUpload(
            filename=file_name, mimetype="application/octet-stream")
        table.importRows(tableId=result["tableId"], media_body=media_body, startLine=1, isStrict=True, encoding="utf-8", delimiter=",").execute()
        return result["tableId"]

if __name__ == "__main__":
    fusion = GoogleFusionTablesOAuth()
    config = fusion.read_config_file(config_file=CONFIG_FILE)
    columns = config['replace']['fusion']['schema']
    fn = config['replace']['fusion']['csv_input_file']
    table_name = config['replace']['fusion']['table_name']
    description = config['replace']['fusion']['description']
    endpoint_url = config['replace']['fusion']['endpoint_url']
    response = fusion.create_table(table_name, description, columns, fn)
    public_url = "https: // www.google.com/fusiontables/DataSource?docid={}".format(response)
    live_url = endpoint_url.format(
        response)
    pprint.pprint(live_url)
