import streamlit as st
import pandas as pd
from collections import defaultdict
import math
import json
import os

# ==========================================
# 1. CONNEXION GOOGLE SHEETS (Le Cerveau)
# ==========================================
# ⚠️ REMPLACE CETTE LIGNE PAR L'ID DE TON FICHIER GOOGLE SHEETS :
SHEET_ID = "13-YI0dvqNnVOD5t5MXc69rP1yvl0SHh3HdPgnRp1XAA" 

@st.cache_data(ttl=60)
def charger_base_google(profil):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={profil}"
    db = defaultdict(dict)
    try:
        df = pd.read_csv(url)
        for _, row in df.iterrows():
            plat = str(row.iloc[0]).strip()
            ing = str(row.iloc[1]).strip()
            try:
                qte = float(str(row.iloc[2]).replace(',', '.'))
            except ValueError:
                qte = 1.0 
            db[plat][ing] = qte
        return dict(db)
    except Exception as e:
        return None

# ==========================================
# 2. BOÎTE À IDÉES & BUDGET
# ==========================================
idees_db = {
    "Vegan (100% Végétal)": {
        "Printemps / Été": {
            "PT8 - Chia Pudding Amande": {"Graines de chia (g)": 30, "Lait d'amande (ml)": 150, "Sirop d'érable (càs)": 1, "Framboises (g)": 50},
            "C8 - Smoothie Protéiné": {"Lait de coco (ml)": 150, "Banane": 1, "Protéine végétale (g)": 30},
            "R31 - Bowl Tofu Fumé": {"Quinoa (g)": 100, "Tofu fumé (g)": 100, "Tomates cerises (g)": 100, "Avocat": 0.5},
        },
        "Automne / Hiver": {
            "PT9 - Tartines Beurre Cacahuète": {"Pain complet (tranches)": 2, "Beurre de cacahuète 100% (càs)": 2, "Banane": 1},
            "R33 - Velouté Courge & Coco": {"Courge/Potiron (g)": 300, "Lait de coco (ml)": 100, "Oignon(s)": 1, "Pain complet (tranches)": 2},
            "R43 - Chili Vegan Soja": {"Haricots rouges (g)": 150, "Protéines de soja texturées (g)": 50, "Tomates concassées (g)": 150, "Maïs (g)": 50},
        }
    },
    "Végétarien (Avec œufs/produits laitiers)": {
        "Printemps / Été": {
            "PT10 - Yaourt Grec Fruits Rouges": {"Yaourt grec (g)": 200, "Framboises (g)": 50, "Flocons d'avoine (g)": 40},
            "R35 - Tarte Tomate Moutarde": {"Pâte brisée": 1, "Tomate(s)": 3, "Moutarde (càs)": 2, "Fromage râpé (g)": 50},
            "R46 - Omelette Feta Courgette": {"Oeuf(s)": 3, "Courgette": 1, "Feta (g)": 40, "Pain complet (tranches)": 2}
        },
        "Automne / Hiver": {
            "PT11 - Oeufs Brouillés Champignons": {"Oeuf(s)": 3, "Champignons (g)": 100, "Pain complet (tranches)": 2},
            "R36 - Gratin Chou-Fleur": {"Chou-fleur (tête)": 0.5, "Crème allégée (ml)": 100, "Fromage râpé (g)": 50, "Pommes de terre": 2},
            "R47 - Risotto Champignons": {"Riz Arborio (g)": 100, "Champignons (g)": 150, "Parmesan (g)": 30, "Bouillon légumes (cube)": 0.5},
        }
    },
    "Flexitarien (30-40% de Viande/Poisson)": {
        "Printemps / Été": {
            "PT12 - Tartine Avocat Oeuf": {"Pain complet (tranches)": 2, "Avocat": 0.5, "Oeuf(s)": 1},
            "R37 - Brochettes Poulet": {"Blanc de poulet (g)": 150, "Poivron(s)": 1, "Riz basmati (g)": 100, "Huile d'olive (càs)": 1},
            "R38 - Salade Saumon": {"Saumon fumé (tranches)": 2, "Salade verte (sachet)": 0.5, "Concombre": 0.5, "Avocat": 0.5},
        },
        "Automne / Hiver": {
            "PT13 - Toast Bacon Oeufs": {"Pain complet (tranches)": 2, "Bacon (g)": 50, "Oeuf(s)": 2},
            "R39 - Saucisses Lentilles": {"Saucisse de Toulouse": 1, "Lentilles vertes crues (g)": 100, "Carotte(s)": 1, "Oignon(s)": 1},
            "R51 - Hachis Parmentier": {"Pommes de terre": 3, "Steak haché 5%": 1, "Lait (ml)": 50, "Fromage râpé (g)": 30},
        }
    }
}

