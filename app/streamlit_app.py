# app/streamlit_app.py
import streamlit as st
from pathlib import Path
from pipeline import test_func
from file_browser import dir_browser

# =========================
# Input
# =========================
st.subheader("Cartella Input")
input_root = Path("/data/input")
input_dir = dir_browser(input_root, "input")
st.write("Input selezionato:", input_dir)

# =========================
# Output
# =========================
st.subheader("Cartella Output")
output_root = Path("/data/output")
output_dir = dir_browser(output_root, "output")
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
