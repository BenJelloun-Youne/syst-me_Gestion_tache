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
    /* Style général */
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px;
        gap: 1rem;
        padding: 1rem;
        margin: 0.5rem;
        transition: all 0.3s ease;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007bff;
        color: white;
        box-shadow: 0 4px 6px rgba(0,123,255,0.2);
    }
    
    /* Style de la sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        padding: 2rem 1rem;
        box-shadow: 2px 0 5px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        background-color: #ffffff;
    }
    
    /* Style des sélecteurs */
    .stSelectbox, .stMultiselect {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        padding: 0.5rem;
    }
    
    /* Style des métriques */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Style des boutons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,123,255,0.2);
    }
    
    /* Style des expanders */
    div[data-testid="stExpander"] div[data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stExpander"] div[data-testid="stExpander"]:hover {
        border-color: #007bff;
        box-shadow: 0 4px 8px rgba(0,123,255,0.1);
        transform: translateY(-2px);
    }
    
    /* Couleurs des statuts */
    .no-deadline {
        color: #28a745;
        font-style: italic;
        font-weight: 500;
    }
    
    .urgent {
        color: #ffc107;
        font-weight: 600;
    }
    
    .warning {
        color: #ffc107;
        font-weight: 600;
    }
    
    .success {
        color: #007bff;
        font-weight: 600;
    }
    
    /* Style du titre principal */
    h1 {
        color: #2E4053;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Style des sous-titres */
    h2, h3 {
        color: #2E4053;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Style des séparateurs */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #e9ecef, transparent);
        margin: 2rem 0;
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
    if deadline_date.date() < today:
        return None
    return (deadline_date.date() - today).days

def get_deadline_status(days_remaining, current_status):
    if days_remaining is None:
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
        if current_status == "OK":
            return "Délai respecté"
        else:
            return "En retard"
    elif days_remaining <= 7:
        return f"{days_remaining} jours restants"
    else:
        return f"{days_remaining} jours restants"

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <img src="https://img.icons8.com/fluency/96/task.png" width="80" style='margin-bottom: 1rem;'>
            <h2 style='color: #2E4053; margin: 0;'>Menu</h2>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Filtres globaux avec style amélioré
    st.markdown("### 🎯 Filtres")
    status_filter = st.multiselect(
        "📊 Statut",
        ["Tous", "Non démarré", "En cours", "OK"],
        default=["Tous"]
    )
    
    responsible_filter = st.multiselect(
        "👥 Responsable",
        ["Tous", "Youness", "Mehdi", "Salma"],
        default=["Tous"]
    )
    
    priority_filter = st.multiselect(
        "⚡ Priorité",
        ["Tous", "Urgent", "À surveiller", "Dans les temps"],
        default=["Tous"]
    )
    
    st.markdown("---")
    st.markdown("### 📈 Statistiques rapides")
    
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
        'OK': '#007bff',       # Bleu pour les tâches terminées
        'en cours': '#ffc107',  # Jaune pour les tâches en cours
        'non démarré': '#28a745'  # Vert pour les tâches non démarrées
    }
    
    # Calculer la plage de dates pour l'axe X
    min_date = None
    max_date = None
    
    # Trouver la première et la dernière date dans les deadlines
    for _, task in df.iterrows():
        if pd.notna(task['deadline']):
            deadline = datetime.strptime(task['deadline'], '%Y-%m-%d').date()
            if min_date is None or deadline < min_date:
                min_date = deadline
            if max_date is None or deadline > max_date:
                max_date = deadline
    
    # Si aucune date n'est trouvée, utiliser la date d'aujourd'hui
    if min_date is None:
        min_date = datetime.now().date()
    if max_date is None:
        max_date = min_date + timedelta(days=30)
    else:
        # Ajouter 30 jours à la date maximale pour la visualisation
        max_date = max_date + timedelta(days=30)
    
    # Créer les dates pour l'axe X
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Ajout des tâches au graphique
    for _, task in df.iterrows():
        if pd.notna(task['deadline']):
            deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
            days_remaining = get_days_remaining(task['deadline'])
            
            # Déterminer la couleur en fonction du statut
            if task['status'] == 'OK':
                color = colors['OK']  # Bleu pour les tâches terminées
            elif days_remaining is None and task['status'] != 'OK':
                color = '#ffc107'  # Jaune pour les tâches en retard
            else:
                color = colors[task['status']]  # Couleur selon le statut
            
            # Calculer la position sur l'axe X
            x_position = (deadline.date() - min_date).days
            
            # Créer le texte pour le tooltip
            status_text = "Terminée" if task['status'] == 'OK' else (
                "En retard" if days_remaining is None else f"{days_remaining} jours restants"
            )
            
            fig.add_trace(go.Bar(
                x=[x_position],
                y=[task['task_name']],
                orientation='h',
                name=task['task_name'],
                marker_color=color,
                text=[f"Deadline: {task['deadline']}<br>Responsable: {task['responsible']}<br>Statut: {task['status']}<br>{status_text}"],
                hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"
            ))
    
    # Mise à jour du layout avec les dates
    fig.update_layout(
        title="Timeline des Tâches",
        xaxis_title="Dates",
        yaxis_title="Tâches",
        showlegend=False,
        height=600,
        template="plotly_white",
        xaxis=dict(
            tickmode='array',
            ticktext=[d.strftime('%d/%m/%Y') for d in date_range[::7]],  # Afficher une date par semaine
            tickvals=list(range(0, len(date_range), 7)),
            tickangle=45
        )
    )
    
    # Ajouter une ligne verticale pour la date d'aujourd'hui
    today = datetime.now().date()
    if min_date <= today <= max_date:
        today_index = (today - min_date).days
        fig.add_vline(
            x=today_index,
            line_dash="dash",
            line_color="red",
            annotation_text="Aujourd'hui",
            annotation_position="top right"
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