"""
Feuilles de style partagées, séparées du code Python des pages.

HOME_CSS ne contient aucune valeur dynamique (pas d'interpolation) —
c'est un bloc statique, donc une simple chaîne plutôt qu'un f-string.
Les valeurs de statistiques (stats['total_plays'], etc.) restent
injectées directement dans Home.py, à l'endroit où le HTML du hero est
construit, puisqu'elles dépendent des données chargées à l'exécution.
"""

HOME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }

.hero-banner {
    position: relative; overflow: hidden;
    background: linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    background-image:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px, transparent 1px, transparent 64px),
        linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    border-radius: 16px; padding: 18px 32px 0; margin-bottom: 0; text-align: center;
}
.hero-eyebrow { font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.14em; color: #EA580C; text-transform: uppercase; margin-bottom: 4px; }
.hero-title { font-weight: 800; font-size: clamp(1.3rem, 2.6vw, 1.8rem); color: #CBD5E1 !important; margin: 0 0 3px; letter-spacing: -0.02em; }
.hero-tagline { font-size: 13px; color: #94A3B8; margin: 0 0 12px; }

.stat-strip {
    display: flex; justify-content: center; gap: 36px;
    background: #111C33; padding: 10px 32px; border-radius: 0 0 16px 16px;
    margin-bottom: 24px; flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-value { font-family: 'Space Mono', monospace; font-size: 17px; font-weight: 700; color: #EA580C; }
.stat-label { font-size: 10px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 1px; }
</style>
"""

# Style minimal réutilisé par les autres pages (import Manrope, sans le hero).
# Évite de dupliquer ce bloc de 4 lignes dans chaque fichier app/pages/*.py.
PAGE_FONT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
</style>
"""
