from PIL import Image, ImageDraw, ImageFont
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


def generer_carte_joueur(nom, poste, team_abbr, team_color, logo_url, photo_url,
                          stat_label, stat_value):
    couleur_rgb = _hex_to_rgb(team_color)
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), couleur_rgb)
    draw = ImageDraw.Draw(img)

    overlay_h = 380
    draw.rectangle([0, CANVAS_SIZE - overlay_h, CANVAS_SIZE, CANVAS_SIZE], fill=(15, 23, 42))

    logo = _charger_image_url(logo_url, (140, 140))
    if logo:
        img.paste(logo, (CANVAS_SIZE - 180, 60), logo)

    photo = _charger_image_url(photo_url, (420, 420))
    if photo:
        mask = Image.new("L", (420, 420), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 420, 420), fill=255)
        img.paste(photo, (330, 140), mask)

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


def generer_carte_equipe(team_name, season, team_color, logo_url, rang_off, epa_off, rang_def, epa_def):
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, CANVAS_SIZE, 90], fill=_hex_to_rgb(team_color))

    logo = _charger_image_url(logo_url, (320, 320))
    if logo:
        img.paste(logo, (CANVAS_SIZE // 2 - 160, 160), logo)

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