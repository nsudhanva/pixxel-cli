import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import rasterio
from google.cloud import storage
import scipy.misc
import boto3
import sqlite3
import json
import os
os.environ["AWS_REQUEST_PAYER"] = "requester"

s3_date_modified = '' 

bucket = 'BUCKET'
command = 'COMMAND'
utm_code = 'UTM_CODE'
latitude_band = 'LATITUDE_BAND'
square = 'SQUARE'
year = 'YEAR'
month = 'MONTH'
day = 'DAY'
sequence = 'SEQUENCE'
resolution = 'RESOLUTION'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(YEAR, MONTH, DAY),
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

def upload_processed_file_to_gcs(bucket_name, source_file_name, destination_blob_name):
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

def request_image_files_from_s3(files):

    response_jp2s = []

    for i in files:
        tile_key = 'TILE_KEY' + i
        print(tile_key)
        nir = rasterio.open('s3://' + tile_key, driver='JP2OpenJPEG')
        response_jp2s.append(nir)

    return response_jp2s

def calculate_index():

    files = LIST_OF_FILES

    tile_key = 'TILE_KEY'
    tile_key = tile_key.replace('/', '_')

    response_jp2s = request_image_files_from_s3(files)
    band1 = response_jp2s[0].read()
    band2 = response_jp2s[1].read()
    normalized_difference = (band1.astype(float) - band2.astype(float)) / (band1 + band2)

    profile = response_jp2s[0].meta
    profile.update(driver='GTiff')
    profile.update(dtype=rasterio.float32)

    data_path = ''

    with open('modifications_previous.json', "r", encoding='utf-8') as mod:
        data = json.load(mod)
        
        date_path = datetime.strptime(data['LastModified'][:10], '%Y/%m/%d')

    with rasterio.open('output_' + 'COMMAND' + '_' + tile_key + '.tif', 'w', **profile) as dataset:
        dataset.write(normalized_difference.astype(rasterio.float32))

    upload_processed_file_to_gcs('pixxel', 'output_' + 'COMMAND' + '_' + tile_key + '.tif', date_path + '/output_'  + 'COMMAND' + '_' + tile_key + '_airflow.tif')

def check_s3_modified():

    tile_key = 'tiles/' + utm_code + '/'+ latitude_band + '/'+ square + '/'+ year + '/'+ month + '/'+ day + '/'+ sequence + '/' + resolution + '/'
    print(tile_key)

    s3_client = boto3.Session(
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    ).client('s3')

    response = s3_client.list_objects_v2(Bucket='sentinel-s2-l2a', Prefix=tile_key, RequestPayer='requester')

    if not os.path.exists('modifications_previous.json'):
        with open('modifications_previous.json', "w", encoding='utf-8') as mod:
            json.dump(response['Contents'][0], mod, sort_keys=True, default=str)

    with open('modifications_previous.json', "r", encoding='utf-8') as mod:
        data = json.load(mod)
        print(data['LastModified'])
        print(response['Contents'][0]['LastModified'])
        
        previous_modified_date = datetime.strptime(data['LastModified'][:10], '%Y-%m-%d')
        new_modified_date = datetime.strptime(str(response['Contents'][0]['LastModified'])[:10], '%Y-%m-%d')
        
        print(previous_modified_date)
        print(new_modified_date)
        
        if new_modified_date > previous_modified_date:

            with open('modifications_previous.json', "w", encoding='utf-8') as mod:
                json.dump(response['Contents'][0], mod, sort_keys=True, default=str)
                
            print('Updated modifications.json')

        else:
            print('No new data')

    with open('modifications.json', "w", encoding='utf-8') as mod:
        json.dump(response['Contents'][0], mod, sort_keys=True, default=str)

tile_key = 'TILE_KEY'
tile_key = tile_key.replace('/', '_')
    
with DAG(
        tile_key, 
        default_args=default_args,    
        schedule_interval=None
    ) as dag:


    t1 = BashOperator(task_id='bash_test', bash_command='echo "hello, it should work"')
     
    t2 = PythonOperator(task_id='python_check_modified_s3', python_callable=check_s3_modified)
    
    t3 = PythonOperator(task_id='python_calculate_index', python_callable=calculate_index)

    t1 >> t2 >> t3