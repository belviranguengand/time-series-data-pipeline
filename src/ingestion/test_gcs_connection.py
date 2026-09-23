from google.cloud import storage

PROJECT_ID = "time-series-data-pipeline"
BUCKET_NAME = "time-series-data-pipeline-raw"

client = storage.Client(project=PROJECT_ID)

bucket = client.get_bucket(BUCKET_NAME)

print(f"[OK] Connexion réussie au bucket : {bucket.name}")
print(f"[OK] Projet GCP : {PROJECT_ID}")