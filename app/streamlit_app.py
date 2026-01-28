# app/streamlit_app.py
import streamlit as st
from pipeline import test_func

st.title("Pipeline di segmentazione")

st.markdown("Seleziona le cartelle (viste dal container)")

input_dir = st.text_input("Cartella input", "/data/input")
output_dir = st.text_input("Cartella output", "/data/output")

if st.button("Esegui segmentazione"):
    try:
        test_func(input_dir, output_dir)
        st.success("Segmentazione completata!")
    except Exception as e:
        st.error(f"Errore durante la segmentazione: {e}")
