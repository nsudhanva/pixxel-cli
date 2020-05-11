import sys
import os
import time

from pixxel.index import Index

# pixxel ndvi utm_code latitude_band square sequence start_pipeline

if __name__ == '__main__':
    os.environ["AWS_REQUEST_PAYER"] = "requester"
    print('Hello World')
    print(sys.argv)

    index = Index()

    if len(sys.argv) != 11:
        print('Please pass proper number of arguments')
        sys.exit()
    else:
        index.create_dag_for_airflow(sys.argv)
