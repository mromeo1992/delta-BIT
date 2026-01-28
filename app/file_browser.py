import streamlit as st
from pathlib import Path
from typing import Optional


def dir_browser(root: Path, key: str) -> Optional[Path]:
    cwd_key = f"{key}_cwd"
    selected_key = f"{key}_selected"
    choice_key = f"{key}_choice"

    # init state
    if cwd_key not in st.session_state:
        st.session_state[cwd_key] = root

    if selected_key not in st.session_state:
        st.session_state[selected_key] = root  # default sicuro

    cwd: Path = st.session_state[cwd_key]

    st.caption(f"📁 Percorso corrente: `{cwd}`")

    # elenco directory
    try:
        subdirs = sorted(p.name for p in cwd.iterdir() if p.is_dir())
    except Exception as e:
        st.error(f"Errore lettura directory: {e}")
        return st.session_state[selected_key]

    options = []
    if cwd != root:
        options.append("..")
    options.extend(subdirs)

    if not options:
        st.info("Nessuna sottocartella")
        return st.session_state[selected_key]

    # selectbox (NON naviga)
    choice = st.selectbox(
        "Naviga",
        options,
        key=choice_key,
    )

    # bottone che applica la navigazione
    if st.button("Apri", key=f"{key}_open"):
        if choice == "..":
            st.session_state[cwd_key] = cwd.parent
        else:
            st.session_state[cwd_key] = cwd / choice
        st.experimental_rerun()

    # conferma directory
    if st.button("✅ Usa questa cartella", key=f"{key}_confirm"):
        st.session_state[selected_key] = st.session_state[cwd_key]

    return st.session_state[selected_key]
