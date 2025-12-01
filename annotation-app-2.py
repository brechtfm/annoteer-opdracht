import streamlit as st
from streamlit_annotation_tools import text_labeler
import json
import os

# scan_folder = "texts"
scans = [
    "NL-HaNA_1.04.02_1711_0191",
    "NL-HaNA_1.04.02_1711_0192",
    "NL-HaNA_1.04.02_1711_0193",
    "NL-HaNA_1.04.02_1711_0194",
    "NL-HaNA_1.04.02_1711_0195",
    "NL-HaNA_1.04.02_1711_0196",
    "NL-HaNA_1.04.02_1711_0197"
    "GM_6_351",
]

ANNOTATIONS_DIR = "annotations"

def ensure_annotations_dir():
    """Create annotations directory if it doesn't exist."""
    if not os.path.exists(ANNOTATIONS_DIR):
        os.makedirs(ANNOTATIONS_DIR)

def get_annotation_filename(scan_filename):
    """Generate annotation filename for a given scan."""
    return os.path.join(ANNOTATIONS_DIR, f"{scan_filename}.json")

def load_annotations(scan_filename):
    """Load saved annotations for a scan file."""
    annotation_file = get_annotation_filename(scan_filename)
    try:
        if os.path.exists(annotation_file):
            with open(annotation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Could not load annotations: {str(e)}")
    
    # Return default labels if no saved annotations
    return {
        "Persoon": [],
        "Organisatie": [],
        "Locatie": [],
        "Datum": [],
    }

def save_annotations(scan_filename, labels):
    """Save annotations for a scan file."""
    ensure_annotations_dir()
    annotation_file = get_annotation_filename(scan_filename)
    try:
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(labels, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving annotations: {str(e)}")
        return False

def load_text_from_file(filename):
    """Load text content from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"File not found: {filename}")
        return ""
    except Exception as e:
        st.error(f"Error reading file {filename}: {str(e)}")
        return ""

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Text Annotator",
        page_icon="📜",
        layout="wide"
    )
    
    st.title("📜 Annotatie Opdracht")
    
    # File selection
    selected_file = st.selectbox(
        "Selecteer pagina:",
        scans,
        index=0
    )
    
    # Load text from selected file
    
    text_snippet = load_text_from_file(f"texts/{selected_file}.txt")
    
    if text_snippet:
        # Clean the text
        text_snippet = text_snippet.replace("\n", " ").replace("„ „", "")
        
        # Load existing annotations for this file
        labels = load_annotations(selected_file)
        
        st.subheader("✍️ Annoteer")
        updated_labels = text_labeler(text_snippet, labels)
        
        # Save button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("💾 Sla annotaties op", type="primary"):
                if save_annotations(selected_file, updated_labels):
                    st.success("Annotaties succesvol opgeslages!")
        
        with col2:
            # Check if annotations exist for this file
            if os.path.exists(get_annotation_filename(selected_file)):
                st.info("📝 Vooropgeslagen annotaties geladen")
        
        # Download button for exporting annotations
        st.download_button(
            label="📥 Download Annotations (JSON)",
            data=json.dumps(updated_labels, indent=2, ensure_ascii=False),
            file_name=f"annotations_{selected_file}.json",
            mime="application/json"
        )
    
    with st.sidebar:
        st.header("ℹ️ Standaard entiteitcategoriën")
        st.markdown(f"""
        1. Datum
        2. Persoon 
        3. Organisatie
        4. Locatie
        
        🔗 **[GLOBALISE transcription viewer](https://transcriptions.globalise.huygens.knaw.nl/detail/urn:globalise:{selected_file})**
        """)
        
        # Show annotation progress
        st.header("📊 Vooruitgang")
        annotated_count = sum(1 for scan in scans 
                             if os.path.exists(get_annotation_filename(scan)))
        st.metric("Documents Annotated", f"{annotated_count}/{len(scans)}")
        
        # List annotated files
        if annotated_count > 0:
            st.markdown("**Geannoteerde documenten:**")
            for scan in scans:
                if os.path.exists(get_annotation_filename(scan)):
                    st.markdown(f"✅ {scan}")

if __name__ == "__main__":
    main()

