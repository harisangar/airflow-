import os
import json
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow import DAG
import requests
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator

import duckdb
import json

# Define the default arguments for the DAG
def fetch_user_data_from_api():
    # Replace with your API URL and add limit parameter if supported by the API
    api_url = "https://jsonplaceholder.typicode.com/users?_limit=20"  # Adding limit query parameter
    
    # Make the API request
    response = requests.get(api_url)
    
     
    # Check if the request was successful
    if response.status_code == 200:
        # Save the response JSON to a file with the first 20 users (if limit isn't supported)
        data = response.json()  # This will only contain 20 records due to the API query limit

        # Define the file path where the JSON data will be saved
        file_path = "/opt/airflow/apidata/users_data.json"  # Adjust the path as needed

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the data to the file
        with open(file_path, 'w') as f:
            json.dump(data, f)

        # Return the file path
        return file_path
    else:
        raise Exception(f"API request failed with status code {response.status_code}")
    
def save_data_to_duckdb(file_path):
    DUCKDB_PATH = "/opt/airflow/apidata/my_duckdb_database.duckdb" 
    # Connect to DuckDB (this will create the database file if it doesn't exist)
    conn = duckdb.connect(DUCKDB_PATH)

    # Read the data from the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Create the table if it doesn't exist (adjust schema according to the API data)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER,
            name TEXT,
            username TEXT,
            email TEXT,
            address_street TEXT,
            address_suite TEXT,
            address_city TEXT,
            address_zipcode TEXT,
            phone TEXT,
            website TEXT,
            company_name TEXT
        )
    """)

    # Insert user data into the table
    for user in data:
        conn.execute("""
            INSERT INTO users (
                id, name, username, email, 
                address_street, address_suite, address_city, address_zipcode, 
                phone, website, company_name
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['id'], user['name'], user['username'], user['email'], 
            user['address']['street'], user['address']['suite'], user['address']['city'], user['address']['zipcode'],
            user['phone'], user['website'], user['company']['name']
        ))

    conn.close()

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 15),
}

# Define the DAG
with DAG(
    'user_data_to_duckdb',
    default_args=default_args,
    description='Fetch user data from API and store it in DuckDB',
    schedule_interval='@daily',  # You can adjust this to your needs
    catchup=False,
) as dag:

    # Task 1: Fetch user data from API and save it to a file
    fetch_task = PythonOperator(
        task_id='fetch_user_data_from_api',
        python_callable=fetch_user_data_from_api,
    )

    # Task 2: Save the fetched data from the file to DuckDB
    save_task = PythonOperator(
        task_id='save_data_to_duckdb',
        python_callable=save_data_to_duckdb,
        op_args=["{{ task_instance.xcom_pull(task_ids='fetch_user_data_from_api') }}"],  # Pull the file path from the first task
    )


    # Task 3: Run the DBT task using BashOperator
    run_dbt_task = BashOperator(
        task_id='run_dbt_transform',
        bash_command="""
        cd /opt/airflow/dags/dbt_models && \
        dbt run --profiles-dir /opt/airflow/dbt/profiles.yml --target dev
        """,
    )


    # Set task dependencies edited
    fetch_task >> save_task >> run_dbt_task