ing_prix = {
    "Oeuf(s)": 0.25, "Riz basmati (g)": 0.003, "Pâtes (g)": 0.0015, "Lentilles corail (g)": 0.0035,
    "Lentilles vertes crues (g)": 0.003, "Pois chiches (g)": 0.002, "Haricots rouges (g)": 0.002,
    "Blanc de poulet (g)": 0.012, "Steak haché 5%": 1.50, "Thon au naturel (boîte)": 1.30,
    "Protéines de soja texturées (g)": 0.006, "Tofu ferme (g)": 0.008, "Tofu fumé (g)": 0.009,
    "Yaourt grec (g)": 0.004, "Feta (g)": 0.012, "Flocons d'avoine (g)": 0.002, "Banane": 0.30,
    "Tomate(s)": 0.40, "Pain complet (tranches)": 0.15, "Tortillas": 0.30, "Lait (ml)": 0.001,
    "Lait de coco (ml)": 0.004, "Avocat": 1.20, "Bacon (g)": 0.015, "Crevettes (g)": 0.018
}

def get_prix(ing, qte):
    prix_unitaire = ing_prix.get(ing, 0.50)
    if "(g)" not in ing and "(ml)" not in ing and ing not in ing_prix: prix_unitaire = 0.50
    elif ing not in ing_prix: prix_unitaire = 0.005 
    return prix_unitaire * qte

magasins = {"Carrefour Market (Villeurbanne)": 1.0, "Lidl / Aldi (Éco)": 0.80, "E.Leclerc / Hyper U": 0.90, "Casino / Monoprix": 1.20}

def get_categorie(ingredient):
    frais = ["Oeuf(s)", "Philadelphia Light (g)", "St Moret protéiné (g)", "Yaourt grec (g)", "Feta (g)", "Lait (ml)", "Crème allégée (ml)", "Mozzarella (g)", "Ricotta (g)", "Parmesan (g)", "Fromage râpé (g)", "Pâte brisée", "Gorgonzola (g)", "Skyr (g)"]
    viandes = ["Blanc de dinde (tranches)", "Jambon végétal (tranche)", "Thon au naturel (boîte)", "Blanc de poulet (g)", "Steak haché 5%", "Tofu ferme (g)", "Tofu fumé (g)", "Protéines de soja texturées (g)", "Saumon fumé (tranches)", "Saucisse de Toulouse", "Cuisse de poulet", "Crevettes (g)", "Bacon (g)"]
    legumes = ["Tomate(s)", "Concombre", "Epinards frais (poignée)", "Champignons (g)", "Banane", "Courgette", "Oignon(s)", "Poivron(s)", "Tomates cerises (g)", "Carotte(s)", "Pommes de terre", "Salade verte (sachet)", "Tomates concassées (g)", "Brocoli (tête)", "Haricots verts (g)", "Courge/Potiron (g)", "Patate douce", "Navet(s)", "Aubergine", "Courge butternut (g)", "Avocat", "Chou-fleur (tête)", "Pomme ou Poire", "Framboises (g)"]
    boulangerie = ["Pain complet (tranches)", "Wäsa fibre", "Pain de mie complet (tranches)", "Muffin complet", "Tortillas", "Pain burger complet"]
    
    if any(i in ingredient for i in frais): return "🧀 Frais & Laitiers"
    if any(i in ingredient for i in viandes): return "🥩 Viandes, Poissons & Simili"
    if any(i in ingredient for i in legumes): return "🥦 Fruits & Légumes"
    if any(i in ingredient for i in boulangerie): return "🥖 Boulangerie"
    return "🥫 Épicerie (Sec, Sauces & Divers)"

