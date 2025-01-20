import duckdb

import os

# Get the current directory where test.py is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Combine the directory path with the database file name
db_path = os.path.join(current_directory, 'my_duckdb_database.duckdb')

# Connect to the DuckDB database
conn = duckdb.connect(db_path)

# Query the filtered_users table (or any table you want)
result = conn.execute("SELECT * FROM transform_users").fetchall()

# Print the results
print("Filtered Users Data:")
for row in result:
    print(row)

# Close the connection
conn.close()
