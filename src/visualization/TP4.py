# Assurez-vous d'installer les bibliothèques nécessaires si elles ne sont pas déjà installées
# pip install pandas matplotlib seaborn

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Connexion à la base de données
db_config = {
    "dbms_engine": "postgresql",
    "dbms_username": "postgres",
    "dbms_password": "admin",
    "dbms_ip": "localhost",
    "dbms_port": "5432",
    "dbms_database": "snowflakedatabase",
}

db_config["database_url"] = (
    f"{db_config['dbms_engine']}://{db_config['dbms_username']}:{db_config['dbms_password']}@"
    f"{db_config['dbms_ip']}:{db_config['dbms_port']}/{db_config['dbms_database']}"
)
print("Connexion ok bg")
# Charger les données dans un DataFrame
df_trip = pd.read_sql_table('Trip', db_config)

# Analyse exploratoire des données pour les 5 premiers KPIs

# KPI 1: Nombre total de voyages
total_trips = df_trip['TripID'].nunique()
print(f"KPI 1: Nombre total de voyages = {total_trips}")

# KPI 2: Revenu total généré par les voyages
total_revenue = df_trip['total_amount'].sum()
print(f"KPI 2: Revenu total généré par les voyages = {total_revenue}")

# KPI 3: Distance totale parcourue
total_distance = df_trip['trip_distance'].sum()
print(f"KPI 3: Distance totale parcourue = {total_distance} miles")

# KPI 4: Nombre moyen de passagers par voyage
average_passengers = df_trip['passenger_count'].mean()
print(f"KPI 4: Nombre moyen de passagers par voyage = {average_passengers:.2f}")

# KPI 5: Durée moyenne des voyages
df_trip['pickup_datetime'] = pd.to_datetime(df_trip['tpep_pickup_datetime'])
df_trip['dropoff_datetime'] = pd.to_datetime(df_trip['tpep_dropoff_datetime'])
df_trip['trip_duration'] = (df_trip['dropoff_datetime'] - df_trip['pickup_datetime']).dt.total_seconds() / 60  # en minutes
average_trip_duration = df_trip['trip_duration'].mean()
print(f"KPI 5: Durée moyenne des voyages = {average_trip_duration:.2f} minutes")

# Visualisation avec des graphiques

# Histogramme du nombre de passagers
plt.figure(figsize=(10, 6))
sns.histplot(df_trip['passenger_count'], bins=30, kde=True)
plt.title('Distribution du nombre de passagers')
plt.xlabel('Nombre de passagers')
plt.ylabel('Fréquence')
plt.show()

# Diagramme à barres du type de paiement
plt.figure(figsize=(8, 5))
sns.countplot(x='payment_type', data=df_trip)
plt.title('Distribution des types de paiement')
plt.xlabel('Type de paiement')
plt.ylabel('Nombre de voyages')
plt.show()

# Carte thermique des corrélations entre les variables numériques
plt.figure(figsize=(10, 8))
sns.heatmap(df_trip.corr(), annot=True, cmap='coolwarm')
plt.title('Carte thermique des corrélations')
plt.show()
