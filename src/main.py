import sys
import os
import time

from pixxel.index import Index

# pixxel ndvi utm_code latitude_band square sequence start_pipeline

if __name__ == '__main__':
    os.environ["AWS_REQUEST_PAYER"] = "requester"

    index = Index()

    if sys.argv[1] == 'list':
        print('Listing all pipelines: ')
        index.list_all_dags()
    elif sys.argv[1] == 'delete':
        print('Enter the pipeline you want to delete: ')
        index.list_all_dags()
        
        option = int(input('Enter the pipeline number you want to delete: '))
        index.delete_a_pipeline(option)
        index.list_all_dags()
    elif len(sys.argv) == 11:
        index.create_dag_for_airflow(sys.argv)
    else:
        print('Oops! Seems like a wrong number of options are passed')

