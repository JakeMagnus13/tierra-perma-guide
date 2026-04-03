#!/usr/bin/env python3
"""
Tierra Perma — Tropical Home Design Guide
Production PDF Builder

SETUP:
  pip install reportlab Pillow
  
  # Download Google Fonts (run once):
  mkdir -p fonts
  # Cormorant Garamond:
  curl -L "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Regular.ttf" -o fonts/CormorantGaramond-Regular.ttf
  curl -L "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Bold.ttf" -o fonts/CormorantGaramond-Bold.ttf
  curl -L "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Italic.ttf" -o fonts/CormorantGaramond-Italic.ttf
  curl -L "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-SemiBold.ttf" -o fonts/CormorantGaramond-SemiBold.ttf
  # DM Sans:
  curl -L "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf" -o fonts/DMSans-Variable.ttf
  curl -L "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans-Italic%5Bopsz%2Cwght%5D.ttf" -o fonts/DMSans-Italic-Variable.ttf

  Or use the download_fonts.sh script included in this repo.

FOLDER STRUCTURE:
  project/
    build_guide.py          (this file)
    download_fonts.sh       (font downloader)
    fonts/                  (fonts go here)
    images/
      diagrams/
        D1-site-reading.png
        D2-orientation.png
        D3-ventilation.png
        D4-roof-detail.png
        D5-shading.png
        D6-wall-sections.png
        D7-site-systems.png
      visuals/
        A1-rainfall-chart.png
        A5-ac-cost-infographic.png
        cover.png
        back-cover.png
        material-texture-strip.png
      photography/          (optional — add as available)
        P1-concrete-block.jpg
        P3-raw-site.jpg
        (etc)
      brand/
        logo.png            (optional — Tierra Perma logo)
    output/                 (PDF generated here)

USAGE:
  python3 build_guide.py
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.utils import ImageReader
from PIL import Image

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent
FONT_DIR = BASE_DIR / "fonts"
IMG_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# FONT REGISTRATION
# ============================================================

# Try Cormorant Garamond first (brand font), fall back to system fonts
FONT_MAP = {
    'Heading': ('CormorantGaramond-Regular.ttf', 'CormorantGaramond-SemiBold.ttf', 'CormorantGaramond-Italic.ttf'),
    'Body': ('DMSans-Variable.ttf', 'DMSans-Variable.ttf', 'DMSans-Italic-Variable.ttf'),
}

def register_fonts():
    """Register brand fonts with fallbacks."""
    font_registered = {}
    
    # Heading font: Cormorant Garamond -> Lora -> Times
    heading_options = [
        ('Heading', FONT_DIR / 'CormorantGaramond-Regular.ttf'),
        ('Heading', FONT_DIR / 'Lora-Variable.ttf'),
    ]
    heading_bold_options = [
        ('Heading-Bold', FONT_DIR / 'CormorantGaramond-SemiBold.ttf'),
        ('Heading-Bold', FONT_DIR / 'Lora-Variable.ttf'),
    ]
    heading_italic_options = [
        ('Heading-Italic', FONT_DIR / 'CormorantGaramond-Italic.ttf'),
        ('Heading-Italic', FONT_DIR / 'Lora-Italic-Variable.ttf'),
    ]
    
    # Body font: DM Sans -> Poppins -> Helvetica
    body_options = [
        ('Body', FONT_DIR / 'DMSans-Variable.ttf'),
        ('Body', FONT_DIR / 'Poppins-Regular.ttf'),
    ]
    body_bold_options = [
        ('Body-Bold', FONT_DIR / 'DMSans-Variable.ttf'),
        ('Body-Bold', FONT_DIR / 'Poppins-Bold.ttf'),
    ]
    body_light_options = [
        ('Body-Light', FONT_DIR / 'DMSans-Variable.ttf'),
        ('Body-Light', FONT_DIR / 'Poppins-Light.ttf'),
    ]
    body_medium_options = [
        ('Body-Medium', FONT_DIR / 'DMSans-Variable.ttf'),
        ('Body-Medium', FONT_DIR / 'Poppins-Medium.ttf'),
    ]
    body_italic_options = [
        ('Body-Italic', FONT_DIR / 'DMSans-Italic-Variable.ttf'),
        ('Body-Italic', FONT_DIR / 'Poppins-Italic.ttf'),
    ]
    
    all_font_sets = [
        heading_options, heading_bold_options, heading_italic_options,
        body_options, body_bold_options, body_light_options, 
        body_medium_options, body_italic_options,
    ]
    
    for font_set in all_font_sets:
        registered = False
        for name, path in font_set:
            if path.exists():
                try:
                    pdfmetrics.registerFont(TTFont(name, str(path)))
                    font_registered[name] = str(path)
                    registered = True
                    break
                except Exception as e:
                    print(f"  Warning: Could not register {name} from {path}: {e}")
        if not registered:
            print(f"  WARNING: No font found for {font_set[0][0]} — using Helvetica fallback")
            # Map to built-in
            font_registered[font_set[0][0]] = 'Helvetica'
    
    print(f"Fonts registered: {list(font_registered.keys())}")
    return font_registered

# ============================================================
# BRAND COLORS
# ============================================================

CREAM = HexColor('#F5F0E8')
DEEP_BROWN = HexColor('#2C1810')
TERRACOTTA = HexColor('#C4704B')
WARM_SAND = HexColor('#D4C5A9')
SAGE = HexColor('#7A8B6F')
DARK_SAGE = HexColor('#4A5A40')
CHARCOAL = HexColor('#3A3A3A')
LIGHT_CREAM = HexColor('#FAF7F2')
MEDIUM_BROWN = HexColor('#5C3D2E')
SOFT_TERRACOTTA = HexColor('#E8A882')

# ============================================================
# PAGE SETUP
# ============================================================

W, H = A4  # 595.27 x 841.89 points (210 x 297 mm)
MARGIN_L = 22 * mm
MARGIN_R = 22 * mm
MARGIN_T = 20 * mm
MARGIN_B = 22 * mm
CONTENT_W = W - MARGIN_L - MARGIN_R
COL_W = (CONTENT_W - 8 * mm) / 2

# ============================================================
# IMAGE HELPER
# ============================================================

def find_image(relative_path):
    """Find an image file, trying common extensions."""
    base = IMG_DIR / relative_path
    if base.exists():
        return str(base)
    # Try without extension, checking common formats
    stem = base.with_suffix('')
    for ext in ['.png', '.jpg', '.jpeg', '.webp', '.tiff']:
        candidate = stem.with_suffix(ext)
        if candidate.exists():
            return str(candidate)
    return None


def draw_image(c, path_key, x, y, w, h, label="", dark=False):
    """Draw an image if available, otherwise draw a placeholder."""
    img_path = find_image(path_key)
    
    if img_path:
        try:
            # Get image dimensions to calculate aspect-preserving fit
            img = Image.open(img_path)
            img_w, img_h = img.size
            img_aspect = img_w / img_h
            box_aspect = w / h
            
            if img_aspect > box_aspect:
                # Image is wider — fit to width, crop height
                draw_w = w
                draw_h = w / img_aspect
                draw_x = x
                draw_y = y + (h - draw_h) / 2
            else:
                # Image is taller — fit to height, crop width
                draw_h = h
                draw_w = h * img_aspect
                draw_x = x + (w - draw_w) / 2
                draw_y = y
            
            c.drawImage(img_path, draw_x, draw_y, draw_w, draw_h, 
                       preserveAspectRatio=True, mask='auto')
            return True
        except Exception as e:
            print(f"  Warning: Could not load image {img_path}: {e}")
    
    # Fallback: draw placeholder
    bg = DEEP_BROWN if dark else WARM_SAND
    fg = CREAM if dark else MEDIUM_BROWN
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=0)
    
    c.setStrokeColor(fg)
    c.setStrokeAlpha(0.15)
    c.setLineWidth(0.5)
    c.line(x, y, x + w, y + h)
    c.line(x + w, y, x, y + h)
    c.setStrokeAlpha(1)
    
    cx, cy = x + w / 2, y + h / 2
    c.setFillColor(fg)
    c.setFillAlpha(0.5)
    c.setFont('Body-Medium', 7)
    label_text = label or path_key
    c.drawCentredString(cx, cy, f"[{label_text.upper()}]")
    c.setFillAlpha(1)
    
    return False


def draw_image_fullbleed(c, path_key, y_bottom, height, label=""):
    """Draw a full-bleed image (edge to edge)."""
    return draw_image(c, path_key, 0, y_bottom, W, height, label)


# ============================================================
# LAYOUT HELPERS
# ============================================================

def draw_pull_quote(c, x, y, w, text, attribution=""):
    """Draw an italic pull quote with terracotta accent line."""
    style = ParagraphStyle(
        'pullquote', fontName='Heading-Italic', fontSize=11.5,
        leading=16, textColor=MEDIUM_BROWN, alignment=TA_LEFT,
    )
    p = Paragraph(text, style)
    pw, ph = p.wrap(w - 15, 200)
    
    c.setStrokeColor(TERRACOTTA)
    c.setLineWidth(2.5)
    c.line(x + 2, y - 6, x + 2, y - 6 - ph - 4)
    
    p.drawOn(c, x + 14, y - 6 - ph)
    bottom = y - 6 - ph - 4
    
    if attribution:
        c.setFont('Body-Medium', 7)
        c.setFillColor(TERRACOTTA)
        c.drawString(x + 14, bottom - 12, attribution)
        bottom -= 16
    
    return bottom


def draw_section_number(c, x, y, number):
    """Draw a large terracotta section number watermark."""
    c.setFillColor(TERRACOTTA)
    c.setFillAlpha(0.12)
    c.setFont('Heading', 72)
    c.drawString(x, y, f"{number:02d}")
    c.setFillAlpha(1)


def draw_body_text(c, x, y, w, text, font='Body', size=9, leading=14.5, 
                   color=CHARCOAL, align=TA_JUSTIFY):
    """Draw body text paragraph, return bottom y."""
    style = ParagraphStyle(
        'body', fontName=font, fontSize=size, leading=leading,
        textColor=color, alignment=align, spaceAfter=3 * mm
    )
    p = Paragraph(text, style)
    pw, ph = p.wrap(w, 500)
    p.drawOn(c, x, y - ph)
    return y - ph


def draw_subheader(c, x, y, text, font='Body-Bold', size=10, color=DEEP_BROWN):
    """Draw a subheader, return y below."""
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)
    return y - 5 * mm


def draw_footer(c, page_num):
    """Draw page footer."""
    c.setFont('Body-Light', 6.5)
    c.setFillColor(WARM_SAND)
    c.drawString(MARGIN_L, 12 * mm, "TIERRA PERMA  —  Regenerative Architecture & Permaculture Design")
    c.drawRightString(W - MARGIN_R, 12 * mm, f"{page_num}")
    c.setStrokeColor(WARM_SAND)
    c.setStrokeAlpha(0.4)
    c.setLineWidth(0.4)
    c.line(MARGIN_L, 15 * mm, W - MARGIN_R, 15 * mm)
    c.setStrokeAlpha(1)


def cream_page(c):
    """Fill page with cream background."""
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def section_header(c, title, subtitle=None, number=None):
    """Draw standard section header with number, title, accent line."""
    if number:
        draw_section_number(c, MARGIN_L - 3 * mm, H - MARGIN_T - 18 * mm, number)
    
    y = H - MARGIN_T - 8 * mm
    
    if isinstance(title, list):
        for i, line in enumerate(title):
            c.setFont('Heading', 22 if len(title) > 1 else 24)
            c.setFillColor(DEEP_BROWN)
            c.drawString(MARGIN_L, y, line)
            y -= 10 * mm
    else:
        c.setFont('Heading', 24)
        c.setFillColor(DEEP_BROWN)
        c.drawString(MARGIN_L, y, title)
        y -= 5 * mm
    
    if subtitle:
        c.setFont('Body-Light', 10)
        c.setFillColor(MEDIUM_BROWN)
        c.drawString(MARGIN_L, y, subtitle)
        y -= 6 * mm
    
    c.setStrokeColor(TERRACOTTA)
    c.setLineWidth(2)
    c.line(MARGIN_L, y, MARGIN_L + 40 * mm, y)
    
    return y - 8 * mm


# ============================================================
# PAGE BUILDERS
# ============================================================

def build_cover(c):
    """Page 1: Cover"""
    cream_page(c)
    
    # Top terracotta accent bar
    c.setFillColor(TERRACOTTA)
    c.rect(0, H - 8 * mm, W, 8 * mm, fill=1, stroke=0)
    
    # Hero image
    img_h = 130 * mm
    img_y = H - 8 * mm - img_h
    draw_image(c, "visuals/cover", 0, img_y, W, img_h, "Cover illustration")
    
    # Title block
    title_y = img_y - 12 * mm
    
    c.setFont('Heading', 34)
    c.setFillColor(DEEP_BROWN)
    c.drawString(MARGIN_L, title_y, "Tropical Home")
    c.drawString(MARGIN_L, title_y - 14 * mm, "Design Guide")
    
    c.setStrokeColor(TERRACOTTA)
    c.setLineWidth(2.5)
    c.line(MARGIN_L, title_y - 20 * mm, MARGIN_L + 50 * mm, title_y - 20 * mm)
    
    style_sub = ParagraphStyle(
        'coversub', fontName='Body-Light', fontSize=10, leading=15,
        textColor=MEDIUM_BROWN, alignment=TA_LEFT,
    )
    subtitle = Paragraph(
        "Design and build for the Guanacaste climate — reduce your electricity bill, "
        "lower your environmental impact, and deepen your connection to the land you inhabit.",
        style_sub
    )
    sw, sh = subtitle.wrap(CONTENT_W * 0.75, 100)
    subtitle.drawOn(c, MARGIN_L, title_y - 24 * mm - sh)
    
    c.setFont('Body-Italic', 8.5)
    c.setFillColor(TERRACOTTA)
    c.drawString(MARGIN_L, title_y - 24 * mm - sh - 8 * mm,
                 "For those looking to build consciously in Costa Rica and not sure where to start.")
    
    # Logo area
    logo_path = find_image("brand/logo")
    if logo_path:
        c.drawImage(logo_path, W - MARGIN_R - 24 * mm, 12 * mm, 20 * mm, 20 * mm,
                    preserveAspectRatio=True, mask='auto')
    
    c.setFont('Body-Medium', 8)
    c.setFillColor(DEEP_BROWN)
    c.drawString(MARGIN_L, 18 * mm, "TIERRA PERMA")
    c.setFont('Body-Light', 7)
    c.setFillColor(MEDIUM_BROWN)
    c.drawString(MARGIN_L, 13 * mm, "Regenerative Architecture & Permaculture Design  ·  Tamarindo, Guanacaste")
    
    c.showPage()


def build_toc(c):
    """Page 2: Table of Contents"""
    cream_page(c)
    
    c.setFont('Heading', 28)
    c.setFillColor(DEEP_BROWN)
    c.drawString(MARGIN_L, H - MARGIN_T - 10 * mm, "Contents")
    
    c.setStrokeColor(TERRACOTTA)
    c.setLineWidth(2)
    c.line(MARGIN_L, H - MARGIN_T - 14 * mm, MARGIN_L + 35 * mm, H - MARGIN_T - 14 * mm)
    
    toc_items = [
        ("01", "Why This Guide Exists", "Understanding the opportunity"),
        ("02", "The Problem with Standard Construction", "What's wrong with the default approach"),
        ("03", "Reading Your Site", "What to look for before you design anything"),
        ("04", "Designing with the Climate", "Passive solar cooling techniques that work"),
        ("05", "Materials That Matter", "From concrete block to earth — the full spectrum"),
        ("06", "Living Systems", "Water, waste, and land integration"),
        ("07", "Resilience & Self-Sufficiency", "Why your home should work when systems don't"),
        ("08", "What to Ask Your Architect", "The questions that reveal who's designing for this climate"),
        ("09", "Key Terms in Spanish", "Essential vocabulary for building in Costa Rica"),
        ("10", "Start the Conversation", "How to take the next step with Tierra Perma"),
    ]
    
    toc_y = H - MARGIN_T - 30 * mm
    
    for num, title, desc in toc_items:
        c.setFont('Heading', 22)
        c.setFillColor(TERRACOTTA)
        c.drawString(MARGIN_L, toc_y, num)
        
        c.setFont('Body-Medium', 10.5)
        c.setFillColor(DEEP_BROWN)
        c.drawString(MARGIN_L + 18 * mm, toc_y + 1, title)
        
        c.setStrokeColor(WARM_SAND)
        c.setLineWidth(0.3)
        c.setDash(1, 3)
        title_end = MARGIN_L + 18 * mm + c.stringWidth(title, 'Body-Medium', 10.5) + 4 * mm
        c.line(title_end, toc_y + 2, W - MARGIN_R, toc_y + 2)
        c.setDash()
        
        c.setFont('Body-Light', 8)
        c.setFillColor(MEDIUM_BROWN)
        c.drawString(MARGIN_L + 18 * mm, toc_y - 5 * mm, desc)
        
        toc_y -= 18 * mm
    
    draw_footer(c, 2)
    c.showPage()


def build_section_01(c):
    """Page 3: Why This Guide Exists"""
    cream_page(c)
    y = section_header(c, "Why This Guide Exists", number=1)
    
    body1 = ("You've found your land. Maybe it's a hillside with ocean views, or a quiet plot "
             "tucked behind dry tropical forest. You can already picture the life you want to live here. "
             "But when it comes to actually building, the options presented to you probably look the same: "
             "concrete block walls, a sealed envelope, air conditioning in every room, and a design that "
             "could exist anywhere in the world.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, body1)
    y -= 3 * mm
    
    y = draw_pull_quote(c, MARGIN_L + 5 * mm, y, CONTENT_W * 0.8,
                        "There's another way. For thousands of years, people built homes that responded "
                        "to the climate they were in — using orientation, airflow, shade, and local materials "
                        "to create comfort without mechanical systems.")
    y -= 6 * mm
    
    body2 = ("These aren't primitive techniques. They're intelligent design principles that modern architecture "
             "has largely forgotten in favour of brute-force solutions like air conditioning and energy-intensive materials.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, body2)
    y -= 2 * mm
    
    # Photo slot
    img_h = 55 * mm
    draw_image(c, "photography/P12-landscape", MARGIN_L, y - img_h, CONTENT_W, img_h, "Guanacaste landscape")
    y -= img_h + 5 * mm
    
    body3 = ("This guide is for anyone planning to build in Costa Rica's tropical dry climate — particularly "
             "Guanacaste and the Pacific coast — who wants a home that works <i>with</i> the environment rather "
             "than against it. Whether you're an expat building your first home, a Tico family looking for a "
             "healthier approach, or an investor developing property that stands apart, the principles in these "
             "pages will change how you think about what a home can be.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, body3)
    y -= 4 * mm
    
    style_callout = ParagraphStyle(
        'callout', fontName='Body-Bold', fontSize=11, leading=16,
        textColor=DEEP_BROWN, alignment=TA_LEFT
    )
    callout = Paragraph("You don't need to build a thatched hut to live sustainably. You need to build intelligently.", style_callout)
    cw, ch = callout.wrap(CONTENT_W, 50)
    callout.drawOn(c, MARGIN_L, y - ch)
    
    draw_footer(c, 3)
    c.showPage()


def build_section_02(c):
    """Page 4: The Problem with Standard Construction"""
    cream_page(c)
    y = section_header(c, ["The Problem with", "Standard Construction"], number=2)
    
    body = ("Walk through any residential neighbourhood in Guanacaste and you'll see the same formula: "
            "concrete block walls, minimal overhangs, small windows positioned for privacy rather than ventilation, "
            "and an air conditioning unit bolted to the outside of every bedroom.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, body)
    y -= 2 * mm
    
    body2 = ("This approach became the default for understandable reasons — concrete block is familiar, widely "
             "available, and fast to build. But it was never designed for this climate. It absorbs heat all day "
             "and radiates it inward through the night. It creates sealed boxes that depend entirely on mechanical "
             "cooling. And it disconnects you from the landscape you chose to live in.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, body2)
    y -= 3 * mm
    
    # Photo: conventional construction
    img_h = 45 * mm
    draw_image(c, "photography/P1-concrete-block", MARGIN_L, y - img_h, CONTENT_W, img_h, "Conventional concrete block")
    y -= img_h + 5 * mm
    
    # Three consequences
    y = draw_subheader(c, MARGIN_L, y, "Your Electricity Bill", color=TERRACOTTA)
    bill_text = ("A typical three-bedroom concrete block home in Guanacaste running AC 10–12 hours a day during "
                 "hot season spends roughly <b>₡185,000/month</b> on cooling alone — approximately <b>$2,500 USD per year</b>. "
                 "That's not a design feature. That's a design failure being paid for monthly.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, bill_text)
    y -= 3 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "Your Health", color=TERRACOTTA)
    health_text = ("Conventional construction materials — treated timber, synthetic paints, adhesives, foam insulation — "
                   "release volatile organic compounds into your living space. In a sealed, air-conditioned home, you're "
                   "recirculating these compounds continuously.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, health_text)
    y -= 3 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "Your Connection to Place", color=TERRACOTTA)
    place_text = ("A concrete box with AC could be anywhere. It shuts out the breeze, the sounds, the shifting light "
                  "of the tropics. The very qualities that drew you to this place get sealed on the other side of the wall.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, place_text)
    
    draw_footer(c, 4)
    c.showPage()


def build_section_03(c):
    """Page 5: Reading Your Site"""
    cream_page(c)
    y = section_header(c, "Reading Your Site", number=3)
    
    body = ("Before a single line is drawn, the most important thing an architect can do is spend time on your land. "
            "Not measuring it — <i>reading</i> it. Every site has a story written in its topography, its vegetation, its "
            "relationship to sun and wind. A good design starts by listening.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, body)
    y -= 3 * mm
    
    # D1 diagram — full width
    img_h = 60 * mm
    draw_image(c, "diagrams/D1-site-reading", MARGIN_L, y - img_h, CONTENT_W, img_h, "D1: Site reading")
    y -= img_h + 6 * mm
    
    # Site reading items in two columns
    left_x = MARGIN_L
    right_x = MARGIN_L + COL_W + 8 * mm
    
    items_left = [
        ("Sun Path", "In Guanacaste (~10°N latitude), the sun tracks almost directly overhead at equinoxes. "
         "Understanding this arc determines where to place living spaces and how deep your overhangs should be."),
        ("Prevailing Winds", "Papagayo winds blow from the northeast in dry season; softer Pacific breezes "
         "come in wet season. Design should capture and channel these — but know when to buffer."),
        ("Topography & Drainage", "Where does water flow during a rainstorm? Natural drainage patterns prevent "
         "expensive problems and reveal opportunities."),
    ]
    
    items_right = [
        ("Existing Vegetation", "A mature Guanacaste tree provides shade equivalent to several tons of AC. "
         "Mapping existing trees should directly inform your layout."),
        ("Soil", "Clay, sand, rock — your soil affects foundations, drainage, thermal mass potential, and "
         "whether earth-building techniques are viable."),
        ("Water Access", "Municipal supply reliability, well potential, rainfall for harvesting. In many parts "
         "of Guanacaste, water is the most critical resource consideration."),
    ]
    
    col_y = y
    for items, x in [(items_left, left_x), (items_right, right_x)]:
        iy = col_y
        for title, desc in items:
            c.setFont('Body-Bold', 9)
            c.setFillColor(TERRACOTTA)
            c.drawString(x, iy, title)
            iy -= 4 * mm
            style = ParagraphStyle('sitebody', fontName='Body', fontSize=8, leading=12,
                                   textColor=CHARCOAL, alignment=TA_LEFT)
            p = Paragraph(desc, style)
            pw, ph = p.wrap(COL_W, 200)
            p.drawOn(c, x, iy - ph)
            iy -= ph + 6 * mm
    
    draw_pull_quote(c, MARGIN_L + 5 * mm, 42 * mm, CONTENT_W * 0.75,
                    "A site reading isn't a luxury. It's the foundation that every other design decision builds on. "
                    "Skip it, and you're guessing. Get it right, and the design almost reveals itself.")
    
    draw_footer(c, 5)
    c.showPage()


def build_section_04(c):
    """Pages 6-7: Designing with the Climate"""
    # PAGE 6
    cream_page(c)
    y = section_header(c, "Designing with the Climate", subtitle="Passive Solar Cooling", number=4)
    
    intro = ("Passive solar design isn't a trend or an ideology. It's physics — applied thoughtfully. The core "
             "principle is simple: manage heat gain, promote natural ventilation, and use thermal mass strategically "
             "so that your home stays comfortable without relying on air conditioning.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, intro)
    y -= 4 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "ORIENTATION", color=DEEP_BROWN)
    orient_text = ("The single most impactful decision. Your longest facades should face north and south, minimising "
                   "exposure to the brutal east (morning) and west (afternoon) sun. The west facade in particular should "
                   "have minimal glazing and maximum shading — afternoon solar gain is the largest contributor to overheating.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, orient_text)
    y -= 3 * mm
    
    # D2 diagram
    img_h = 48 * mm
    draw_image(c, "diagrams/D2-orientation", MARGIN_L, y - img_h, CONTENT_W, img_h, "D2: Orientation")
    y -= img_h + 5 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "CROSS-VENTILATION", color=DEEP_BROWN)
    vent_text = ("Design every inhabited room with openings on at least two sides, positioned to catch the prevailing "
                 "northeast breeze. High openings on the leeward side allow hot air to escape (the stack effect), while "
                 "lower openings on the windward side draw cooler air in. Even moderate air movement of 1–2 m/s can make "
                 "a space feel <b>3–5°C cooler</b> than the actual air temperature.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, vent_text)
    y -= 3 * mm
    
    # D3 diagram
    img_h = 42 * mm
    draw_image(c, "diagrams/D3-ventilation", MARGIN_L, y - img_h, CONTENT_W, img_h, "D3: Cross-ventilation")
    
    draw_footer(c, 6)
    c.showPage()
    
    # PAGE 7
    cream_page(c)
    y = H - MARGIN_T - 5 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "ROOF DESIGN", color=DEEP_BROWN)
    roof_text = ("Your roof is the largest surface exposed to the sun. A ventilated roof — with an air gap between "
                 "the roof skin and the ceiling plane — dramatically reduces heat transfer into living spaces. "
                 "Light-coloured materials reflect rather than absorb solar radiation. Extended overhangs of 1.2m or "
                 "more shade walls and windows from direct sun while still admitting diffused daylight.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, roof_text)
    y -= 3 * mm
    
    # D4 diagram
    img_h = 45 * mm
    draw_image(c, "diagrams/D4-roof-detail", MARGIN_L, y - img_h, CONTENT_W, img_h, "D4: Ventilated roof")
    y -= img_h + 5 * mm
    
    # Thermal mass & Shading side by side
    c.setFont('Body-Bold', 10)
    c.setFillColor(DEEP_BROWN)
    c.drawString(MARGIN_L, y, "THERMAL MASS")
    c.drawString(MARGIN_L + COL_W + 8 * mm, y, "SHADING")
    y -= 5 * mm
    
    mass_text = ("Dense materials like stone, earth, and concrete absorb heat slowly during the day and release it "
                 "at night. In a well-ventilated home, thermal mass stabilises interior temperatures. The key is "
                 "coupling mass with ventilation — thermal mass in a sealed room just becomes a heat battery.")
    shade_text = ("External shading is always more effective than internal. Pergolas, deep eaves, louvers, and "
                  "vegetation prevent solar radiation from ever reaching your glass. Once sunlight passes through a "
                  "window, it becomes trapped heat. Stop it before it enters.")
    
    style_col = ParagraphStyle('colbody', fontName='Body', fontSize=8.5, leading=13,
                               textColor=CHARCOAL, alignment=TA_JUSTIFY)
    p1 = Paragraph(mass_text, style_col)
    p1w, p1h = p1.wrap(COL_W, 300)
    p1.drawOn(c, MARGIN_L, y - p1h)
    
    p2 = Paragraph(shade_text, style_col)
    p2w, p2h = p2.wrap(COL_W, 300)
    p2.drawOn(c, MARGIN_L + COL_W + 8 * mm, y - p2h)
    y -= max(p1h, p2h) + 5 * mm
    
    # D5 shading diagram
    img_h = 35 * mm
    draw_image(c, "diagrams/D5-shading", MARGIN_L, y - img_h, CONTENT_W, img_h, "D5: Shading comparison")
    y -= img_h + 5 * mm
    
    # Cost comparison — A5 infographic
    y = draw_subheader(c, MARGIN_L, y, "THE NUMBERS", color=TERRACOTTA)
    num_intro = ("What does all this add up to? Using conservative assumptions for a three-bedroom home in Guanacaste:")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, num_intro)
    y -= 2 * mm
    
    # A5 infographic or fallback table
    img_h = 50 * mm
    a5_found = draw_image(c, "visuals/A5-ac-cost-infographic", MARGIN_L, y - img_h, CONTENT_W, img_h, "A5: Cost comparison")
    
    if not a5_found:
        # Fallback: draw the table
        table_data = [
            ['SCENARIO', 'AC HOURS/DAY\n(HOT SEASON)', 'ANNUAL\nAC COST'],
            ['Conventional concrete block', '10–12 hrs', '~$2,500'],
            ['Passive — conservative (50%)', '5–6 hrs', '~$1,270'],
            ['Passive — moderate (70%)', '~3 hrs', '~$760'],
            ['Passive — optimised (90%)', '1 hr or less', '~$250'],
        ]
        col_widths = [CONTENT_W * 0.50, CONTENT_W * 0.25, CONTENT_W * 0.25]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Body-Bold', 7),
            ('FONT', (0, 1), (-1, -1), 'Body', 8),
            ('TEXTCOLOR', (0, 0), (-1, 0), CREAM),
            ('TEXTCOLOR', (0, 1), (-1, -1), CHARCOAL),
            ('BACKGROUND', (0, 0), (-1, 0), DEEP_BROWN),
            ('BACKGROUND', (0, 1), (-1, 1), HexColor('#F0E8DC')),
            ('BACKGROUND', (0, 2), (-1, 2), HexColor('#F5F0E8')),
            ('BACKGROUND', (0, 3), (-1, 3), HexColor('#EAF0E6')),
            ('BACKGROUND', (0, 4), (-1, 4), HexColor('#DDE8D6')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, WARM_SAND),
        ]))
        tw, th = table.wrap(CONTENT_W, 200)
        table.drawOn(c, MARGIN_L, y - th)
    
    draw_footer(c, 7)
    c.showPage()


def build_section_05(c):
    """Pages 8-9: Materials That Matter"""
    cream_page(c)
    y = section_header(c, "Materials That Matter", number=5)
    
    intro = ("The materials you build with determine how your home feels, performs, ages, and affects your health. "
             "There's a wider spectrum available than most people realise — and where you land depends on your "
             "priorities, budget, and how far you want to go.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, intro)
    y -= 2 * mm
    
    # Material texture strip
    img_h = 22 * mm
    draw_image(c, "visuals/material-texture-strip", MARGIN_L, y - img_h, CONTENT_W, img_h, "Material texture strip")
    y -= img_h + 5 * mm
    
    materials = [
        ("Concrete Block", "The Default",
         "Fast, familiar, structurally straightforward. But high embodied energy, poor thermal performance, "
         "and creates sealed environments requiring mechanical cooling. Not wrong for every application — "
         "but shouldn't be the unquestioned default."),
        ("Timber Frame", "Warmth & Character",
         "Excellent structural performance with significantly lower embodied energy. Locally sourced hardwoods "
         "(teak, melina, cenízaro) breathe, regulate humidity naturally, and age with character. The choice between "
         "toxic chemical treatments and natural alternatives has real health implications."),
        ("Bamboo", "Strength & Lightness",
         "Costa Rica's Guadua bamboo has a strength-to-weight ratio rivalling steel. Grows rapidly, sequesters "
         "carbon, and enables open, airy structures. Requires specialised knowledge — connections and moisture "
         "management are where bamboo buildings succeed or fail."),
        ("Stone", "Permanence & Mass",
         "Unmatched thermal mass, durability, and connection to the land. Regulates temperature passively, requires "
         "virtually no maintenance, and only improves with age. Works best as a strategic element — a thermal mass "
         "wall, a feature element, a foundation."),
        ("Earth", "The Original Material",
         "Wattle and daub, adobe, rammed earth — the lowest environmental footprint of any method. Superb thermal "
         "mass, natural humidity regulation, zero off-gassing. Requires skill and rain protection, but has been "
         "used successfully in tropical climates for millennia."),
    ]
    
    photo_keys = [
        "photography/P1-concrete-block",
        "photography/P5-timber",
        "photography/P6-bamboo",
        "photography/P7-stone",
        "photography/P8-earth",
    ]
    
    for i, (name, tagline, desc) in enumerate(materials):
        if y < 55 * mm:
            draw_footer(c, 8)
            c.showPage()
            cream_page(c)
            y = H - MARGIN_T - 5 * mm
        
        c.setFont('Body-Bold', 10)
        c.setFillColor(DEEP_BROWN)
        c.drawString(MARGIN_L, y, name)
        c.setFont('Body-Italic', 8)
        c.setFillColor(TERRACOTTA)
        c.drawString(MARGIN_L + c.stringWidth(name, 'Body-Bold', 10) + 4 * mm, y, f"— {tagline}")
        y -= 5 * mm
        
        img_w = 50 * mm
        img_h = 32 * mm
        text_w = CONTENT_W - img_w - 6 * mm
        
        if i % 2 == 0:
            draw_image(c, photo_keys[i], MARGIN_L, y - img_h, img_w, img_h, name)
            style = ParagraphStyle('matbody', fontName='Body', fontSize=8.5, leading=13,
                                   textColor=CHARCOAL, alignment=TA_JUSTIFY)
            p = Paragraph(desc, style)
            pw, ph = p.wrap(text_w, 200)
            p.drawOn(c, MARGIN_L + img_w + 6 * mm, y - ph)
            y -= max(img_h, ph) + 6 * mm
        else:
            draw_image(c, photo_keys[i], W - MARGIN_R - img_w, y - img_h, img_w, img_h, name)
            style = ParagraphStyle('matbody', fontName='Body', fontSize=8.5, leading=13,
                                   textColor=CHARCOAL, alignment=TA_JUSTIFY)
            p = Paragraph(desc, style)
            pw, ph = p.wrap(text_w, 200)
            p.drawOn(c, MARGIN_L, y - ph)
            y -= max(img_h, ph) + 6 * mm
    
    # Health dimension
    y -= 2 * mm
    y = draw_subheader(c, MARGIN_L, y, "THE HEALTH DIMENSION", color=TERRACOTTA)
    health = ("What most people don't consider: conventional materials release formaldehyde, benzene, and other "
              "volatile organic compounds for years after construction. In a sealed, air-conditioned home, you're "
              "living inside a low-grade chemical environment. Natural materials don't have this problem. They breathe. "
              "They regulate humidity. They create an indoor environment that is measurably healthier.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, health)
    
    # D6 wall sections
    if y > 55 * mm:
        y -= 3 * mm
        img_h = 45 * mm
        draw_image(c, "diagrams/D6-wall-sections", MARGIN_L, y - img_h, CONTENT_W, img_h, "D6: Wall sections")
    
    draw_footer(c, 9)
    c.showPage()


def build_section_06(c):
    """Page 10: Living Systems"""
    cream_page(c)
    y = section_header(c, "Living Systems", subtitle="Water, Waste, and Land Integration", number=6)
    
    intro = ("A home is not just a building. It's a node in a larger system — receiving water, energy, and resources, "
             "and producing waste, runoff, and heat. In Guanacaste, these centralised systems are more fragile than they appear.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, intro)
    y -= 3 * mm
    
    # D7 systems diagram
    img_h = 55 * mm
    draw_image(c, "diagrams/D7-site-systems", MARGIN_L, y - img_h, CONTENT_W, img_h, "D7: Site systems")
    y -= img_h + 5 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "RAINWATER HARVESTING", color=DEEP_BROWN)
    rain = ("Guanacaste receives 1,500–2,000mm of rainfall annually — almost all between May and November. "
            "A <b>150m² roof can harvest roughly 200,000 litres per wet season</b>. With filtration and UV treatment, "
            "this is suitable for all household use. The infrastructure cost is modest compared to drilling a well.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, rain)
    y -= 3 * mm
    
    # Rainfall chart
    img_h = 30 * mm
    draw_image(c, "visuals/A1-rainfall-chart", MARGIN_L, y - img_h, CONTENT_W, img_h, "A1: Rainfall chart")
    y -= img_h + 5 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "GREYWATER RECYCLING", color=DEEP_BROWN)
    grey = ("Water from sinks, showers, and laundry — roughly 50–60% of household use — can be filtered "
            "through simple biological systems and reused for irrigation. In a climate where every drop "
            "matters during dry season, this is sensible design, not luxury.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, grey)
    y -= 3 * mm
    
    y = draw_subheader(c, MARGIN_L, y, "COMPOSTING & NUTRIENT CYCLING", color=DEEP_BROWN)
    comp = ("Organic waste is not waste at all — it's fertility. A composting system integrated into your "
            "site design closes the nutrient loop and feeds the landscape around your home, connecting "
            "directly to food production — fruit trees, kitchen gardens, and agroforestry systems "
            "that transform your land from something you maintain into something that sustains you.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, comp)
    
    draw_footer(c, 10)
    c.showPage()


def build_section_07(c):
    """Page 11: Resilience & Self-Sufficiency"""
    cream_page(c)
    y = section_header(c, ["Resilience &", "Self-Sufficiency"], number=7)
    
    intro = ("There's a practical conversation happening quietly among people building here — and around the world. "
             "It goes beyond sustainability. Municipal water systems in Guanacaste are under stress. Electricity grids face "
             "disruption. Supply chains for imported materials are longer and more fragile than most people realise.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, intro)
    y -= 2 * mm
    
    y = draw_pull_quote(c, MARGIN_L + 5 * mm, y, CONTENT_W * 0.8,
                        "How much should your home depend on centralised systems that you have no control over? "
                        "The goal is not autarky. It's optionality.")
    y -= 6 * mm
    
    # Photo
    img_h = 45 * mm
    draw_image(c, "photography/P11-solar", MARGIN_L, y - img_h, CONTENT_W, img_h, "Self-sufficient home")
    y -= img_h + 5 * mm
    
    # Four pillars
    pillars = [
        ("Water Autonomy", "Your household can function through dry season without relying on overstressed municipal supply. "
         "Rainwater harvesting, efficient use, and greywater recycling gets you there."),
        ("Energy Independence", "Solar potential in Guanacaste is excellent. When a home is passively cooled, a modest "
         "solar installation covers most or all needs. Net metering is available through ICE."),
        ("Food Integration", "Design your landscape to include fruit trees, herbs, and productive species. A well-planned "
         "food forest requires minimal maintenance once established."),
        ("Material Resilience", "Build with materials that can be repaired locally, that don't depend on imported supply "
         "chains, and that age gracefully rather than degrading."),
    ]
    
    left_x = MARGIN_L
    right_x = MARGIN_L + COL_W + 8 * mm
    col_y = y
    
    for i, (title, desc) in enumerate(pillars):
        px = left_x if i % 2 == 0 else right_x
        py = col_y if i < 2 else col_y - 42 * mm
        
        c.setFillColor(SAGE)
        c.circle(px + 2.5 * mm, py + 1 * mm, 2.5 * mm, fill=1, stroke=0)
        c.setFont('Body-Bold', 7)
        c.setFillColor(CREAM)
        c.drawCentredString(px + 2.5 * mm, py - 0.5 * mm, f"{i + 1}")
        
        c.setFont('Body-Bold', 9)
        c.setFillColor(DEEP_BROWN)
        c.drawString(px + 8 * mm, py, title)
        
        style = ParagraphStyle('pillar', fontName='Body', fontSize=8, leading=12,
                               textColor=CHARCOAL, alignment=TA_LEFT)
        p = Paragraph(desc, style)
        pw, ph = p.wrap(COL_W - 8 * mm, 200)
        p.drawOn(c, px + 8 * mm, py - 4 * mm - ph)
    
    draw_footer(c, 11)
    c.showPage()


def build_section_08(c):
    """Page 12: What to Ask Your Architect"""
    cream_page(c)
    y = section_header(c, "What to Ask Your Architect", number=8)
    
    intro = ("Not every architect thinks about these things. Many are trained to design beautiful spaces without deeply "
             "considering how those spaces perform in a specific climate, or what the long-term implications of their "
             "material choices are. These questions will quickly reveal who is designing for Guanacaste and who is "
             "applying a generic template.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, intro)
    y -= 5 * mm
    
    questions = [
        ("On Orientation & Climate Response", [
            "How will you orient the home to minimise solar heat gain?",
            "What's your strategy for natural ventilation?",
            "Can you show me a sun path analysis for my site?"
        ]),
        ("On Materials", [
            "What materials are you specifying and why?",
            "What are the thermal properties of the wall assembly?",
            "What chemical treatments will be used, and what are the alternatives?"
        ]),
        ("On Water & Energy", [
            "Have you designed homes with rainwater harvesting?",
            "How would you size a system for this site?",
            "What's the projected energy demand after passive strategies?"
        ]),
        ("On Site Response", [
            "Have you spent time on the site? What did you observe?",
            "How does the design respond to wind, drainage, and vegetation?",
        ]),
        ("On Lifecycle Costs", [
            "What will this home cost to run — not just to build?",
            "How will materials age over 20 years?",
            "What maintenance will be required?"
        ]),
    ]
    
    for cat_title, items in questions:
        if y < 45 * mm:
            draw_footer(c, 12)
            c.showPage()
            cream_page(c)
            y = H - MARGIN_T - 10 * mm
        
        c.setFont('Body-Bold', 9.5)
        c.setFillColor(TERRACOTTA)
        c.drawString(MARGIN_L, y, cat_title)
        c.setStrokeColor(TERRACOTTA)
        c.setStrokeAlpha(0.3)
        c.setLineWidth(0.5)
        c.line(MARGIN_L, y - 2 * mm, MARGIN_L + CONTENT_W, y - 2 * mm)
        c.setStrokeAlpha(1)
        y -= 7 * mm
        
        for q in items:
            c.setFillColor(SAGE)
            c.circle(MARGIN_L + 2 * mm, y + 1.5 * mm, 1.2 * mm, fill=1, stroke=0)
            
            style = ParagraphStyle('q', fontName='Body', fontSize=8.5, leading=13,
                                   textColor=CHARCOAL, alignment=TA_LEFT)
            p = Paragraph(q, style)
            pw, ph = p.wrap(CONTENT_W - 10 * mm, 50)
            p.drawOn(c, MARGIN_L + 8 * mm, y - ph + 3.5)
            y -= ph + 2 * mm
        y -= 4 * mm
    
    y -= 4 * mm
    draw_pull_quote(c, MARGIN_L + 5 * mm, y, CONTENT_W * 0.8,
                    "The architect who can answer these questions confidently is the one designing a home "
                    "for your site, in your climate, for your life. The one who can't is designing a building "
                    "that happens to be located here.")
    
    draw_footer(c, 12)
    c.showPage()


def build_section_09(c):
    """Page 13: Key Terms in Spanish"""
    cream_page(c)
    y = section_header(c, ["Key Construction &", "Design Terms in Spanish"], number=9)
    
    intro = ("If you're building in Costa Rica, you'll be communicating with contractors, engineers, and municipal "
             "offices in Spanish. Having the right vocabulary makes these conversations productive — and earns respect.")
    y = draw_body_text(c, MARGIN_L, y, CONTENT_W, intro)
    y -= 5 * mm
    
    terms = [
        ['ENGLISH', 'ESPAÑOL', 'NOTES'],
        ['Gutters', 'Canoas', ''],
        ['Eaves / Overhang', 'Aleros', 'Critical for tropical shading'],
        ['Roof ridge', 'Cumbrera', ''],
        ['Beam', 'Viga', ''],
        ['Column', 'Columna', ''],
        ['Foundation', 'Cimentación', ''],
        ['Concrete block', 'Bloque de concreto', 'Standard wall material'],
        ['Rebar', 'Varilla', ''],
        ['Formwork', 'Formaleta', ''],
        ['Slab', 'Losa', ''],
        ['Retaining wall', 'Muro de contención', ''],
        ['Rainwater tank', 'Tanque de captación', ''],
        ['Building permit', 'Permiso de construcción', 'Issued by municipalidad'],
        ['Setbacks', 'Retiros', 'Distance from property lines'],
        ['Plot / Lot', 'Lote', ''],
        ['Land survey', 'Plano catastrado', 'Registered with CFIA'],
        ['Foreman', 'Maestro de obras', 'Key relationship'],
        ['Plumber', 'Fontanero', ''],
        ['Electrician', 'Electricista', ''],
        ['Carpenter', 'Carpintero', ''],
        ['Welder', 'Soldador', ''],
        ['Bamboo (structural)', 'Caña de bambú', 'Guadua species'],
        ['Natural ventilation', 'Ventilación natural', ''],
        ['Cross-ventilation', 'Ventilación cruzada', ''],
        ['Passive cooling', 'Enfriamiento pasivo', 'May need explaining'],
    ]
    
    col_widths_t = [CONTENT_W * 0.30, CONTENT_W * 0.32, CONTENT_W * 0.38]
    table = Table(terms, colWidths=col_widths_t)
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Body-Bold', 7),
        ('FONT', (0, 1), (0, -1), 'Body-Medium', 7.5),
        ('FONT', (1, 1), (1, -1), 'Body-Bold', 7.5),
        ('FONT', (2, 1), (2, -1), 'Body-Light', 7),
        ('TEXTCOLOR', (0, 0), (-1, 0), CREAM),
        ('TEXTCOLOR', (0, 1), (0, -1), CHARCOAL),
        ('TEXTCOLOR', (1, 1), (1, -1), DEEP_BROWN),
        ('TEXTCOLOR', (2, 1), (2, -1), MEDIUM_BROWN),
        ('BACKGROUND', (0, 0), (-1, 0), DEEP_BROWN),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_CREAM, CREAM]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, TERRACOTTA),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, WARM_SAND),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    tw, th = table.wrap(CONTENT_W, 400)
    table.drawOn(c, MARGIN_L, y - th)
    
    draw_footer(c, 13)
    c.showPage()


def build_section_10(c):
    """Page 14: CTA / Back Cover"""
    # Dark background
    c.setFillColor(DEEP_BROWN)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    
    # Back cover image
    img_h = 110 * mm
    draw_image(c, "visuals/back-cover", 0, H - img_h, W, img_h, "Back cover")
    
    # Terracotta accent line
    c.setStrokeColor(TERRACOTTA)
    c.setLineWidth(3)
    y = H - img_h - 15 * mm
    c.line(MARGIN_L, y, MARGIN_L + 50 * mm, y)
    y -= 12 * mm
    
    c.setFont('Heading', 28)
    c.setFillColor(CREAM)
    c.drawString(MARGIN_L, y, "Start the Conversation")
    y -= 14 * mm
    
    style_cta = ParagraphStyle(
        'ctabody', fontName='Body-Light', fontSize=10, leading=16,
        textColor=WARM_SAND, alignment=TA_LEFT,
    )
    cta_text = Paragraph(
        "If what you've read here resonates — if you want a home designed for this climate, "
        "built with materials that respect your health and the environment, and connected to "
        "the land it sits on — we'd welcome the opportunity to talk about your project.",
        style_cta
    )
    cw, ch = cta_text.wrap(CONTENT_W * 0.8, 100)
    cta_text.drawOn(c, MARGIN_L, y - ch)
    y -= ch + 10 * mm
    
    cta2 = Paragraph(
        "Every project begins with a conversation and a site visit. No obligations, no sales pitch — "
        "just an honest discussion about what's possible on your land.",
        style_cta
    )
    c2w, c2h = cta2.wrap(CONTENT_W * 0.8, 100)
    cta2.drawOn(c, MARGIN_L, y - c2h)
    y -= c2h + 14 * mm
    
    # Contact details
    contact_items = [
        ("BOOK A DISCOVERY CALL", "[link]"),
        ("VISIT OUR WORK", "tierraperma.com"),
        ("EMAIL", "[email]"),
        ("INSTAGRAM", "@tierraperma"),
    ]
    
    for label, value in contact_items:
        c.setFont('Body-Medium', 7)
        c.setFillColor(TERRACOTTA)
        c.drawString(MARGIN_L, y, label)
        c.setFont('Body', 9)
        c.setFillColor(CREAM)
        c.drawString(MARGIN_L + 45 * mm, y, value)
        y -= 8 * mm
    
    # Logo
    y -= 8 * mm
    logo_path = find_image("brand/logo")
    if logo_path:
        try:
            c.drawImage(logo_path, MARGIN_L, y - 8 * mm, 20 * mm, 20 * mm,
                       preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    c.setFont('Body-Medium', 9)
    c.setFillColor(CREAM)
    c.drawString(MARGIN_L + 28 * mm, y + 2, "TIERRA PERMA")
    c.setFont('Body-Light', 7)
    c.setFillColor(WARM_SAND)
    c.drawString(MARGIN_L + 28 * mm, y - 7, "Regenerative Architecture & Permaculture Design")
    
    # Copyright
    c.setFont('Body-Light', 6)
    c.setFillColor(MEDIUM_BROWN)
    c.drawCentredString(W / 2, 12 * mm, "© Tierra Perma — Regenerative Architecture & Permaculture Design — Tamarindo, Guanacaste, Costa Rica")
    
    c.showPage()


# ============================================================
# MAIN BUILD
# ============================================================

def main():
    print("=" * 60)
    print("TIERRA PERMA — Tropical Home Design Guide")
    print("PDF Builder")
    print("=" * 60)
    
    # Register fonts
    print("\nRegistering fonts...")
    register_fonts()
    
    # Check for images
    print(f"\nImage directory: {IMG_DIR}")
    if IMG_DIR.exists():
        image_count = sum(1 for _ in IMG_DIR.rglob('*') if _.is_file())
        print(f"Found {image_count} image files")
    else:
        print("WARNING: images/ directory not found — will use placeholders")
        IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build PDF
    output_path = OUTPUT_DIR / "Tierra-Perma-Tropical-Home-Design-Guide.pdf"
    print(f"\nBuilding PDF: {output_path}")
    
    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setTitle("Tropical Home Design Guide — Tierra Perma")
    c.setAuthor("Tierra Perma")
    c.setSubject("Regenerative Architecture & Permaculture Design")
    
    build_cover(c)
    print("  ✓ Cover")
    
    build_toc(c)
    print("  ✓ Table of Contents")
    
    build_section_01(c)
    print("  ✓ Section 01: Why This Guide Exists")
    
    build_section_02(c)
    print("  ✓ Section 02: The Problem")
    
    build_section_03(c)
    print("  ✓ Section 03: Reading Your Site")
    
    build_section_04(c)
    print("  ✓ Section 04: Designing with the Climate (2 pages)")
    
    build_section_05(c)
    print("  ✓ Section 05: Materials That Matter")
    
    build_section_06(c)
    print("  ✓ Section 06: Living Systems")
    
    build_section_07(c)
    print("  ✓ Section 07: Resilience & Self-Sufficiency")
    
    build_section_08(c)
    print("  ✓ Section 08: What to Ask Your Architect")
    
    build_section_09(c)
    print("  ✓ Section 09: Key Terms in Spanish")
    
    build_section_10(c)
    print("  ✓ Section 10: Start the Conversation (Back Cover)")
    
    c.save()
    print(f"\n{'=' * 60}")
    print(f"PDF saved to: {output_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
