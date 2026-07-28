from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO

CANVAS_SIZE = 1080


def _charger_police(taille, gras=False):
    chemins_possibles = [
        "app/assets/fonts/Manrope-Bold.ttf" if gras else "app/assets/fonts/Manrope-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if gras else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for chemin in chemins_possibles:
        try:
            return ImageFont.truetype(chemin, taille)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size=taille)
    except TypeError:
        return ImageFont.load_default()


def _charger_image_url(url, taille=None):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        if taille:
            img = img.resize(taille, Image.LANCZOS)
        return img
    except Exception:
        return None


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _cercle_net(img, diametre):
    """Découpe un cercle net et anti-aliasé, cadré sans déformation.
    Supersampling 4x avant downscale : évite les bords crénelés d'un
    masque tracé directement à la taille finale."""
    facteur = 4
    taille_super = diametre * facteur

    img_cadree = ImageOps.fit(
        img.convert("RGB"), (taille_super, taille_super),
        method=Image.LANCZOS, centering=(0.5, 0.35),
    ).convert("RGBA")

    mask = Image.new("L", (taille_super, taille_super), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, taille_super, taille_super), fill=255)
    img_cadree.putalpha(mask)

    return img_cadree.resize((diametre, diametre), Image.LANCZOS)


def _dessiner_badge_rang(draw, centre, rang, rayon=48):
    x, y = centre
    draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=(15, 23, 42))
    police = _charger_police(int(rayon * 0.9), gras=True)
    draw.text((x, y), f"#{rang}", font=police, fill="white", anchor="mm")


def _dessiner_badge_evolution(draw, centre, evolution, rayon=42):
    x, y = centre

    if evolution is None or evolution != evolution:
        draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=(100, 116, 139))
        police = _charger_police(20, gras=True)
        draw.text((x, y), "NEW", font=police, fill="white", anchor="mm")
        return

    if evolution == 0:
        draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=(100, 116, 139))
        police = _charger_police(30, gras=True)
        draw.text((x, y), "-", font=police, fill="white", anchor="mm")
        return

    monte = evolution > 0
    couleur = (22, 163, 74) if monte else (220, 38, 38)
    draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=couleur)

    # Triangle dessiné à la main : évite tout risque de glyphe manquant
    # selon la police disponible sur le serveur.
    tri_largeur, tri_hauteur = 13, 11
    tri_centre_y = y - 14
    if monte:
        points = [
            (x, tri_centre_y - tri_hauteur * 0.6),
            (x - tri_largeur, tri_centre_y + tri_hauteur * 0.5),
            (x + tri_largeur, tri_centre_y + tri_hauteur * 0.5),
        ]
    else:
        points = [
            (x, tri_centre_y + tri_hauteur * 0.6),
            (x - tri_largeur, tri_centre_y - tri_hauteur * 0.5),
            (x + tri_largeur, tri_centre_y - tri_hauteur * 0.5),
        ]
    draw.polygon(points, fill="white")

    police = _charger_police(int(rayon * 0.55), gras=True)
    draw.text((x, y + 16), str(int(abs(evolution))), font=police, fill="white", anchor="mm")



