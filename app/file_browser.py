# app/file_browser.py
import streamlit as st
from pathlib import Path


def dir_browser(root: Path, key: str) -> Path | None:
    cwd_key = f"cwd_{key}"
    select_key = f"nav_{key}"
    confirm_key = f"confirm_{key}"
    selected_key = f"selected_{key}"

    if cwd_key not in st.session_state:
        st.session_state[cwd_key] = root

    cwd = st.session_state[cwd_key]

    st.caption(f"📁 Percorso corrente: `{cwd}`")

    # Directory disponibili (lazy)
    try:
        dirs = sorted(p for p in cwd.iterdir() if p.is_dir())
    except PermissionError:
        st.error("Permessi insufficienti")
        return None

    options = []
    if cwd != root:
        options.append(".. (su)")
    options.extend(d.name for d in dirs)

    choice = st.selectbox(
        "Naviga",
        options,
        index=None,
        key=select_key,
        placeholder="Seleziona una directory"
    )

    # Navigazione SOLO su azione esplicita
    if st.button("Apri", key=f"open_{key}") and choice:
        if choice == ".. (su)":
            st.session_state[cwd_key] = cwd.parent
        else:
            st.session_state[cwd_key] = cwd / choice

    # Conferma selezione
    if st.button("✅ Usa questa cartella", key=confirm_key):
        st.session_state[selected_key] = cwd

    return st.session_state.get(selected_key)
