import os
import requests
from io import BytesIO
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate

# ─── Brand Colours ───────────────────────────────────────────────────────────
DARK_TEAL   = HexColor("#1a3c34")   # deep header/accent
MID_TEAL    = HexColor("#2a6b5f")   # secondary
LIGHT_TEAL  = HexColor("#4a8a7e")   # tag backgrounds
GOLD        = HexColor("#c8a96a")   # accent gold
LIGHT_BG    = HexColor("#f5f5f0")   # section bg
LIGHT_GREY  = HexColor("#e8e8e0")   # dividers
TEXT_DARK   = HexColor("#1a1a1a")
TEXT_MID    = HexColor("#444444")
TEXT_LIGHT  = HexColor("#888888")
WHITE       = HexColor("#ffffff")

W, H = A4   # 595.27 x 841.89 pts

IMAGES_DIR = "/home/claude/Kota-Stone-Factory/Images"
OUT_DIR    = "/mnt/user-data/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# ─── Styles ──────────────────────────────────────────────────────────────────
def make_styles():
    return {
        "cover_brand": ParagraphStyle("cover_brand", fontName="Helvetica-Bold",
            fontSize=36, textColor=WHITE, alignment=TA_CENTER, leading=44),
        "cover_tagline": ParagraphStyle("cover_tagline", fontName="Helvetica",
            fontSize=13, textColor=HexColor("#d4e8e4"), alignment=TA_CENTER, leading=20),
        "cover_title": ParagraphStyle("cover_title", fontName="Helvetica-Bold",
            fontSize=28, textColor=WHITE, alignment=TA_CENTER, leading=36, spaceAfter=6),
        "cover_subtitle": ParagraphStyle("cover_subtitle", fontName="Helvetica",
            fontSize=14, textColor=HexColor("#c8ddd9"), alignment=TA_CENTER, leading=22),
        "section_tag": ParagraphStyle("section_tag", fontName="Helvetica-Bold",
            fontSize=9, textColor=LIGHT_TEAL, spaceAfter=4, leading=14,
            letterSpacing=2),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold",
            fontSize=20, textColor=DARK_TEAL, spaceAfter=8, leading=28),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold",
            fontSize=13, textColor=DARK_TEAL, spaceAfter=4, leading=18),
        "body": ParagraphStyle("body", fontName="Helvetica",
            fontSize=10, textColor=TEXT_MID, leading=16, spaceAfter=8,
            alignment=TA_JUSTIFY),
        "body_small": ParagraphStyle("body_small", fontName="Helvetica",
            fontSize=9, textColor=TEXT_MID, leading=14, spaceAfter=6),
        "feature_title": ParagraphStyle("feature_title", fontName="Helvetica-Bold",
            fontSize=11, textColor=DARK_TEAL, spaceAfter=3, leading=15),
        "feature_body": ParagraphStyle("feature_body", fontName="Helvetica",
            fontSize=9, textColor=TEXT_MID, leading=13),
        "spec_key": ParagraphStyle("spec_key", fontName="Helvetica-Bold",
            fontSize=9, textColor=DARK_TEAL, leading=13),
        "spec_val": ParagraphStyle("spec_val", fontName="Helvetica",
            fontSize=9, textColor=TEXT_MID, leading=13),
        "sku_code": ParagraphStyle("sku_code", fontName="Helvetica-Bold",
            fontSize=10, textColor=GOLD, leading=14),
        "sku_name": ParagraphStyle("sku_name", fontName="Helvetica-Bold",
            fontSize=12, textColor=DARK_TEAL, leading=16),
        "sku_body": ParagraphStyle("sku_body", fontName="Helvetica",
            fontSize=9, textColor=TEXT_MID, leading=13),
        "footer_text": ParagraphStyle("footer_text", fontName="Helvetica",
            fontSize=8, textColor=TEXT_LIGHT, alignment=TA_CENTER),
        "contact_label": ParagraphStyle("contact_label", fontName="Helvetica-Bold",
            fontSize=9, textColor=DARK_TEAL, leading=14),
        "contact_val": ParagraphStyle("contact_val", fontName="Helvetica",
            fontSize=9, textColor=TEXT_MID, leading=14),
        "pill": ParagraphStyle("pill", fontName="Helvetica-Bold",
            fontSize=8, textColor=WHITE, alignment=TA_CENTER),
        "gold_label": ParagraphStyle("gold_label", fontName="Helvetica-Bold",
            fontSize=10, textColor=GOLD, leading=14),
        "page_title_box": ParagraphStyle("page_title_box", fontName="Helvetica-Bold",
            fontSize=16, textColor=WHITE, alignment=TA_CENTER, leading=22),
    }

S = make_styles()

# ─── Helper: load local image ─────────────────────────────────────────────────
def load_local_image(path, width=None, height=None):
    try:
        img = Image(path)
        if width and height:
            img.drawWidth = width
            img.drawHeight = height
        elif width:
            ratio = img.drawHeight / img.drawWidth
            img.drawWidth = width
            img.drawHeight = width * ratio
        elif height:
            ratio = img.drawWidth / img.drawHeight
            img.drawHeight = height
            img.drawWidth = height * ratio
        return img
    except:
        return None

# ─── Helper: load Unsplash image (with fallback) ──────────────────────────────
def load_web_image(url, width=None, height=None):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            bio = BytesIO(resp.content)
            img = Image(bio)
            if width and height:
                img.drawWidth = width
                img.drawHeight = height
            elif width:
                ratio = img.drawHeight / img.drawWidth
                img.drawWidth = width
                img.drawHeight = width * ratio
            return img
    except:
        pass
    return None

# ─── Page decoration callback ─────────────────────────────────────────────────
def make_page_decorator(title, page_num_ref):
    def decorator(canvas_obj, doc):
        canvas_obj.saveState()
        # Header bar
        canvas_obj.setFillColor(DARK_TEAL)
        canvas_obj.rect(0, H - 28*mm, W, 28*mm, fill=1, stroke=0)
        # Brand name
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(15*mm, H - 16*mm, "KOTASTONE")
        # Gold dot separator
        canvas_obj.setFillColor(GOLD)
        canvas_obj.circle(15*mm + 85, H - 12.5*mm, 2, fill=1, stroke=0)
        # Page title in header
        canvas_obj.setFillColor(HexColor("#c8ddd9"))
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(15*mm + 100, H - 16*mm, title)
        # Right: certified badge
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.drawRightString(W - 15*mm, H - 13*mm, "ISO 9001:2015  |  Grade A Quality  |  Export Certified")
        # Gold bottom accent line on header
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, H - 28*mm, W, 1.5, fill=1, stroke=0)
        # Footer
        canvas_obj.setFillColor(DARK_TEAL)
        canvas_obj.rect(0, 0, W, 18*mm, fill=1, stroke=0)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, 18*mm, W, 1, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor("#aaccaa"))
        canvas_obj.setFont("Helvetica", 7.5)
        canvas_obj.drawString(15*mm, 11*mm, "KotaStone India  |  Ramganj Mandi, Kota, Rajasthan – 326519")
        canvas_obj.drawString(15*mm, 6*mm, "Phone: +91 86194 59354  |  Email: info@kotastone.in  |  www.kotastone.in")
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawRightString(W - 15*mm, 8.5*mm, f"Page {doc.page}")
        canvas_obj.restoreState()
    return decorator