# ==========================================
# 3. GESTION DES SAUVEGARDES LOCALES
# ==========================================
SAVE_FILE = "mes_semaines.json"
def charger_sauvegardes():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def sauvegarder_semaine(nom, data, profil):
    saves = charger_sauvegardes()
    if profil not in saves: saves[profil] = {}
    saves[profil][nom] = data
    with open(SAVE_FILE, "w", encoding="utf-8") as f: json.dump(saves, f, indent=4)

# ==========================================
# 4. INTERFACE WEB 
# ==========================================
st.set_page_config(page_title="Meal Planner Pro", page_icon="🛒", layout="centered")

# --- SÉLECTEUR DE PROFIL ---
st.sidebar.title("👤 Qui es-tu ?")
# J'AI MODIFIÉ CETTE LIGNE POUR GARDER UNIQUEMENT TON PROFIL :
profil_choisi = st.sidebar.selectbox("Choisis ton profil :", ["Tristan"])
st.sidebar.markdown("---")

db_sheet = charger_base_google(profil_choisi)

if 'profil_actuel' not in st.session_state or st.session_state.profil_actuel != profil_choisi:
    st.session_state.profil_actuel = profil_choisi
    if db_sheet:
        st.session_state.recettes_db = db_sheet
    else:
        st.session_state.recettes_db = {}
        
if not st.session_state.recettes_db:
    st.error(f"⚠️ Aucun repas trouvé pour '{profil_choisi}'. Crée un onglet à ce nom dans ton Google Sheets !")
    st.stop()

st.title("🛒 Générateur de Courses Pro")
tab_plan, tab_idees, tab_save = st.tabs(["📝 Planification & Courses", "💡 Boîte à Idées", "💾 Sauvegardes"])

liste_pt = ["- Aucun -"] + [k for k in st.session_state.recettes_db.keys() if k.startswith("PT")]
liste_c = ["- Aucun -"] + [k for k in st.session_state.recettes_db.keys() if k.startswith("C")]
liste_r = ["- Aucun -"] + [k for k in st.session_state.recettes_db.keys() if k.startswith("R")]

