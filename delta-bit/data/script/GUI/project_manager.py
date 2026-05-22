from pathlib import Path
import json
import shutil

PROJECTS_DIR = Path('projects')
PROJECTS_DIR.mkdir(exist_ok=True)


# -------------------------
# PROGETTI
# -------------------------
def project_path(name: str):
    return PROJECTS_DIR / name


def subjects_file(name: str):
    return project_path(name) / 'subjects.json'


def new_project(name: str):
    path = project_path(name)

    if path.exists():
        return False

    path.mkdir()
    subjects_file(name).write_text('[]')
    return True


def list_projects():
    return [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()]


# -------------------------
# SUBJECTS
# -------------------------
def load_subjects(project: str):
    file = subjects_file(project)

    if not file.exists():
        return []

    return json.loads(file.read_text())


def save_subjects(project: str, data: list):
    subjects_file(project).write_text(json.dumps(data, indent=2))


def create_subject(project, name, info, tmp_path, filename):

    base = project_path(project)

    subjects = load_subjects(project)
    subject_id = len(subjects) + 1

    subject_dir = base / f"subject_{subject_id:03d}"
    subject_dir.mkdir(exist_ok=True)

    dest = subject_dir / filename

    shutil.copy(tmp_path, dest)

    meta = {
        "id": subject_id,
        "name": name,
        "info": info,
        "file": str(dest)
    }

    (subject_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    subjects.append(meta)
    save_subjects(project, subjects)

    return meta