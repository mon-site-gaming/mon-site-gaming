#!/usr/bin/env python3
"""
========================================================================
 BUILD.PY - Generateur de site statique
========================================================================

Ce script transforme les articles (fichiers JSON dans /articles) en
pages HTML pretes a etre publiees, dans le dossier /site.

C'est ce script que l'Agent 3 (Publisher) va appeler automatiquement
plus tard, chaque fois qu'un nouvel article est genere par l'IA.

STRUCTURE D'UN ARTICLE (fichier .json dans /articles) :
{
    "titre": "...",
    "description": "resume de 1-2 phrases pour le SEO",
    "contenu_html": "<p>...</p><h2>...</h2><p>...</p>",
    "lien_affiliation": "https://...",
    "cta_texte": "Envie de tester GameFly ?",
    "cta_bouton": "Voir l'offre",
    "date": "2026-07-14",
    "slug": "meilleur-prix-location-gta-6"
}

CONFIGURATION : modifie les valeurs dans CONFIG ci-dessous.
========================================================================
"""

import json
import re
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------
# CONFIGURATION - a adapter
# ------------------------------------------------------------------
CONFIG = {
    "site_name": "TechDeals Hub",
    "site_description": "Software, VPN and hosting deals, reviewed and updated regularly.",
    "base_url": "https://tonpseudo.github.io/tech-deals-hub",
}

BASE_DIR = Path(__file__).parent
ARTICLES_DIR = BASE_DIR / "articles"
SITE_DIR = BASE_DIR  # generation directement a la racine du depot (plus de sous-dossier site/)
TEMPLATES_DIR = BASE_DIR / "templates"

ARTICLES_DIR.mkdir(exist_ok=True)
SITE_DIR.mkdir(exist_ok=True)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text[:80]


def load_articles():
    articles = []
    for f in sorted(ARTICLES_DIR.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
                articles.append(data)
        except Exception as e:
            print(f"   /!\\ Erreur lecture {f.name} : {e}")
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return articles


def build_article_page(article, template):
    slug = article.get("slug") or slugify(article["titre"])
    html = template
    html = html.replace("{{TITLE}}", article["titre"])
    html = html.replace("{{DESCRIPTION}}", article.get("description", ""))
    html = html.replace("{{CANONICAL_URL}}", f"{CONFIG['base_url']}/{slug}.html")
    html = html.replace("{{DATE}}", article.get("date", datetime.now().strftime("%Y-%m-%d")))
    html = html.replace("{{CONTENT}}", article.get("contenu_html", ""))
    html = html.replace("{{CTA_TEXT}}", article.get("cta_texte", "Interesse ?"))
    html = html.replace("{{CTA_BUTTON_TEXT}}", article.get("cta_bouton", "En savoir plus"))
    html = html.replace("{{AFFILIATE_LINK}}", article.get("lien_affiliation", "#"))
    html = html.replace("{{SITE_NAME}}", CONFIG["site_name"])
    html = html.replace("{{YEAR}}", str(datetime.now().year))

    output_path = SITE_DIR / f"{slug}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return slug, output_path


def build_index(articles, template):
    cards = []
    for a in articles:
        slug = a.get("slug") or slugify(a["titre"])
        cards.append(f"""
        <div class="article-card">
            <a href="{slug}.html">
                <h2>{a['titre']}</h2>
                <div class="date">{a.get('date', '')}</div>
                <div class="excerpt">{a.get('description', '')}</div>
            </a>
        </div>""")

    html = template
    html = html.replace("{{ARTICLE_LIST}}", "\n".join(cards) if cards else "<p>Aucun article pour le moment.</p>")
    html = html.replace("{{SITE_NAME}}", CONFIG["site_name"])
    html = html.replace("{{SITE_DESCRIPTION}}", CONFIG["site_description"])
    html = html.replace("{{YEAR}}", str(datetime.now().year))

    with open(SITE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def build_sitemap(articles):
    urls = [f"{CONFIG['base_url']}/"]
    for a in articles:
        slug = a.get("slug") or slugify(a["titre"])
        urls.append(f"{CONFIG['base_url']}/{slug}.html")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f"  <url><loc>{u}</loc></url>")
    xml.append("</urlset>")

    with open(SITE_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))


def create_sample_article_if_empty():
    """Cree un article d'exemple si aucun article n'existe, pour que tu voies le resultat."""
    if list(ARTICLES_DIR.glob("*.json")):
        return

    sample = {
        "titre": "NordVPN Deal: How to Get the Best Price on a VPN Subscription",
        "description": "A comparison of the best ways to save on a NordVPN subscription right now.",
        "contenu_html": (
            "<p>With online privacy concerns growing, more people are turning to VPN services "
            "like NordVPN to protect their browsing. Finding the right deal can make a big "
            "difference on long-term subscription costs.</p>"
            "<h2>Why a long-term plan usually pays off</h2>"
            "<p>Monthly VPN plans often cost significantly more per month than yearly or "
            "multi-year commitments. If you plan to use a VPN regularly, a longer plan "
            "usually offers the best value per month.</p>"
        ),
        "lien_affiliation": "https://exemple-affiliation.com/ton-lien",
        "cta_texte": "Want to see the current NordVPN pricing?",
        "cta_bouton": "View the deal",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "slug": "nordvpn-best-deal"
    }

    with open(ARTICLES_DIR / "exemple.json", "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    print("   -> Article d'exemple cree dans /articles/exemple.json")


def main():
    print("=" * 60)
    print(" CONSTRUCTION DU SITE")
    print("=" * 60)

    create_sample_article_if_empty()

    article_template = (TEMPLATES_DIR / "article.html").read_text(encoding="utf-8")
    index_template = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")

    articles = load_articles()
    print(f"\n{len(articles)} article(s) trouve(s).")

    for article in articles:
        slug, path = build_article_page(article, article_template)
        print(f"   -> Page generee : {path.name}")

    build_index(articles, index_template)
    build_sitemap(articles)

    print(f"\nSite genere directement a la racine de : {SITE_DIR.resolve()}")
    print("Ouvre 'index.html' dans ton navigateur pour voir le resultat.")
    print("Le depot est deja pret pour git add / commit / push (voir agent4_orchestrator.py).")


if __name__ == "__main__":
    main()