def generer_carte_joueur(nom, poste, team_abbr, team_color, logo_url, photo_url,
                          stat_label, stat_value, rang=None, evolution=None):
    couleur_rgb = _hex_to_rgb(team_color)
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), couleur_rgb)
    draw = ImageDraw.Draw(img)

    overlay_h = 380
    draw.rectangle([0, CANVAS_SIZE - overlay_h, CANVAS_SIZE, CANVAS_SIZE], fill=(15, 23, 42))

    logo = _charger_image_url(logo_url, (140, 140))
    if logo:
        img.paste(logo, (CANVAS_SIZE - 180, 60), logo)

    photo_brute = _charger_image_url(photo_url)
    if photo_brute:
        photo = _cercle_net(photo_brute, 420)
        img.paste(photo, (330, 140), photo)

    if rang is not None:
        _dessiner_badge_rang(draw, (110, 110), rang)
    if evolution is not None or rang is not None:
        _dessiner_badge_evolution(draw, (110, 210), evolution)

    police_titre = _charger_police(64, gras=True)
    police_sous = _charger_police(36)
    police_stat = _charger_police(96, gras=True)
    police_label = _charger_police(32)

    draw.text((CANVAS_SIZE // 2, CANVAS_SIZE - overlay_h + 40), nom,
              font=police_titre, fill="white", anchor="mm")
    draw.text((CANVAS_SIZE // 2, CANVAS_SIZE - overlay_h + 95), f"{poste} · {team_abbr}",
              font=police_sous, fill="#94A3B8", anchor="mm")
    draw.text((CANVAS_SIZE // 2, CANVAS_SIZE - 160), str(stat_value),
              font=police_stat, fill="#EA580C", anchor="mm")
    draw.text((CANVAS_SIZE // 2, CANVAS_SIZE - 80), stat_label.upper(),
              font=police_label, fill="#94A3B8", anchor="mm")

    return img

COULEURS_RANG_HEX = ["#FBBF24", "#CBD5E1", "#D97706"]  # or / argent / bronze


def generer_podium_image(entries, titre, sous_titre=None):
    """entries : liste de 1 à 3 dicts avec les clés :
    rang, nom, sous_texte, team_color, logo_url, valeur (str déjà formatée),
    photo_url (optionnel — absent pour un podium d'équipes)."""
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    police_titre = _charger_police(52, gras=True)
    police_sous_titre = _charger_police(26)
    draw.text((CANVAS_SIZE // 2, 80), titre, font=police_titre, fill="white", anchor="mm")
    if sous_titre:
        draw.text((CANVAS_SIZE // 2, 130), sous_titre.upper(), font=police_sous_titre, fill="#94A3B8", anchor="mm")

    n = len(entries)
    entries_triees = sorted(entries, key=lambda e: e["rang"])
    ordre_affichage = [1, 0, 2][:n] if n >= 3 else list(range(n))

    hauteurs = [400, 320, 260]
    espacement = 300
    x_centre = CANVAS_SIZE // 2
    positions_x = {
        3: [x_centre - espacement, x_centre, x_centre + espacement],
        2: [x_centre - espacement // 2, x_centre + espacement // 2],
        1: [x_centre],
    }
    y_base = 980

    police_nom = _charger_police(28, gras=True)
    police_sous = _charger_police(20)
    police_valeur = _charger_police(32, gras=True)
    police_rang = _charger_police(24, gras=True)

    for position, i in enumerate(ordre_affichage):
        entree = entries_triees[i]
        rang = entree["rang"]
        x = positions_x[n][position]
        hauteur_barre = hauteurs[rang - 1] if rang <= 3 else 200
        couleur_equipe_rgb = _hex_to_rgb(entree["team_color"])

        avatar_diam = 130
        avatar_y = y_base - hauteur_barre - avatar_diam - 100

        photo_url = entree.get("photo_url")
        if photo_url:
            photo_brute = _charger_image_url(photo_url)
            if photo_brute:
                avatar = _cercle_net(photo_brute, avatar_diam)
                img.paste(avatar, (x - avatar_diam // 2, avatar_y), avatar)
            else:
                draw.ellipse((x - avatar_diam // 2, avatar_y, x + avatar_diam // 2, avatar_y + avatar_diam),
                              fill=couleur_equipe_rgb)
            logo_mini = _charger_image_url(entree.get("logo_url"), (44, 44))
            if logo_mini:
                lx, ly = x + avatar_diam // 2 - 32, avatar_y + avatar_diam - 32
                draw.ellipse((lx - 4, ly - 4, lx + 48, ly + 48), fill="white")
                img.paste(logo_mini, (lx, ly), logo_mini)
        else:
            logo = _charger_image_url(entree.get("logo_url"), (avatar_diam - 20, avatar_diam - 20))
            draw.ellipse((x - avatar_diam // 2, avatar_y, x + avatar_diam // 2, avatar_y + avatar_diam), fill="white")
            if logo:
                img.paste(logo, (x - (avatar_diam - 20) // 2, avatar_y + 10), logo)

        badge_rayon = 24
        badge_y = avatar_y - 6
        couleur_badge = _hex_to_rgb(COULEURS_RANG_HEX[rang - 1]) if rang <= 3 else (100, 116, 139)
        draw.ellipse((x - badge_rayon, badge_y - badge_rayon, x + badge_rayon, badge_y + badge_rayon), fill=couleur_badge)
        draw.text((x, badge_y), str(rang), font=police_rang, fill=(31, 41, 55), anchor="mm")

        nom_y = avatar_y + avatar_diam + 34
        draw.text((x, nom_y), entree["nom"], font=police_nom, fill="white", anchor="mm")
        draw.text((x, nom_y + 30), entree.get("sous_texte", ""), font=police_sous, fill="#94A3B8", anchor="mm")
        draw.text((x, nom_y + 62), entree["valeur"], font=police_valeur, fill="#EA580C", anchor="mm")

        barre_largeur = 220
        draw.rectangle([x - barre_largeur // 2, y_base - hauteur_barre, x + barre_largeur // 2, y_base],
                        fill=couleur_equipe_rgb)

    return img


def _formatter_valeur(valeur, decimals):
    return f"{valeur:,.0f}" if decimals == 0 else f"{valeur:.{decimals}f}"

def generer_carte_equipe(team_name, season, team_color, logo_url, rang_off, epa_off,
                          rang_def, epa_def, rang_semaine=None, evolution_semaine=None):
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, CANVAS_SIZE, 90], fill=_hex_to_rgb(team_color))

    logo = _charger_image_url(logo_url, (320, 320))
    if logo:
        img.paste(logo, (CANVAS_SIZE // 2 - 160, 160), logo)

    if rang_semaine is not None:
        _dessiner_badge_rang(draw, (110, 150), rang_semaine)
    if evolution_semaine is not None or rang_semaine is not None:
        _dessiner_badge_evolution(draw, (110, 250), evolution_semaine)

    police_titre = _charger_police(70, gras=True)
    police_label = _charger_police(30)
    police_stat = _charger_police(56, gras=True)

    draw.text((CANVAS_SIZE // 2, 550), team_name, font=police_titre, fill="white", anchor="mm")
    draw.text((CANVAS_SIZE // 2, 610), f"Saison {season}", font=police_label, fill="#94A3B8", anchor="mm")

    draw.text((CANVAS_SIZE // 4, 780), f"#{rang_off}", font=police_stat, fill="#EA580C", anchor="mm")
    draw.text((CANVAS_SIZE // 4, 850), "EPA OFFENSE", font=police_label, fill="#94A3B8", anchor="mm")
    draw.text((CANVAS_SIZE // 4, 890), f"{epa_off:.3f}", font=police_label, fill="white", anchor="mm")

    draw.text((3 * CANVAS_SIZE // 4, 780), f"#{rang_def}", font=police_stat, fill="#EA580C", anchor="mm")
    draw.text((3 * CANVAS_SIZE // 4, 850), "EPA DÉFENSE", font=police_label, fill="#94A3B8", anchor="mm")
    draw.text((3 * CANVAS_SIZE // 4, 890), f"{epa_def:.3f}", font=police_label, fill="white", anchor="mm")

    return img