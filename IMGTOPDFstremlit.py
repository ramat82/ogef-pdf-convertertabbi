import streamlit as st
import os
from PIL import Image
import io
from pathlib import Path
import base64
import re
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="OGEF – Convertisseur Images ➜ PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp', '.gif'}
MAX_PREVIEW_IMAGES = 20


# -------------------------------------------------
# CUSTOM STYLE
# -------------------------------------------------
def add_custom_style():
    st.markdown("""
    <style>
    /* Fond principal */
    .stApp {
        background: linear-gradient(135deg, #1a2b3c 0%, #2c3e50 100%);
        color: white !important;
    }

    /* Conteneur principal */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }

    /* Logo OGEF */
    .logo-container {
        text-align: center;
        margin: 20px 0 30px 0;
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(50, 205, 50, 0.3);
    }

    /* Titres */
    .main-title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
        background: linear-gradient(90deg, #32CD32, #00CED1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(50, 205, 50, 0.3);
    }

    .section-title {
        font-size: 24px;
        color: #32CD32;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(50, 205, 50, 0.3);
    }

    /* Cartes */
    .card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        border-color: #32CD32;
    }

    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #32CD32, #228B22);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        padding: 12px 24px;
        transition: all 0.3s ease;
        font-size: 16px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(50, 205, 50, 0.4);
    }

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        color: #aaa;
        font-weight: bold;
    }

    .stTabs [aria-selected="true"] {
        background-color: #32CD32 !important;
        color: white !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 25px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        border-top: 1px solid rgba(50, 205, 50, 0.2);
    }

    .signature {
        text-align: center;
        margin-top: 20px;
        font-size: 14px;
        color: #888;
        font-style: italic;
    }

    .signature strong {
        color: #32CD32;
        font-size: 16px;
    }

    /* Statut */
    .status-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
    }

    .success {
        background: rgba(0, 200, 83, 0.2);
        border-left: 5px solid #00C853;
    }

    .warning {
        background: rgba(255, 193, 7, 0.2);
        border-left: 5px solid #FFC107;
    }

    .error {
        background: rgba(244, 67, 54, 0.2);
        border-left: 5px solid #F44336;
    }

    /* Aperçu images */
    .image-preview {
        border: 2px solid rgba(50, 205, 50, 0.3);
        border-radius: 10px;
        padding: 5px;
        background: rgba(0, 0, 0, 0.2);
    }

    /* Tri */
    .sort-controls {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }

    </style>
    """, unsafe_allow_html=True)


add_custom_style()


