#!/usr/bin/env python3
"""
========================================================================
 SECURITY_CHECK.PY - Verification reelle de securite avant publication
========================================================================

Verifie 2 choses concretes, avant chaque git push :
1. Que le fichier .env n'est PAS suivi par Git (donc jamais publie sur GitHub)
2. Qu'aucun texte ressemblant a une cle API n'est present dans les fichiers
   qui vont etre publies (detection de motifs comme cles Groq, tokens
   Telegram, etc., au cas ou quelqu'un aurait colle une cle par erreur
   dans un fichier de code au lieu du .env)

Retourne 0 si tout est sain, 1 si un probleme de securite est detecte.
========================================================================
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent  # gaming-site2/, le depot git

# Motifs qui ressemblent a des cles/tokens sensibles
SECRET_PATTERNS = [
    (r"gsk_[A-Za-z0-9]{20,}", "cle API Groq"),
    (r"\d{8,10}:AA[A-Za-z0-9_-]{30,}", "token Bot Telegram"),
    (r"AIza[A-Za-z0-9_-]{30,}", "cle API Google"),
    (r"sk-[A-Za-z0-9]{20,}", "cle API OpenAI/style sk-"),
]


def check_env_not_tracked():
    """Verifie que .env n'est pas suivi par git (donc ne sera jamais publie)."""
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", ".env"],
        cwd=str(REPO_DIR), capture_output=True, text=True
    )
    # Si la commande reussit (code 0), ca veut dire que .env EST suivi par git = danger
    return result.returncode != 0


def scan_files_for_secrets():
    """Scanne tous les fichiers qui seraient publies pour des cles API en clair."""
    problemes = []

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_DIR), capture_output=True, text=True
    )
    fichiers_modifies = [line[3:].strip() for line in result.stdout.splitlines()]

    # On scanne aussi tous les fichiers deja suivis, pas seulement les nouveaux
    result_tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=str(REPO_DIR), capture_output=True, text=True
    )
    tous_fichiers = set(fichiers_modifies) | set(result_tracked.stdout.splitlines())

    for filename in tous_fichiers:
        filepath = REPO_DIR / filename
        if not filepath.exists() or not filepath.is_file():
            continue
        if filename == ".env" or filename.endswith(".env"):
            continue  # normal qu'il y ait des cles ici, tant qu'il n'est pas suivi par git

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, nom in SECRET_PATTERNS:
            if re.search(pattern, content):
                problemes.append(f"{filename} -> contient ce qui ressemble a une {nom}")

    return problemes


def main():
    print("=" * 60)
    print(" VERIFICATION DE SECURITE")
    print("=" * 60)

    erreurs = []

    if not check_env_not_tracked():
        erreurs.append(".env est suivi par Git ! Il risque d'etre publie publiquement avec tes cles API.")

    secrets_trouves = scan_files_for_secrets()
    erreurs.extend(secrets_trouves)

    if erreurs:
        print(f"\n[ALERTE SECURITE] {len(erreurs)} probleme(s) detecte(s) :")
        for e in erreurs:
            print(f"   - {e}")
        print("\nLa publication est BLOQUEE tant que ce n'est pas corrige.")
        sys.exit(1)
    else:
        print("\n[OK] Aucun probleme de securite detecte.")
        sys.exit(0)


if __name__ == "__main__":
    main()
