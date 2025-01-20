-- /opt/airflow/dags/dbt_models/transform_users.sql


WITH users AS (
    SELECT * FROM {{ source('apidata', 'users')  }}
)

SELECT
    id,
    name,
    username,
    email,
    address_street,
    address_suite,
    address_city,
    address_zipcode,
    phone,
    website,
    company_name
FROM users
WHERE address_city = 'Gwenborough'