# -------------------------------------------------
# LOGO OGEF
# -------------------------------------------------
def display_logo():
    """Affiche le logo OGEF avec gestion de fallback"""

    # Essayer de charger le logo local
    logo_path = "ogef_logo.png"

    if os.path.exists(logo_path):
        try:
            # Convertir l'image en base64
            with open(logo_path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode()

            logo_html = f"""
            <div class='logo-container'>
                <img src='data:image/png;base64,{b64_string}' 
                     style='max-height: 120px; max-width: 100%;' 
                     alt='Logo OGEF'>
            </div>
            """
        except:
            # Fallback si erreur de lecture
            logo_html = """
            <div class='logo-container'>
                <div style='font-size: 48px; color: #32CD32;'>📄</div>
                <div style='font-size: 28px; color: white; font-weight: bold; margin-top: 10px;'>
                    OGEF - Algérie
                </div>
            </div>
            """
    else:
        # Logo par défaut stylisé
        logo_html = """
        <div class='logo-container'>
            <div style='
                display: inline-block;
                background: linear-gradient(135deg, #32CD32, #228B22);
                padding: 20px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(50, 205, 50, 0.3);
            '>
                <div style='
                    background: white;
                    padding: 20px;
                    border-radius: 15px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                '>
                    <span style='font-size: 48px; color: #32CD32;'>📄</span>
                    <div style='
                        margin-top: 15px;
                        text-align: center;
                        color: #1a2b3c;
                    '>
                        <div style='font-size: 28px; font-weight: bold;'>OGEF</div>
                        <div style='font-size: 16px;'>Ordre des Géomètres Experts</div>
                        <div style='font-size: 14px; color: #666;'>Algérie</div>
                    </div>
                </div>
            </div>
        </div>
        """

    st.markdown(logo_html, unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Convertisseur Professionnel Images → PDF</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; margin-bottom:30px;'>"
                "Conversion avancée avec tri intelligent et options multiples</p>",
                unsafe_allow_html=True)


# -------------------------------------------------
# SORTING FUNCTIONS
# -------------------------------------------------
def natural_sort_key(s):
    """Clé de tri naturel pour les noms de fichiers"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]


def sort_images(image_list, sort_by="nom"):
    """Trie les images selon différents critères"""
    if not image_list:
        return []

    if sort_by == "nom":
        # Tri naturel (1, 2, 10 au lieu de 1, 10, 2)
        return sorted(image_list, key=natural_sort_key)

    elif sort_by == "date_creation":
        # Trier par date de création (du plus ancien au plus récent)
        images_with_dates = []
        for img in image_list:
            try:
                if "uploaded_file" in st.session_state:
                    # Pour les fichiers uploadés
                    file_path = img.name
                else:
                    # Pour les fichiers locaux
                    file_path = os.path.join(st.session_state.get("folder", ""), img)

                if os.path.exists(file_path):
                    creation_time = os.path.getctime(file_path)
                    images_with_dates.append((img, creation_time))
            except:
                images_with_dates.append((img, 0))

        return [img for img, _ in sorted(images_with_dates, key=lambda x: x[1])]

    elif sort_by == "taille":
        # Trier par taille (croissante)
        images_with_sizes = []
        for img in image_list:
            try:
                if "uploaded_file" in st.session_state:
                    size = len(img.getvalue())
                else:
                    file_path = os.path.join(st.session_state.get("folder", ""), img)
                    size = os.path.getsize(file_path)
                images_with_sizes.append((img, size))
            except:
                images_with_sizes.append((img, 0))

        return [img for img, _ in sorted(images_with_sizes, key=lambda x: x[1])]

    elif sort_by == "type":
        # Trier par type d'extension
        return sorted(image_list, key=lambda x: Path(x).suffix.lower())

    return sorted(image_list)


# -------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------
def init_session_state():
    """Initialise les variables de session"""
    defaults = {
        "folder": None,
        "uploaded_files": [],
        "selected_images": [],
        "sort_method": "nom",
        "current_tab": "dossier",
        "processing": False,
        "preview_images": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

# -------------------------------------------------
# DISPLAY LOGO
# -------------------------------------------------
display_logo()

# -------------------------------------------------
# MAIN TABS
# -------------------------------------------------
st.markdown("<div class='section-title'>📁 Méthode de Sélection</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📂 **Par Dossier**", "📄 **Par Fichiers**"])

with tab1:
    st.markdown("<div class='card'><h4 style='color:#32CD32; margin-bottom:15px;'>"
                "📂 Sélection par Dossier</h4>", unsafe_allow_html=True)

    # Option Tkinter pour sélection de dossier
    try:
        from tkinter import Tk, filedialog

        tkinter_available = True
    except:
        tkinter_available = False

    col1, col2 = st.columns([3, 1])

    with col1:
        folder_input = st.text_input(
            "Chemin du dossier :",
            value=st.session_state.folder or "",
            placeholder="Ex: C:/Users/OGEF/Images/Projet",
            help="Saisissez le chemin complet du dossier contenant les images"
        )

    with col2:
        if tkinter_available:
            if st.button("📁 Parcourir", use_container_width=True):
                try:
                    root = Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    folder_selected = filedialog.askdirectory(
                        title="Sélectionnez un dossier d'images"
                    )
                    root.destroy()

                    if folder_selected:
                        st.session_state.folder = folder_selected
                        st.session_state.current_tab = "dossier"
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")
        else:
            st.button("📁 Parcourir", disabled=True,
                      help="Tkinter non disponible sur cette plateforme")

    # Mettre à jour le dossier dans session_state
    if folder_input and os.path.isdir(folder_input):
        st.session_state.folder = folder_input

    # Afficher les images du dossier sélectionné
    if st.session_state.folder and os.path.isdir(st.session_state.folder):
        st.markdown("<div class='sort-controls'>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])

        with col1:
            sort_method = st.selectbox(
                "Trier les images par :",
                ["nom", "date_creation", "taille", "type"],
                index=0,
                help="Choisissez la méthode de tri des images"
            )

            if sort_method != st.session_state.sort_method:
                st.session_state.sort_method = sort_method
                st.rerun()

        with col2:
            reverse_order = st.checkbox("Ordre inversé", value=False)

        st.markdown("</div>", unsafe_allow_html=True)

        # Lire les images du dossier
        try:
            all_files = os.listdir(st.session_state.folder)
            image_files = [f for f in all_files
                           if Path(f).suffix.lower() in ALLOWED_EXTENSIONS]

            if image_files:
                # Trier les images
                sorted_images = sort_images(image_files, st.session_state.sort_method)
                if reverse_order:
                    sorted_images = list(reversed(sorted_images))

                st.markdown(f"<div class='status-box success'>✅ {len(sorted_images)} images trouvées</div>",
                            unsafe_allow_html=True)

                # Sélection multiple d'images
                st.write("### Sélectionnez les images à inclure :")

                # Cases à cocher pour toutes les images
                all_selected = st.checkbox("Tout sélectionner", value=True)

                # Grille de sélection
                cols = st.columns(4)
                selected_images = []

                for idx, img_file in enumerate(sorted_images):
                    with cols[idx % 4]:
                        if all_selected or st.checkbox(img_file, value=all_selected, key=f"img_{idx}"):
                            selected_images.append(img_file)

                st.session_state.selected_images = selected_images

                # Aperçu des images sélectionnées
                if selected_images:
                    st.write(f"### Aperçu ({len(selected_images)} images sélectionnées)")

                    # Limiter l'aperçu
                    preview_images = selected_images[:MAX_PREVIEW_IMAGES]
                    cols_preview = st.columns(min(4, len(preview_images)))

                    for idx, img_file in enumerate(preview_images):
                        with cols_preview[idx % 4]:
                            try:
                                img_path = os.path.join(st.session_state.folder, img_file)
                                image = Image.open(img_path)
                                st.image(image, caption=img_file, use_column_width=True)
                            except:
                                st.text(f"📄 {img_file}")

                    if len(selected_images) > MAX_PREVIEW_IMAGES:
                        st.info(f"... et {len(selected_images) - MAX_PREVIEW_IMAGES} autres images")

            else:
                st.markdown("<div class='status-box warning'>⚠️ Aucune image trouvée dans ce dossier</div>",
                            unsafe_allow_html=True)

        except PermissionError:
            st.markdown("<div class='status-box error'>❌ Permission refusée pour accéder à ce dossier</div>",
                        unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"<div class='status-box error'>❌ Erreur : {str(e)}</div>",
                        unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='card'><h4 style='color:#32CD32; margin-bottom:15px;'>"
                "📄 Sélection par Fichiers</h4>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Glissez-déposez vos images ici",
        type=['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'webp', 'gif'],
        accept_multiple_files=True,
        help="Sélectionnez plusieurs images à convertir en PDF"
    )

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.session_state.current_tab = "fichiers"

        st.markdown("<div class='sort-controls'>", unsafe_allow_html=True)
        sort_method_files = st.selectbox(
            "Trier les fichiers par :",
            ["nom", "taille", "type"],
            index=0,
            key="sort_files"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Préparer la liste des fichiers
        file_list = [f.name for f in uploaded_files]
        sorted_files = sort_images(file_list, sort_method_files)

        st.markdown(f"<div class='status-box success'>✅ {len(uploaded_files)} fichiers chargés</div>",
                    unsafe_allow_html=True)

        # Afficher les fichiers
        st.write("### Fichiers chargés :")
        cols = st.columns(4)

        for idx, file in enumerate(sorted_files):
            with cols[idx % 4]:
                # Afficher un aperçu miniature
                try:
                    img = Image.open(uploaded_files[idx])
                    st.image(img, caption=file, use_column_width=True)
                except:
                    st.text(f"📄 {file}")


# -------------------------------------------------
# PDF CREATION FUNCTIONS
# -------------------------------------------------
def create_pdf_from_folder(folder_path, image_files):
    """Crée un PDF à partir d'images d'un dossier"""
    images = []
    total = len(image_files)

    if total == 0:
        raise ValueError("Aucune image sélectionnée")

    # Barre de progression
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        for idx, filename in enumerate(image_files):
            # Mettre à jour la progression
            progress = (idx + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"📄 Traitement : {filename} ({idx + 1}/{total})")

            try:
                img_path = os.path.join(folder_path, filename)
                img = Image.open(img_path).convert("RGB")

                # Option de redimensionnement
                max_dimension = st.session_state.get("max_dimension", 2000)
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                images.append(img)

            except Exception as e:
                st.warning(f"⚠️ Image ignorée : {filename} - {str(e)}")
                continue

        if not images:
            raise ValueError("Aucune image valide n'a pu être traitée")

        # Créer le PDF
        status_text.text("🎯 Création du PDF en cours...")
        pdf_bytes = io.BytesIO()

        # Options de qualité
        quality = st.session_state.get("pdf_quality", 95)

        images[0].save(
            pdf_bytes,
            format='PDF',
            save_all=True,
            append_images=images[1:],
            quality=quality,
            optimize=True
        )
        pdf_bytes.seek(0)

        # Nettoyer
        for img in images:
            img.close()

        progress_bar.empty()
        status_text.empty()

        return pdf_bytes, len(images)

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        raise e


def create_pdf_from_uploaded_files(uploaded_files):
    """Crée un PDF à partir de fichiers uploadés"""
    images = []
    total = len(uploaded_files)

    if total == 0:
        raise ValueError("Aucun fichier sélectionné")

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        for idx, uploaded_file in enumerate(uploaded_files):
            progress = (idx + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"📄 Traitement : {uploaded_file.name} ({idx + 1}/{total})")

            try:
                img = Image.open(uploaded_file).convert("RGB")

                max_dimension = st.session_state.get("max_dimension", 2000)
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                images.append(img)

            except Exception as e:
                st.warning(f"⚠️ Fichier ignoré : {uploaded_file.name} - {str(e)}")
                continue

        if not images:
            raise ValueError("Aucun fichier valide n'a pu être traité")

        status_text.text("🎯 Création du PDF en cours...")
        pdf_bytes = io.BytesIO()

        quality = st.session_state.get("pdf_quality", 95)

        images[0].save(
            pdf_bytes,
            format='PDF',
            save_all=True,
            append_images=images[1:],
            quality=quality,
            optimize=True
        )
        pdf_bytes.seek(0)

        for img in images:
            img.close()

        progress_bar.empty()
        status_text.empty()

        return pdf_bytes, len(images)

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        raise e


# -------------------------------------------------
# SIDEBAR - OPTIONS
# -------------------------------------------------
with st.sidebar:
    st.markdown("<div class='card'><h4 style='color:#32CD32;'>⚙️ Options PDF</h4></div>",
                unsafe_allow_html=True)

    # Nom du fichier
    pdf_name = st.text_input(
        "Nom du fichier PDF :",
        value=f"OGEF_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        help="Nom du fichier PDF à télécharger"
    )

    # Qualité
    pdf_quality = st.slider(
        "Qualité du PDF :",
        min_value=50,
        max_value=100,
        value=95,
        help="Plus la qualité est élevée, plus le fichier sera volumineux"
    )
    st.session_state.pdf_quality = pdf_quality

    # Redimensionnement
    max_dimension = st.selectbox(
        "Dimension maximale :",
        options=["Original", "1000px", "1500px", "2000px", "2500px", "3000px"],
        index=3,
        help="Redimensionner les images si elles sont trop grandes"
    )

    if max_dimension == "Original":
        st.session_state.max_dimension = 10000  # Très grand
    else:
        st.session_state.max_dimension = int(max_dimension.replace("px", ""))

    st.markdown("---")

    # Statistiques
    if st.session_state.current_tab == "dossier" and st.session_state.selected_images:
        st.markdown("**📊 Statistiques :**")
        st.info(f"• Images sélectionnées : {len(st.session_state.selected_images)}\n"
                f"• Méthode de tri : {st.session_state.sort_method}\n"
                f"• Dossier : {os.path.basename(st.session_state.folder) if st.session_state.folder else 'N/A'}")

    elif st.session_state.current_tab == "fichiers" and st.session_state.uploaded_files:
        st.markdown("**📊 Statistiques :**")
        total_size = sum(len(f.getvalue()) for f in st.session_state.uploaded_files) // 1024
        st.info(f"• Fichiers chargés : {len(st.session_state.uploaded_files)}\n"
                f"• Taille totale : {total_size} Ko")

# -------------------------------------------------
# CREATE PDF BUTTON
# -------------------------------------------------
st.markdown("<div class='section-title'>🚀 Création du PDF</div>", unsafe_allow_html=True)

# Vérifier si des images sont disponibles
has_images = False
if st.session_state.current_tab == "dossier" and st.session_state.selected_images:
    has_images = True
    source_type = "dossier"
    image_count = len(st.session_state.selected_images)

elif st.session_state.current_tab == "fichiers" and st.session_state.uploaded_files:
    has_images = True
    source_type = "fichiers"
    image_count = len(st.session_state.uploaded_files)

if has_images:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🚀 **Créer le PDF**", type="primary", use_container_width=True):
            try:
                st.session_state.processing = True

                with st.spinner("📄 Conversion en cours..."):
                    if source_type == "dossier":
                        pdf_data, processed_count = create_pdf_from_folder(
                            st.session_state.folder,
                            st.session_state.selected_images
                        )
                    else:
                        pdf_data, processed_count = create_pdf_from_uploaded_files(
                            st.session_state.uploaded_files
                        )

                # Succès
                st.balloons()
                st.markdown(f"<div class='status-box success'>"
                            f"✅ PDF créé avec succès ! ({processed_count} images traitées)</div>",
                            unsafe_allow_html=True)

                # Bouton de téléchargement
                st.download_button(
                    label=f"⬇ Télécharger {pdf_name}",
                    data=pdf_data,
                    file_name=pdf_name,
                    mime="application/pdf",
                    icon="📥",
                    use_container_width=True,
                    key="download_pdf"
                )

                # Statistiques
                with st.expander("📊 Détails de la conversion"):
                    st.write(f"**Images traitées :** {processed_count}")
                    st.write(f"**Qualité :** {pdf_quality}%")
                    st.write(f"**Dimension max :** {max_dimension}")
                    st.write(f"**Date :** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            except Exception as e:
                st.markdown(f"<div class='status-box error'>❌ Erreur : {str(e)}</div>",
                            unsafe_allow_html=True)

            finally:
                st.session_state.processing = False
else:
    st.info("ℹ️ Veuillez sélectionner des images (par dossier ou fichiers) pour créer un PDF")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")

# Signature
st.markdown(
    """
    <div class='signature'>
        <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
            <div style='width: 30px; height: 2px; background: #32CD32;'></div>
            <span>Développé avec ❤️ par <strong>TABBI_Gef322</strong></span>
            <div style='width: 30px; height: 2px; background: #32CD32;'></div>
        </div>
        <div style='margin-top: 5px; font-size: 12px; color: #666;'>
            Solution professionnelle pour l'Ordre des Géomètres Experts Algérie
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Footer principal
st.markdown(
    """
    <div class='footer'>
        <div style='font-size: 18px; color: #32CD32; font-weight: bold; margin-bottom: 10px;'>
            OGEF – Ordre des Géomètres Experts Fonciers
        </div>
        <div style='font-size: 14px; color: #aaa;'>
            République Algérienne Démocratique et Populaire<br>
            <span style='font-size: 12px; color: #888;'>
                © 2025 Tous droits réservés | Version 2.0
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
