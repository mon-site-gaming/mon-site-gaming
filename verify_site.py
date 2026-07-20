#!/usr/bin/env python3
"""
========================================================================
 VERIFY_SITE.PY - Verificateur de liens casses (QA reel)
========================================================================

Verifie que TOUS les liens internes du site genere pointent bien vers
des fichiers qui existent reellement, avant toute publication.

Retourne un code de sortie 0 si tout est bon, 1 si des liens sont casses.
Utilise par agent4_orchestrator.py et agent5_telegram_commands.py pour
bloquer automatiquement le git push si un probleme est detecte.

Usage :
    python verify_site.py
========================================================================
"""

import re
import sys
import io
from pathlib import Path

# Force un encodage UTF-8 sur la sortie, meme sur console Windows qui utilise
# souvent un encodage different par defaut (evite les plantages sur les accents/emojis)
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SITE_DIR = Path(__file__).parent  # ce script vit dans gaming-site2/


def get_all_html_files():
    return list(SITE_DIR.glob("*.html"))


def extract_internal_links(html_content: str):
    """Extrait tous les liens internes (pas http/https, pas ancre pure #)."""
    links = re.findall(r'href="([^"]+)"', html_content)
    internal = []
    for link in links:
        if link.startswith("http://") or link.startswith("https://"):
            continue  # lien externe, pas notre probleme ici
        if link.startswith("#"):
            continue  # ancre pure, pas un fichier
        if link.startswith("mailto:"):
            continue
        internal.append(link)
    return internal


def check_broken_links():
    html_files = get_all_html_files()
    erreurs = []
    avertissements = []

    if not html_files:
        return ["Aucun fichier HTML trouve dans le site."], []

    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8")
        internal_links = extract_internal_links(content)

        for link in internal_links:
            target = (SITE_DIR / link).resolve()
            if not target.exists():
                erreurs.append(f"{html_file.name} -> lien casse vers '{link}' (fichier introuvable)")

        # Verification complementaire : lien d'affiliation encore en placeholder
        if "#lien-a-venir" in content:
            avertissements.append(f"{html_file.name} -> utilise encore le lien placeholder '#lien-a-venir'")

    return erreurs, avertissements


def main():
    print("=" * 60)
    print(" VERIFICATION DU SITE (QA avant publication)")
    print("=" * 60)

    erreurs, avertissements = check_broken_links()

    if avertissements:
        print(f"\n[AVERTISSEMENT] {len(avertissements)} avertissement(s) (non bloquant) :")
        for a in avertissements:
            print(f"   - {a}")

    if erreurs:
        print(f"\n[ERREUR] {len(erreurs)} erreur(s) BLOQUANTE(S) trouvee(s) :")
        for e in erreurs:
            print(f"   - {e}")
        print("\nLa publication est BLOQUEE tant que ces liens ne sont pas corriges.")
        sys.exit(1)
    else:
        print("\n[OK] Aucun lien casse detecte. Le site peut etre publie en toute securite.")
        sys.exit(0)


if __name__ == "__main__":
    main()
