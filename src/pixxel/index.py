import boto3
import rasterio
from google.cloud import storage
import scipy.misc
import boto3
import json
import sys

# export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
# export GOOGLE_APPLICATION_CREDENTIALS="keys.json"
"""
gcloud composer environments run sample connections -- -a --conn_id aws_default --conn_type aws --conn_extra '{"region_name": "us-east-1", "aws_access_key_id":"AKIAS2PFB57PYNF32REQ", "aws_secret_access_key": "h7IfqZG5nDKUoz/WoKrVqtfukEhs+CBmF3kFUGAz"}'
bin/pixxel ndvi sentinel-s2-l2a 10 S DG 2018 12 31 0 R60m
"""

GCS_DAGS_BUCKET_NAME = 'us-central1-sample-a3ef44ca-bucket'
GCP_PROJECT_NAME = 'initiable'

class Index:

    def __init__(self):
        pass

    def blob_exists(self, filename, projectname=GCP_PROJECT_NAME, bucket_name=GCS_DAGS_BUCKET_NAME):
        client = storage.Client(projectname)
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        return blob.exists()

    def list_all_dags(self):
        client = storage.Client()
        for index, blob in enumerate(client.list_blobs(GCS_DAGS_BUCKET_NAME, prefix='dags/')):
            print(index, str(blob.name))

    def delete_a_pipeline(self, number):
        client = storage.Client()
        file_name = client.list_blobs(GCS_DAGS_BUCKET_NAME, prefix='dags/')

        for index, blob in enumerate(client.list_blobs(GCS_DAGS_BUCKET_NAME, prefix='dags/')):
            if index == number:
                blob.delete()
                print(str(blob.name) + ' deleted')

    def upload_dag(self, source_file_name, destination_blob_name, bucket_name=GCS_DAGS_BUCKET_NAME):
        """Uploads a file to the bucket."""

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )

    def get_list_of_files_from_command(self, command):
        with open('config.json') as json_file: 
            config = json.load(json_file)

        return config[command]
        
    def create_dag_for_airflow(self, parameters):

        # print(parameters)
        file_name, command, bucket, utm_code, latitude_band, square, year, month, day, sequence, resolution = parameters

        tile_key = bucket + '/tiles' + '/' + utm_code + '/'+ latitude_band + '/'+ square + '/'+ year + '/'+ month + '/'+ day + '/'+ sequence + '/' + resolution + '/'

        if self.blob_exists(filename='dags/pixxel_dag_' + tile_key.replace('/', '_') + '.py'):
            print('This pipeline already exists')
            sys.exit()

        dag_file_template = open('./dags/pixxel_dag.py', 'r')
        dag_file = open('./dags/pixxel_dag_' + tile_key.replace('/', '_') + '.py', 'w')

        list_of_files = self.get_list_of_files_from_command(command)

        check_words = ('LIST_OF_FILES', 'TILE_KEY', 'COMMAND', 'BUCKET', 'UTM_CODE', 'LATITUDE_BAND', 'SQUARE', 'YEAR', 'MONTH', 'DAY', 'SEQUENCE', 'RESOLUTION')
        rep_words = (str(list_of_files), tile_key, command, bucket, utm_code, latitude_band, square, year, month, day, sequence, resolution)
        
        for line in dag_file_template:
            for check, rep in zip(check_words, rep_words):
                line = line.replace(check, rep)

            dag_file.write(line)

        dag_file_template.close()
        dag_file.close()
        self.upload_dag('./dags/pixxel_dag_' + tile_key.replace('/', '_') + '.py', 'dags/pixxel_dag_' + tile_key.replace('/', '_') + '.py')