# ─── Cover Page builder ───────────────────────────────────────────────────────
def build_cover(story, title, subtitle, description, image_path=None, web_image_url=None,
                color_swatch=None, badge_text=None):
    """Build a visually rich cover page."""
    # We'll draw the cover manually using a canvas trick via a custom flowable
    class CoverFlowable(Flowable):
        def __init__(self):
            Flowable.__init__(self)
            self.width = W - 30*mm  # fit within margins
            self.height = 0  # zero height — drawn via canvas directly
        def draw(self):
            c = self.canv
            c.saveState()
            # Full-page dark background
            c.setFillColor(DARK_TEAL)
            c.rect(0, 0, W, H, fill=1, stroke=0)
            # Geometric accent: right triangle
            c.setFillColor(MID_TEAL)
            p = c.beginPath()
            p.moveTo(W * 0.55, H)
            p.lineTo(W, H)
            p.lineTo(W, H * 0.3)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
            # Gold accent bar (left)
            c.setFillColor(GOLD)
            c.rect(0, 0, 6, H, fill=1, stroke=0)
            # Gold horizontal line
            c.rect(15*mm, H * 0.52, W - 30*mm, 1.5, fill=1, stroke=0)
            # Brand
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 42)
            c.drawString(15*mm, H * 0.88, "KOTA")
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 42)
            c.drawString(15*mm + 108, H * 0.88, "STONE")
            # Tagline under brand
            c.setFillColor(HexColor("#c8ddd9"))
            c.setFont("Helvetica", 11)
            c.drawString(15*mm, H * 0.84, "India's Premium Natural Limestone — Direct from Kota, Rajasthan")
            # Gold tag pill
            if badge_text:
                c.setFillColor(GOLD)
                c.roundRect(15*mm, H * 0.74, 90, 18, 4, fill=1, stroke=0)
                c.setFillColor(DARK_TEAL)
                c.setFont("Helvetica-Bold", 8)
                c.drawCentredString(15*mm + 45, H * 0.74 + 6, badge_text.upper())
            # Main title
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 34)
            y_title = H * 0.63
            c.drawString(15*mm, y_title, title)
            # Subtitle
            c.setFillColor(GOLD)
            c.setFont("Helvetica", 15)
            c.drawString(15*mm, y_title - 28, subtitle)
            # Description lines
            c.setFillColor(HexColor("#c8ddd9"))
            c.setFont("Helvetica", 10)
            # wrap text manually
            words = description.split()
            line = ""
            y = y_title - 58
            for word in words:
                test = line + " " + word if line else word
                if c.stringWidth(test, "Helvetica", 10) < W - 30*mm:
                    line = test
                else:
                    c.drawString(15*mm, y, line)
                    y -= 16
                    line = word
            if line:
                c.drawString(15*mm, y, line)
            # Color swatch if provided
            if color_swatch:
                r1, g1, b1 = color_swatch[0]
                r2, g2, b2 = color_swatch[1]
                sw_x = W - 80*mm
                sw_y = H * 0.62
                c.setFillColorRGB(r1/255, g1/255, b1/255)
                c.roundRect(sw_x, sw_y, 35*mm, 35*mm, 4, fill=1, stroke=0)
                c.setFillColorRGB(r2/255, g2/255, b2/255)
                c.roundRect(sw_x + 38*mm, sw_y, 20*mm, 35*mm, 4, fill=1, stroke=0)
                c.setFillColor(HexColor("#c8ddd9"))
                c.setFont("Helvetica", 8)
                c.drawCentredString(sw_x + 27*mm, sw_y - 12, "Colour Range")
            # Bottom contact strip
            c.setFillColor(HexColor("#0f2620"))
            c.rect(0, 0, W, 30*mm, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.rect(0, 30*mm, W, 1.5, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(15*mm, 20*mm, "+91 86194 59354")
            c.drawCentredString(W/2, 20*mm, "info@kotastone.in")
            c.drawRightString(W - 15*mm, 20*mm, "www.kotastone.in")
            c.setFillColor(HexColor("#aaaaaa"))
            c.setFont("Helvetica", 8)
            c.drawString(15*mm, 13*mm, "Ramganj Mandi, Kota, Rajasthan – 326519")
            c.drawRightString(W - 15*mm, 13*mm, "ISO 9001:2015 Certified | Grade A | Export Ready")
            c.drawCentredString(W/2, 7*mm, f"© 2025 KotaStone India. All rights reserved.")
            c.restoreState()

    story.append(CoverFlowable())
    story.append(PageBreak())

# ─── Section divider ──────────────────────────────────────────────────────────
def section_header(story, tag, title):
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(tag.upper(), S["section_tag"]))
    story.append(Paragraph(title, S["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8))

# ─── Feature grid: 2 columns ──────────────────────────────────────────────────
def feature_grid(story, features):
    """features: list of (icon_char, title, body)"""
    rows = []
    for i in range(0, len(features), 2):
        row = []
        for feat in features[i:i+2]:
            _, title, body = feat
            cell = [
                Paragraph(title, S["feature_title"]),
                Paragraph(body, S["feature_body"]),
            ]
            row.append(cell)
        if len(row) == 1:
            row.append("")
        rows.append(row)

    tbl = Table(rows, colWidths=[(W - 30*mm)/2 - 3*mm, (W - 30*mm)/2 - 3*mm],
                hAlign='LEFT', spaceAfter=6)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('LINEABOVE', (0,0), (-1,0), 2, LIGHT_TEAL),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

# ─── Specs table ─────────────────────────────────────────────────────────────
def specs_table(story, specs, title="Technical Specifications"):
    section_header(story, "Technical Data", title)
    rows = [["Property", "Value", "Standard"]]
    for row in specs:
        rows.append(list(row))
    tbl = Table(rows, colWidths=[60*mm, 80*mm, 25*mm], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TEXTCOLOR', (0,1), (0,-1), DARK_TEAL),
        ('TEXTCOLOR', (1,1), (-1,-1), TEXT_MID),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

# ─── SKU cards ────────────────────────────────────────────────────────────────
def sku_grid(story, skus):
    """skus: list of (code, name, desc, finish)"""
    section_header(story, "Product Catalogue", "Grade & Finish Codes")
    rows = []
    for i in range(0, len(skus), 2):
        row_data = []
        for sku in skus[i:i+2]:
            code, name, desc, finish = sku
            cell = [
                Paragraph(code, S["sku_code"]),
                Paragraph(name, S["sku_name"]),
                Paragraph(desc, S["sku_body"]),
                Spacer(1, 4),
                Paragraph(f"● {finish}", S["body_small"]),
            ]
            row_data.append(cell)
        if len(row_data) == 1:
            row_data.append("")
        rows.append(row_data)
    tbl = Table(rows, colWidths=[(W - 30*mm)/2 - 3*mm, (W - 30*mm)/2 - 3*mm],
                hAlign='LEFT', spaceAfter=8)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ('GRID', (0,0), (-1,-1), 1, LIGHT_TEAL),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEABOVE', (0,0), (-1,0), 3, GOLD),
    ]))
    story.append(tbl)

# ─── Sizes box ────────────────────────────────────────────────────────────────
def sizes_section(story, sizes, thicknesses):
    data = []
    # header row
    data.append([
        Paragraph("Available Sizes", S["spec_key"]),
        Paragraph("Thickness Options", S["spec_key"]),
    ])
    max_rows = max(len(sizes), len(thicknesses))
    for i in range(max_rows):
        s = sizes[i] if i < len(sizes) else ("", "")
        t = thicknesses[i] if i < len(thicknesses) else ("", "")
        data.append([
            Paragraph(f"{s[0]}  <font color='#888888'>{s[1]}</font>", S["spec_val"]),
            Paragraph(f"{t[0]}  <font color='#888888'>{t[1]}</font>", S["spec_val"]),
        ])
    col_w = (W - 30*mm) / 2 - 3*mm
    tbl = Table(data, colWidths=[col_w, col_w], hAlign='LEFT', spaceAfter=8)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(tbl)

# ─── Applications list ────────────────────────────────────────────────────────
def applications_list(story, apps):
    """apps: list of (title, desc)"""
    section_header(story, "Best Suited For", "Ideal Applications")
    rows = []
    for title, desc in apps:
        rows.append([
            Paragraph(f"✦  {title}", S["feature_title"]),
            Paragraph(desc, S["feature_body"]),
        ])
    tbl = Table(rows, colWidths=[55*mm, W - 30*mm - 55*mm - 6*mm], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('LINEABOVE', (0,0), (-1,0), 2, MID_TEAL),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

# ─── CTA bar ─────────────────────────────────────────────────────────────────
def cta_bar(story, text="Request a Free Sample or Bulk Quote Today"):
    data = [[
        Paragraph(text, ParagraphStyle("cta", fontName="Helvetica-Bold",
            fontSize=12, textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("Call: +91 86194 59354\nWhatsApp: +91 86194 59354\ninfo@kotastone.in",
            ParagraphStyle("cta2", fontName="Helvetica", fontSize=9,
            textColor=GOLD, alignment=TA_CENTER, leading=14)),
    ]]
    tbl = Table(data, colWidths=[(W-30*mm)*0.65, (W-30*mm)*0.35], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_TEAL),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,0), (-1,0), 3, GOLD),
    ]))
    story.append(Spacer(1, 8*mm))
    story.append(tbl)

# ─── Image row ────────────────────────────────────────────────────────────────
def image_row(story, local_paths, caption=""):
    imgs = []
    valid = []
    for p in local_paths:
        if p and os.path.exists(p):
            valid.append(p)
    if not valid:
        return
    n = len(valid)
    cell_w = (W - 30*mm) / n - 3*mm
    row = []
    for p in valid:
        try:
            img = Image(p, width=cell_w, height=cell_w * 0.65)
            img.hAlign = 'CENTER'
            row.append(img)
        except:
            pass
    if row:
        tbl = Table([row], colWidths=[cell_w]*n, hAlign='LEFT')
        tbl.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(tbl)
        if caption:
            story.append(Paragraph(caption, ParagraphStyle("cap",
                fontName="Helvetica", fontSize=8, textColor=TEXT_LIGHT,
                alignment=TA_CENTER, spaceBefore=3)))
        story.append(Spacer(1, 4*mm))

