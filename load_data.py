import pandas as pd
from database import get_connection

print("Loading CSV file...")
df = pd.read_csv('data/job_descriptions.csv', nrows=2000, on_bad_lines='skip', engine='python')

print("Cleaning columns...")
df_clean = pd.DataFrame()
df_clean['job_title']        = df['Job Title']
df_clean['company']          = df['Company']
df_clean['required_skills']  = df['skills']
df_clean['job_role']         = df['Role']
df_clean['experience_level'] = df['Experience']
df_clean['description']      = df['Job Description']

print("Saving to database...")
conn = get_connection()
df_clean.to_sql('jobs', conn, if_exists='replace', index=False)
conn.close()

print(f"Done! Loaded {len(df_clean)} jobs successfully!")