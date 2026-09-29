# Energy Consumption Monitoring Pipeline

Pipeline Data Engineering de bout en bout construit à partir du dataset **ASHRAE – Great Energy Predictor III**.

L'objectif du projet est de mettre en place une architecture permettant de valider, ingérer, stocker, transformer, contrôler et orchestrer des données de consommation énergétique multi-sites.

## Architecture

```text
ASHRAE CSV
    ↓
Validation Python
    ↓
Google Cloud Storage
    ↓
BigQuery RAW
    ↓
Contrôles qualité
    ↓
dbt
    ↓
BigQuery Analytics
    ↓
Dashboard
```

**Apache Airflow** orchestre les différentes étapes du pipeline.

## Stack technique

- Python
- SQL
- Google Cloud Storage
- BigQuery
- dbt
- Apache Airflow
- PostgreSQL
- Docker / Docker Compose
- Git / GitHub
- GitHub Actions
- pytest

PySpark sera intégré dans une phase dédiée au traitement distribué et au passage à l'échelle.

## Dataset

Le projet utilise le dataset **ASHRAE – Great Energy Predictor III**.

Sources principales utilisées :

- `building_metadata.csv`
- `weather_train.csv`
- `train.csv`

Le dataset principal contient plus de **20 millions de mesures de consommation énergétique**.

## Pipeline

Le DAG Airflow `energy_pipeline` orchestre les étapes suivantes :

```text
start
  ↓
validate_sources
  ↓
ingest_to_gcs
  ↓
load_to_bigquery
  ↓
check_bigquery_data
  ↓
dbt_build
  ↓
end
```

### 1. Validation des sources

Avant l'ingestion, les fichiers CSV sont contrôlés avec Python :

- présence du fichier ;
- fichier non vide ;
- présence des colonnes attendues.

Le pipeline applique une stratégie **fail fast** : une source invalide empêche la poursuite du traitement.

### 2. Ingestion vers Google Cloud Storage

Les fichiers validés sont chargés dans :

```text
gs://time-series-data-pipeline-raw/ashrae/raw/
```

L'ingestion est idempotente : un fichier déjà présent avec la même taille n'est pas transféré à nouveau.

### 3. Chargement BigQuery

Les données sont chargées dans le dataset :

```text
raw_ashrae
```

Tables :

- `building_metadata`
- `weather_train`
- `train`

Les tables temporelles sont partitionnées sur `timestamp`.

Pour ce snapshot statique, le chargement RAW utilise `WRITE_TRUNCATE` afin de rendre les réexécutions reproductibles et d'éviter la duplication des données.

### 4. Data Quality

Des contrôles sont appliqués sur les données :

- valeurs manquantes ;
- doublons ;
- validité des valeurs ;
- intégrité référentielle ;
- continuité temporelle ;
- volumétrie attendue.

Un contrôle post-chargement vérifie également les volumes présents dans BigQuery.

Volumes attendus :

```text
building_metadata :     1 449 lignes
weather_train      :   139 773 lignes
train              : 20 216 100 lignes
```

### 5. Transformations dbt

dbt transforme les données RAW en modèles analytiques.

Couche staging :

- `stg_building_metadata`
- `stg_weather`
- `stg_train`

Couche marts :

- `mart_energy_consumption`
- `mart_daily_site_consumption`

Les modèles et tests sont exécutés avec :

```bash
dbt build
```

État actuel :

```text
PASS=34
WARN=0
ERROR=0
SKIP=0
TOTAL=34
```

## Orchestration Airflow

Airflow est exécuté dans Docker avec PostgreSQL comme base de métadonnées.

Le pipeline gère :

- les dépendances entre les tâches ;
- les logs ;
- les statuts d'exécution ;
- les retries sur les opérations susceptibles d'échouer temporairement ;
- le blocage des tâches en aval en cas d'échec.

Le dataset ASHRAE utilisé étant un snapshot statique, le DAG est actuellement configuré avec :

```python
schedule=None
```

Une planification automatique a également été testée afin de valider le mécanisme de scheduling Airflow.

## Sécurité GCP et IAM

Le pipeline utilise un service account dédié :

```text
energy-pipeline@time-series-data-pipeline.iam.gserviceaccount.com
```

Les permissions sont limitées aux ressources nécessaires au pipeline.

Le service account dispose notamment :

```text
GCS bucket
└── accès aux objets et métadonnées nécessaires

BigQuery project
└── BigQuery Job User

BigQuery raw_ashrae
└── BigQuery Data Editor

BigQuery analytics
└── BigQuery Data Editor
```

En environnement local, Airflow utilise **Application Default Credentials (ADC)** avec **service account impersonation**.

```text
Airflow / Docker
        ↓
ADC
        ↓
Service Account Impersonation
        ↓
energy-pipeline
        ↓
GCS + BigQuery
```

Cette approche permet d'éviter de stocker une clé privée permanente du service account dans le projet ou dans Git.

En environnement de production GCP, l'objectif serait d'utiliser directement une identité de service attachée au runtime plutôt que des credentials utilisateur locaux.

## Tests automatisés

Les fonctions de validation des sources sont couvertes par des tests unitaires avec `pytest`.

Les tests couvrent notamment :

- fichier présent ;
- fichier absent ;
- fichier vide ;
- fichier non vide ;
- schéma valide ;
- colonne manquante ;
- échec global de validation ;
- succès global de validation.

État actuel :

```text
8 tests passed
```

## CI

Une pipeline CI est configurée avec **GitHub Actions**.

À chaque push ou pull request vers `main`, GitHub Actions :

1. récupère le dépôt ;
2. configure Python 3.12 ;
3. installe les dépendances ;
4. exécute les tests unitaires.

Les tests nécessitant une authentification GCP sont séparés des tests unitaires afin que la CI ne dépende pas de credentials personnels.

## Exécution locale

L'environnement Airflow peut être lancé avec :

```bash
docker compose up -d
```

Vérification des conteneurs :

```bash
docker compose ps
```

Interface Airflow :

```text
http://localhost:8080
```

Arrêt :

```bash
docker compose down
```

## Structure du projet

```text
time-series-data-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml
├── airflow/
│   └── dags/
│       └── energy_pipeline_dag.py
├── data/
│   ├── raw/
│   └── processed/
├── dbt/
│   └── energy_pipeline/
├── docker/
│   └── airflow/
├── docs/
│   └── screenshots/
├── sql/
│   └── data_quality/
├── src/
│   ├── ingestion/
│   └── monitoring/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

Les données brutes, environnements virtuels, secrets et fichiers de credentials ne sont pas versionnés.

## État du projet

Déjà implémenté :

- audit des données ;
- validation des sources ;
- ingestion GCS ;
- chargement BigQuery ;
- contrôles Data Quality ;
- transformations dbt ;
- tests dbt ;
- orchestration Airflow ;
- monitoring ;
- tests unitaires ;
- CI GitHub Actions ;
- authentification GCP avec service account et impersonation.

Prochaines étapes :

- PySpark et traitement distribué ;
- dashboard de restitution ;
- finalisation de la documentation et du portfolio.