# ─── Build PDF ────────────────────────────────────────────────────────────────
def build_pdf(filename, page_title, story_builder):
    path = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=35*mm, bottomMargin=25*mm,
    )
    story = []
    story_builder(story)
    doc.build(story, onFirstPage=make_page_decorator(page_title, [0]),
              onLaterPages=make_page_decorator(page_title, [0]))
    print(f"  ✓ {filename}")
    return path

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 1: MAIN CATALOGUE (catalogue.pdf)
# ═══════════════════════════════════════════════════════════════════════════════
def build_main_catalogue(story):
    build_cover(story,
        title="Complete Product Catalogue",
        subtitle="Stone Variants · Finishes · Applications · Technical Specs",
        description="The definitive guide to KotaStone India's premium Kota limestone products — sourced directly from the quarries of Kota, Rajasthan. Trusted by architects, builders, and homeowners across India and 30+ countries.",
        badge_text="2025 Edition",
        color_swatch=[(74, 138, 126), (160, 100, 40)],
    )

    # ── Overview
    section_header(story, "About KotaStone India", "India's Most Trusted Natural Stone Supplier")
    story.append(Paragraph(
        "KotaStone India has been India's premier direct-from-quarry supplier of Kota limestone since 1975. "
        "We operate our own quarries in Ramganj Mandi, Kota, Rajasthan — the global epicentre of Kota Stone production — "
        "ensuring complete quality control from extraction to delivery. Our stone is ISO 9001:2015 certified and exported "
        "to over 30 countries across Asia, the Middle East, Europe, and North America.", S["body"]))

    # Quick stats bar
    stats = [
        ["50+\nYears Experience", "Grade A\nQuality", "30+\nCountries Served", "ISO 9001\nCertified"],
    ]
    tbl = Table(stats, colWidths=[(W-30*mm)/4]*4, hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,-1), WHITE),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LINEABOVE', (0,0), (-1,0), 3, GOLD),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8*mm))

    # ── Stone Variants
    section_header(story, "Stone Variants", "Kota Blue & Kota Brown")
    story.append(Paragraph(
        "Kota Stone is available in two primary colour families — the iconic Kota Blue (blue-green tones) and the "
        "warm Kota Brown (amber and earthy tones). Both share identical structural properties but offer dramatically "
        "different aesthetic characters to suit any project vision.", S["body"]))
    image_row(story,
        [f"{IMAGES_DIR}/Kota Blue.png", f"{IMAGES_DIR}/Kota Brown.png"],
        "Left: Kota Blue (blue-green)  |  Right: Kota Brown (warm amber)")

    # Variant comparison
    var_data = [
        [Paragraph("Feature", S["spec_key"]),
         Paragraph("Kota Blue", S["spec_key"]),
         Paragraph("Kota Brown", S["spec_key"])],
        ["Colour Range", "Blue-Green to Aqua-Grey", "Amber, Brown & Tan"],
        ["Compressive Strength", "≥ 70 MPa", "≥ 68 MPa"],
        ["Water Absorption", "< 0.5%", "< 0.5%"],
        ["Mohs Hardness", "3 – 4", "3 – 4"],
        ["Best Use", "Contemporary & Modern", "Heritage & Traditional"],
        ["Availability", "All finishes", "All finishes"],
    ]
    tbl = Table(var_data, colWidths=[55*mm, 65*mm, 65*mm], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    # ── Finishes
    section_header(story, "Surface Finishes", "Five Finish Options for Every Application")
    finishes = [
        ("Polished", "Mirror-like high-gloss surface. Luxury lobbies, showrooms, premium interiors."),
        ("Honed", "Smooth satin-matte. Contemporary residences, bathrooms, offices."),
        ("Natural", "Original quarried texture. Outdoor areas, terraces, heritage projects."),
        ("Leather", "Wire-brushed micro-texture. Pool surrounds, wet areas, outdoor entertaining."),
        ("Sandblasted", "Coarse anti-slip texture. Industrial, heavy-traffic, safety-critical zones."),
    ]
    f_data = [[Paragraph("Finish", S["spec_key"]), Paragraph("Description & Best Use", S["spec_key"])]]
    for name, desc in finishes:
        f_data.append([Paragraph(name, S["feature_title"]), Paragraph(desc, S["feature_body"])])
    tbl = Table(f_data, colWidths=[45*mm, W - 30*mm - 45*mm - 6*mm], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,1), (0,-1), DARK_TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    # ── Full Specs
    specs_table(story, [
        ("Stone Type", "Fine-Grained Limestone", "—"),
        ("Origin", "Kota, Rajasthan, India", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 68–70 MPa", "IS 1121"),
        ("Flexural Strength", "≥ 10 MPa", "IS 1723"),
        ("Mohs Hardness", "3 – 4", "—"),
        ("Density", "2600–2700 kg/m³", "IS 1124"),
        ("Abrasion Resistance", "High", "IS 1237"),
        ("Frost Resistance", "Excellent", "—"),
        ("Chemical Resistance", "High", "—"),
    ], "Full Technical Specifications")

    # ── Sizes
    section_header(story, "Dimensions", "Standard Sizes & Thickness Options")
    sizes_section(story,
        [("600 × 600 mm", "Standard Module"), ("600 × 900 mm", "Large Plank"),
         ("300 × 600 mm", "Plank Format"), ("400 × 400 mm", "Classic Square"),
         ("Custom Cut", "Any Dimension")],
        [("20 mm", "Standard Flooring"), ("25 mm", "Heavy Duty"),
         ("30 mm", "Industrial Grade"), ("10–12 mm", "Wall Cladding"),
         ("40+ mm", "Stair Tread")])

    # ── Applications
    section_header(story, "Applications", "Where Kota Stone Performs")
    image_row(story,
        [f"{IMAGES_DIR}/Outdoor_Flooring.png", f"{IMAGES_DIR}/Wall_Cladding.png",
         f"{IMAGES_DIR}/Pool.png"],
        "Flooring · Wall Cladding · Pool Surrounds")
    applications_list(story, [
        ("Flooring", "Residential, commercial, institutional — lasts 50+ years with minimal care."),
        ("Outdoor Pathways", "Garden paths, driveways, courtyards — weather and slip resistant."),
        ("Wall Cladding", "10–12 mm thin panels for interior feature walls and facades."),
        ("Pool Surrounds", "Anti-slip, cool underfoot, moisture resistant — ideal around water."),
        ("Staircases", "40+ mm treads for structural integrity and lasting beauty."),
        ("Kitchen Countertops", "Heat resistant to 300°C, food-safe, hygienic when sealed."),
        ("Industrial Flooring", "Heavy load rated, chemical resistant, zero maintenance."),
        ("Parking Areas", "Vehicle load rated, anti-skid, all-weather durable."),
    ])

    # ── Pricing Guide
    section_header(story, "Pricing Guide", "Indicative Price Ranges (INR per sq.ft.)")
    price_data = [
        [Paragraph("Product", S["spec_key"]), Paragraph("Finish", S["spec_key"]),
         Paragraph("Price Range (INR/sq.ft.)", S["spec_key"]), Paragraph("Notes", S["spec_key"])],
        ["Kota Blue", "Natural", "₹ 25 – 40", "Most economical"],
        ["Kota Blue", "Honed", "₹ 35 – 55", "Popular for interiors"],
        ["Kota Blue", "Polished", "₹ 50 – 80", "Premium finish"],
        ["Kota Blue", "Leather", "₹ 45 – 70", "Pool/outdoor specialist"],
        ["Kota Brown", "Natural", "₹ 28 – 45", "Heritage projects"],
        ["Kota Brown", "Honed", "₹ 38 – 58", "Warm interiors"],
        ["Custom Sizes", "Any", "POA", "Call for bulk quote"],
    ]
    tbl = Table(price_data, colWidths=[40*mm, 35*mm, 60*mm, 40*mm], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, LIGHT_GREY),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (2,1), (2,-1), MID_TEAL),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "* Prices are indicative and subject to quantity, finish, size, and delivery location. "
        "Contact our sales team for a firm quotation on your project.", S["body_small"]))

    cta_bar(story, "Download Free Sample Pack · Get a Project Quote · Schedule a Site Visit")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 2: KOTA BLUE
