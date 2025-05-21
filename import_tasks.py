import sqlite3
from datetime import datetime
import os
import tempfile
import streamlit as st

def get_db_path():
    if os.environ.get('STREAMLIT_SERVER_RUNNING'):
        # Sur Streamlit Cloud, utiliser un chemin temporaire
        return os.path.join(tempfile.gettempdir(), 'roadmap.db')
    else:
        # En local, utiliser le chemin normal
        return 'roadmap.db'

def import_tasks():
    try:
        # Connexion à la base de données
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Création de la table si elle n'existe pas
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT,
                description TEXT,
                status TEXT,
                responsible TEXT,
                deadline TEXT,
                comments TEXT
            )
        ''')

        # Liste des tâches à importer
        tasks = [
            {
                "task_name": "GenAI/ ADV / restructuration d'analyse",
                "description": "Cette tâche consiste à revoir entièrement la manière dont les analyses sont présentées dans le module GenAI/ADV. L'objectif est de rendre les résultats plus clairs, mieux structurés et plus faciles à exploiter, notamment pour les équipes non techniques.",
                "status": "en cours",
                "responsible": "Youness/ Mehdi",
                "deadline": "2025-05-10",
                "comments": "Était prévu pour le 10 mai 2025. Une sous-estimation de la charge de travail a nécessité une requalification pour une durée plus longue."
            },
            {
                "task_name": "Création d'un espace commentaire pour recueillir les motivations des agents",
                "description": "Mise en place d'un champ texte sur la plateforme permettant aux agents d'exprimer librement leurs motivations. Ces retours peuvent être utilisés pour mieux comprendre les attentes du personnel et nourrir les réflexions RH.",
                "status": "OK",
                "responsible": "Mehdi /Youness",
                "deadline": "2025-04-25",
                "comments": "Deployer"
            },
            {
                "task_name": "Scraping DATA WEB offre",
                "description": "Collecte automatique de données publiques disponibles sur des sites web externes afin d'analyser les offres concurrentes. Ces données sont ensuite structurées et exploitées dans des rapports internes.",
                "status": "OK",
                "responsible": "Youness/ Salma",
                "deadline": "2025-05-05",
                "comments": "OK"
            },
            {
                "task_name": "Rapport : Mail des humeurs négatives envoyé à N+1 en anonymat",
                "description": "Automatisation d'un système d'envoi d'emails anonymes aux managers (N+1) lorsque des signaux d'humeur négative sont détectés. L'objectif est de sensibiliser les responsables hiérarchiques tout en respectant l'anonymat des collaborateurs.",
                "status": "OK",
                "responsible": "Mehdi",
                "deadline": "2025-04-25",
                "comments": "Deployer"
            },
            {
                "task_name": "Ajout de la possibilité de consulter les primes des autres groupes et projets",
                "description": "Développement d'un nouvel affichage permettant aux agents de comparer les systèmes de primes en vigueur dans d'autres projets ou équipes. Ce mécanisme vise à favoriser la transparence et à susciter l'émulation.",
                "status": "OK",
                "responsible": "Mehdi/Youness",
                "deadline": "2025-05-07",
                "comments": "Deployer"
            },
            {
                "task_name": "Dashboard QA : interface pour valider/rejeter manuellement certains tokens et améliorer le modèle",
                "description": "Création d'un tableau de bord permettant aux utilisateurs de vérifier manuellement certaines décisions prises par l'IA (les 'tokens' ou unités de texte) et de les accepter ou les corriger. Ces retours permettront d'améliorer progressivement la performance du modèle.",
                "status": "en cours",
                "responsible": "Youness/ salma/mehdi",
                "deadline": None,
                "comments": "a lancer apres la tache Chat dialogue"
            },
            {
                "task_name": "Feedback loop : intégration d'un module de réapprentissage continu à partir du feedback utilisateur",
                "description": "Développement d'un système dans lequel les retours des utilisateurs (via validations ou corrections) sont automatiquement intégrés dans un cycle de réapprentissage de l'IA. Cela permet au système de devenir plus performant au fil du temps.",
                "status": "en cours",
                "responsible": "Youness/Salma/Mehdi",
                "deadline": None,
                "comments": "Tache coupler avec Dashboard QA"
            },
            {
                "task_name": "Chat dialogue et statistique",
                "description": "Mise en place d'un assistant conversationnel capable de répondre aux questions des utilisateurs sur les statistiques disponibles (ex. indicateurs d'activité, performances…). Une première version est déjà fonctionnelle mais reste limitée à des cas simples. Une version plus complète est en cours de développement pour répondre à des demandes plus complexes.",
                "status": "en cours",
                "responsible": "Youness/Salma/Mehdi",
                "deadline": None,
                "comments": "V1 réalisée / Revue pour qu'elle soit à la hauteur de la demande, car V1 est seulement capable de répondre à des questions statistiques de vigie 'Chargé de flux'"
            }
        ]

        # Vérifier si la table est vide avant d'insérer
        c.execute("SELECT COUNT(*) FROM tasks")
        if c.fetchone()[0] == 0:
            # Insertion des tâches
            for task in tasks:
                c.execute('''
                    INSERT INTO tasks (task_name, description, status, responsible, deadline, comments)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    task["task_name"],
                    task["description"],
                    task["status"],
                    task["responsible"],
                    task["deadline"],
                    task["comments"]
                ))
            conn.commit()
            print("Import des tâches terminé avec succès!")
        else:
            print("La base de données contient déjà des tâches. Import ignoré.")

    except Exception as e:
        print(f"Erreur lors de l'import des tâches: {str(e)}")
        raise e
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_tasks() 