#!/usr/bin/env python3
"""
========================================================================
 PREVIEW_DESIGN.PY - Apercu du nouveau design (sans publication)
========================================================================

Genere une version de PREVIEW du site avec les nouveaux templates
professionnels (index_v2.html, article_v2.html), dans un dossier separe
"preview/". Ca ne touche JAMAIS au site en production tant que tu n'as
pas valide.

Usage :
    python preview_design.py
Puis ouvre preview/index.html dans ton navigateur pour regarder.
========================================================================
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import CONFIG, ARTICLES_DIR, slugify, load_articles

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
PREVIEW_DIR = BASE_DIR / "preview"
PREVIEW_DIR.mkdir(exist_ok=True)


def split_site_name(site_name: str):
    parts = site_name.split(" ", 1)
    if len(parts) == 2:
        return parts[0], " " + parts[1]
    return site_name, ""


def build_article_page_v2(article, template):
    slug = article.get("slug") or slugify(article["titre"])
    part1, part2 = split_site_name(CONFIG["site_name"])

    html = template
    html = html.replace("{{TITLE}}", article["titre"])
    html = html.replace("{{DESCRIPTION}}", article.get("description", ""))
    html = html.replace("{{CANONICAL_URL}}", f"{CONFIG['base_url']}/{slug}.html")
    html = html.replace("{{DATE}}", article.get("date", datetime.now().strftime("%Y-%m-%d")))
    html = html.replace("{{CONTENT}}", article.get("contenu_html", ""))
    html = html.replace("{{CTA_TEXT}}", article.get("cta_texte", "Interesse ?"))
    html = html.replace("{{CTA_BUTTON_TEXT}}", article.get("cta_bouton", "En savoir plus"))
    html = html.replace("{{AFFILIATE_LINK}}", article.get("lien_affiliation", "#"))
    html = html.replace("{{SITE_NAME_PART1}}", part1)
    html = html.replace("{{SITE_NAME_PART2}}", part2)
    html = html.replace("{{SITE_NAME}}", CONFIG["site_name"])
    html = html.replace("{{YEAR}}", str(datetime.now().year))

    output_path = PREVIEW_DIR / f"{slug}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return slug


def build_index_v2(articles, template):
    part1, part2 = split_site_name(CONFIG["site_name"])
    cards = []
    for a in articles:
        slug = a.get("slug") or slugify(a["titre"])
        cards.append(f"""
        <div class="card">
            <a href="{slug}.html">
                <span class="tag">Deal</span>
                <h2>{a['titre']}</h2>
                <div class="date">{a.get('date', '')}</div>
                <p class="excerpt">{a.get('description', '')}</p>
            </a>
        </div>""")

    html = template
    html = html.replace("{{ARTICLE_LIST}}", "\n".join(cards) if cards else "<p>Aucun article pour le moment.</p>")
    html = html.replace("{{SITE_NAME_PART1}}", part1)
    html = html.replace("{{SITE_NAME_PART2}}", part2)
    html = html.replace("{{SITE_NAME}}", CONFIG["site_name"])
    html = html.replace("{{SITE_DESCRIPTION}}", CONFIG["site_description"])
    html = html.replace("{{YEAR}}", str(datetime.now().year))

    with open(PREVIEW_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def main():
    print("=" * 60)
    print(" GENERATION DE L'APERCU DU NOUVEAU DESIGN")
    print("=" * 60)

    article_template = (TEMPLATES_DIR / "article_v2.html").read_text(encoding="utf-8")
    index_template = (TEMPLATES_DIR / "index_v2.html").read_text(encoding="utf-8")

    articles = load_articles()
    print(f"\n{len(articles)} article(s) trouve(s) pour l'apercu.")

    for article in articles:
        slug = build_article_page_v2(article, article_template)
        print(f"   -> Apercu genere : {slug}.html")

    build_index_v2(articles, index_template)

    print(f"\nApercu complet genere dans : {PREVIEW_DIR.resolve()}")
    print("Ouvre 'preview/index.html' dans ton navigateur pour le voir.")
    print("\nCe dossier n'est PAS publie. Rien ne change sur ton vrai site")
    print("tant que tu n'as pas valide via /valider_design sur Telegram.")


if __name__ == "__main__":
    main()
