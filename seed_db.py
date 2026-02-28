import pandas as pd
import json
import random
from integrations import _ensure_snowflake_table, _get_snowflake_conn

print('Ensure table...')
_ensure_snowflake_table()

print('Loading dataset...')
df = pd.read_csv('Training.csv')
disease_counts = df['prognosis'].value_counts().to_dict()

conn = _get_snowflake_conn()
cur = conn.cursor()
cur.execute('USE DATABASE HEALTHAI')
cur.execute('USE SCHEMA PUBLIC')

print('Clearing old data...')
cur.execute('DELETE FROM health_checkups')

print('Building bulk insert...')
rows = []
for prognosis, count in disease_counts.items():
    insert_count = max(1, int(count * 0.1))
    for _ in range(insert_count):
        age = random.choice(['18-25', '26-35', '36-45', '46-55', '56-65'])
        gender = random.choice(['Male', 'Female'])
        rows.append(f"('{age}', '{gender}', '{prognosis}')")

print('Inserting...')
values_str = ',\n'.join(rows)
query = f'INSERT INTO health_checkups (age_range, gender, predicted_disease) VALUES {values_str}'

cur.execute(query)
conn.close()
print(f'Successfully imported {len(rows)} real records into Snowflake!')
