import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import plotly.graph_objects as go
import os
import sys
import tempfile

# Configuration de la page
st.set_page_config(
    page_title="Système de Gestion des Tâches",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour obtenir le chemin de la base de données
def get_db_path():
    if os.environ.get('STREAMLIT_SERVER_RUNNING'):
        # Sur Streamlit Cloud, utiliser un chemin temporaire
        return os.path.join(tempfile.gettempdir(), 'roadmap.db')
    else:
        # En local, utiliser le chemin normal
        return 'roadmap.db'

# Fonction pour initialiser la base de données
def init_db():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                description TEXT,
                status TEXT,
                responsible TEXT,
                deadline TEXT,
                comments TEXT
            )
        ''')
        conn.commit()
        conn.close()
        st.success("Base de données initialisée avec succès!")
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        sys.exit(1)

# Fonction pour ajouter une tâche
def add_task(task_name, description, status, responsible, deadline, comments):
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO tasks (task_name, description, status, responsible, deadline, comments)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task_name, description, status, responsible, deadline, comments))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'ajout de la tâche: {str(e)}")
        return False

# Initialiser la base de données si elle n'existe pas
try:
    db_path = get_db_path()
    if not os.path.exists(db_path):
        init_db()
        # Importer les tâches initiales
        try:
            from import_tasks import import_tasks
            import_tasks()
            st.success("Tâches initiales importées avec succès!")
        except Exception as e:
            st.error(f"Erreur lors de l'importation des tâches: {str(e)}")
except Exception as e:
    st.error(f"Erreur lors de l'initialisation: {str(e)}")
    sys.exit(1)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    div[data-testid="stExpander"] div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    div[data-testid="stExpander"] div[data-testid="stExpander"]:hover {
        border-color: #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .no-deadline {
        color: #28a745;
        font-style: italic;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .metric-card:hover {
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .urgent {
        color: #ffc107;
        font-weight: bold;
    }
    .warning {
        color: #ffc107;
        font-weight: bold;
    }
    .success {
        color: #007bff;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def get_task_status_color(status):
    return {
        "OK": "success",
        "en cours": "warning",
        "non démarré": "urgent"
    }.get(status, "")

def get_days_remaining(deadline):
    if pd.isna(deadline):
        return None
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
    today = datetime.now().date()
    return (deadline_date.date() - today).days

def get_deadline_status(days_remaining, current_status):
    if days_remaining is None:
        return "Non définie"
    if days_remaining < 0:
        if current_status == "OK":
            return "Délai respecté"
        else:
            return "En retard"
    elif days_remaining <= 7:
        return "À surveiller"
    else:
        return "Dans les temps"

def get_deadline_comment(days_remaining, current_status):
    if days_remaining is None:
        return "Non définie"
    if days_remaining < 0:
        if current_status == "OK":
            return "Délai respecté"
        else:
            return f"En retard de {abs(days_remaining)} jours"
    elif days_remaining <= 7:
        return f"{days_remaining} jours restants"
    else:
        return f"{days_remaining} jours restants"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/task.png", width=100)
    st.title("Menu")
    st.markdown("---")
    
    # Filtres globaux
    st.subheader("Filtres")
    status_filter = st.multiselect(
        "Statut",
        ["Tous", "Non démarré", "En cours", "OK"],
        default=["Tous"]
    )
    
    responsible_filter = st.multiselect(
        "Responsable",
        ["Tous", "Youness", "Mehdi", "Salma"],
        default=["Tous"]
    )
    
    # Filtre par priorité
    priority_filter = st.multiselect(
        "Priorité",
        ["Tous", "Urgent", "À surveiller", "Dans les temps"],
        default=["Tous"]
    )
    
    st.markdown("---")
    st.markdown("### Statistiques rapides")
    
    # Connexion à la base de données
    conn = sqlite3.connect('roadmap.db')
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    
    # Calcul des statistiques
    total_tasks = len(df)
    completed_tasks = len(df[df['status'] == 'OK'])
    in_progress_tasks = len(df[df['status'] == 'en cours'])
    not_started_tasks = len(df[df['status'] == 'non démarré'])
    
    # Calcul des tâches urgentes
    urgent_tasks = sum(1 for _, row in df.iterrows() 
                      if get_days_remaining(row['deadline']) is not None 
                      and get_days_remaining(row['deadline']) < 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", total_tasks)
        st.metric("Terminées", completed_tasks)
    with col2:
        st.metric("En cours", in_progress_tasks)
        st.metric("Non démarrées", not_started_tasks)
    
    st.markdown("---")
    st.markdown("### Tâches urgentes")
    if urgent_tasks > 0:
        st.error(f"⚠️ {urgent_tasks} tâche(s) en retard")
    else:
        st.success("✅ Aucune tâche en retard")

# Titre principal avec style
st.markdown("""
    <h1 style='text-align: center; color: #2E4053; padding: 20px;'>
        📊 Tableau de Bord des Tâches
    </h1>
""", unsafe_allow_html=True)

# Interface principale
tab1, tab2, tab3 = st.tabs(["📋 Liste des Tâches", "🗺️ Roadmap", "➕ Ajouter une Tâche"])

with tab1:
    # Filtrage des données
    filtered_df = df.copy()
    if "Tous" not in status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if "Tous" not in responsible_filter:
        filtered_df = filtered_df[filtered_df['responsible'].str.contains('|'.join(responsible_filter))]
    
    # Filtrage par priorité
    if "Tous" not in priority_filter:
        filtered_df = filtered_df[filtered_df.apply(lambda row: 
            ("Urgent" in priority_filter and get_days_remaining(row['deadline']) is not None and get_days_remaining(row['deadline']) < 0) or
            ("À surveiller" in priority_filter and get_days_remaining(row['deadline']) is not None and 0 <= get_days_remaining(row['deadline']) <= 7) or
            ("Dans les temps" in priority_filter and (get_days_remaining(row['deadline']) is None or get_days_remaining(row['deadline']) > 7)),
            axis=1
        )]
    
    # Affichage des tâches avec un design amélioré
    for _, row in filtered_df.iterrows():
        days_remaining = get_days_remaining(row['deadline'])
        priority_class = get_task_status_color(row['status'])
        
        with st.expander(f"📌 {row['task_name']}", expanded=False):
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"**Description:** {row['description']}")
                st.markdown(f"**Commentaires:** {row['comments']}")
            with col2:
                status_icons = {
                    "OK": "🟢",
                    "en cours": "🟡",
                    "non démarré": "⚪"
                }
                status_color = status_icons.get(row['status'], "⚪")
                st.markdown(f"**Statut:** {status_color} {row['status']}")
                st.markdown(f"**Responsable:** 👤 {row['responsible']}")
                
                if pd.notna(row['deadline']):
                    days_remaining = get_days_remaining(row['deadline'])
                    deadline_status = get_deadline_status(days_remaining, row['status'])
                    deadline_comment = get_deadline_comment(days_remaining, row['status'])
                    
                    if deadline_status == "En retard":
                        st.markdown(f"**Deadline:** 📅 <span class='warning'>{deadline_comment}</span>", unsafe_allow_html=True)
                    elif deadline_status == "À surveiller":
                        st.markdown(f"**Deadline:** 📅 <span class='warning'>{deadline_comment}</span>", unsafe_allow_html=True)
                    elif deadline_status == "Délai respecté":
                        st.markdown(f"**Deadline:** 📅 <span class='success'>{deadline_comment}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Deadline:** 📅 <span class='success'>{deadline_comment}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**Deadline:** ⏳ <span class='no-deadline'>Non définie</span>", unsafe_allow_html=True)

with tab2:
    # Création du graphique Gantt
    fig = go.Figure()
    
    # Couleurs pour les différents statuts
    colors = {
        'en cours': '#ffc107',  # Jaune
        'OK': '#007bff',       # Bleu
        'non démarré': '#28a745'  # Vert
    }
    
    # Ajout des tâches au graphique
    for _, task in df.iterrows():
        if pd.notna(task['deadline']):
            deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
            start_date = deadline.replace(day=1)
            days_remaining = get_days_remaining(task['deadline'])
            
            # Ajuster la couleur en fonction de la priorité
            if days_remaining < 0:
                color = '#ffc107'  # Jaune pour les tâches en retard
            elif days_remaining <= 7:
                color = '#ffc107'  # Jaune pour les tâches à surveiller
            else:
                color = colors.get(task['status'], '#28a745')  # Vert par défaut
            
            fig.add_trace(go.Bar(
                x=[(deadline - start_date).days],
                y=[task['task_name']],
                orientation='h',
                name=task['task_name'],
                marker_color=color,
                text=[f"Deadline: {task['deadline']}<br>Responsable: {task['responsible']}<br>Jours restants: {days_remaining}"],
                hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"
            ))
    
    # Mise à jour du layout
    fig.update_layout(
        title="Timeline des Tâches",
        xaxis_title="Jours avant deadline",
        yaxis_title="Tâches",
        showlegend=False,
        height=600,
        template="plotly_white",
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=7
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques détaillées
    st.subheader("📊 Statistiques détaillées")
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique de répartition par statut
        fig_status = px.pie(
            df,
            names='status',
            title='Répartition par statut',
            color_discrete_sequence=['#28a745', '#ffc107', '#007bff']  # Vert, Jaune, Bleu
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Graphique de répartition par responsable
        fig_responsible = px.bar(
            df.groupby('responsible').size().reset_index(name='count'),
            x='responsible',
            y='count',
            title='Tâches par responsable',
            color='responsible',
            color_discrete_sequence=['#28a745', '#ffc107', '#007bff']  # Vert, Jaune, Bleu
        )
        st.plotly_chart(fig_responsible, use_container_width=True)

with tab3:
    st.subheader("Ajouter une nouvelle tâche")
    
    with st.form("new_task_form"):
        task_name = st.text_input("📝 Nom de la tâche")
        description = st.text_area("📄 Description")
        
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("📊 Statut", ["Non démarré", "En cours", "OK"])
            responsible = st.multiselect("👥 Responsable(s)", ["Youness", "Mehdi", "Salma"])
        with col2:
            has_deadline = st.checkbox("📅 Définir une deadline", value=True)
            deadline = st.date_input("📅 Deadline", disabled=not has_deadline) if has_deadline else None
            comments = st.text_area("💬 Commentaires")
        
        submitted = st.form_submit_button("➕ Ajouter la tâche")
        
        if submitted:
            if not task_name or not description or not responsible:
                st.error("⚠️ Veuillez remplir tous les champs obligatoires")
            else:
                add_task(
                    task_name,
                    description,
                    status,
                    ", ".join(responsible),
                    deadline.strftime("%Y-%m-%d") if has_deadline and deadline else None,
                    comments
                )
                st.success("✅ Tâche ajoutée avec succès!") 