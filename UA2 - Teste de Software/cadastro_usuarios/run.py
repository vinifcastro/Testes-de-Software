#!/usr/bin/env python3
"""
Launcher cross-platform para rodar o app Flask.

Uso:
  python run.py
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib.util
import time

PROJECT_ROOT = Path(__file__).parent.resolve()
PY = sys.executable  # garante o mesmo Python em Windows/Linux
IS_WINDOWS = os.name == "nt"

REQS = PROJECT_ROOT / "requirements.txt"
APP = PROJECT_ROOT / "app.py"

def sh(cmd, env=None, cwd=None):
    """Executa comando e faz stream do output."""
    print(f"\n$ {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=cwd or PROJECT_ROOT, env=env or os.environ.copy())
    proc.wait()
    if proc.returncode != 0:
        sys.exit(proc.returncode)

def ensure_requirements():
    if REQS.exists():
        # atualiza pip (seguro ignorar falhas) e instala deps
        try:
            sh([PY, "-m", "pip", "install", "--upgrade", "pip"])
        except SystemExit:
            pass
        sh([PY, "-m", "pip", "install", "-r", str(REQS)])
    else:
        print("requirements.txt não encontrado — pulando instalação de dependências.")

def init_db():
    # importa app.py e chama init_db() se existir
    spec = importlib.util.spec_from_file_location("app", str(APP))
    if not spec or not spec.loader:
        print("Não consegui carregar app.py.")
        sys.exit(1)
    app_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_mod)
    if hasattr(app_mod, "init_db"):
        print("\nInicializando banco de dados...")
        app_mod.init_db()
    else:
        print("Função init_db() não encontrada — pulando etapa de banco.")

def run_server():
    env = os.environ.copy()
    # deixando o debug ligado só em ambiente local
    env.setdefault("FLASK_DEBUG", "1")
    # Flask 3 não precisa de FLASK_APP se chamarmos diretamente app.py
    print("\nIniciando servidor Flask…")
    sh([PY, str(APP)], env=env)

def main():
    print(f"Sistema operacional: {'Windows' if IS_WINDOWS else 'Linux/Unix-like'}")
    print(f"Python: {sys.version.split()[0]}  |  Executável: {PY}")
    ensure_requirements()
    init_db()
    # pequeno delay opcional para logs ficarem legíveis
    time.sleep(0.3)
    run_server()

if __name__ == "__main__":
    main()
