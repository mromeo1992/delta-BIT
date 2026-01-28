import streamlit as st
from pathlib import Path
from typing import Optional

def dir_browser(root: Path, key: str) -> Optional[Path]:
    """
    Directory browser dropdown compatibile Python 3.8,
    mantiene il path tra interazioni Streamlit.
    Se non viene selezionata alcuna cartella, di default usa `root`.
    """
    cwd_key = f"cwd_{key}"
    selected_key = f"selected_{key}"
    choice_key = f"select_{key}"

    # --- inizializza cwd e selected se mancanti ---
    if cwd_key not in st.session_state:
        st.session_state[cwd_key] = root

    if selected_key not in st.session_state:
        st.session_state[selected_key] = root  # default: root

    cwd = st.session_state[cwd_key]

    st.caption(f"📁 Percorso corrente: `{cwd}`")

    # --- lista directory ---
    try:
        dirs = sorted([p for p in cwd.iterdir() if p.is_dir()])
    except PermissionError:
        st.error("Permessi insufficienti")
        return st.session_state[selected_key]

    # --- opzioni selectbox ---
    options = [".. (su)"] if cwd != root else []
    options.extend([d.name for d in dirs])

    if not options:
        st.warning("Nessuna directory disponibile")
        return st.session_state[selected_key]

    # --- inizializza scelta selectbox ---
    if choice_key not in st.session_state or st.session_state[choice_key] not in options:
        st.session_state[choice_key] = options[0]

    # --- selectbox con callback per aggiornare cwd ---
    choice = st.selectbox(
        "Naviga",
        options,
        index=options.index(st.session_state[choice_key]),
        key=choice_key,
        on_change=lambda: update_cwd(cwd_key, choice_key, cwd)
    )

    # --- conferma selezione ---
    if st.button("✅ Usa questa cartella", key=f"confirm_{key}"):
        st.session_state[selected_key] = st.session_state[cwd_key]

    return st.session_state[selected_key]


def update_cwd(cwd_key: str, choice_key: str, cwd: Path):
    """
    Callback per aggiornare cwd nello session_state al cambio di selectbox
    """
    choice = st.session_state[choice_key]
    if choice == ".. (su)":
        st.session_state[cwd_key] = cwd.parent
    else:
        st.session_state[cwd_key] = cwd / choice