# --- ONGLET 1 : PLANIFICATION ---
with tab_plan:
    c_p1, c_p2, c_p3 = st.columns(3)
    nb_jours = c_p1.number_input("Nombre de jours", 1, 30, 7)
    nb_personnes = c_p2.number_input("Personnes", 1, 5, 1)
    profil_mangeur = c_p3.selectbox("Appétit", ["Normal (x1)", "Gros Mangeur (x1.5)"])

    mult_global = nb_personnes * (1.5 if "Gros" in profil_mangeur else 1.0)

    st.markdown("---")
    st.header("🍽️ Planification des repas")
    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    repas_selectionnes = []
    choix_actuels = {}

    for i in range(nb_jours):
        nom_jour = jours_semaine[i % 7] if i < 7 else f"{jours_semaine[i % 7]} (S{i//7 + 1})"
        
        with st.expander(f"📅 {nom_jour}", expanded=False):
            c1, c2 = st.columns(2)
            pt = c1.selectbox("Petit-Déjeuner", liste_pt, key=f"pt_{i}")
            midi = c1.selectbox("Midi", liste_r, key=f"midi_{i}")
            col = c2.selectbox("Collation", liste_c, key=f"c_{i}")
            soir = c2.selectbox("Soir", liste_r, key=f"soir_{i}")
            
            choix_actuels[f"pt_{i}"] = pt
            choix_actuels[f"midi_{i}"] = midi
            choix_actuels[f"c_{i}"] = col
            choix_actuels[f"soir_{i}"] = soir
            
            for r in [pt, midi, col, soir]:
                if r != "- Aucun -": repas_selectionnes.append(r)

    st.markdown("---")
    st.header("📦 Stocks, Budget & Liste")
    
    magasin = st.selectbox("Où fais-tu tes courses ?", list(magasins.keys()))
    mult_magasin = magasins[magasin]

    liste_brute = defaultdict(float)
    budget_estime = 0.0
    
    for repas in repas_selectionnes:
        for ing, qte in st.session_state.recettes_db[repas].items():
            qte_reelle = qte * mult_global
            liste_brute[ing] += qte_reelle
            budget_estime += get_prix(ing, qte_reelle) * mult_magasin

    if not liste_brute:
        st.info("Sélectionne des repas pour générer la liste.")
    else:
        st.metric("💶 Budget Estimé", f"{budget_estime:.2f} €")
        st.write("Ajuste les quantités en stock :")
        stocks_utilisateurs = {}
        
        cols = st.columns(3)
        i = 0
        for ing, qte_necessaire in sorted(liste_brute.items()):
            with cols[i % 3]:
                qte_arrondie = math.ceil(qte_necessaire) if qte_necessaire.is_integer() else round(qte_necessaire, 1)
                stocks_utilisateurs[ing] = st.number_input(f"{ing} ({qte_arrondie})", min_value=0.0, value=0.0, step=1.0)
            i += 1
            
        if st.button("🚀 GÉNÉRER LA LISTE FINALE", type="primary", use_container_width=True):
            st.markdown("---")
            liste_finale = defaultdict(dict)
            texte_fichier = f"🛒 MA LISTE DE COURSES ({profil_choisi})\n=======================\n\n"
            
            for ing, qte_necessaire in liste_brute.items():
                a_acheter = qte_necessaire - stocks_utilisateurs[ing]
                if a_acheter > 0:
                    liste_finale[get_categorie(ing)][ing] = a_acheter
                    
            if not liste_finale:
                st.success("🎉 Tu as déjà tout en stock !")
            else:
                for cat in sorted(liste_finale.keys()):
                    st.subheader(cat)
                    texte_fichier += f"{cat}\n"
                    for ing, qte in sorted(liste_finale[cat].items()):
                        affichage_qte = math.ceil(qte) if qte.is_integer() else round(qte, 1)
                        st.markdown(f"- **{affichage_qte}** x {ing}")
                        texte_fichier += f"[ ] {affichage_qte} x {ing}\n"
                    texte_fichier += "\n"

                st.download_button(
                    label="📄 Télécharger ma liste (.txt)",
                    data=texte_fichier,
                    file_name=f"courses_{profil_choisi}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# --- ONGLET 2 : BOÎTE À IDÉES ---
with tab_idees:
    st.header("💡 Explore de nouveaux menus")
    col_regime, col_saison = st.columns(2)
    with col_regime: choix_regime = st.selectbox("Type d'alimentation", list(idees_db.keys()))
    with col_saison: choix_saison = st.selectbox("Saison", list(idees_db[choix_regime].keys()))
        
    def ajouter_a_ma_base(nom_recette, ingredients):
        if nom_recette not in st.session_state.recettes_db:
            st.session_state.recettes_db[nom_recette] = ingredients
            st.toast(f"✅ Ajouté à ta session !")
            st.info("💡 Astuce : Ajoute cette recette dans ton onglet Google Sheets pour la garder à vie.")
            
    for nom_recette, ingredients in idees_db[choix_regime][choix_saison].items():
        with st.container():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{nom_recette}**")
            c1.caption(f"Ingrédients : {', '.join([f'{k}' for k in ingredients.keys()])}")
            
            if nom_recette in st.session_state.recettes_db:
                c2.button("✅ Ajouté", key=f"done_{nom_recette}", disabled=True)
            else:
                c2.button("➕ Tester", key=f"add_{nom_recette}", on_click=ajouter_a_ma_base, args=(nom_recette, ingredients))
            st.write("---")

# --- ONGLET 3 : SAUVEGARDES ---
with tab_save:
    st.header("💾 Mes Semaines Types")
    saves = charger_sauvegardes()
    mes_saves = saves.get(profil_choisi, {})
    
    nom_sauvegarde = st.text_input("Nom de la semaine (ex: Semaine Classique)")
    if st.button("Sauvegarder la planification actuelle"):
        if nom_sauvegarde:
            sauvegarder_semaine(nom_sauvegarde, choix_actuels, profil_choisi)
            st.success(f"Semaine '{nom_sauvegarde}' sauvegardée pour {profil_choisi} !")
            st.rerun()
            
    st.markdown("---")
    st.subheader("Charger une semaine type")
    if mes_saves:
        choix_load = st.selectbox("Sélectionne une sauvegarde", list(mes_saves.keys()))
        if st.button("Charger ce menu"):
            for k, v in mes_saves[choix_load].items():
                st.session_state[k] = v
            st.success("Menu chargé ! Retourne dans l'onglet Planification.")
    else:
        st.write(f"Aucune sauvegarde pour {profil_choisi} pour le moment.")
