# app/streamlit_app.py
import streamlit as st
from pathlib import Path
from pipeline import test_func

st.title("Pipeline di segmentazione")
st.markdown("Seleziona le cartelle di input e output")

# =========================
# Funzione helper: selezione cartella con selectbox ricorsivo
# =========================
def choose_folder(start_path: Path, key_prefix=""):
    path = start_path
    while True:
        dirs = [p for p in path.iterdir() if p.is_dir()]
        if not dirs:
            break

        scelta = st.selectbox(
            f"Scegli cartella ({path})", ["--"] + [d.name for d in dirs], key=f"{key_prefix}_{path}"
        )
        if scelta == "--":
            break
        path = path / scelta

    return path

# =========================
# Input
# =========================
st.subheader("Cartella Input")
input_root = Path("/data/input")
input_dir = choose_folder(input_root, "input")
st.write("Input selezionato:", input_dir)

# =========================
# Output
# =========================
st.subheader("Cartella Output")
output_root = Path("/data/output")
output_dir = choose_folder(output_root, "output")
st.write("Output selezionato:", output_dir)

# =========================
# Esecuzione pipeline
# =========================
if st.button("Esegui segmentazione"):
    if not input_dir or not output_dir:
        st.error("Seleziona sia la cartella input che la cartella output!")
    else:
        try:
            test_func(input_dir, output_dir)
            st.success("Segmentazione completata!")
            st.write(f"Input: `{input_dir}`")
            st.write(f"Output: `{output_dir}`")
        except Exception as e:
            st.error(f"Errore durante la segmentazione: {e}")
