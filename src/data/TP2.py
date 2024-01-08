import gc
import os
import sys
from minio import Minio
from minio.error import ResponseError
import pandas as pd
from sqlalchemy import create_engine

def download_from_minio(minio_client, bucket_name, object_name, local_path):
    try:
        minio_client.fget_object(bucket_name, object_name, local_path)
    except ResponseError as err:
        print(f"Error downloading {object_name} from Minio: {err}")

def write_data_postgres(dataframe: pd.DataFrame, engine, table_name):
    try:
        with engine.connect():
            success: bool = True
            print("Connection successful! Processing DataFrame")
            dataframe.to_sql(table_name, engine, index=False, if_exists='append')
    
    except Exception as e:
        success: bool = False
        print(f"Error writing data to PostgreSQL: {e}")
        return success
    return success

def clean_column_name(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe.columns = map(str.lower, dataframe.columns)
    return dataframe

def main():
    minio_endpoint = 'localhost:9000'
    minio_access_key = 'minio'
    minio_secret_key = 'minio123'
    bucket_name = 'nyc-taxi'
    local_path = 'yellow_tripdata_2023-02.parquet'

    # Initialisez le client Minio
    minio_client = Minio(minio_endpoint,
                         access_key=minio_access_key,
                         secret_key=minio_secret_key,
                         secure=False)

    # Téléchargez le fichier depuis Minio
    download_from_minio(minio_client, bucket_name, 'yellow_tripdata_2023-02.parquet', local_path)

    # Initialisez le moteur PostgreSQL
    db_config = {
        "dbms_engine": "postgresql",
        "dbms_username": "postgres",
        "dbms_password": "admin",
        "dbms_ip": "localhost",
        "dbms_port": "5432",
        "dbms_database": "nyc_warehouse",
        "dbms_table": "nyc_raw"
    }

    db_url = (
        f"{db_config['dbms_engine']}://{db_config['dbms_username']}:{db_config['dbms_password']}@"
        f"{db_config['dbms_ip']}:{db_config['dbms_port']}/{db_config['dbms_database']}"
    )
    engine = create_engine(db_url)

    # Lisez le fichier parquet dans un DataFrame
    parquet_df = pd.read_parquet(local_path, engine='pyarrow')
    clean_column_name(parquet_df)

    # Écrivez les données dans PostgreSQL
    if not write_data_postgres(parquet_df, engine, db_config['dbms_table']):
        return

    print("Data import successful!")

if __name__ == '__main__':
    sys.exit(main())