# ═══════════════════════════════════════════════════════════════════════════════
def build_kota_blue(story):
    build_cover(story,
        title="Kota Blue Stone",
        subtitle="The Iconic Blue-Green Limestone",
        description="The legendary blue-green limestone gracing India's finest homes, temples, and institutions for centuries. Timeless, durable, distinctively beautiful.",
        badge_text="Stone Variant",
        color_swatch=[(74, 138, 126), (42, 107, 95)],
    )
    section_header(story, "About This Variant", "What is Kota Blue Stone?")
    story.append(Paragraph(
        "Kota Blue is the most iconic variety of Kota Stone. Its characteristic blue-green hue — ranging from deep sea-blue "
        "to soft aqua-grey — results from the unique mineral composition found exclusively in the Kota district of Rajasthan. "
        "Formed over millions of years, Kota Blue is a fine-grained limestone with exceptional compressive strength, low water "
        "absorption (under 0.5%), and a naturally non-slip surface. It is the preferred material for architects, infrastructure "
        "projects, and discerning homeowners across India and over 30 countries.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Kota Blue.png"], "Kota Blue Stone — Blue-Green Limestone")

    section_header(story, "Why Choose Kota Blue", "Key Features & Benefits")
    feature_grid(story, [
        ("shield", "Exceptional Durability", "With compressive strength over 70 MPa, Kota Blue withstands extreme loads, heavy traffic, and harsh weather without cracking or degrading for generations."),
        ("tint", "Very Low Water Absorption", "Under 0.5% water absorption makes Kota Blue highly resistant to moisture, staining, and frost damage — ideal for both wet and dry environments."),
        ("shoe", "Natural Non-Slip Surface", "The naturally textured surface provides excellent grip even when wet, making it intrinsically safer than polished marble or ceramic tiles."),
        ("leaf", "100% Natural & Eco-Friendly", "No synthetic treatments, dyes, or coatings needed. Completely natural limestone — safe for families and environmentally responsible."),
        ("coins", "Outstanding Value", "Delivers the premium look of marble at a fraction of the cost, with far superior durability. Total lifecycle cost is significantly lower than most alternatives."),
        ("paint", "Multiple Finish Options", "Available in polished, honed, natural, leather, flamed, and sandblasted finishes — transforming the stone's appearance to suit any architectural vision."),
    ])
    specs_table(story, [
        ("Stone Type", "Fine-Grained Limestone", "—"),
        ("Origin", "Kota, Rajasthan, India", "—"),
        ("Colour Range", "Blue-Green to Aqua-Grey", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Flexural Strength", "≥ 10 MPa", "IS 1723"),
        ("Mohs Hardness", "3 – 4", "—"),
        ("Density", "2600–2700 kg/m³", "IS 1124"),
        ("Abrasion Resistance", "High", "IS 1237"),
    ])
    section_header(story, "Dimensions", "Available Sizes & Thickness")
    sizes_section(story,
        [("600 × 600 mm", "Standard Module"), ("600 × 900 mm", "Large Plank"),
         ("300 × 600 mm", "Plank Format"), ("400 × 400 mm", "Classic Square"),
         ("Custom Cut", "Any Dimension")],
        [("20 mm", "Standard Flooring"), ("25 mm", "Heavy Duty"),
         ("30 mm", "Industrial Grade"), ("10–12 mm", "Wall Cladding"),
         ("40+ mm", "Stair Tread")])
    sku_grid(story, [
        ("KBS01", "Sombre", "Deep blue-grey toned natural finish with a slightly textured surface. Ideal for heavy-duty outdoor flooring, pathways, and industrial use.", "Natural Finish"),
        ("KBS02", "Riverwatch", "Medium blue with aqua undertones in a smooth honed surface. Perfect for residential living rooms, offices, and contemporary interiors.", "Honed Finish"),
        ("KBS03", "Leather", "Wire-brushed leathered surface with a warm blue-green tone. The premier choice for pool surrounds, wet areas, and exterior terraces.", "Leather Finish"),
        ("KBS04", "Mirror", "High-gloss mirror polish with vivid blue-green pigmentation. The most glamorous expression of Kota Stone for luxury lobbies and showrooms.", "Polished Finish"),
        ("KBS05", "Mirror Satin", "Medium sheen between honed and full polish — soft reflective surface for upscale residential interiors and premium offices.", "Satin Polish"),
        ("KBS06", "High Honed", "Extra-fine honed surface with near-satin smoothness and subtle sheen. A modern, sophisticated finish for premium projects.", "High Honed"),
    ])
    applications_list(story, [
        ("Residential Flooring", "Perfect for living rooms, verandas and courtyards — creates a cool, elegant ambience that ages gracefully."),
        ("Commercial Spaces", "Hotels, hospitals, offices, and schools rely on Kota Blue for its low maintenance, durability, and professional appearance."),
        ("Outdoor Pathways", "The natural non-slip finish and weather resistance make Kota Blue ideal for garden paths, driveways, and public walkways."),
        ("Wall Cladding", "10–12 mm thin slabs add architectural depth and texture to interior feature walls and external building facades."),
        ("Pool Surrounds", "Anti-slip and moisture-resistant — the safest and most aesthetically stunning choice around swimming pools."),
        ("Staircases", "With 40+ mm tread thickness and natural grip, Kota Blue staircases offer structural integrity and enduring beauty."),
    ])
    cta_bar(story, "Request a Kota Blue Sample · Get a Bulk Quote · Delivery Pan-India in 7 Days")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 3: KOTA BROWN
# ═══════════════════════════════════════════════════════════════════════════════
def build_kota_brown(story):
    build_cover(story,
        title="Kota Brown Stone",
        subtitle="Rich Amber Limestone with Warm Character",
        description="Rich amber and brown hues that bring warmth, character, and rustic elegance to homes, heritage spaces, and outdoor landscapes.",
        badge_text="Stone Variant",
        color_swatch=[(160, 100, 40), (200, 140, 70)],
    )
    section_header(story, "About This Variant", "What is Kota Brown Stone?")
    story.append(Paragraph(
        "Kota Brown is the warm, earthy counterpart to the iconic Kota Blue. Featuring rich brown, amber, and tan hues, "
        "it brings the comfort of natural stone to interiors and exteriors where warmth and rustic elegance are desired. "
        "Quarried from the same geological formations in Kota, Rajasthan, Kota Brown shares the structural excellence of "
        "its blue sibling — identical compressive strength, low porosity, and long-term durability — while offering a "
        "dramatically different visual character that complements wood, terracotta, and heritage designs.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Kota Brown.png"], "Kota Brown Stone — Warm Amber Limestone")

    section_header(story, "Why Choose Kota Brown", "Key Features & Benefits")
    feature_grid(story, [
        ("palette", "Warm Earthy Palette", "Rich brown and amber hues pair beautifully with wood, terracotta, and earthy materials, creating naturally warm and inviting spaces."),
        ("shield", "Proven Durability", "Same geological composition as Kota Blue — compressive strength of 68+ MPa, frost resistant, and long-lasting in any climate condition."),
        ("mountain", "Unique Natural Variation", "Every slab carries unique natural veining and tonal variation — meaning no two installations are ever identical."),
        ("building", "Heritage & Traditional", "Preferred for heritage restoration, temples, traditional havelis, and community buildings where warm stone aesthetics are culturally significant."),
        ("coins", "Cost-Effective", "More economical than brown marble alternatives, with superior durability and identical warmth of tone at a fraction of the maintenance cost."),
        ("leaf", "Eco-Friendly", "100% natural limestone — no synthetic binders, dyes, or chemical treatments. Safe for families, sustainable for the planet."),
    ])
    specs_table(story, [
        ("Stone Type", "Fine-Grained Limestone", "—"),
        ("Origin", "Kota, Rajasthan, India", "—"),
        ("Colour Range", "Amber, Brown & Tan", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 68 MPa", "IS 1121"),
        ("Flexural Strength", "≥ 10 MPa", "IS 1723"),
        ("Mohs Hardness", "3 – 4", "—"),
        ("Density", "2600–2700 kg/m³", "IS 1124"),
        ("Abrasion Resistance", "High", "IS 1237"),
    ])
    section_header(story, "Dimensions", "Available Sizes & Thickness")
    sizes_section(story,
        [("600 × 600 mm", "Standard Module"), ("600 × 900 mm", "Large Plank"),
         ("300 × 600 mm", "Plank Format"), ("400 × 400 mm", "Classic Square"),
         ("Custom Cut", "Any Dimension")],
        [("20 mm", "Standard Flooring"), ("25 mm", "Heavy Duty"),
         ("30 mm", "Industrial Grade"), ("10–12 mm", "Wall Cladding"),
         ("40+ mm", "Stair Tread")])
    sku_grid(story, [
        ("KBR01", "Haveli Tan", "Classic tan-brown natural finish — the authentic Rajasthani heritage look for courtyards, temples, and traditional bungalows.", "Natural Finish"),
        ("KBR02", "Amber Honed", "Smooth amber-brown honed surface. Warm and sophisticated for modern interiors that blend heritage with contemporary design.", "Honed Finish"),
        ("KBR03", "Burnished", "Wire-brushed leather finish in warm brown tones. Ideal for outdoor entertainment areas, garden pathways, and pool surrounds.", "Leather Finish"),
        ("KBR04", "Amber Mirror", "High-polish brown finish that amplifies the warm amber tones. Perfect for feature walls, reception counters, and luxury interiors.", "Polished Finish"),
    ])
    applications_list(story, [
        ("Heritage Buildings & Temples", "The natural warmth of Kota Brown is the material of choice for temples, havelis, and heritage restoration projects."),
        ("Residential Courtyards", "Creates the traditional Indian courtyard aesthetic — warm, grounded, and beautifully authentic."),
        ("Landscape & Garden Design", "Blends naturally with soil, planting, and wood in garden pathways and outdoor seating areas."),
        ("Commercial Feature Walls", "Dramatic warm stone feature walls in restaurant, hotel, and retail environments."),
        ("Flooring", "An alternative to ceramic for those who want warmth and character in living and dining spaces."),
        ("Outdoor Pathways", "All-weather resistant; the warm brown tone ages naturally and develops rich character over time."),
    ])
    cta_bar(story, "Request a Kota Brown Sample · Get a Heritage Project Quote")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 4: POLISHED FINISH
# ═══════════════════════════════════════════════════════════════════════════════
def build_polished(story):
    build_cover(story,
        title="Polished Kota Stone",
        subtitle="Mirror-Like Luxury for Premium Interiors",
        description="A high-gloss, mirror-like surface achieved through multi-stage diamond polishing. The pinnacle of Kota Stone refinement for luxury hotels, showrooms, and premium residences.",
        badge_text="Surface Finish",
    )
    section_header(story, "About This Finish", "What is Polished Kota Stone?")
    story.append(Paragraph(
        "Polished Kota Stone undergoes a rigorous multi-stage diamond polishing process that progressively refines the surface "
        "from coarse to ultra-fine grits until a highly reflective, mirror-like sheen is achieved. The result is a surface that "
        "reflects light beautifully, amplifying the natural blue-green tones of the stone. This finish is the most glamorous "
        "expression of Kota Stone — perfect for luxury hotel lobbies, upscale residential interiors, retail showrooms, and "
        "high-end commercial spaces where visual impact is paramount.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Polished.png"], "Polished Kota Stone — High-Gloss Mirror Surface")

    section_header(story, "Why Choose Polished Finish", "Features & Benefits")
    feature_grid(story, [
        ("circle", "Mirror-Like Reflection", "The high-gloss surface creates a stunning visual effect that reflects light and makes interior spaces appear larger, brighter, and more luxurious."),
        ("palette", "Enhanced Natural Colour", "Polishing intensifies Kota Stone's characteristic blue-green pigmentation, making the colour deeper, more vivid, and visually striking."),
        ("broom", "Easy Maintenance", "The smooth, non-porous polished surface is exceptionally easy to mop and clean — ideal for high-traffic areas requiring frequent sanitation."),
        ("building", "Premium Aesthetic", "Delivers the luxury visual of polished marble at a fraction of the cost — the preferred choice for budget-conscious luxury projects."),
        ("shield", "Scratch & Stain Resistant", "The dense, closed-pore polished surface resists everyday scratching, chemical spills, and staining from oils, beverages, and cleaning agents."),
        ("layer", "Consistent Quality", "Our polishing process ensures uniform gloss level, colour consistency, and surface flatness across every slab in a project order."),
    ])
    specs_table(story, [
        ("Surface Gloss Level", "High (60°–80° gloss meter)", "—"),
        ("Surface Finish", "Diamond-Polished Multi-Stage", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Slip Resistance (dry)", "R9", "DIN 51130"),
        ("Mohs Hardness", "3 – 4", "—"),
        ("Recommended Sealant", "Penetrating Stone Sealer", "—"),
        ("Maintenance", "Damp mop; avoid acid cleaners", "—"),
    ])
    section_header(story, "Dimensions", "Available Sizes & Thickness")
    sizes_section(story,
        [("600 × 600 mm", "Standard Module"), ("600 × 900 mm", "Large Plank"),
         ("300 × 600 mm", "Plank Format"), ("Custom Cut", "Any Dimension")],
        [("20 mm", "Standard Flooring"), ("25 mm", "Heavy Duty"), ("10–12 mm", "Wall Cladding")])
    applications_list(story, [
        ("Hotel & Resort Lobbies", "The mirror finish creates a dramatic first impression in hospitality spaces."),
        ("Luxury Residences", "Master bedrooms, living rooms, and corridors in premium villas and apartments."),
        ("Retail Showrooms", "Reflects merchandise and lighting beautifully — ideal for jewellery, fashion, and luxury retail."),
        ("Corporate Offices", "Prestigious boardrooms, reception areas, and executive floors."),
        ("Restaurants & Fine Dining", "Adds glamour and visual drama to upscale dining interiors."),
        ("Temple Sanctuaries", "The rich, vivid colour suits the grandeur of temple interiors and mandapas."),
    ])
    cta_bar(story, "Order Polished Kota Stone Samples · Bulk Pricing Available")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 5: HONED FINISH
# ═══════════════════════════════════════════════════════════════════════════════
def build_honed(story):
    build_cover(story,
        title="Honed Kota Stone",
        subtitle="Smooth Matte Sophistication for Modern Spaces",
        description="A smooth, satin-matte surface that captures contemporary refinement. Non-reflective, scratch-resistant, and ideal for modern residential and commercial interiors.",
        badge_text="Surface Finish",
    )
    section_header(story, "About This Finish", "What is Honed Kota Stone?")
    story.append(Paragraph(
        "Honed Kota Stone is produced by grinding the surface to a smooth, uniform finish without the final polishing step "
        "that creates high gloss. The result is a satin-smooth, non-reflective matte surface that highlights the stone's natural "
        "texture and subtle colour variation without the sheen of polished stone. The honed finish is the preferred choice among "
        "contemporary interior designers for its clean, understated sophistication. It is significantly more slip-resistant — "
        "making it safer in wet areas such as bathrooms, spa environments, and kitchen floors.", S["body"]))
    section_header(story, "Why Choose Honed Finish", "Features & Benefits")
    feature_grid(story, [
        ("grip", "Smooth Matte Aesthetic", "A contemporary, non-glossy surface that works beautifully in minimalist, Scandinavian, and modern Indian design schemes."),
        ("shoe", "Superior Slip Resistance", "More textured than polished stone, the honed finish provides better grip in wet areas — ideal for bathrooms, spas, and kitchen floors."),
        ("eye", "Scratch-Forgiving Surface", "Minor scratches and surface wear marks are far less visible on a matte surface compared to high-gloss polished stone."),
        ("broom", "Easy Maintenance", "Smooth enough for easy cleaning while textured enough to not show every fingerprint and smudge — far more practical in daily use."),
        ("home", "Versatile Indoor Use", "Works equally well for flooring, wall cladding, bathroom tiling, kitchen platforms, and step risers."),
        ("palette", "Natural Colour Tone", "Preserves the stone's authentic natural colour without the amplified vividity of polished stone — a more organic, grounded palette."),
    ])
    specs_table(story, [
        ("Surface Gloss Level", "Low-Matte (5°–15° gloss meter)", "—"),
        ("Surface Finish", "Machine-Ground, Uniform Matte", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Slip Resistance (wet)", "R10", "DIN 51130"),
        ("Mohs Hardness", "3 – 4", "—"),
        ("Recommended Sealant", "Penetrating Sealer (optional)", "—"),
        ("Maintenance", "Damp mop; neutral pH cleaner", "—"),
    ])
    applications_list(story, [
        ("Bathrooms & Wet Rooms", "The safer non-slip matte surface, combined with low water absorption, makes honed Kota Stone ideal for bathroom floors and walls."),
        ("Living Rooms & Bedrooms", "Creates a calm, sophisticated ambience without the 'cold' feel of highly polished surfaces."),
        ("Kitchen Flooring", "Practical, hygienic, and easy to clean — handles spills, traffic, and dropped items without showing damage."),
        ("Offices & Commercial Spaces", "Professional, contemporary appearance — works well in open-plan offices, clinics, and educational institutions."),
        ("Stair Risers & Treads", "Safer underfoot than polished alternatives — particularly suited for residential staircase applications."),
        ("Feature Walls", "A subtle, textured wall surface that adds depth without competing with furniture and decor."),
    ])
    cta_bar(story, "Order Honed Kota Stone Samples · Modern Interior Specialists")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 6: NATURAL FINISH
# ═══════════════════════════════════════════════════════════════════════════════
def build_natural(story):
    build_cover(story,
        title="Natural Finish Kota Stone",
        subtitle="Raw, Authentic & Built for the Outdoors",
        description="Stone as nature intended — raw, textured, and authentic. The natural quarried surface trusted for outdoor spaces and heritage construction for centuries.",
        badge_text="Surface Finish",
    )
    section_header(story, "About This Finish", "What is Natural Finish Kota Stone?")
    story.append(Paragraph(
        "Natural Finish Kota Stone is the stone in its most authentic form — with the original quarried surface preserved after "
        "minimal processing. The surface retains natural undulations, quarry splits, and textural variations that give each piece "
        "a truly unique, organic character. This finish is the most traditional and widely used form of Kota Stone, especially "
        "for outdoor applications where its naturally high anti-slip rating and weather resistance are paramount. It is the "
        "preferred choice for open terraces, garden pathways, courtyards, temple complexes, and any project that celebrates "
        "the honest beauty of natural stone.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Outdoor_Flooring.png", f"{IMAGES_DIR}/Pathway.png"],
        "Natural Finish Kota Stone — Outdoor Flooring & Garden Pathways")

    section_header(story, "Why Choose Natural Finish", "Features & Benefits")
    feature_grid(story, [
        ("mountain", "Authentic Natural Surface", "The preserved quarried texture gives each installation a genuine, organic character that no manufactured tile can replicate."),
        ("shoe", "Maximum Anti-Slip", "The highest slip resistance of all Kota Stone finishes — the natural surface undulation creates truly secure footing in all weather."),
        ("cloud", "All-Weather Performance", "Handles extreme heat, heavy monsoon rain, and freezing temperatures without surface degradation, spalling, or colour fade."),
        ("coins", "Most Cost-Effective", "Minimal processing makes natural finish the most economical Kota Stone option — ideal for large-area projects and infrastructure."),
        ("leaf", "Eco-Friendly", "Zero chemical processing — the most environmentally friendly form of Kota Stone with the smallest carbon footprint."),
        ("tools", "Low Maintenance", "Occasional sweeping and washing is all that's needed to keep natural finish stone looking great for decades."),
    ])
    specs_table(story, [
        ("Surface Finish", "Natural Quarried — Minimal Processing", "—"),
        ("Anti-Slip Rating", "R12 (Outdoor Grade)", "DIN 51130"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Frost Resistance", "Excellent", "—"),
        ("UV Stability", "Excellent — No Colour Fade", "—"),
        ("Maintenance", "Sweep & wash — no sealant needed", "—"),
    ])
    applications_list(story, [
        ("Open Terraces & Rooftops", "The natural anti-slip texture and weather resistance make it the gold standard for exposed rooftop terraces and sun decks."),
        ("Garden Paths & Driveways", "Blends naturally with the landscape and handles vehicle and pedestrian traffic without showing wear."),
        ("Temple & Heritage Complexes", "The honest, unprocessed surface is culturally appropriate for traditional and heritage sacred spaces."),
        ("Courtyards & Verandas", "Creates the quintessential Indian courtyard experience — cool, durable, and beautifully natural."),
        ("Public Infrastructure", "Pavements, public plazas, community spaces, and government buildings across India."),
        ("Industrial Outdoor Areas", "Loading bays, factory yards, and warehousing areas where maximum durability is critical."),
    ])
    cta_bar(story, "Order Natural Finish Stone · Ideal for Large Outdoor Projects")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 7: LEATHER FINISH
# ═══════════════════════════════════════════════════════════════════════════════
def build_leather(story):
    build_cover(story,
        title="Leather Finish Kota Stone",
        subtitle="Brushed Texture — Elegance Meets Safety",
        description="A sophisticated brushed texture that combines premium aesthetics with exceptional grip. The perfect balance of elegance and practicality for wet and outdoor applications.",
        badge_text="Surface Finish",
    )
    section_header(story, "About This Finish", "What is Leather Finish Kota Stone?")
    story.append(Paragraph(
        "Leather Finish Kota Stone undergoes a specialised wire-brushing process that creates a slightly rough, tactile surface "
        "texture that resembles the feel of aged leather. The surface is neither as smooth as honed nor as rough as natural — it "
        "occupies a premium middle ground that combines aesthetic refinement with practical safety. The wire-brushing process opens "
        "the stone's crystalline structure just enough to create a micro-textured surface that provides excellent grip when wet, "
        "while still appearing sophisticated and refined. This makes leather finish especially popular for pool decks, spa surrounds, "
        "outdoor entertaining areas, and luxury bathroom floors.", S["body"]))

    section_header(story, "Why Choose Leather Finish", "Features & Benefits")
    feature_grid(story, [
        ("hand", "Premium Tactile Texture", "The wire-brushed surface has a unique, pleasant texture underfoot and to the touch — elevating any space with a sense of luxury craftsmanship."),
        ("pool", "Pool & Wet Area Safety", "Specifically engineered for wet environments — the micro-texture provides excellent R10/R11 wet slip resistance around pools and water features."),
        ("palette", "Enhanced Natural Depth", "The brushing process reveals deeper colour layers within the stone, creating a richer, more nuanced tonal palette than smoother finishes."),
        ("shield", "Hides Surface Wear", "The textured surface naturally hides minor scratches and wear marks, maintaining a fresh appearance even in high-traffic areas over time."),
        ("sun", "Outdoor & UV Stable", "The leather finish does not degrade or fade under intense UV exposure — perfect for sun-drenched outdoor terraces and pool areas."),
        ("star", "Distinctive Character", "Gives projects a distinctive, one-of-a-kind character that sets them apart from standard polished or natural stone — favoured by architects."),
    ])
    specs_table(story, [
        ("Surface Process", "Wire-Brushed (Leather / Bush-Hammered)", "—"),
        ("Anti-Slip Rating", "R10–R11 (Wet)", "DIN 51130"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("UV Stability", "Excellent", "—"),
        ("Maintenance", "Rinse with water; neutral cleaner", "—"),
        ("Available Variants", "Kota Blue & Kota Brown", "—"),
    ])
    image_row(story, [f"{IMAGES_DIR}/Pool.png", f"{IMAGES_DIR}/Pool2.jpg"],
        "Leather Finish in Pool & Wet Area Applications")
    applications_list(story, [
        ("Pool Surrounds & Decks", "The safest, most aesthetic choice for pool areas — premium look with R10/R11 slip resistance."),
        ("Spa & Wellness Centres", "Creates a premium, tactile atmosphere in wellness environments — durable and hygienic in wet conditions."),
        ("Outdoor Entertaining Areas", "Patios, terraces, and entertainment decks — beautiful, durable, and safer than smooth stone."),
        ("Luxury Bathroom Floors", "Provides the safety of a textured surface with the elegance expected in a high-end bathroom."),
        ("Commercial Exterior Facades", "The textured surface adds dramatic depth and shadow to building exteriors and landscape walls."),
        ("Restaurant Outdoor Seating", "Weather-resistant, attractive, and practical — ideal for cafe and restaurant outdoor areas."),
    ])
    cta_bar(story, "Order Leather Finish Samples · Pool & Outdoor Specialists")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 8: APPLICATION — FLOORING
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_flooring(story):
    build_cover(story,
        title="Kota Stone Flooring",
        subtitle="India's #1 Natural Stone Floor — Built to Last Generations",
        description="Tough enough for industrial facilities, elegant enough for luxury homes. Kota Stone flooring lasts generations with minimal care.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "Why Kota Stone is India's #1 Flooring Choice")
    story.append(Paragraph(
        "For centuries, Kota Stone has been the foundation of Indian construction. From ancient havelis to modern corporate towers, "
        "its unparalleled durability and timeless aesthetic have made it the undisputed number-one natural stone flooring choice "
        "across the country. Kota Stone flooring is three times more durable than ceramic tiles and costs significantly less to "
        "maintain over its lifetime. It stays cool in summer, requires no special sealants, and ages gracefully — developing a "
        "beautiful natural patina that actually improves its appearance over decades.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Outdoor_Flooring.png"], "Kota Stone Flooring — Residential & Commercial Applications")

    section_header(story, "Why Choose Kota Stone Floor", "Key Advantages")
    feature_grid(story, [
        ("shield", "Decades of Durability", "Installed correctly, Kota Stone flooring can last 50+ years without replacement — far outlasting ceramic tiles, vinyl, and even marble in high-traffic settings."),
        ("thermometer", "Natural Cool Surface", "Kota Stone stays naturally cool in summer — reducing thermal discomfort of walking barefoot compared to ceramic tiles or synthetic flooring."),
        ("coins", "Cost-Effective Solution", "Lower material cost than marble and granite, combined with minimal maintenance requirements, make Kota Stone the best long-term value in flooring."),
        ("shoe", "Non-Slip Safety", "The natural surface provides excellent grip — particularly valuable in schools, hospitals, and public spaces where floor safety is a priority."),
        ("broom", "Effortless Maintenance", "Simple sweep and mop is all that is required. No special chemicals, sealers, or treatments needed — just soap and water for a lifetime of beauty."),
        ("expand", "Any Scale Supply", "From 100 sq ft residential rooms to 100,000 sq ft mega-projects — we can supply consistent quality stone at any project scale, delivered pan-India."),
    ])
    specs_table(story, [
        ("Recommended Finish", "Honed, Natural, or Polished", "—"),
        ("Standard Thickness", "20 mm (residential), 25–30 mm (commercial)", "—"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Abrasion Resistance", "High (< 2.0 mm wear)", "IS 1237"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Slip Resistance", "R9 (polished) – R12 (natural)", "DIN 51130"),
        ("Thermal Conductivity", "Low (stays cool)", "—"),
        ("Standard Sizes", "600×600, 400×400, 300×600 mm", "—"),
    ], "Flooring Technical Specifications")
    applications_list(story, [
        ("Residential Homes & Villas", "Living rooms, bedrooms, kitchens, balconies, and courtyards — Kota Stone creates a cohesive, elegant flow throughout the entire home."),
        ("Commercial Buildings", "Office lobbies, corridors, and common areas — durable and professional with minimal maintenance overhead."),
        ("Hospitals & Healthcare", "Hygienic, easy-to-clean, non-porous surface ideal for clinical environments requiring regular disinfection."),
        ("Educational Institutions", "Schools, colleges, and universities — withstands decades of student foot traffic without degradation."),
        ("Heritage & Government Buildings", "Architecturally appropriate, durable, and aligned with Indian heritage aesthetics."),
        ("Retail & Hospitality", "Hotels, restaurants, and retail stores — cost-effective luxury that impresses guests and customers."),
    ])
    cta_bar(story, "Get a Flooring Quote · Free Sample Delivery Pan-India")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 9: APPLICATION — KITCHEN
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_kitchen(story):
    build_cover(story,
        title="Kota Stone Kitchen",
        subtitle="Heat-Resistant · Hygienic · Naturally Beautiful",
        description="Heat-resistant, hygienic, and beautifully natural — Kota Stone kitchen countertops and flooring bring lasting elegance and practicality to the heart of your home.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "Kota Stone for Modern Kitchens")
    story.append(Paragraph(
        "The kitchen is the most demanding surface environment in any home — it faces heat, moisture, food acids, heavy pots, "
        "and constant spillage every single day. Kota Stone's unique physical properties make it an outstanding natural material "
        "choice for kitchen countertops and flooring. Unlike ceramic tiles that chip and crack, or engineered stone that can "
        "delaminate over time, Kota Stone is a single solid natural material quarried from the earth — with no adhesives, resins, "
        "or synthetic binders. Its density makes it resistant to most kitchen impacts, while its natural composition is inherently "
        "food-safe and non-toxic.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Kitchen.png"], "Kota Stone Kitchen Applications")

    section_header(story, "Why Kota Stone in the Kitchen", "Key Advantages")
    feature_grid(story, [
        ("fire", "Heat Resistant to 300°C", "Kota Stone withstands temperatures up to 300°C without cracking, discolouring, or surface damage — hot pots and pans from the stove can be placed directly on the surface."),
        ("shield", "Hygienic & Food-Safe", "The dense, low-porosity surface does not harbour bacteria. When sealed correctly, Kota Stone is inherently hygienic for food preparation areas."),
        ("knife", "Scratch Resistant", "Harder than most ceramic tiles (Mohs 3–4), Kota Stone countertops resist ordinary knife cuts and kitchen utensil scratches that mark softer surfaces."),
        ("tint", "Stain Resistant When Sealed", "A single application of penetrating stone sealer at installation significantly reduces stain risk from oils, curries, and coloured liquids."),
        ("broom", "Effortless Cleaning", "The smooth honed or polished surface can be wiped clean quickly — no grout lines to trap food or bacteria, unlike tile flooring."),
        ("coins", "Outstanding Value", "A Kota Stone kitchen countertop is a fraction of the cost of granite or marble, with comparable or superior performance in the kitchen environment."),
    ])
    specs_table(story, [
        ("Recommended Finish", "Honed or Polished (with sealer)", "—"),
        ("Heat Resistance", "Up to 300°C", "—"),
        ("Water Absorption", "< 0.5% (sealed: < 0.1%)", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Recommended Thickness (Counter)", "25–30 mm", "—"),
        ("Recommended Thickness (Floor)", "20 mm", "—"),
        ("Food Safety", "GRAS — No chemical treatments", "—"),
        ("Sealer Recommendation", "Penetrating stone sealer at install", "—"),
    ], "Kitchen Application Specifications")
    applications_list(story, [
        ("Kitchen Countertops", "Heat and scratch resistant — handle the daily demands of Indian cooking without showing wear."),
        ("Kitchen Flooring", "Anti-slip when honed, hygienic and easy to mop — the practical choice for busy family kitchens."),
        ("Kitchen Backsplash", "10–12 mm thin slabs create a seamless, elegant backsplash that wipes clean instantly."),
        ("Island Tops", "Large format slabs for kitchen islands — dramatic, natural, and unique in every installation."),
        ("Utility Rooms", "Extends naturally from the kitchen into laundry and utility rooms for a cohesive finish."),
        ("Outdoor Kitchens", "The natural finish variant handles outdoor cooking environments with complete weather resistance."),
    ])
    cta_bar(story, "Kitchen Countertop Samples Available · Installation Guidance Provided")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 10: APPLICATION — POOL SURROUNDS
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_pool(story):
    build_cover(story,
        title="Kota Stone Pool Surrounds",
        subtitle="Safe · Cool Underfoot · Strikingly Beautiful",
        description="The safest, most beautiful pool decking material in India. Anti-slip by nature, cool underfoot, and visually stunning around any swimming pool or water feature.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "The Perfect Pool Decking Material")
    story.append(Paragraph(
        "Pool surrounds have very demanding requirements — the surface must be permanently wet-slip resistant, cool enough to "
        "walk on barefoot in summer heat, resistant to pool chemicals, and beautiful enough to complement the aesthetic of a "
        "luxury pool. Natural and leather finish Kota Stone provides all of these properties in a single material. "
        "Unlike ceramic pool tiles that become dangerously slippery when wet, or concrete that becomes unbearably hot, "
        "Kota Stone is the natural choice that architects and pool designers across India have trusted for decades.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Pool.png", f"{IMAGES_DIR}/Pool2.jpg"],
        "Kota Stone Pool Surrounds — Natural & Leather Finish")

    feature_grid(story, [
        ("pool", "R11 Wet Slip Resistance", "Leather and natural finish Kota Stone provide R11 rated wet slip resistance — the highest safety standard for pool and wet area applications."),
        ("thermometer", "Stays Cool in Summer Heat", "Unlike dark stone, ceramic, or concrete, Kota Stone's light-toned surface does not absorb heat — safe for bare feet in 45°C summer temperatures."),
        ("tint", "Chemical Resistant", "Resistant to chlorine, salt water, pH balancing chemicals, and pool cleaning agents — no surface degradation or discolouration over years of use."),
        ("shield", "Frost & Monsoon Resistant", "With less than 0.5% water absorption, Kota Stone does not crack or spall even through freeze-thaw cycles or extreme monsoon conditions."),
        ("palette", "Visually Stunning", "The natural blue-green tones of Kota Stone complement the water of a pool perfectly — creating a resort-like aesthetic at any property."),
        ("tools", "Low Maintenance", "Rinse with water after pool use. No special cleaning agents needed — the stone does not stain, fade, or degrade with regular pool water exposure."),
    ])
    specs_table(story, [
        ("Recommended Finish", "Leather or Natural (R10–R12)", "—"),
        ("Wet Slip Resistance", "R10–R11", "DIN 51130"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Chemical Resistance", "High (chlorine, salt, pH chemicals)", "—"),
        ("UV Colour Stability", "Excellent — No fading", "—"),
        ("Thermal Performance", "Low heat absorption — cool underfoot", "—"),
        ("Standard Thickness", "20–25 mm", "—"),
        ("Recommended Size", "600×600 mm or 400×400 mm", "—"),
    ], "Pool Application Specifications")
    applications_list(story, [
        ("Swimming Pool Surrounds", "The primary application — safe, beautiful, and durable around all pool types."),
        ("Pool Coping", "Edge coping in 40 mm thickness for structural and aesthetic pool edge finishing."),
        ("Outdoor Spa & Jacuzzi", "Handles the heat, humidity, and chemical exposure of spa environments."),
        ("Water Features & Fountains", "Natural and leather finish complement the aesthetic of garden water features beautifully."),
        ("Wet Room Bathrooms", "Interior wet rooms and shower areas where both safety and elegance are required."),
        ("Beach & Lakeside Properties", "Handles saline and natural water environments with complete durability."),
    ])
    cta_bar(story, "Pool Surround Samples Available · Installation Guidance for Pool Projects")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 11: APPLICATION — WALL CLADDING
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_wall(story):
    build_cover(story,
        title="Kota Stone Wall Cladding",
        subtitle="Architectural Depth & Natural Texture for Walls",
        description="Add architectural depth, natural texture, and timeless beauty to interior feature walls and exterior building facades with 10–12 mm thin stone panels.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "Kota Stone Wall Cladding")
    story.append(Paragraph(
        "Kota Stone wall cladding transforms ordinary walls into architectural statements. Cut into 10–12 mm thin panels, "
        "Kota Stone creates a surface that is dramatically lighter than traditional masonry while retaining the full visual "
        "impact of natural stone. The natural blue-green and brown tones of Kota Stone bring a sophisticated, grounded energy "
        "to feature walls, building exteriors, and landscape structures. From luxury hotel lobbies to exterior commercial "
        "facades, Kota Stone wall cladding delivers unmatched natural beauty with decades of durability.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Wall_Cladding.png"], "Kota Stone Wall Cladding Applications")

    feature_grid(story, [
        ("building", "Architectural Impact", "10–12 mm thin stone panels create dramatic feature walls with the full aesthetic weight of natural stone at a fraction of the structural load."),
        ("shield", "Weather Resistant", "Suitable for both interior and exterior applications — UV stable, frost resistant, and unaffected by the full range of Indian climate conditions."),
        ("coins", "Cost-Effective Facade", "Delivers the premium look of full-depth stonework at a significantly lower material and installation cost — ideal for large commercial facades."),
        ("tools", "Simple Installation", "Thin panels can be fixed directly to existing walls with tile adhesive or mechanical fixings — no specialist masonry skills required."),
        ("palette", "Versatile Aesthetics", "Available in all finishes — polished for interior luxury, natural for exterior authenticity, leather for textured outdoor walls."),
        ("leaf", "Sustainable Choice", "Natural stone cladding has far lower embodied carbon than manufactured cladding materials and lasts indefinitely without replacement."),
    ])
    specs_table(story, [
        ("Recommended Thickness", "10–12 mm (cladding panels)", "—"),
        ("Standard Panel Sizes", "300×600 mm, 600×600 mm, Custom", "—"),
        ("Weight per sqm", "26–32 kg/m²", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("UV Stability", "Excellent — No colour fade", "—"),
        ("Frost Resistance", "Excellent", "—"),
        ("Installation", "Tile adhesive or mechanical fixing", "—"),
    ], "Wall Cladding Specifications")
    applications_list(story, [
        ("Interior Feature Walls", "Living room accent walls, bedroom headboards, and dining room feature walls — dramatic natural stone at low structural weight."),
        ("Hotel Lobbies & Corridors", "Large-format cladding panels create a sophisticated, premium first impression in hospitality spaces."),
        ("Building Exterior Facades", "Full-facade or partial cladding for commercial buildings, residential apartments, and institutional structures."),
        ("Garden & Landscape Walls", "Boundary walls, garden feature walls, and retaining wall facings — all-weather natural stone cladding."),
        ("Retail & Showroom Interiors", "Background walls in premium retail, showroom, and gallery environments."),
        ("Religious & Cultural Buildings", "Culturally appropriate natural stone cladding for temples, community halls, and public buildings."),
    ])
    cta_bar(story, "Wall Cladding Samples Available · Facade & Interior Specialists")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 12: APPLICATION — OUTDOOR PATHWAYS
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_outdoor(story):
    build_cover(story,
        title="Kota Stone Outdoor Pathways",
        subtitle="Zero Maintenance · All-Weather · Naturally Non-Slip",
        description="Naturally non-slip, weather resistant, and beautiful in any outdoor setting. Kota Stone pathways and driveways last for generations with virtually zero maintenance.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "Kota Stone for Outdoor Pathways")
    story.append(Paragraph(
        "Outdoor pathways face one of the toughest demands in construction — they must withstand monsoon rains, scorching summer "
        "heat, vehicle loads, constant foot traffic, and decades of weather exposure without replacement. Kota Stone's natural "
        "non-slip surface, exceptional compressive strength, and near-zero water absorption make it the ideal material for "
        "any outdoor pathway application. The natural, slightly rough surface provides an R12-rated anti-slip grip even in "
        "wet conditions — significantly safer than smooth stone, ceramic, or concrete alternatives.", S["body"]))
    image_row(story, [f"{IMAGES_DIR}/Pathway.png", f"{IMAGES_DIR}/Outdoor_Flooring.png"],
        "Kota Stone Outdoor Pathways & Driveways")

    feature_grid(story, [
        ("sun", "Extreme Weather Resistant", "Handles 45°C summer heat, heavy monsoon flooding, and freezing winters without cracking, spalling, or colour change."),
        ("shoe", "R12 Anti-Slip Safety", "The highest anti-slip rating — provides secure grip in all weather conditions, reducing slip-and-fall risk in outdoor areas."),
        ("car", "Load Bearing", "25–30 mm thickness handles pedestrian and vehicle loads — suitable for driveways, car parks, and service roads."),
        ("leaf", "Naturally Weed Resistant", "Tightly laid Kota Stone paving with sand jointing minimises weed penetration compared to irregular stone alternatives."),
        ("paint", "Ages Beautifully", "Develops a natural weathered patina over decades that enhances its organic character — unlike synthetic materials that degrade."),
        ("coins", "Most Cost-Effective", "Natural finish requires no polishing, sealants, or special treatment — the most economical outdoor paving solution available."),
    ])
    specs_table(story, [
        ("Recommended Finish", "Natural (Outdoor) or Leather", "—"),
        ("Slip Resistance", "R12 (Natural Finish Outdoor)", "DIN 51130"),
        ("Recommended Thickness", "25 mm (pedestrian) — 30 mm (vehicle)", "—"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Frost Resistance", "Excellent", "—"),
        ("UV Stability", "No colour fade over decades", "—"),
        ("Jointing", "Sand, mortar, or polymeric", "—"),
    ], "Outdoor Pathway Specifications")
    applications_list(story, [
        ("Garden Pathways", "Winding garden paths that blend naturally with planting and landscaping."),
        ("Driveways", "25–30 mm thickness handles vehicle loads with zero maintenance over decades."),
        ("Public Plazas & Pavements", "Large-area public paving for parks, commercial precincts, and civic spaces."),
        ("Courtyards & Terraces", "The quintessential Indian courtyard surface — cool, durable, and beautiful."),
        ("Temple & Heritage Complexes", "Culturally appropriate outdoor paving for sacred and heritage spaces."),
        ("Industrial Outdoor Areas", "Factory yards, warehousing, and logistics areas with heavy vehicle traffic."),
    ])
    cta_bar(story, "Outdoor Pathway Samples · Large Area Project Pricing Available")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 13: APPLICATION — STAIRCASES
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_stairs(story):
    build_cover(story,
        title="Kota Stone Staircases",
        subtitle="Structural Strength · Natural Safety · Enduring Beauty",
        description="Structurally strong, naturally safe, and strikingly beautiful — Kota Stone stair treads and risers are built for a lifetime of confident use in any building type.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "Kota Stone Staircases — Built to Last Generations")
    story.append(Paragraph(
        "Staircases are one of the highest-stress elements in any building — they endure concentrated point loads, constant "
        "abrasion, and the safety-critical requirement of providing secure grip underfoot at every step. Kota Stone stair treads "
        "are supplied in 40+ mm thickness to provide the structural depth required for cantilevered, straight-flight, and spiral "
        "staircase designs. The natural and honed surfaces provide the grip needed to meet building safety codes, while the stone's "
        "natural beauty makes every staircase a architectural feature in its own right.", S["body"]))

    feature_grid(story, [
        ("stairs", "40+ mm Structural Treads", "Extra-thick tread slabs provide the structural rigidity required for cantilever, floating, and high-load staircase designs."),
        ("shoe", "Natural Grip Safety", "Natural and honed finishes provide anti-slip ratings that meet and exceed Indian and international staircase safety standards."),
        ("shield", "Impact Resistant", "Kota Stone withstands the concentrated impact of foot traffic, dropped objects, and furniture movement on staircases without chipping or cracking."),
        ("tools", "Custom Nosing & Profiles", "Stair treads can be supplied with bullnose, bevelled, or square nosing profiles, and with anti-slip groove inserts for extra safety."),
        ("paint", "Architectural Statement", "Every Kota Stone staircase becomes a feature of the building's interior — natural stone that cannot be replicated by synthetic alternatives."),
        ("building", "All Building Types", "Suitable for residential, commercial, institutional, industrial, and heritage staircase applications at any scale."),
    ])
    specs_table(story, [
        ("Tread Thickness", "40 mm (standard) — 50 mm (heavy duty)", "—"),
        ("Riser Thickness", "20 mm (typical)", "—"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Flexural Strength (tread)", "≥ 10 MPa", "IS 1723"),
        ("Slip Resistance", "R10 (honed) — R12 (natural)", "DIN 51130"),
        ("Standard Tread Width", "300 mm (standard riser depth)", "—"),
        ("Custom Lengths", "Up to 2400 mm in single piece", "—"),
        ("Nosing Options", "Bullnose, Square, Bevelled, Anti-Slip Groove", "—"),
    ], "Staircase Specifications")
    applications_list(story, [
        ("Residential Staircases", "The centrepiece of any home — grand, elegant, and built to last the life of the building."),
        ("Commercial Buildings", "Offices, hotels, malls, and institutions — durable treads that survive decades of heavy foot traffic."),
        ("Educational Institutions", "Schools and colleges — anti-slip, durable, and low-maintenance for high-traffic student use."),
        ("Heritage Buildings", "Replacement and restoration of heritage staircase treads in culturally significant buildings."),
        ("Industrial Facilities", "Heavy-duty 50 mm treads for factories, warehouses, and processing plants with maximum load requirements."),
        ("Exterior Staircases", "Natural finish treads for outdoor steps, entrance staircases, and garden terracing."),
    ])
    cta_bar(story, "Staircase Tread Samples Available · Custom Sizes on Request")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 14: APPLICATION — INDUSTRIAL
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_industrial(story):
    build_cover(story,
        title="Kota Stone Industrial Flooring",
        subtitle="Superhuman Durability for Industrial Environments",
        description="India's most reliable industrial flooring material. Used in factories, warehouses, cold stores, and processing plants across the country for its superhuman durability.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "Kota Stone for Industrial Environments")
    story.append(Paragraph(
        "Industrial flooring is subjected to conditions that defeat most materials — extreme mechanical loads, chemical spills, "
        "forklift traffic, thermal cycling, and constant abrasion. Unlike epoxy coatings that chip and delaminate, or concrete "
        "floors that crack and dust, Kota Stone industrial flooring maintains its structural integrity and surface quality "
        "indefinitely. At 30 mm thickness, Kota Stone can bear loads far exceeding typical industrial requirements, while its "
        "natural chemical resistance handles most industrial substances without surface damage.", S["body"]))

    feature_grid(story, [
        ("industry", "Heavy Load Rating", "30 mm Kota Stone handles point loads from forklift trucks, heavy machinery, and storage racking systems without cracking or surface failure."),
        ("flask", "Chemical Resistance", "Naturally resistant to oils, mild acids, alkalis, and most industrial chemicals — no coatings required that can peel or fail."),
        ("shield", "Abrasion Resistant", "Withstands forklift wheel traffic, pallet dragging, and constant foot traffic without surface wear — tested to IS 1237 standards."),
        ("thermometer", "Thermal Stable", "Handles extreme temperature variation in cold stores, foundries, and processing environments without thermal cracking."),
        ("broom", "Dust-Free Surface", "Unlike bare concrete that generates harmful silica dust, Kota Stone's sealed surface remains dust-free — improving air quality in industrial spaces."),
        ("coins", "Lowest Lifetime Cost", "Install once, maintain with a broom — Kota Stone industrial flooring has virtually zero ongoing cost compared to coatings that require annual reapplication."),
    ])
    specs_table(story, [
        ("Recommended Thickness", "30 mm (standard) — 40 mm (heavy duty)", "—"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Abrasion Resistance", "< 1.5 mm wear", "IS 1237"),
        ("Chemical Resistance", "Oils, mild acids, alkalis", "—"),
        ("Point Load Capacity", "Up to 20 tonnes/m² (30 mm)", "—"),
        ("Anti-Dust Surface", "Natural sealed stone — no dust generation", "—"),
        ("Recommended Finish", "Natural (anti-slip industrial grade)", "—"),
        ("Standard Sizes", "600×600 mm, 400×400 mm, Custom", "—"),
    ], "Industrial Flooring Specifications")
    applications_list(story, [
        ("Manufacturing Factories", "Main production floor areas requiring maximum load bearing and chemical resistance."),
        ("Warehouses & Logistics", "Heavy forklift traffic and pallet storage areas — no surface damage over decades."),
        ("Cold Storage Facilities", "Frost-resistant stone handles freeze-thaw cycling in cold stores and refrigerated warehouses."),
        ("Food Processing Plants", "Hygienic, sealed surface meets food safety requirements — easy to clean and sanitise."),
        ("Automotive Workshops", "Oil and chemical resistant — handles vehicle workshop environments without surface staining."),
        ("Pharmaceutical Facilities", "Dust-free, cleanroom-compatible surface for pharmaceutical manufacturing environments."),
    ])
    cta_bar(story, "Industrial Flooring Samples · Bulk Project Pricing · Site Visits Available")

# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 15: APPLICATION — PARKING
# ═══════════════════════════════════════════════════════════════════════════════
def build_app_parking(story):
    build_cover(story,
        title="Kota Stone Parking Tiles",
        subtitle="Heavy-Load Rated · Anti-Skid · Virtually Indestructible",
        description="India's most trusted natural stone for parking lots, driveways, and vehicle areas. Heavy-load rated, anti-skid, and virtually indestructible — even under constant vehicle traffic.",
        badge_text="Application Guide",
    )
    section_header(story, "Application", "The #1 Choice for Indian Parking Lots")
    story.append(Paragraph(
        "Parking areas face some of the most demanding conditions of any flooring use case — constant vehicle loads, oil and "
        "fuel spills, tyre abrasion, and exposure to all weather conditions. Unlike concrete pavers that crack under load or "
        "ceramic tiles that become dangerously slippery when wet, Kota Stone parking tiles offer a complete solution: exceptional "
        "structural strength to handle vehicle loads, natural anti-skid surface for vehicle and pedestrian safety, and chemical "
        "resistance to oil, fuel, and cleaning agents.", S["body"]))

    feature_grid(story, [
        ("car", "Vehicle Load Rated", "30 mm Kota Stone tiles handle passenger car, SUV, and light commercial vehicle loads without cracking or surface damage."),
        ("shoe", "Anti-Skid Surface", "Natural and leather finish Kota Stone provides the anti-skid grip required for safe vehicle manoeuvring and pedestrian zones in parking areas."),
        ("tint", "Oil & Fuel Resistant", "Naturally resistant to petrol, diesel, and engine oil spills that permanently stain and damage concrete and ceramic alternatives."),
        ("cloud", "All-Weather Durable", "No cracking in summer heat, no slipping in monsoon rains, no spalling in cool northern winters — all-climate performance guaranteed."),
        ("shield", "Frost Resistant", "Low water absorption prevents freeze-thaw damage — critical for parking areas in colder regions of India."),
        ("tools", "Easy Replacement", "Individual tiles can be replaced without disturbing the surrounding area — unlike monolithic concrete which requires full-section replacement."),
    ])
    specs_table(story, [
        ("Recommended Thickness", "30 mm (passenger vehicles)", "—"),
        ("Compressive Strength", "≥ 70 MPa", "IS 1121"),
        ("Abrasion Resistance", "High — IS 1237 compliant", "IS 1237"),
        ("Slip Resistance", "R11 (Natural/Leather Finish)", "DIN 51130"),
        ("Chemical Resistance", "Oil, fuel, cleaning agents", "—"),
        ("Water Absorption", "< 0.5%", "IS 1124"),
        ("Frost Resistance", "Excellent", "—"),
        ("Standard Sizes", "600×600 mm, 400×400 mm", "—"),
    ], "Parking Tile Specifications")
    applications_list(story, [
        ("Residential Parking Areas", "Home driveways and basement parking — durable, attractive, and oil-resistant for family vehicles."),
        ("Commercial Parking Lots", "Surface and multi-storey car parks for commercial buildings, malls, and offices."),
        ("Hotel & Resort Parking", "Premium parking areas where aesthetic quality matters alongside functional performance."),
        ("Hospital & Institutional", "High-turnover parking areas for hospitals, government buildings, and educational institutions."),
        ("Industrial Vehicle Areas", "Loading bays, truck turning areas, and forklift traffic zones in industrial facilities."),
        ("Petrol Stations", "The chemical resistance of Kota Stone makes it ideal for fuel station forecourts."),
    ])
    cta_bar(story, "Parking Tile Samples · Bulk Pricing for Large Projects · Pan-India Supply")

# ═══════════════════════════════════════════════════════════════════════════════
#  GENERATE ALL PDFs
# ═══════════════════════════════════════════════════════════════════════════════
pdfs = [
    ("catalogue.pdf",                 "Complete Product Catalogue",      build_main_catalogue),
    ("kota-blue-catalogue.pdf",       "Kota Blue Stone",                 build_kota_blue),
    ("kota-brown-catalogue.pdf",      "Kota Brown Stone",                build_kota_brown),
    ("polished-finish-catalogue.pdf", "Polished Kota Stone",             build_polished),
    ("honed-finish-catalogue.pdf",    "Honed Kota Stone",                build_honed),
    ("natural-finish-catalogue.pdf",  "Natural Finish Kota Stone",       build_natural),
    ("leather-finish-catalogue.pdf",  "Leather Finish Kota Stone",       build_leather),
    ("flooring-catalogue.pdf",        "Kota Stone Flooring",             build_app_flooring),
    ("kitchen-catalogue.pdf",         "Kitchen Applications",            build_app_kitchen),
    ("pool-catalogue.pdf",            "Pool Surrounds",                  build_app_pool),
    ("wall-cladding-catalogue.pdf",   "Wall Cladding",                   build_app_wall),
    ("outdoor-catalogue.pdf",         "Outdoor Pathways",                build_app_outdoor),
    ("stairs-catalogue.pdf",          "Staircases",                      build_app_stairs),
    ("industrial-catalogue.pdf",      "Industrial Flooring",             build_app_industrial),
    ("parking-catalogue.pdf",         "Parking Tiles",                   build_app_parking),
]

print(f"Generating {len(pdfs)} PDFs...\n")
generated = []
for fname, title, builder in pdfs:
    try:
        path = build_pdf(fname, title, builder)
        generated.append(path)
    except Exception as e:
        print(f"  ✗ {fname}: {e}")

print(f"\nDone. {len(generated)}/{len(pdfs)} PDFs generated.")