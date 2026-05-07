"""
KotaStone India — Professional PDF Generator v2
Fully redesigned: proper cover pages, section layouts, image handling,
typography hierarchy, and visual consistency throughout.
"""

import io, os
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image, KeepTogether, Frame, BaseDocTemplate, PageTemplate
)
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas as pdfcanvas

# ══════════════════════════════════════════════════════════════
# BRAND TOKENS
# ══════════════════════════════════════════════════════════════
C_DARK    = HexColor("#1C2B3A")   # deep navy
C_BLUE    = HexColor("#1B4F72")   # brand blue
C_BLUE2   = HexColor("#2980B9")   # mid blue
C_GOLD    = HexColor("#C9A84C")   # gold accent
C_GOLD2   = HexColor("#F0C040")   # lighter gold
C_LIGHT   = HexColor("#F8F6F0")   # warm off-white
C_RULE    = HexColor("#D4AF7A")   # warm rule
C_GREY    = HexColor("#5D6D7E")   # body grey
C_LGREY   = HexColor("#E8E8E3")   # light grey divider
C_ROW1    = HexColor("#FFFFFF")
C_ROW2    = HexColor("#F4F2EC")
C_HERO_BG = HexColor("#1C2B3A")
WHITE     = colors.white
BLACK     = colors.black

PW  = A4[0]   # 595.27
PH  = A4[1]   # 841.89
LM  = 22*mm
RM  = 22*mm
TM  = 22*mm
BM  = 22*mm
CW  = PW - LM - RM   # content width ≈ 551 pt

PIMG = os.path.join(os.path.dirname(__file__), "processed_images")
OUT  = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT, exist_ok=True)

# ══════════════════════════════════════════════════════════════
# IMAGE HELPER
# ══════════════════════════════════════════════════════════════
def load_img(name, w_mm, h_mm=None, fit=True):
    """Load a pre-processed image. Returns Image flowable or None."""
    path = os.path.join(PIMG, name)
    if not os.path.exists(path):
        return None
    try:
        w_pt = w_mm * mm
        h_pt = h_mm * mm if h_mm else None
        if fit and h_pt:
            # Keep aspect ratio within box
            pil = PILImage.open(path)
            aw, ah = pil.size
            scale = min(w_pt/aw, h_pt/ah)
            return Image(path, width=aw*scale, height=ah*scale)
        return Image(path, width=w_pt, height=h_pt)
    except Exception:
        return None

def img_fill(name, w_mm, h_mm):
    """Crop-fill an image into exact w×h box (cover behaviour)."""
    path = os.path.join(PIMG, name)
    if not os.path.exists(path):
        return None
    try:
        pil = PILImage.open(path).convert("RGB")
        aw, ah = pil.size
        tw, th = int(w_mm*mm*3), int(h_mm*mm*3)   # 3× for quality
        scale = max(tw/aw, th/ah)
        nw, nh = int(aw*scale), int(ah*scale)
        pil = pil.resize((nw, nh), PILImage.LANCZOS)
        left = (nw - tw)//2; top = (nh - th)//2
        pil = pil.crop((left, top, left+tw, top+th))
        buf = io.BytesIO(); pil.save(buf, "JPEG", quality=88); buf.seek(0)
        return Image(buf, width=w_mm*mm, height=h_mm*mm)
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════
# TYPOGRAPHY
# ══════════════════════════════════════════════════════════════
_base = getSampleStyleSheet()

def _ps(name, **kw):
    return ParagraphStyle(name, **kw)

# Cover styles
PS_COVER_BRAND   = _ps("PS_COVER_BRAND",  fontName="Helvetica-Bold", fontSize=11,
                        textColor=C_GOLD, alignment=TA_LEFT, leading=14)
PS_COVER_TITLE   = _ps("PS_COVER_TITLE",  fontName="Helvetica-Bold", fontSize=30,
                        textColor=C_DARK, alignment=TA_LEFT, leading=36, spaceAfter=0)
PS_COVER_SUB     = _ps("PS_COVER_SUB",    fontName="Helvetica", fontSize=13,
                        textColor=C_BLUE, alignment=TA_LEFT, leading=18, spaceAfter=4)
PS_COVER_TAG     = _ps("PS_COVER_TAG",    fontName="Helvetica-Oblique", fontSize=9.5,
                        textColor=C_GREY, alignment=TA_LEFT, leading=14)

# Section styles
PS_SEC_LABEL     = _ps("PS_SEC_LABEL",    fontName="Helvetica-Bold", fontSize=7.5,
                        textColor=C_GOLD, leading=10, spaceBefore=0, spaceAfter=3,
                        letterSpacing=1.8)
PS_SEC_HEAD      = _ps("PS_SEC_HEAD",     fontName="Helvetica-Bold", fontSize=18,
                        textColor=C_DARK, leading=22, spaceBefore=0, spaceAfter=2)
PS_SUB_HEAD      = _ps("PS_SUB_HEAD",     fontName="Helvetica-Bold", fontSize=11,
                        textColor=C_BLUE, leading=15, spaceBefore=6, spaceAfter=3)
PS_BODY          = _ps("PS_BODY",         fontName="Helvetica", fontSize=9.5,
                        textColor=C_DARK, leading=15.5, spaceAfter=6,
                        alignment=TA_JUSTIFY)
PS_BODY_S        = _ps("PS_BODY_S",       fontName="Helvetica", fontSize=8.5,
                        textColor=C_GREY, leading=13, spaceAfter=4)
PS_FEAT_TITLE    = _ps("PS_FEAT_TITLE",   fontName="Helvetica-Bold", fontSize=9.5,
                        textColor=C_DARK, leading=13, spaceAfter=2)
PS_FEAT_BODY     = _ps("PS_FEAT_BODY",    fontName="Helvetica", fontSize=8.5,
                        textColor=C_GREY, leading=13, spaceAfter=0)
PS_TBL_HDR       = _ps("PS_TBL_HDR",     fontName="Helvetica-Bold", fontSize=8.5,
                        textColor=WHITE, alignment=TA_CENTER, leading=11)
PS_TBL_CELL      = _ps("PS_TBL_CELL",    fontName="Helvetica", fontSize=8.5,
                        textColor=C_DARK, leading=12)
PS_TBL_CELL_C    = _ps("PS_TBL_CELL_C",  fontName="Helvetica", fontSize=8.5,
                        textColor=C_DARK, alignment=TA_CENTER, leading=12)
PS_SKU_CODE      = _ps("PS_SKU_CODE",     fontName="Helvetica-Bold", fontSize=8,
                        textColor=C_GOLD, leading=11, spaceAfter=1)
PS_SKU_NAME      = _ps("PS_SKU_NAME",     fontName="Helvetica-Bold", fontSize=10,
                        textColor=C_DARK, leading=13, spaceAfter=2)
PS_SKU_DESC      = _ps("PS_SKU_DESC",     fontName="Helvetica", fontSize=8.5,
                        textColor=C_GREY, leading=12.5, spaceAfter=3)
PS_SKU_TAG       = _ps("PS_SKU_TAG",      fontName="Helvetica-Oblique", fontSize=8,
                        textColor=C_BLUE2, leading=11)
PS_CALLOUT       = _ps("PS_CALLOUT",      fontName="Helvetica-Bold", fontSize=22,
                        textColor=C_GOLD, alignment=TA_CENTER, leading=26)
PS_CALLOUT_LBL   = _ps("PS_CALLOUT_LBL", fontName="Helvetica", fontSize=8,
                        textColor=C_GREY, alignment=TA_CENTER, leading=11)
PS_FOOTER        = _ps("PS_FOOTER",       fontName="Helvetica", fontSize=7,
                        textColor=C_GREY, alignment=TA_CENTER, leading=10)
PS_CONTACT_VAL   = _ps("PS_CONTACT_VAL", fontName="Helvetica-Bold", fontSize=8.5,
                        textColor=WHITE, alignment=TA_CENTER, leading=12)
PS_CONTACT_LBL   = _ps("PS_CONTACT_LBL", fontName="Helvetica", fontSize=7,
                        textColor=HexColor("#A0B4C8"), alignment=TA_CENTER, leading=10)
PS_BULLET        = _ps("PS_BULLET",       fontName="Helvetica", fontSize=9,
                        textColor=C_DARK, leading=14, leftIndent=8)
PS_NOTE          = _ps("PS_NOTE",         fontName="Helvetica-Oblique", fontSize=7.5,
                        textColor=C_GREY, leading=11)

# ══════════════════════════════════════════════════════════════
# SHORTHAND FLOWABLE BUILDERS
# ══════════════════════════════════════════════════════════════
def sp(h=6):   return Spacer(1, h)
def slabel(t): return Paragraph(t.upper(), PS_SEC_LABEL)
def shead(t):  return Paragraph(t, PS_SEC_HEAD)
def subhd(t):  return Paragraph(t, PS_SUB_HEAD)
def body(t):   return Paragraph(t, PS_BODY)
def bodys(t):  return Paragraph(t, PS_BODY_S)
def note(t):   return Paragraph(t, PS_NOTE)
def bullet(t): return Paragraph(f"\u25b8\u2002{t}", PS_BULLET)

def gold_rule(space_before=4, space_after=8):
    return HRFlowable(width="100%", thickness=1.5, color=C_GOLD,
                      spaceAfter=space_after, spaceBefore=space_before)

def thin_rule(space_before=4, space_after=6):
    return HRFlowable(width="100%", thickness=0.5, color=C_LGREY,
                      spaceAfter=space_after, spaceBefore=space_before)

def section_header(label, title, rule=True):
    items = [sp(4), slabel(label), shead(title)]
    if rule:
        items.append(gold_rule())
    return items

# ══════════════════════════════════════════════════════════════
# TABLE BUILDERS
# ══════════════════════════════════════════════════════════════
def spec_table(rows, col_widths=None, col_aligns=None):
    """Clean specification table with navy header."""
    n_cols = len(rows[0])
    col_widths = col_widths or [CW / n_cols] * n_cols
    col_aligns = col_aligns or (["LEFT"] + ["CENTER"] * (n_cols - 1))

    # Wrap header cells
    tbl_data = [[Paragraph(str(c), PS_TBL_HDR) for c in rows[0]]]
    for row in rows[1:]:
        tbl_row = []
        for i, cell in enumerate(row):
            sty = PS_TBL_CELL_C if col_aligns[i] == "CENTER" else PS_TBL_CELL
            tbl_row.append(Paragraph(str(cell), sty))
        tbl_data.append(tbl_row)

    t = Table(tbl_data, colWidths=col_widths, repeatRows=1)
    row_bg = []
    for i in range(1, len(tbl_data)):
        bg = C_ROW1 if i % 2 == 1 else C_ROW2
        row_bg.append(("BACKGROUND", (0, i), (-1, i), bg))

    t.setStyle(TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0), C_BLUE),
        ("TOPPADDING",    (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        # Body
        ("TOPPADDING",    (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_LGREY),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.0, C_GOLD),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_ROW1, C_ROW2]),
    ] + row_bg))
    return t


def feat_grid(features, cols=2):
    """2-column feature card grid."""
    rows = []
    for i in range(0, len(features), cols):
        grp = features[i:i+cols]
        cells = []
        for icon, title, desc in grp:
            cell = [
                Paragraph(f"{icon}  {title}", PS_FEAT_TITLE),
                Paragraph(desc, PS_FEAT_BODY),
            ]
            cells.append(cell)
        while len(cells) < cols:
            cells.append("")
        rows.append(cells)

    col_w = (CW - (cols - 1) * 4*mm) / cols
    t = Table(rows, colWidths=[col_w] * cols, spaceBefore=0)
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [C_ROW1, C_ROW2]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_LGREY),
        ("LINEBEFORE",    (1, 0), (1, -1),  0.4, C_LGREY),
    ]))
    return t


def sku_grid(skus):
    """3-column SKU product grid."""
    rows = []
    for i in range(0, len(skus), 3):
        grp = skus[i:i+3]
        cells = []
        for code, name, desc, finish in grp:
            cell = [
                Paragraph(code, PS_SKU_CODE),
                Paragraph(name, PS_SKU_NAME),
                Paragraph(desc, PS_SKU_DESC),
                Paragraph(f"● {finish}", PS_SKU_TAG),
            ]
            cells.append(cell)
        while len(cells) < 3:
            cells.append(Paragraph("", PS_BODY))
        rows.append(cells)

    col_w = CW / 3
    t = Table(rows, colWidths=[col_w] * 3)
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [C_ROW2, C_ROW1]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.4, C_LGREY),
        ("LINEAFTER",     (0, 0), (1, -1),  0.4, C_LGREY),
        ("LINEBEFORE",    (0, 0), (0, -1),  2.0, C_GOLD),
    ]))
    return t


def stat_bar(stats):
    """A row of stat callout boxes: [(value, label), ...]"""
    n = len(stats)
    cells = [[
        [Paragraph(v, PS_CALLOUT), Paragraph(l, PS_CALLOUT_LBL)]
        for v, l in stats
    ]]
    t = Table(cells, colWidths=[CW / n] * n)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_DARK),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LINEAFTER",     (0, 0), (-2, -1),  0.5, C_GREY),
    ]))
    return t


def contact_strip():
    """Footer contact bar."""
    items = [
        ("+91 86194 59354", "Phone"),
        ("info@kotastonefactory.in", "Email"),
        ("www.kotastonefactory.com", "Website"),
        ("Ramganj Mandi, Kota, RJ 326519", "Location"),
    ]
    cells = [[
        [Paragraph(v, PS_CONTACT_VAL), Paragraph(l, PS_CONTACT_LBL)]
        for v, l in items
    ]]
    t = Table(cells, colWidths=[CW / 4] * 4)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_DARK),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LINEAFTER",     (0, 0), (-2, -1),  0.4, C_GREY),
    ]))
    return t


def badge_strip(badges):
    """Certification / badge row."""
    cells = [[Paragraph(b, _ps(f"b{i}", fontName="Helvetica-Bold", fontSize=8,
                                textColor=C_DARK, alignment=TA_CENTER, leading=12))
              for i, b in enumerate(badges)]]
    t = Table(cells, colWidths=[CW / len(badges)] * len(badges))
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_LGREY),
    ]))
    return t


def two_col_list(left_title, left_items, right_title, right_items):
    """Two-column bulleted list block."""
    def col(title, items):
        content = [Paragraph(title, PS_SUB_HEAD)]
        for it in items:
            content.append(Paragraph(f"\u25b8\u2002{it}", PS_BULLET))
        return content

    rows = [[col(left_title, left_items), col(right_title, right_items)]]
    cw = (CW - 4*mm) / 2
    t = Table(rows, colWidths=[cw, cw])
    t.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("BACKGROUND",   (0, 0), (0, -1), C_ROW2),
        ("BACKGROUND",   (1, 0), (1, -1), C_ROW1),
        ("LINEAFTER",    (0, 0), (0, -1), 0.5, C_LGREY),
        ("BOX",          (0, 0), (-1, -1), 0.4, C_LGREY),
    ]))
    return t


# ══════════════════════════════════════════════════════════════
# PAGE TEMPLATE WITH HEADER/FOOTER
# ══════════════════════════════════════════════════════════════
class KotaDoc(SimpleDocTemplate):
    def __init__(self, path, doc_title="KotaStone India", accent=C_BLUE):
        self.doc_title = doc_title
        self.accent = accent
        super().__init__(
            path, pagesize=A4,
            leftMargin=LM, rightMargin=RM,
            topMargin=TM + 8*mm, bottomMargin=BM + 10*mm,
        )

    def build(self, story, **kw):
        def _hf(canv, doc):
            canv.saveState()
            # ── Top bar ──
            canv.setFillColor(self.accent)
            canv.rect(0, PH - 11*mm, PW, 11*mm, fill=1, stroke=0)
            # Brand name
            canv.setFont("Helvetica-Bold", 9)
            canv.setFillColor(C_GOLD)
            canv.drawString(LM, PH - 7.5*mm, "KOTASTONE")
            canv.setFont("Helvetica", 9)
            canv.setFillColor(WHITE)
            canv.drawString(LM + 62, PH - 7.5*mm, "INDIA")
            # Doc title
            canv.setFont("Helvetica", 7.5)
            canv.setFillColor(HexColor("#A8C0D6"))
            canv.drawCentredString(PW / 2, PH - 7.5*mm, self.doc_title)
            # Page number right
            canv.setFont("Helvetica", 7.5)
            canv.setFillColor(WHITE)
            canv.drawRightString(PW - RM, PH - 7.5*mm, f"Page {doc.page}")

            # ── Gold accent line under header ──
            canv.setStrokeColor(C_GOLD)
            canv.setLineWidth(1.0)
            canv.line(LM, PH - 11*mm - 1, PW - RM, PH - 11*mm - 1)

            # ── Footer line ──
            canv.setStrokeColor(C_LGREY)
            canv.setLineWidth(0.4)
            canv.line(LM, BM + 6*mm, PW - RM, BM + 6*mm)
            canv.setFont("Helvetica", 6.5)
            canv.setFillColor(C_GREY)
            canv.drawString(LM, BM + 2*mm,
                "© 2025 KotaStone India. All rights reserved.  |  Ramganj Mandi, Kota, Rajasthan")
            canv.drawRightString(PW - RM, BM + 2*mm,
                "info@kotastonefactory.in  |  +91 86194 59354")
            canv.restoreState()

        super().build(story, onFirstPage=_hf, onLaterPages=_hf)


# ══════════════════════════════════════════════════════════════
# COVER PAGE (drawn on canvas, not flowable)
# ══════════════════════════════════════════════════════════════
def draw_cover(canv, title_lines, subtitle, tagline, img_name, accent=C_BLUE, cat_type=""):
    """Draw a full-bleed cover page directly on the canvas."""
    canv.saveState()

    # ── Full bleed dark background top half ──
    canv.setFillColor(C_DARK)
    canv.rect(0, PH * 0.45, PW, PH * 0.55, fill=1, stroke=0)

    # ── Hero image (top portion, full-width) ──
    img_path = os.path.join(PIMG, img_name)
    if os.path.exists(img_path):
        try:
            pil = PILImage.open(img_path).convert("RGB")
            aw, ah = pil.size
            tw, th = int(PW * 3), int(PH * 0.55 * 3)
            scale = max(tw / aw, th / ah)
            nw, nh = int(aw * scale), int(ah * scale)
            pil = pil.resize((nw, nh), PILImage.LANCZOS)
            left = (nw - tw) // 2
            top  = (nh - th) // 2
            pil = pil.crop((left, top, left + tw, top + th))
            buf = io.BytesIO(); pil.save(buf, "JPEG", quality=85); buf.seek(0)
            canv.drawImage(buf, 0, PH * 0.45, PW, PH * 0.55,
                           preserveAspectRatio=False, anchor='c')
        except Exception:
            pass

    # ── Dark overlay gradient on image ──
    # Simulate gradient with stacked semi-transparent rects
    from reportlab.lib.colors import Color
    for i in range(10):
        alpha = 0.05 + i * 0.04
        canv.setFillColor(Color(0.11, 0.17, 0.23, alpha=alpha))
        band_h = PH * 0.55 / 10
        canv.rect(0, PH * 0.45 + i * band_h, PW, band_h + 1, fill=1, stroke=0)

    # ── Gold accent bar at 45% mark ──
    canv.setFillColor(C_GOLD)
    canv.rect(0, PH * 0.45 - 3, PW, 4, fill=1, stroke=0)

    # ── White content area (bottom 55%) ──
    canv.setFillColor(WHITE)
    canv.rect(0, 0, PW, PH * 0.45, fill=1, stroke=0)

    # ── Left accent strip ──
    canv.setFillColor(accent)
    canv.rect(0, 0, 6, PH * 0.45, fill=1, stroke=0)

    # ── Category pill on image ──
    if cat_type:
        pill_txt = cat_type.upper()
        canv.setFillColor(C_GOLD)
        canv.roundRect(LM, PH * 0.45 + 14*mm, len(pill_txt)*6 + 20, 18, 4, fill=1, stroke=0)
        canv.setFont("Helvetica-Bold", 8)
        canv.setFillColor(C_DARK)
        canv.drawString(LM + 10, PH * 0.45 + 14*mm + 5, pill_txt)

    # ── Title on image (large, white) ──
    canv.setFont("Helvetica-Bold", 32)
    canv.setFillColor(WHITE)
    y_title = PH * 0.45 + 40*mm
    for line in title_lines:
        canv.drawString(LM, y_title, line)
        y_title += 38

    # ── Subtitle on image ──
    canv.setFont("Helvetica", 14)
    canv.setFillColor(HexColor("#D0E8F8"))
    canv.drawString(LM, PH * 0.45 + 32*mm, subtitle)

    # ── Content in white zone ──
    y = PH * 0.45 - 16*mm

    # Tagline
    canv.setFont("Helvetica-Oblique", 10)
    canv.setFillColor(C_GREY)
    # Word-wrap tagline manually
    words = tagline.split()
    line_max = 72
    lines_out = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 <= line_max:
            cur = (cur + " " + w).strip()
        else:
            lines_out.append(cur); cur = w
    if cur: lines_out.append(cur)
    for ln in lines_out:
        canv.drawString(LM + 6, y, ln)
        y -= 13

    # Gold divider
    canv.setStrokeColor(C_GOLD)
    canv.setLineWidth(1.2)
    canv.line(LM + 6, y - 4, PW - RM, y - 4)
    y -= 14

    # Badges
    badges = ["ISO 9001:2015 Certified", "Grade A Quality", "Direct from Quarry",
              "Custom Sizing", "Pan-India Delivery", "Export Quality"]
    bw = (PW - LM - RM - 6) / len(badges)
    bx = LM + 6
    canv.setFont("Helvetica-Bold", 7)
    for bdg in badges:
        canv.setFillColor(C_LIGHT)
        canv.roundRect(bx, y - 14, bw - 3, 18, 3, fill=1, stroke=0)
        canv.setStrokeColor(C_LGREY)
        canv.setLineWidth(0.4)
        canv.roundRect(bx, y - 14, bw - 3, 18, 3, fill=0, stroke=1)
        canv.setFillColor(C_DARK)
        canv.drawCentredString(bx + (bw - 3) / 2, y - 8, bdg)
        bx += bw
    y -= 22

    # Contacts
    y -= 8
    contacts = [
        ("PHONE",   "+91 86194 59354"),
        ("EMAIL",   "info@kotastonefactory.in"),
        ("WEB",     "www.kotastonefactory.com"),
        ("ADDRESS", "Ramganj Mandi, Kota, Rajasthan – 326519"),
    ]
    cw_each = (PW - LM - RM - 6) / len(contacts)
    cx = LM + 6
    for lbl, val in contacts:
        canv.setFillColor(C_DARK)
        canv.rect(cx, y - 22, cw_each - 3, 28, fill=1, stroke=0)
        canv.setFont("Helvetica", 6.5)
        canv.setFillColor(HexColor("#7090AA"))
        canv.drawCentredString(cx + (cw_each - 3)/2, y + 1, lbl)
        canv.setFont("Helvetica-Bold", 8)
        canv.setFillColor(WHITE)
        # Truncate long values
        if len(val) > 28:
            val = val[:26] + "…"
        canv.drawCentredString(cx + (cw_each - 3)/2, y - 11, val)
        cx += cw_each

    # ── Brand watermark on image (top right) ──
    canv.setFont("Helvetica-Bold", 11)
    canv.setFillColor(WHITE)
    canv.drawRightString(PW - RM, PH - 18*mm, "KOTA")
    canv.setFont("Helvetica", 11)
    canv.setFillColor(C_GOLD)
    canv.drawRightString(PW - RM, PH - 25*mm, "STONE INDIA")
    canv.setFont("Helvetica", 7.5)
    canv.setFillColor(HexColor("#90B0C8"))
    canv.drawRightString(PW - RM, PH - 31*mm, "Since 1975")

    canv.restoreState()
    canv.showPage()


# ══════════════════════════════════════════════════════════════
# PDF BUILDER
# ══════════════════════════════════════════════════════════════
def build(filename, story, doc_title, accent=C_BLUE):
    path = os.path.join(OUT, filename)
    doc = KotaDoc(path, doc_title=doc_title, accent=accent)
    doc.build(story)
    kb = os.path.getsize(path) / 1024
    print(f"  ✓  {filename:52s}  {kb:6.0f} KB")
    return path


def make_pdf(filename, cover_args, story_fn, doc_title, accent=C_BLUE):
    """Build a PDF: draw cover on page 1, then content pages."""
    path = os.path.join(OUT, filename)

    # We need a canvas-level trick: draw cover first, then doc
    # Strategy: render cover into page 1 via onFirstPage hook with platypus.
    # Use a dummy first-page that starts on page 2 via canvas.
    story = story_fn()

    class _Doc(SimpleDocTemplate):
        def __init__(self):
            super().__init__(
                path, pagesize=A4,
                leftMargin=LM, rightMargin=RM,
                topMargin=TM + 8*mm, bottomMargin=BM + 10*mm,
            )
        def build(self, flowables):
            def first_page(canv, doc):
                draw_cover(canv, **cover_args, accent=accent)
                # After cover is drawn we need the content to start fresh
                # The cover already called showPage(), so we're on page 2 now

            def later_pages(canv, doc):
                canv.saveState()
                canv.setFillColor(accent)
                canv.rect(0, PH - 11*mm, PW, 11*mm, fill=1, stroke=0)
                canv.setFont("Helvetica-Bold", 9); canv.setFillColor(C_GOLD)
                canv.drawString(LM, PH - 7.5*mm, "KOTASTONE")
                canv.setFont("Helvetica", 9); canv.setFillColor(WHITE)
                canv.drawString(LM + 62, PH - 7.5*mm, " INDIA")
                canv.setFont("Helvetica", 7.5); canv.setFillColor(HexColor("#A8C0D6"))
                canv.drawCentredString(PW/2, PH - 7.5*mm, doc_title)
                canv.setFont("Helvetica", 7.5); canv.setFillColor(WHITE)
                canv.drawRightString(PW - RM, PH - 7.5*mm, f"Page {doc.page - 1}")
                canv.setStrokeColor(C_GOLD); canv.setLineWidth(1.0)
                canv.line(LM, PH - 12*mm, PW - RM, PH - 12*mm)
                canv.setStrokeColor(C_LGREY); canv.setLineWidth(0.4)
                canv.line(LM, BM + 6*mm, PW - RM, BM + 6*mm)
                canv.setFont("Helvetica", 6.5); canv.setFillColor(C_GREY)
                canv.drawString(LM, BM + 2*mm,
                    "© 2025 KotaStone India  |  Ramganj Mandi, Kota, Rajasthan  |  ISO 9001:2015 Certified")
                canv.drawRightString(PW - RM, BM + 2*mm,
                    "info@kotastonefactory.in  |  +91 86194 59354")
                canv.restoreState()

            super().build(flowables, onFirstPage=first_page, onLaterPages=later_pages)

    _Doc().build(story)
    kb = os.path.getsize(path) / 1024
    print(f"  ✓  {filename:52s}  {kb:6.0f} KB")
    return path


# ══════════════════════════════════════════════════════════════
# SHARED CONTENT BLOCKS
# ══════════════════════════════════════════════════════════════
def cta_block(text):
    items = []
    items.append(sp(6))
    items += section_header("Get Started", "Request Samples · Get a Quote")
    items.append(body(text))
    items.append(sp(8))
    items.append(contact_strip())
    return items


def why_kotastone_block():
    return [
        sp(6),
        *section_header("Why KotaStone India", "Trusted for Over 50 Years"),
        body("KotaStone India has been at the forefront of premium Kota Stone quarrying and processing since 1975. "
             "Headquartered at Ramganj Mandi — the global epicentre of Kota Stone production — we combine traditional "
             "quarrying expertise with modern processing technology to deliver consistently superior natural stone "
             "products to residential, commercial, and industrial clients across India and 30+ export markets."),
        sp(6),
        stat_bar([
            ("50+", "Years of\nExperience"),
            ("30+", "Export\nMarkets"),
            ("Grade A", "Quality\nCertified"),
            ("ISO", "9001:2015\nCertified"),
        ]),
        sp(12),
    ]


# ══════════════════════════════════════════════════════════════
# PDF 1 — MASTER CATALOGUE
# ══════════════════════════════════════════════════════════════
def make_catalogue():
    def story():
        s = [sp(4)]

        # ── About ──
        s += section_header("About KotaStone India", "India's Premier Natural Stone Manufacturer")
        s.append(body(
            "KotaStone India has been the most trusted name in premium Kota Stone quarrying, processing, and supply "
            "for over five decades. Operating directly from Ramganj Mandi, Kota — the geological heartland of Kota "
            "Stone production in Rajasthan — we combine generations of quarrying expertise with modern processing "
            "technology to deliver consistently superior Grade A natural stone to clients across India and 30+ countries."
        ))
        s.append(body(
            "Every slab leaving our facility undergoes rigorous quality inspection against Bureau of Indian Standards "
            "(BIS) specifications, ensuring that every order — from 10 sq ft sample sets to 100,000 sq ft mega-project "
            "supplies — meets our uncompromising quality standard. We offer custom sizing, surface finishing, "
            "quality certification, and end-to-end logistics support for projects of any scale."
        ))
        s.append(sp(8))
        s.append(stat_bar([
            ("50+",  "Years in\nBusiness"),
            ("30+",  "Countries\nExported To"),
            ("100+", "Product\nVariants"),
            ("A",    "Grade\nCertified"),
        ]))
        s.append(sp(14))

        # ── Stone Variants ──
        s += section_header("Stone Variants", "Kota Blue & Kota Brown")
        s.append(body(
            "KotaStone India supplies two primary stone variants quarried from the Vindhyan sedimentary basin of "
            "the Kota district. Both are fine-grained limestones sharing identical geological excellence — differing "
            "only in their mineral composition, which produces their distinct colour palette."
        ))
        s.append(sp(8))
        var_rows = [[
            [Paragraph("KOTA BLUE", _ps("VH1", fontName="Helvetica-Bold", fontSize=12, textColor=C_BLUE, spaceAfter=5)),
             Paragraph("The most iconic variety — a timeless blue-green limestone ranging from deep sea-blue "
                       "to soft aqua-grey. The architects' first choice for luxury residential, commercial, "
                       "and institutional projects.", PS_BODY_S),
             Paragraph("Colour: Blue-Green, Aqua-Grey", PS_BODY_S),
             Paragraph("Water Absorption: < 0.5%  |  Strength: ≥ 70 MPa", PS_BODY_S),
             Paragraph("Best For: Luxury interiors, pools, commercial floors, cladding", PS_BODY_S)],
            [Paragraph("KOTA BROWN", _ps("VH2", fontName="Helvetica-Bold", fontSize=12, textColor=HexColor("#8B5E3C"), spaceAfter=5)),
             Paragraph("Warm amber and brown tones produced by higher iron oxide content. The heritage "
                       "builder's material of choice — pairs beautifully with wood, terracotta, and natural "
                       "earthy interiors.", PS_BODY_S),
             Paragraph("Colour: Brown, Amber, Tan", PS_BODY_S),
             Paragraph("Water Absorption: < 0.5%  |  Strength: ≥ 68 MPa", PS_BODY_S),
             Paragraph("Best For: Heritage, temples, kitchens, warm interiors", PS_BODY_S)],
        ]]
        vt = Table(var_rows, colWidths=[(CW-4*mm)/2]*2)
        vt.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(0,-1), HexColor("#EBF3FB")),
            ("BACKGROUND",    (1,0),(1,-1), HexColor("#FDF5EC")),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("TOPPADDING",    (0,0),(-1,-1), 14),("BOTTOMPADDING",(0,0),(-1,-1),14),
            ("LEFTPADDING",   (0,0),(-1,-1), 14),("RIGHTPADDING",(0,0),(-1,-1),14),
            ("LINEBEFORE",    (0,0),(0,-1),  3, C_BLUE),
            ("LINEBEFORE",    (1,0),(1,-1),  3, HexColor("#8B5E3C")),
            ("LINEAFTER",     (0,0),(0,-1),  0.4, C_LGREY),
        ]))
        s.append(vt); s.append(sp(14))

        # ── Finishes ──
        s += section_header("Surface Finishes", "Six Professional Treatment Options")
        s.append(body("Kota Stone is available in six distinct surface finishes, each engineered for specific "
                      "applications and aesthetic requirements. The choice of finish significantly affects the "
                      "stone's slip resistance, maintenance requirements, and visual character."))
        s.append(sp(6))
        s.append(feat_grid([
            ("✦", "Polished",     "Mirror-like high-gloss surface (60–90 GU). Amplifies colour depth. Best for luxury hotel lobbies, corporate reception, upscale residential interiors. Indoor dry areas only."),
            ("◈", "Honed",        "Satin-matte smooth surface (10–25 GU). Contemporary, non-reflective. R10 wet slip rating. Best for bathrooms, bedrooms, kitchens, and modern commercial interiors."),
            ("◇", "Natural",      "Original quarried texture with natural undulations. Highest anti-slip rating (R12). Most economical finish. Best for outdoor pathways, temples, terraces, and industrial floors."),
            ("◉", "Leather",      "Wire-brushed micro-textured surface. R10–R11 wet slip resistance. Reveals deeper colour tones. Best for pool surrounds, spas, and luxury outdoor terraces."),
            ("▲", "Flamed",       "Thermally treated rough surface. Maximum grip (R12+). Highly durable finish. Best for heavy-duty industrial, commercial outdoor, and high-footfall public zones."),
            ("□", "Sandblasted",  "Fine abrasive texture, uniform matte appearance. Good grip and weather resistance. Best for wall cladding panels, decorative facades, and architectural feature surfaces."),
        ]))
        s.append(sp(14))

        # ── Technical Specs ──
        s += section_header("Technical Specifications", "Physical & Mechanical Properties")
        s.append(spec_table(
            [["Property", "Value", "Test Standard", "Significance"],
             ["Stone Classification", "Fine-Grained Limestone", "IS 1122", "Natural sedimentary origin"],
             ["Geological Origin", "Vindhyan Formation, Kota District, RJ", "—", "Single-source authenticity"],
             ["Density", "2,600 – 2,700 kg/m³", "IS 1124", "High mass = high durability"],
             ["Water Absorption", "< 0.5%", "IS 1124", "Frost & stain resistant"],
             ["Compressive Strength", "≥ 70 MPa", "IS 1121", "3× stronger than ceramics"],
             ["Flexural Strength", "≥ 10 MPa", "IS 1723", "Resists point loads"],
             ["Modulus of Rupture", "≥ 6.9 MPa", "ASTM C99", "Stair tread safe"],
             ["Mohs Hardness", "3 – 4", "—", "Scratch resistant"],
             ["Abrasion Resistance", "High (I ≤ 2.0)", "IS 1237", "Long service life"],
             ["Thermal Expansion", "Low (0.004 mm/m·°C)", "—", "Stable in extreme temps"],
             ["Slip Resistance (Natural)", "R10 – R12", "DIN 51130", "Safe in wet conditions"],
             ["Frost Resistance", "Yes (Class F4)", "EN 12371", "Suitable for all climates"],],
            col_widths=[CW*0.30, CW*0.25, CW*0.20, CW*0.25],
            col_aligns=["LEFT","CENTER","CENTER","LEFT"],
        ))
        s.append(sp(14))

        # ── Sizes ──
        s += section_header("Standard Dimensions", "Sizes, Formats & Thickness Options")
        s.append(spec_table(
            [["Format", "Dimensions", "Standard Thickness", "Typical Application"],
             ["Standard Module",  "600 × 600 mm",         "20 mm",    "Residential & Commercial Flooring"],
             ["Large Plank",      "600 × 900 mm",         "20–25 mm", "Open-plan Commercial Floors"],
             ["Plank Format",     "300 × 600 mm",         "20 mm",    "Rectangular Corridor Layouts"],
             ["Classic Square",   "400 × 400 mm",         "20–25 mm", "Standard Residential Flooring"],
             ["Heavy Duty",       "600 × 600 mm",         "30 mm",    "Industrial Floors & Parking"],
             ["Stair Tread",      "900 × 300–450 mm",     "40–50 mm", "Staircases — Structural Slabs"],
             ["Riser Panel",      "900 × 150–180 mm",     "20–25 mm", "Vertical Stair Faces"],
             ["Cladding Panel",   "300–600 × Any Length", "10–12 mm", "Interior & Exterior Wall Cladding"],
             ["Kerb / Edge",      "100 × Any Length",     "50–75 mm", "Path Edging & Pool Coping"],
             ["Custom Cut",       "Any Dimension",         "As Spec'd", "Bespoke Project Requirements"],],
            col_widths=[CW*0.20, CW*0.22, CW*0.20, CW*0.38],
            col_aligns=["LEFT","CENTER","CENTER","LEFT"],
        ))
        s.append(note("* All sizes are nominal. Custom dimensions available. Tolerances: ±2 mm on length/width, ±1 mm on thickness."))
        s.append(sp(14))

        # ── Pricing ──
        s += section_header("Price Reference", "Indicative Ex-Factory Rates — Kota, Rajasthan")
        s.append(body("The following price ranges are indicative ex-factory rates. Actual pricing depends on "
                      "order quantity, grade, size specification, and delivery destination. Contact us for a "
                      "formal project quotation with exact pricing, timeline, and logistics plan."))
        s.append(sp(6))
        s.append(spec_table(
            [["Product", "Finish Grade", "Price Range (per sq ft)", "Notes"],
             ["Kota Blue",          "Natural",         "₹ 35 – 55",        "Standard grade, bulk volume"],
             ["Kota Blue",          "Honed",           "₹ 55 – 80",        "Machine honed, Grade A"],
             ["Kota Blue",          "Polished",        "₹ 75 – 120",       "Mirror finish, premium grade"],
             ["Kota Blue",          "Leather",         "₹ 65 – 95",        "Wire-brushed, export quality"],
             ["Kota Brown",         "Natural",         "₹ 30 – 50",        "Standard grade, bulk volume"],
             ["Kota Brown",         "Honed",           "₹ 50 – 75",        "Machine honed"],
             ["Kota Brown",         "Polished",        "₹ 65 – 100",       "Mirror finish"],
             ["Stair Tread (40mm)", "Honed/Natural",   "₹ 180 – 350 each", "Per running tread, supplied"],
             ["Wall Cladding",      "Honed/Natural",   "₹ 45 – 80",        "Per sq ft, 10–12 mm panels"],
             ["Industrial (30mm)",  "Natural",         "₹ 65 – 90",        "Heavy-duty grade, bulk"],],
            col_widths=[CW*0.22, CW*0.18, CW*0.28, CW*0.32],
            col_aligns=["LEFT","LEFT","CENTER","LEFT"],
        ))
        s.append(note("* Prices are indicative ex-factory Kota. GST, transportation, and installation are additional. "
                      "Prices subject to change without notice. Formal quotation required for project orders."))
        s.append(sp(14))

        # ── Applications ──
        s += section_header("Application Guide", "Where Kota Stone Performs Best")
        s.append(feat_grid([
            ("◈", "Flooring",            "Residential homes, commercial offices, hotels, hospitals, schools, and industrial facilities. Lasts 50+ years with minimal care. Available in all finishes."),
            ("◇", "Outdoor Pathways",    "Garden paths, driveways, temple walkways, and public pedestrian zones. Natural finish provides R12 anti-slip grip in all weather conditions."),
            ("✦", "Wall Cladding",       "Interior feature walls and exterior building facades. 10–12 mm thin panels are lightweight, moisture-resistant, and architecturally striking."),
            ("◉", "Pool Surrounds",      "The safest pool decking material — anti-slip (R10–R12) when wet, cool underfoot, and chlorine-resistant. Available in natural and leather finishes."),
            ("▲", "Staircases",          "40–50 mm structural tread slabs with natural grip. Resists edge chipping and nosing abrasion for the lifetime of any building."),
            ("□", "Kitchen Countertops", "Heat-resistant to 300°C, hygienic, scratch-resistant (Mohs 4), and food-safe. Lower cost than granite or quartz with superior durability."),
            ("◈", "Parking Tiles",       "70+ MPa compressive strength in 25–30 mm thickness supports vehicle loads. Anti-skid, oil-resistant, zero maintenance for 25+ years."),
            ("◉", "Industrial Floors",   "Heavy-duty 25–30 mm slabs handle forklift traffic, chemical spills, and temperature extremes. No replacement cycle — lasts the building's lifetime."),
        ]))
        s.append(sp(14))

        # ── CTA ──
        s += cta_block(
            "Our stone experts are available to help you select the right variant, finish, and specification "
            "for your project. We offer free samples, site consultation, technical data sheets, IS certification "
            "documents, and competitive bulk pricing for projects of any scale. Pan-India delivery within 7–10 "
            "working days. Export orders handled with full documentation."
        )
        return s

    return make_pdf(
        "catalogue.pdf",
        dict(title_lines=["KotaStone India", "Product E-Catalogue"],
             subtitle="All Variants · All Finishes · Specifications · Pricing",
             tagline="India's most trusted natural limestone — quarried and processed in Kota, Rajasthan since 1975. Grade A quality, ISO 9001:2015 certified, exported to 30+ countries.",
             img_name="kota_blue.jpg",
             cat_type="Master Catalogue"),
        story,
        doc_title="KotaStone India — Product E-Catalogue",
    )


# ══════════════════════════════════════════════════════════════
# PRODUCT PDF FACTORY
# ══════════════════════════════════════════════════════════════
def make_product(filename, cover_kw, doc_title,
                 about_head, about_paras,
                 stats, features,
                 spec_rows, spec_cw, spec_ca,
                 sizes, thicknesses,
                 skus, applications,
                 care_tips, cta_text, accent=C_BLUE):

    def story():
        s = [sp(4)]

        # About
        s += section_header("About This Product", about_head)
        for p in about_paras:
            s.append(body(p))
        s.append(sp(8))
        if stats:
            s.append(stat_bar(stats))
        s.append(sp(14))

        # Features
        s += section_header("Key Features & Benefits", "Why Professionals Choose This Stone")
        s.append(feat_grid(features))
        s.append(sp(14))

        # Specs
        s += section_header("Technical Specifications", "Physical & Mechanical Properties")
        s.append(spec_table(spec_rows, spec_cw, spec_ca))
        s.append(sp(10))

        # Sizes & thickness
        s.append(two_col_list(
            "Available Sizes", sizes,
            "Thickness Options", thicknesses,
        ))
        s.append(sp(14))

        # SKUs
        if skus:
            s += section_header("Product Catalogue", "Grade & Finish Reference Codes")
            s.append(body("The following product codes identify specific finish grades within this stone range. "
                          "Quote the product code when placing an order for precise specification matching."))
            s.append(sp(6))
            s.append(sku_grid(skus))
            s.append(sp(14))

        # Applications
        s += section_header("Ideal Applications", "Project Types & Use Cases")
        s.append(feat_grid(applications))
        s.append(sp(14))

        # Care & maintenance
        if care_tips:
            s += section_header("Care & Maintenance", "Keeping Your Kota Stone in Perfect Condition")
            s.append(feat_grid(care_tips, cols=2))
            s.append(sp(14))

        # CTA
        s += cta_block(cta_text)
        return s

    return make_pdf(filename, cover_kw, story, doc_title, accent)


# ══════════════════════════════════════════════════════════════
# APPLICATION PDF FACTORY
# ══════════════════════════════════════════════════════════════
def make_application(filename, cover_kw, doc_title,
                     intro_head, intro_paras,
                     stats, advantages,
                     spec_rows, spec_cw,
                     install_rows,
                     project_types, cta_text):

    def story():
        s = [sp(4)]

        # Intro
        s += section_header("Overview", intro_head)
        for p in intro_paras:
            s.append(body(p))
        s.append(sp(8))
        if stats:
            s.append(stat_bar(stats))
        s.append(sp(14))

        # Advantages
        s += section_header("Key Advantages", "Why Kota Stone Outperforms Alternatives")
        s.append(feat_grid(advantages))
        s.append(sp(14))

        # Spec table
        s += section_header("Technical Specifications", "Product Selection Guide")
        s.append(spec_table(spec_rows, spec_cw))
        s.append(sp(14))

        # Installation
        if install_rows:
            s += section_header("Installation Guide", "Recommended Installation Method")
            s.append(spec_table(install_rows, [CW*0.25, CW*0.35, CW*0.40]))
            s.append(sp(14))

        # Project types
        s += section_header("Project Types", "Where We Supply")
        s.append(feat_grid(project_types))
        s.append(sp(14))

        # Comparison vs alternatives
        s += cta_block(cta_text)
        return s

    return make_pdf(filename, cover_kw, story, doc_title)


# ══════════════════════════════════════════════════════════════
# DATA — ALL PRODUCTS & APPLICATIONS
# ══════════════════════════════════════════════════════════════

CARE_STANDARD = [
    ("◈", "Daily Cleaning",       "Sweep with a soft broom or vacuum to remove dust and grit. Mop with warm water and a pH-neutral cleaner. Avoid acidic cleaners (vinegar, lemon) which etch limestone."),
    ("◇", "Stain Removal",        "Blot spills immediately. For oil stains, use a baking soda poultice. For rust, use a specialist stone rust remover. Never use bleach or abrasive pads on polished surfaces."),
    ("◉", "Periodic Maintenance", "Polished surfaces: buff annually with a stone polishing compound. Natural and honed surfaces require no polishing — re-seal every 2–3 years with a penetrating impregnator sealer."),
    ("▲", "What to Avoid",        "Avoid dragging heavy furniture without felt pads. Do not use steel wool, wire brushes, or abrasive scouring pads. Avoid prolonged standing water on joints and grout lines."),
]

INSTALL_FLOORING = [
    ["Step", "Method", "Details"],
    ["1. Sub-base", "Prepare level substrate", "Concrete or sand-cement screed, min 75 mm, fully cured. Max deviation: 3 mm in 3 m."],
    ["2. Adhesive", "Apply tile adhesive", "C2 flexible tile adhesive applied with 6 mm notched trowel. Full-bed coverage required."],
    ["3. Laying", "Set stone tiles", "Back-butter each tile. Align with string line. 3–5 mm joint width. Check level constantly."],
    ["4. Grouting", "Grout joints", "After 24 hr cure, apply cement-based or epoxy grout. Colour-match to stone variant."],
    ["5. Sealing", "Apply impregnator", "After 7 days curing, apply penetrating stone sealer. Wipe off excess within 10 minutes."],
    ["6. Curing", "Allow full cure", "Avoid foot traffic for 24 hr, heavy loads for 7 days. Wet-cure adhesive in hot conditions."],
]

def run_all():
    paths = []
    print("\nGenerating KotaStone Professional PDFs...\n")

    # ── 1. MASTER CATALOGUE ──────────────────────────────────────
    paths.append(make_catalogue())

    # ── 2. KOTA BLUE ─────────────────────────────────────────────
    paths.append(make_product(
        "kota-blue-catalogue.pdf",
        dict(title_lines=["Kota Blue Stone"],
             subtitle="Classic Blue-Green Limestone from Kota, Rajasthan",
             tagline="The legendary blue-green limestone gracing India's finest homes, temples, and institutions for centuries. Timeless, durable, and distinctively beautiful.",
             img_name="kota_blue.jpg",
             cat_type="Stone Variant"),
        "Kota Blue Stone — Product Catalogue",
        "What is Kota Blue Stone?",
        ["Kota Blue is the most iconic variety of Kota Stone. Its characteristic blue-green hue — ranging from deep "
         "sea-blue to soft aqua-grey — results from the unique mineral composition found exclusively in the Kota district "
         "of Rajasthan. Each slab carries the subtle veining and tonal variation of natural stone — meaning no two "
         "installations are ever identical.",
         "Formed over millions of years in the Vindhyan sedimentary basin, Kota Blue is a fine-grained limestone with "
         "exceptional compressive strength, very low water absorption (under 0.5%), and a naturally non-slip surface. "
         "It is the preferred material for architects, infrastructure projects, and discerning homeowners across India "
         "and over 30 countries worldwide.",
         "From luxury villas and five-star hotel lobbies to heritage temples and hospital corridors, Kota Blue delivers "
         "unmatched structural performance and visual elegance over decades — often centuries — of use."],
        [("70+ MPa", "Compressive\nStrength"), ("< 0.5%", "Water\nAbsorption"),
         ("R10–R12", "Slip\nResistance"), ("50+", "Year\nService Life")],
        [("◈", "Exceptional Durability",        "With compressive strength exceeding 70 MPa, Kota Blue withstands extreme loads, heavy traffic, and harsh weather without cracking or degrading. Three times stronger than standard ceramic tiles."),
         ("◇", "Very Low Water Absorption",      "Under 0.5% water absorption rate makes Kota Blue highly resistant to moisture penetration, frost damage, and staining — ideal for both wet outdoor and controlled indoor environments."),
         ("◉", "Natural Non-Slip Surface",       "The naturally textured surface provides excellent R10–R12 grip even when wet — intrinsically safer than polished marble, granite, or ceramic tiles in bathrooms and outdoor areas."),
         ("✦", "100% Natural & Eco-Friendly",    "No synthetic treatments, dyes, or coatings needed. Completely natural limestone — free from VOCs, resins, and chemical binders. Safe for families, pets, and the environment."),
         ("▲", "Outstanding Lifecycle Value",    "Delivers the premium look of polished marble at a fraction of the cost, with far superior durability. Total lifecycle cost (material + maintenance + replacement) is dramatically lower."),
         ("□", "Six Finish Options",             "Available in polished, honed, natural, leather, flamed, and sandblasted finishes. One stone variant, six distinct aesthetic personalities — suitable for any design requirement."),],
        [["Property", "Value", "Standard"],
         ["Stone Classification", "Fine-Grained Limestone", "IS 1122"],
         ["Colour Range", "Blue-Green to Aqua-Grey", "—"],
         ["Water Absorption", "< 0.5%", "IS 1124"],
         ["Compressive Strength", "≥ 70 MPa", "IS 1121"],
         ["Flexural Strength", "≥ 10 MPa", "IS 1723"],
         ["Mohs Hardness", "3 – 4", "—"],
         ["Density", "2,600–2,700 kg/m³", "IS 1124"],
         ["Abrasion Resistance", "High (I ≤ 2.0)", "IS 1237"],
         ["Thermal Expansion", "0.004 mm/m·°C", "—"],
         ["Frost Resistance", "Yes — Class F4", "EN 12371"],
         ["Slip Resistance", "R10–R12", "DIN 51130"],],
        [CW*0.44, CW*0.34, CW*0.22],
        ["LEFT","CENTER","CENTER"],
        ["600 × 600 mm  —  Standard Module",
         "600 × 900 mm  —  Large Plank Format",
         "300 × 600 mm  —  Plank Format",
         "400 × 400 mm  —  Classic Square",
         "900 × 300 mm  —  Stair Tread",
         "Custom Cut    —  Any Dimension"],
        ["10–12 mm  —  Wall Cladding Panels",
         "18–20 mm  —  Standard Flooring",
         "25 mm      —  Heavy Commercial Floor",
         "30 mm      —  Industrial / Parking Grade",
         "40–50 mm  —  Stair Treads (Structural)",
         "75 mm      —  Kerb & Coping Stones"],
        [("KBS01","Sombre","Deep blue-grey natural finish with textured quarried surface. Maximum anti-slip grip. Ideal for heavy-duty outdoor flooring, temple pathways, and industrial use.","Natural Finish"),
         ("KBS02","Riverwatch","Medium blue-green with aqua undertones in a smooth honed surface. Contemporary matte. Perfect for residential living rooms, offices, and modern commercial interiors.","Honed Finish"),
         ("KBS03","Leather Blue","Wire-brushed leathered surface revealing deep colour tones. R10/R11 wet grip. Premier choice for pool surrounds, spa areas, and luxury outdoor terraces.","Leather Finish"),
         ("KBS04","Mirror","High-gloss mirror polish amplifying vivid blue-green pigmentation. 60–90 GU. Most glamorous finish for luxury lobbies, showrooms, and premium residences.","Polished Finish"),
         ("KBS05","Mirror Satin","Satin polish between honed and full mirror. Soft reflective sheen for upscale residential interiors, master bedrooms, and premium office reception areas.","Satin Polish"),
         ("KBS06","High Honed","Extra-fine honed with near-satin smoothness. Contemporary, sophisticated finish for premium residential, boutique hospitality, and upscale retail projects.","High Honed"),],
        [("◈", "Residential Flooring",     "Living rooms, verandas, bedrooms, and courtyards — Kota Blue creates a cool, elegant ambience that ages gracefully over decades of daily use."),
         ("◇", "Commercial Spaces",        "Hotels, hospitals, offices, airports, and schools rely on Kota Blue for its low maintenance burden, exceptional durability, and professional appearance."),
         ("◉", "Outdoor Pathways",         "Garden paths, temple walkways, and public pedestrian zones — the natural non-slip finish ensures safe footing in all weather conditions including monsoon."),
         ("✦", "Wall Cladding",            "10–12 mm thin slab panels add architectural depth, texture, and organic beauty to interior feature walls and exterior building facades."),
         ("▲", "Pool Surrounds",           "Anti-slip (R10–R12), cool underfoot, chlorine-resistant, and UV-stable — the safest and most aesthetically stunning choice for any pool deck."),
         ("□", "Staircases",              "40–50 mm structural tread slabs with natural grip exceed building code requirements. Resists edge chipping at nosing zones for the building's lifetime."),],
        CARE_STANDARD,
        "Get a free sample set of all six Kota Blue finish grades, a bulk quotation, or technical data sheets for your "
        "project. Our stone specialists can advise on the optimal finish for your specific application. We deliver "
        "pan-India within 7–10 working days.",
    ))

    # ── 3. KOTA BROWN ────────────────────────────────────────────
    paths.append(make_product(
        "kota-brown-catalogue.pdf",
        dict(title_lines=["Kota Brown Stone"],
             subtitle="Warm Earthy Limestone — Rich Amber & Brown Tones",
             tagline="The stone of tradition, warmth, and heritage. Trusted for centuries across India's homes, temples, havelis, and heritage institutions.",
             img_name="kota_brown.jpg",
             cat_type="Stone Variant"),
        "Kota Brown Stone — Product Catalogue",
        "What is Kota Brown Stone?",
        ["Kota Brown is the warm-toned counterpart to Kota Blue, featuring rich brown, amber, and tan hues produced "
         "by higher iron oxide content in the limestone's natural mineral composition. While geologically identical to "
         "Kota Blue in structure and strength, its warm colour palette gives it a completely distinct aesthetic character "
         "and design personality.",
         "Kota Brown carries identical physical performance properties — 68+ MPa compressive strength, sub-0.5% water "
         "absorption, and natural non-slip surface texture — making it equally suited for all demanding residential, "
         "commercial, and infrastructure applications where Kota Stone excels.",
         "It is the preferred material for heritage restoration projects, traditional Rajasthani havelis, temple "
         "complexes, warm contemporary interiors, and any project where earthy, organic warmth is the desired aesthetic. "
         "The natural variation in each slab ensures a truly one-of-a-kind installation that no manufactured tile can replicate."],
        [("68+ MPa", "Compressive\nStrength"), ("< 0.5%", "Water\nAbsorption"),
         ("R10–R12", "Slip\nResistance"), ("Centuries", "Proven\nHeritage")],
        [("◈", "Warm Earthy Palette",         "Rich brown, amber, and tan hues pair beautifully with wood, terracotta, jute, and earthy materials — creating naturally warm, inviting spaces that feel grounded and sophisticated."),
         ("◇", "Identical Structural Excellence","Same Vindhyan limestone composition as Kota Blue. Compressive strength of 68+ MPa, frost resistant, and long-lasting in any climate or load condition."),
         ("◉", "Unique Natural Variation",     "Every slab carries distinct natural veining, iron streaking, and tonal variation from amber to deep brown — meaning no two installations are ever identical."),
         ("✦", "Heritage & Traditional Value", "The material of choice for heritage restoration, temple construction, traditional havelis, and community buildings where warm stone aesthetics are culturally significant."),
         ("▲", "100% Natural & Eco-Friendly",  "Zero chemical processing, zero synthetic treatments. Natural limestone that is fully safe for children, pets, food contact surfaces, and the environment."),
         ("□", "Excellent Lifecycle Value",    "Delivers warm stone aesthetics comparable to expensive sandstone or travertine at a fraction of the investment, with a service life that far outlasts both."),],
        [["Property", "Value", "Standard"],
         ["Stone Classification", "Fine-Grained Limestone", "IS 1122"],
         ["Colour Range", "Brown, Amber, Tan", "—"],
         ["Water Absorption", "< 0.5%", "IS 1124"],
         ["Compressive Strength", "≥ 68 MPa", "IS 1121"],
         ["Flexural Strength", "≥ 9 MPa", "IS 1723"],
         ["Mohs Hardness", "3 – 4", "—"],
         ["Density", "2,580–2,680 kg/m³", "IS 1124"],
         ["Abrasion Resistance", "High (I ≤ 2.0)", "IS 1237"],
         ["Frost Resistance", "Yes — Class F4", "EN 12371"],
         ["Slip Resistance", "R10–R12", "DIN 51130"],],
        [CW*0.44, CW*0.34, CW*0.22],
        ["LEFT","CENTER","CENTER"],
        ["600 × 600 mm  —  Standard Module",
         "600 × 900 mm  —  Large Plank Format",
         "300 × 600 mm  —  Plank Format",
         "400 × 400 mm  —  Classic Square",
         "900 × 300 mm  —  Stair Tread",
         "Custom Cut    —  Any Dimension"],
        ["10–12 mm  —  Wall Cladding Panels",
         "18–20 mm  —  Standard Flooring",
         "25 mm      —  Heavy Commercial Floor",
         "30 mm      —  Industrial / Parking Grade",
         "40–50 mm  —  Stair Treads (Structural)"],
        [("KBR01","Terra","Rich warm brown natural finish. Highest texture and anti-slip grip. Ideal for outdoor pathways, temple surrounds, courtyards, and heritage building approaches.","Natural Finish"),
         ("KBR02","Amber Honed","Smooth honed surface with warm golden-amber undertones. Perfect for residential living rooms, boutique hospitality interiors, and warm commercial spaces.","Honed Finish"),
         ("KBR03","Rustic Leather","Wire-brushed leathered surface with rich brown-amber tones. R10/R11 slip resistance. Excellent for pool surrounds, spa terraces, and outdoor entertaining areas.","Leather Finish"),
         ("KBR04","Gloss Amber","High-gloss polished surface revealing vivid brown-amber veining and iron streaking. Stunning for reception areas, luxury feature walls, and premium lobbies.","Polished Finish"),
         ("KBR05","Satin Brown","Satin-polished surface with warm earthy tones and soft reflective sheen. Ideal for premium residential interiors and boutique commercial hospitality spaces.","Satin Polish"),
         ("KBR06","Heritage Natural","Thick 25–30 mm heavy-duty natural finish. Maximum slip resistance and load-bearing capacity. Designed for factory floors, heritage courtyards, and industrial use.","Natural — Heavy Duty"),],
        [("◈", "Residential Interiors",        "Warm earthy tones complement wooden furniture, terracotta accessories, and rustic decor in living rooms, dining rooms, bedrooms, and home studios."),
         ("◇", "Kitchens & Courtyards",        "Heat-resistant (300°C), easy to clean, and naturally hygienic. A practical, stylish choice for kitchen platforms, utility areas, and outdoor courtyards."),
         ("◉", "Heritage & Temple Projects",   "The warm, earthy character aligns with traditional Indian architecture. The preferred choice for temples, havelis, dharamshalas, and heritage conservation."),
         ("✦", "Outdoor Pathways",             "Naturally non-slip and all-weather resistant — perfect for garden paths, estate driveways, rural home forecourts, and outdoor terrace areas."),
         ("▲", "Accent Walls & Facades",       "Kota Brown cladding panels create dramatic rustic feature walls in hospitality venues, farm-stay resorts, restaurants, and retail flagship stores."),
         ("□", "Industrial & Commercial Floors","The darker earthy tones conceal dust, grime, and wear better in workshops, warehouses, and industrial facilities — maintaining a cleaner appearance."),],
        CARE_STANDARD,
        "Request free samples of Kota Brown in all available finish grades. Get a formal project quotation with "
        "competitive bulk pricing. Our team can advise on the best finish and specification for your specific project requirements.",
        accent=HexColor("#8B5E3C"),
    ))

    # ── 4. POLISHED ──────────────────────────────────────────────
    paths.append(make_product(
        "polished-finish-catalogue.pdf",
        dict(title_lines=["Polished Kota Stone"],
             subtitle="Mirror-Like Luxury Finish for Premium Interior Spaces",
             tagline="The most glamorous expression of Kota Stone — where the raw beauty of natural limestone meets the reflective elegance of high-end interior design.",
             img_name="polished.jpg",
             cat_type="Surface Finish"),
        "Polished Kota Stone — Finish Catalogue",
        "What is Polished Finish Kota Stone?",
        ["Polished Kota Stone undergoes a rigorous multi-stage diamond polishing process, progressing through a sequence "
         "of abrasive grits — from 80 grit through to 3,000 grit — until the surface achieves a highly reflective, "
         "mirror-like sheen with a gloss reading of 60–90 Gloss Units. The process is performed on calibrated grinding "
         "machines under controlled conditions to ensure uniform gloss level across entire project quantities.",
         "The polished finish is the most glamorous and visually dramatic expression of Kota Stone. It is the preferred "
         "choice for luxury hotel lobbies, five-star resort interiors, upscale residential living spaces, retail "
         "showrooms, and corporate reception areas where visual impact and brand impression are paramount.",
         "Despite the high-gloss finish, polished Kota Stone retains all of the material's inherent structural and "
         "durability properties. It is easier to clean than matte surfaces, resistant to everyday chemical spills, "
         "and develops a beautiful deep patina over time that only enhances its character."],
        [("60–90", "Gloss\nUnits (GU)"), ("Mirror", "Surface\nFinish"),
         ("R9", "Dry Slip\nRating"), ("Easy", "Maintenance\nLevel")],
        [("◈", "Mirror-Like Light Reflection",   "The high-gloss surface reflects both natural and artificial light, creating a stunning visual effect that makes interior spaces appear larger, brighter, and more luxurious."),
         ("◇", "Amplified Natural Colour",        "Polishing intensifies Kota Stone's characteristic pigmentation — making the blue-green or brown tones deeper, more vivid, and visually striking compared to matte finishes."),
         ("◉", "Effortless Surface Maintenance",  "The smooth, closed-pore polished surface is the easiest Kota Stone finish to clean. Simple damp mopping removes all surface contaminants without residue."),
         ("✦", "Premium Aesthetic at Lower Cost", "Delivers the luxury visual impression of polished marble or granite at a fraction of the material cost — the preferred choice for budget-conscious luxury projects."),
         ("▲", "Scratch & Chemical Resistance",   "The dense, closed-pore polished surface resists everyday surface scratching, common chemical spills, and staining from oils, beverages, and cleaning agents."),
         ("□", "Uniform Quality Across Batches",  "Our controlled polishing process ensures uniform gloss level, colour consistency, and surface flatness across every slab in a project — no variation between deliveries."),],
        [["Property", "Value", "Standard"],
         ["Finish Classification", "High-Gloss Mirror Polish", "—"],
         ["Gloss Level", "60–90 Gloss Units (GU)", "ASTM C1299"],
         ["Surface Roughness (Ra)", "0.05–0.2 µm", "ISO 4287"],
         ["Slip Rating (Dry)", "R9 (adequate for dry indoor)", "DIN 51130"],
         ["Water Absorption", "< 0.5%", "IS 1124"],
         ["Compressive Strength", "≥ 70 MPa", "IS 1121"],
         ["Chemical Resistance", "Good (avoid acids)", "—"],
         ["Available Variants", "Kota Blue & Kota Brown", "—"],
         ["Recommended Environment", "Indoor — Dry Areas Only", "—"],
         ["Re-polish Interval", "5–10 years (high traffic)", "—"],],
        [CW*0.40, CW*0.38, CW*0.22], ["LEFT","CENTER","CENTER"],
        ["600 × 600 mm  —  Standard Module",
         "600 × 900 mm  —  Large Plank",
         "300 × 600 mm  —  Plank Format",
         "400 × 400 mm  —  Classic Square",
         "Custom Cut    —  Any Dimension"],
        ["10–12 mm  —  Wall Cladding Panels",
         "18–20 mm  —  Standard Flooring",
         "25 mm      —  Premium Commercial Floor"],
        None,
        [("◈", "Hotel & Resort Lobbies",        "The mirror finish creates a dramatic first impression in hospitality spaces, complementing chandeliers, marble reception desks, and luxury furnishings."),
         ("◇", "Luxury Retail Showrooms",       "Luxury retail brands and high-end product showrooms use polished Kota Stone to create a pristine, upscale sales environment that elevates product presentation."),
         ("◉", "Corporate Reception & Lobbies", "Projects a prestigious, permanent quality impression in corporate headquarters, financial institutions, law firms, and executive office reception areas."),
         ("✦", "Premium Residences",            "Master bedrooms, formal living rooms, drawing rooms, and upscale dining areas — polished stone creates an air of refined, understated elegance."),
         ("▲", "Healthcare Corridors",          "Easy-to-sanitise, smooth surface with excellent chemical resistance is ideal for hospital corridors, clinical areas, and healthcare facility flooring."),
         ("□", "Feature Wall Panels",           "Polished Kota Stone cladding panels create visually striking feature walls in residential and commercial settings with minimal grout joints and seamless appearance."),],
        [("◈", "Daily Care",      "Sweep daily with a microfibre mop. Wet mop with pH-neutral stone cleaner diluted in warm water. Dry with a clean cloth to avoid water spots on polished surfaces."),
         ("◇", "Protection",     "Use felt pads under all furniture. Place entry mats at doors to trap grit. Avoid dragging abrasive objects. Use stone-safe cleaning products only — avoid vinegar, bleach, and citrus."),
         ("◉", "Re-polishing",   "In high-traffic commercial areas, a light machine re-polish may be required every 5–10 years to restore full mirror gloss. This is a simple on-site operation requiring no stone replacement."),
         ("▲", "Stain Response", "Blot spills immediately with a clean cloth. For oil-based stains, apply a baking soda poultice. For wine or coffee, use a hydrogen peroxide stone poultice. Always rinse thoroughly after treatment."),],
        "Transform your interior with the premium gloss of polished Kota Stone. Request free finish samples "
        "in both Kota Blue and Kota Brown, or obtain a bulk quotation for your project. Available for "
        "residential, hospitality, retail, and institutional projects of all scales.",
    ))

    # ── 5. HONED ─────────────────────────────────────────────────
    paths.append(make_product(
        "honed-finish-catalogue.pdf",
        dict(title_lines=["Honed Kota Stone"],
             subtitle="Satin-Matte Contemporary Finish — Sophistication Without the Gloss",
             tagline="The interior designer's first choice — understated sophistication, superior slip resistance, and lasting elegance for modern living and working spaces.",
             img_name="kota_blue.jpg",
             cat_type="Surface Finish"),
        "Honed Kota Stone — Finish Catalogue",
        "What is Honed Finish Kota Stone?",
        ["Honed Kota Stone is produced by grinding the stone surface through a sequence of abrasive grits — typically "
         "finishing at 400–800 grit — without proceeding to the final polishing stages that produce high gloss. The "
         "result is a uniformly smooth, non-reflective, satin-matte surface with a gloss reading of 10–25 GU. "
         "The surface is flat and smooth to the touch, but does not reflect light.",
         "The honed finish has become the preferred choice among contemporary interior designers and architects "
         "across India for its clean, understated sophistication. It reads as modern and restrained — perfectly "
         "suited to minimalist, Japandi, contemporary Indian, and Scandinavian-influenced design aesthetics.",
         "Critically, the honed finish provides significantly better slip resistance than polished stone (R10 wet rating), "
         "making it the safer choice for bathrooms, spas, kitchen floors, and staircases. It also forgives surface "
         "scratches and wear marks far better — minor abrasions are nearly invisible on a matte surface."],
        [("10–25", "Gloss\nUnits (GU)"), ("R10", "Wet Slip\nRating"),
         ("Matte", "Surface\nCharacter"), ("Indoor/Out", "Usage\nZones")],
        [("◈", "Contemporary Matte Aesthetic",   "A non-glossy, satin-smooth surface that works beautifully in minimalist, Scandinavian, Japandi, and modern Indian design schemes. Calm and sophisticated."),
         ("◇", "Superior Wet Slip Resistance",   "R10 wet slip resistance — significantly safer than polished stone in bathrooms, wet rooms, kitchen floors, and semi-outdoor covered areas."),
         ("◉", "Scratch-Forgiving Surface",      "Minor scratches and everyday surface wear marks are nearly invisible on a matte honed surface — making it far more practical for long-term high-traffic use."),
         ("✦", "Practical Daily Maintenance",    "Smooth enough for effortless cleaning, yet textured enough to not show every fingerprint, smudge, or water droplet. The most practical finish for everyday living."),
         ("▲", "Versatile Indoor Application",   "Works equally well for flooring, wall cladding panels, bathroom floor tiles, kitchen countertops, and interior stair treads across residential and commercial projects."),
         ("□", "Preserves Natural Colour Depth", "Retains the stone's authentic natural colour tone — not amplified like polished, not concealed like natural. An honest, organic presentation of the stone's palette."),],
        [["Property", "Value", "Standard"],
         ["Finish Classification", "Honed — Satin Matte", "—"],
         ["Gloss Level", "10–25 Gloss Units (GU)", "ASTM C1299"],
         ["Surface Roughness (Ra)", "0.5–1.5 µm", "ISO 4287"],
         ["Slip Rating (Wet)", "R10", "DIN 51130"],
         ["Water Absorption", "< 0.5%", "IS 1124"],
         ["Compressive Strength", "≥ 70 MPa", "IS 1121"],
         ["Available Variants", "Kota Blue & Kota Brown", "—"],
         ["Recommended Environment", "Indoor & Semi-Outdoor", "—"],
         ["Re-honing Interval", "Not typically required", "—"],],
        [CW*0.40, CW*0.38, CW*0.22], ["LEFT","CENTER","CENTER"],
        ["600 × 600 mm  —  Standard Module",
         "600 × 900 mm  —  Large Plank",
         "300 × 600 mm  —  Plank Format",
         "400 × 400 mm  —  Classic Square",
         "Custom Cut    —  Any Dimension"],
        ["10–12 mm  —  Wall Cladding",
         "18–20 mm  —  Standard Flooring",
         "25 mm      —  Heavy Duty Floor",
         "20–25 mm  —  Kitchen Countertop"],
        None,
        [("◈", "Bathrooms & Wet Rooms",          "The R10 wet slip rating, combined with low water absorption and easy cleaning, makes honed Kota Stone the ideal floor and wall tile for all bathroom applications."),
         ("◇", "Living & Dining Rooms",           "Creates a sophisticated, calm aesthetic in open-plan living and dining spaces — perfectly complementing contemporary furniture, neutral colour palettes, and natural materials."),
         ("◉", "Kitchen Floors & Countertops",    "Heat-resistant, easy to clean, and hygienic — the honed surface minimises visible fingerprints, water spots, and cooking residue marks from daily kitchen use."),
         ("✦", "Spas & Wellness Centres",         "The subtle matte finish creates a serene, natural wellness environment — while the R10 slip resistance ensures safe footing on wet spa floors and in hydrotherapy areas."),
         ("▲", "Interior Staircases",             "Better traction than polished finishes makes honed Kota Stone a safer and more practical choice for residential and commercial interior staircases."),
         ("□", "Contemporary Wall Cladding",      "Thin honed panels create refined, minimal feature walls in residential and commercial settings — without the overpowering visual noise of high-gloss polished stone."),],
        CARE_STANDARD,
        "Request free honed finish samples in both Kota Blue and Kota Brown. Our team can advise on the optimal "
        "hone grade (standard 400 grit, fine 800 grit, or high honed 1,200 grit) for your specific project application.",
    ))

    # ── 6. NATURAL FINISH ────────────────────────────────────────
    paths.append(make_product(
        "natural-finish-catalogue.pdf",
        dict(title_lines=["Natural Finish", "Kota Stone"],
             subtitle="Stone as Nature Intended — Raw, Textured & Authentically Beautiful",
             tagline="The most traditional, most anti-slip, and most economical form of Kota Stone. Trusted for outdoor spaces, heritage projects, and industrial floors for centuries.",
             img_name="pathway.jpg",
             cat_type="Surface Finish"),
        "Natural Finish Kota Stone — Finish Catalogue",
        "What is Natural Finish Kota Stone?",
        ["Natural Finish Kota Stone is the stone in its most authentic form — with the original quarried surface "
         "preserved after minimal processing. The stone is cut to dimension and edges are dressed, but the top face "
         "retains its natural undulations, quarry texture, and unique surface variations that give each piece an "
         "organic, one-of-a-kind character that no manufactured tile can replicate.",
         "This is the most traditional and most widely used form of Kota Stone across India, especially for outdoor "
         "applications where its naturally very high anti-slip rating and exceptional all-weather performance are "
         "critical safety and durability requirements. It is the recommended finish for any exposed outdoor surface.",
         "Natural finish is also the most economical option due to minimal processing requirements — making it the "
         "ideal choice for large-scale infrastructure projects, housing schemes, temple construction, educational "
         "institution campuses, and budget-conscious builders who refuse to compromise on material quality."],
        [("R12", "Outdoor Slip\nResistance"), ("Zero", "Processing\nChemicals"),
         ("Most", "Cost-\nEffective"), ("50+", "Year\nService Life")],
        [("◈", "Authentic Quarried Surface",      "The preserved natural texture gives each installation genuine organic character — subtle undulations, natural texture variation, and honest stone character that evolves beautifully with age."),
         ("◇", "Maximum Anti-Slip Performance",   "R12 outdoor slip resistance — the highest rating for any Kota Stone finish. The natural surface undulation provides a truly secure footing in monsoon rain, frost, and wet conditions."),
         ("◉", "All-Weather Durability",          "Handles India's extreme seasonal range — intense monsoon rain, 45°C+ summer heat, and winter frost — without surface degradation, colour fade, spalling, or loss of performance."),
         ("✦", "Most Cost-Effective Option",      "Minimal processing requirements make natural finish the most economical Kota Stone option. Ideal for large-area projects, infrastructure, and volume-sensitive construction budgets."),
         ("▲", "Smallest Environmental Footprint","Zero chemical processing, zero grinding compounds, zero synthetic treatments. The most environmentally responsible form of Kota Stone with the smallest embodied carbon footprint."),
         ("□", "Virtually Zero Maintenance",      "Requires no special sealants, no polishing, no periodic treatments. Occasional sweeping and hosing is all that's needed to maintain natural finish stone in perfect condition for decades."),],
        [["Property", "Value", "Standard"],
         ["Finish Classification", "Natural Quarried Surface", "—"],
         ["Surface Character", "Natural Undulations & Texture", "—"],
         ["Slip Resistance", "R12 (Outdoor)", "DIN 51130"],
         ["Water Absorption", "< 0.5%", "IS 1124"],
         ["Compressive Strength", "≥ 70 MPa", "IS 1121"],
         ["UV Colour Stability", "Excellent — No Fade", "—"],
         ["Frost Resistance", "Class F4", "EN 12371"],
         ["Maintenance Sealer", "Optional — Not Required", "—"],
         ["Recommended Environment", "Outdoor & Industrial", "—"],],
        [CW*0.40, CW*0.38, CW*0.22], ["LEFT","CENTER","CENTER"],
        ["600 × 600 mm  —  Standard Module",
         "300 × 600 mm  —  Plank Format",
         "400 × 400 mm  —  Classic Square",
         "900 × 300 mm  —  Stair Tread",
         "Custom Cut    —  Any Dimension"],
        ["20 mm      —  Standard Outdoor Flooring",
         "25 mm      —  Pathway & Open Terrace",
         "30 mm      —  Parking & Driveway",
         "40–50 mm  —  Stair Treads (Structural)",
         "75 mm      —  Kerb & Coping Stones"],
        None,
        [("◈", "Open Terraces & Rooftops",        "The R12 anti-slip texture and outstanding weather resistance make natural finish Kota Stone the gold standard for exposed rooftop terraces and open sun decks."),
         ("◇", "Garden & Landscape Pathways",     "Creates beautiful, naturalistic garden paths and stepping stone layouts that blend harmoniously with lawns, planted borders, and natural water features."),
         ("◉", "Temples & Heritage Sites",        "The authentic natural surface aligns visually and culturally with traditional Indian sacred architecture. Used in thousands of temples across Rajasthan, Gujarat, and Madhya Pradesh."),
         ("✦", "Industrial & Factory Floors",     "The rough natural texture provides R12 slip resistance in factories, loading docks, chemical processing areas, and storage facilities where wet floor safety is critical."),
         ("▲", "Driveways & Parking Areas",       "At 25–30 mm, natural Kota Stone handles full vehicle loads including cars, SUVs, and light commercial vehicles — with anti-skid grip even on oily or muddy surfaces."),
         ("□", "Government & Institutional",      "Schools, colleges, municipal buildings, government complexes, and public infrastructure rely on natural Kota Stone for its combination of durability, safety, and economy."),],
        [("◈", "Routine Care",    "Sweep regularly with a stiff broom or blow clean with compressed air to remove loose grit. Wash with clean water using a hose or pressure washer 1–2 times per year."),
         ("◇", "Organic Growth",  "In shaded or damp areas, moss and algae may develop over time. Clean with a dilute solution of bleach (1:10) applied by brush, left for 30 minutes, then hosed off thoroughly."),
         ("◉", "Sealing",         "Sealing is optional for natural finish outdoors. If sealing for stain resistance (e.g., on terraces near cooking areas), use a breathable penetrating impregnator only — never a surface film sealer."),
         ("▲", "Joint Care",      "Check and repoint joints every 5–7 years. Use a cement-based mortar for outdoor joints. Ensure proper drainage around the installation to prevent water pooling in joints."),],
        "Natural finish Kota Stone — the most economical, most traditional, and most enduring choice for outdoor and "
        "heritage projects. Request a bulk project quotation with delivery schedule. Free samples available for architects and contractors.",
    ))

    # ── 7. LEATHER FINISH ────────────────────────────────────────
    paths.append(make_product(
        "leather-finish-catalogue.pdf",
        dict(title_lines=["Leather Finish", "Kota Stone"],
             subtitle="Premium Wire-Brushed Texture — R10/R11 Safety Meets Design Excellence",
             tagline="Where sophisticated aesthetics meet practical wet-area safety. The architect's choice for luxury pool surrounds, resort spas, and outdoor entertaining spaces.",
             img_name="pool.jpg",
             cat_type="Surface Finish"),
        "Leather Finish Kota Stone — Finish Catalogue",
        "What is Leather Finish Kota Stone?",
        ["Leather Finish Kota Stone undergoes a specialised wire-brushing process in which rotating steel wire brushes "
         "are drawn across the stone surface under controlled pressure. This abrades the surface at a micro level — "
         "opening the stone's crystalline structure just enough to create a slightly rough, tactile texture that "
         "closely resembles the feel of aged, brushed leather.",
         "The surface occupies a premium middle ground between the smooth sophistication of honed stone and the raw "
         "texture of natural stone. It is neither reflective nor fully matte — it has a subtle, sophisticated sheen "
         "that reveals the stone's depth of colour without the full reflectivity of a polished finish.",
         "The wire-brushing process also has a unique secondary effect: it reveals colour layers within the stone "
         "that are not visible in smoother finishes. Kota Blue leather often reveals deeper cobalt and teal tones "
         "beneath the surface — giving installations a rich, layered visual character that becomes more beautiful "
         "over time as the surface ages gracefully in outdoor conditions."],
        [("R10–R11", "Wet Slip\nRating"), ("UV", "Stable\nOutdoor"), 
         ("Premium", "Tactile\nTexture"), ("Pool", "Safe\nGrade")],
        [("◈", "Premium Tactile Texture",          "The wire-brushed surface has a unique, tactile quality that is pleasant both underfoot and to the touch — creating a sense of artisan craftsmanship and luxury quality in any application."),
         ("◇", "Pool & Wet Area Safety",            "Engineered for high-moisture environments. The micro-texture provides R10/R11 wet slip resistance around pool edges, spa walkways, and water features — dramatically safer than smooth tiles."),
         ("◉", "Enhanced Colour Depth",             "The brushing process reveals deeper colour layers within the stone, creating a richer, more nuanced tonal palette — blue stones reveal deeper teals; brown stones reveal richer ambers."),
         ("✦", "Conceals Surface Wear Naturally",   "The textured surface naturally masks minor surface scratches and everyday wear marks — maintaining a fresh, premium appearance even in high-traffic outdoor environments over many years."),
         ("▲", "UV & Climate Stable",               "The leather finish does not degrade, fade, or change character under intense UV exposure or thermal cycling — perfect for sun-drenched Indian outdoor terraces and pool decks."),
         ("□", "Distinctive Architectural Identity","Gives projects a sophisticated, one-of-a-kind character that sets them apart from standard stone surfaces — increasingly specified by leading architects and landscape designers."),],
        [["Property", "Value", "Standard"],
         ["Finish Classification", "Wire-Brushed Leather", "—"],
         ["Surface Character", "Micro-Textured, Tactile Matte", "—"],
         ["Slip Resistance (Wet)", "R10 – R11", "DIN 51130"],
         ["Water Absorption", "< 0.5%", "IS 1124"],
         ["Compressive Strength", "≥ 70 MPa", "IS 1121"],
         ["UV Colour Stability", "Excellent — No Fade", "—"],
         ["Chlorine Resistance", "Yes — Pool Water Safe", "—"],
         ["Thermal Stability", "Low Expansion Coefficient", "—"],
         ["Recommended Environment", "Pool, Outdoor, Spa, Bathroom", "—"],],
        [CW*0.40, CW*0.38, CW*0.22], ["LEFT","CENTER","CENTER"],
        ["600 × 600 mm  —  Standard Module",
         "600 × 900 mm  —  Large Plank",
         "300 × 600 mm  —  Plank Format",
         "Custom Cut    —  Any Dimension"],
        ["10–12 mm  —  Feature Walls & Facades",
         "20 mm      —  Terrace & Spa Flooring",
         "25 mm      —  Pool Surround (Standard)",
         "30 mm      —  Heavy Outdoor / Driveway"],
        None,
        [("◈", "Pool Surrounds & Decks",           "The safest, most beautiful pool decking material. R10/R11 wet grip prevents slipping accidents. Cool underfoot. Chlorine-resistant. UV-stable for decades of poolside luxury."),
         ("◇", "Resort & Hotel Spas",              "Creates a premium luxury wellness environment — the tactile texture underfoot heightens sensory experience in hydrotherapy rooms, heated pools, and spa relaxation areas."),
         ("◉", "Outdoor Entertaining Terraces",    "UV-stable, non-slip, and architecturally distinctive — the leather finish thrives on exposed terraces, rooftop bars, infinity decks, and alfresco dining areas."),
         ("✦", "Luxury Bathroom Floors",           "Provides a premium spa-like bathroom experience with R11 wet slip resistance and sophisticated tactile character — superior to polished stone in safety and to natural in aesthetics."),
         ("▲", "Boutique Hospitality Venues",      "Resort pool decks, hotel spa terraces, beach club floors, and boutique hospitality outdoor areas rely on leather finish for its unique combination of safety and luxury brand aesthetics."),
         ("□", "Architectural Facades & Walls",    "Leather finish cladding panels create visually interesting, tactile building facades — increasingly used in contrast with smooth polished panels for dramatic architectural effect."),],
        [("◈", "Regular Care",    "Brush loose debris with a stiff outdoor broom. Hose or pressure wash 2–3 times per year. The textured surface naturally resists surface contaminants and is easy to restore with water."),
         ("◇", "Pool Areas",      "Rinse thoroughly with fresh water after chlorine exposure. A mild detergent solution removes sunscreen and oil residue. Avoid high-concentration acid cleaners around pool stone."),
         ("◉", "Sealing",         "For outdoor use, a breathable penetrating impregnator sealer is recommended. Apply once at installation and every 3 years thereafter. This improves oil and organic stain resistance."),
         ("▲", "Moss & Algae",   "In shaded damp outdoor areas, treat organic growth with a dilute bleach solution or specialist biocide. Rinse thoroughly. Regular sun exposure and air flow prevent recurrence."),],
        "Ideal for pool surrounds, resort spas, outdoor terraces, and luxury bathrooms. Request leather finish samples "
        "in both Kota Blue and Kota Brown, or obtain a formal project quotation for your residential or hospitality development.",
    ))

    # ════════════════════════════════════════════════════
    # APPLICATION PDFs
    # ════════════════════════════════════════════════════

    # ── 8. FLOORING ──────────────────────────────────────────────
    paths.append(make_application(
        "application-flooring.pdf",
        dict(title_lines=["Kota Stone Flooring"],
             subtitle="India's #1 Natural Stone Flooring — Durable, Safe & Timeless",
             tagline="Tough enough for industrial facilities, elegant enough for luxury residences. Kota Stone flooring lasts 50+ years with near-zero maintenance — the smart long-term investment.",
             img_name="flooring.jpg",
             cat_type="Application Guide"),
        "Kota Stone Flooring — Application Guide",
        "Why Kota Stone is India's #1 Flooring Material",
        ["For centuries, Kota Stone has been the foundation of Indian construction. From ancient Rajasthani havelis to "
         "modern corporate towers, its unparalleled durability and timeless aesthetic have made it the undisputed "
         "number-one natural stone flooring material across the country — used in more buildings than any other "
         "natural stone, at any price point.",
         "Kota Stone flooring is three times more durable than standard ceramic tiles and costs dramatically less "
         "to maintain over its lifetime. It stays naturally cool in summer (critical in India's climate), requires "
         "no special sealants or chemical treatments, and ages gracefully — developing a beautiful natural patina "
         "that actually improves its appearance over decades of use.",
         "Available in multiple finishes (polished for luxury, honed for contemporary, natural for outdoor), and "
         "multiple thicknesses (18 mm residential to 30 mm industrial), Kota Stone flooring adapts to any design "
         "requirement, any building type, and any budget level while delivering consistent premium quality."],
        [("50+", "Year\nService Life"), ("3×", "More Durable\nThan Ceramics"),
         ("Cool", "Natural Surface\nTemperature"), ("Zero", "Special Maintenance\nRequired")],
        [("◈", "Unmatched Lifetime Durability",   "Installed correctly, Kota Stone flooring can last 50–100 years without replacement. In contrast, ceramic tiles typically require replacement every 15–20 years in high-traffic settings."),
         ("◇", "Naturally Cool Surface",           "Kota Stone's thermal mass keeps it significantly cooler than ceramic tiles, porcelain, or vinyl in Indian summer conditions — a material benefit with real daily comfort impact."),
         ("◉", "Superior Non-Slip Safety",         "The natural surface texture provides excellent slip resistance — particularly valuable in schools, hospitals, government buildings, and public spaces where floor safety is a legal requirement."),
         ("✦", "Zero Special Maintenance",         "Simple sweep and damp mop with any pH-neutral cleaner is all that is required. No special chemicals, periodic sealers, waxes, or treatments — just soap and water for a lifetime of performance."),
         ("▲", "Best Lifecycle Value",             "Lower material cost than marble and granite, combined with minimal maintenance and zero replacement cost, produces the lowest total 50-year lifecycle cost of any premium flooring material."),
         ("□", "Any Scale, Consistent Quality",   "From 100 sq ft residential rooms to 500,000 sq ft airport terminals — we can supply consistent Grade A quality stone at any project scale, with matched colour and finish across all deliveries."),],
        [["Usage Category", "Recommended Finish", "Thickness", "Typical Size"],
         ["Luxury Residential", "Polished or Honed", "18–20 mm", "600×600 or 600×900 mm"],
         ["Standard Residential", "Honed or Natural", "18–20 mm", "600×600 or 400×400 mm"],
         ["Commercial — Offices", "Honed or Natural", "20–25 mm", "600×600 or 600×900 mm"],
         ["Hospitality — Hotels", "Polished or Honed", "20–25 mm", "600×900 or Custom"],
         ["Healthcare Facilities", "Honed or Natural", "20–25 mm", "600×600 mm"],
         ["Educational Institutions", "Natural or Honed", "20–25 mm", "600×600 or 400×400 mm"],
         ["Industrial Floors", "Natural", "25–30 mm", "600×600 mm"],
         ["Parking Areas", "Natural or Flamed", "25–30 mm", "600×600 mm"],
         ["Outdoor Terraces", "Natural or Leather", "25 mm", "600×600 or Custom"],
         ["Wall Cladding", "Any Finish", "10–12 mm", "300×600 or Custom"],],
        [CW*0.25, CW*0.22, CW*0.18, CW*0.35],
        INSTALL_FLOORING,
        [("◈", "Luxury Homes & Villas",            "Living rooms, master bedrooms, entrance foyers, kitchen platforms, and verandas — Kota Stone creates a cohesive, premium aesthetic throughout the entire home."),
         ("◇", "Corporate & Office Spaces",        "Reception lobbies, open office floors, executive corridors, conference rooms — projects professionalism and endures daily heavy foot traffic for decades."),
         ("◉", "Hotels & Resorts",                 "Grand entrance lobbies, restaurant floors, spa areas, guest room corridors — delivers the premium stone aesthetic demanded by hospitality brands at the right price point."),
         ("✦", "Hospitals & Healthcare",           "Hygienic, easy to sanitise, non-slip, and highly durable — meets all requirements for healthcare facility flooring in high-traffic patient circulation zones."),
         ("▲", "Educational Campuses",             "Schools, colleges, and universities across India have trusted Kota Stone flooring for generations. Safe, economical, and easily maintainable across large campus areas."),
         ("□", "Industrial & Warehouse Floors",    "Heavy-load 30 mm industrial Kota Stone handles forklift traffic, heavy machinery standloads, and chemical spills in factories and logistics facilities."),],
        "Get expert guidance, free finish samples, and competitive bulk pricing for your Kota Stone flooring project. "
        "We supply residential, commercial, hospitality, healthcare, and industrial projects pan-India with "
        "consistent Grade A quality and complete delivery documentation.",
    ))

    # ── 9. OUTDOOR ───────────────────────────────────────────────
    paths.append(make_application(
        "application-outdoor.pdf",
        dict(title_lines=["Kota Stone Outdoor", "Pathways & Driveways"],
             subtitle="All-Weather Safety · Zero Maintenance · Natural Beauty",
             tagline="Naturally non-slip in monsoon rain. Zero maintenance for decades. Genuinely beautiful in any landscape. Kota Stone outdoor pathways outlast every alternative at a lower total cost.",
             img_name="pathway.jpg",
             cat_type="Application Guide"),
        "Kota Stone Outdoor Pathways — Application Guide",
        "The Outdoor Flooring Material Built for India's Climate",
        ["Outdoor pathways, terraces, and driveways face the most demanding conditions in any construction project. "
         "They must simultaneously withstand India's extreme monsoon rainfall, intense summer heat above 45°C, "
         "winter temperature drops in northern regions, vehicle loads, constant foot traffic, and biological growth "
         "— while remaining safe, functional, and beautiful year after year, decade after decade.",
         "Natural finish Kota Stone meets all of these requirements with no compromises and no special treatments. "
         "Its slightly rough natural surface provides R12 anti-slip grip in all weather conditions — the highest "
         "rating achievable in natural stone — eliminating the dangerous slip hazard created by polished or glazed "
         "surfaces when wet from rain or irrigation.",
         "With proper installation on a sand-cement or concrete bed, Kota Stone outdoor pathways require virtually "
         "zero maintenance for their entire 50+ year service life. No resealing, no repainting, no anti-slip coating "
         "applications, no periodic treatments of any kind — just occasional hosing to remove accumulated dirt."],
        [("R12", "Monsoon Slip\nResistance"), ("50+", "Year Service\nLife"),
         ("Zero", "Periodic\nMaintenance"), ("Low", "Total Lifecycle\nCost")],
        [("◈", "All-Weather Durability",           "Handles India's full seasonal range — extreme monsoon rainfall, 45°C+ summer heat, coastal salt air, and winter frost in northern regions — without cracking, spalling, or performance loss."),
         ("◇", "R12 Slip Resistance",              "Natural finish Kota Stone achieves R12 slip resistance (the maximum DIN 51130 outdoor classification) — ensuring completely safe footing even on sloped paths in torrential monsoon rain."),
         ("◉", "Vehicle Load Capacity",            "30 mm thick Kota Stone on a proper concrete substrate withstands full car and light commercial vehicle traffic on driveways and paved forecourts without cracking or differential settlement."),
         ("✦", "Blends with Natural Surroundings", "The natural stone aesthetic, warm colours, and organic texture integrate harmoniously with garden planting, water features, and natural landscape — far more than concrete pavers ever can."),
         ("▲", "Zero Maintenance Required",        "Unlike timber decking (yearly oiling), stamped concrete (periodic sealing), or patterned pavers (joint maintenance), natural Kota Stone outdoor surfaces require no periodic treatment whatsoever."),
         ("□", "Lowest Long-Term Cost",            "Lower material and installation cost than most premium alternatives, with zero maintenance cost over a 50+ year service life, produces the lowest total lifetime cost of any outdoor paving material."),],
        [["Specification", "Standard Grade", "Heavy Duty Grade"],
         ["Thickness", "20 mm", "25–30 mm"],
         ["Recommended Finish", "Natural", "Natural or Flamed"],
         ["Slip Resistance", "R11", "R12"],
         ["Compressive Strength", "≥ 70 MPa", "≥ 70 MPa"],
         ["Substrate / Bed", "50 mm Sand-Cement", "75–100 mm Concrete"],
         ["Joint Width", "3–5 mm", "5–8 mm (Grouted)"],
         ["Vehicle Load Capacity", "Pedestrian Only", "Cars & Light Vehicles"],
         ["Sealer Required", "No", "No"],],
        [CW*0.30, CW*0.35, CW*0.35],
        None,
        [("◈", "Residential Gardens & Landscapes", "Kota Stone stepping paths, garden walkways, and stepping stone layouts blend seamlessly with lawns, planted borders, and water features in private residential gardens."),
         ("◇", "Driveways & Entrance Forecourts",  "30 mm Kota Stone on a reinforced concrete substrate handles residential car traffic with ease — creating a premium first impression at the entrance to any home or estate."),
         ("◉", "Temple & Heritage Walkways",       "Thousands of temples across India have used Kota Stone as their pathway material for generations — spiritually appropriate, traditionally authentic, and structurally enduring."),
         ("✦", "Commercial & Institutional",       "Corporate campuses, retail parks, school campuses, and government building approaches use Kota Stone pathways for their combination of durability, safety, and low collective maintenance."),
         ("▲", "Public Pedestrian Infrastructure", "Municipal corporations, urban planners, and NHAI use Kota Stone for public walkways, heritage district paving, and pedestrian zone surfacing across Indian cities."),
         ("□", "Resort & Hotel Grounds",           "Luxury resorts, wellness retreats, and boutique hotels use Kota Stone pathway networks throughout their grounds to create a seamless, natural aesthetic complementing the landscape."),],
        "Get expert pathway design guidance and competitive bulk pricing for your outdoor Kota Stone project. "
        "Free samples and site visit consultation available for large projects. Pan-India supply and delivery.",
    ))

    # ── 10. WALL CLADDING ────────────────────────────────────────
    paths.append(make_application(
        "application-wall.pdf",
        dict(title_lines=["Kota Stone Wall Cladding"],
             subtitle="Architectural Stone Panels for Interior & Exterior Walls",
             tagline="Transform ordinary walls into architectural statements. Natural stone texture, depth, and warmth — in lightweight 10–12 mm panels suitable for any wall surface.",
             img_name="wall.jpg",
             cat_type="Application Guide"),
        "Kota Stone Wall Cladding — Application Guide",
        "Kota Stone Wall Cladding — Architectural Stone for Every Surface",
        ["Kota Stone wall cladding transforms ordinary walls into permanent architectural statements. Cut into "
         "lightweight 10–12 mm thin slab panels, Kota Stone can be applied to interior and exterior walls using "
         "standard tile adhesive — creating dramatic visual effects that range from sleek contemporary feature "
         "walls to richly textured rustic facade treatments.",
         "The natural blue-green and brown tones of Kota Stone bring warmth, depth, and organic beauty to "
         "spaces that would otherwise feel cold or clinical. In high-end hospitality design, corporate architecture, "
         "luxury retail, and premium residential interiors, Kota Stone cladding instantly signals quality, "
         "permanence, and premium brand positioning.",
         "On building exteriors, Kota Stone cladding serves a dual function — enhancing the building's "
         "aesthetic character while simultaneously providing weather protection and thermal insulation. "
         "The dense limestone panels act as a protective skin that improves the thermal performance of the "
         "underlying wall structure and extends the building's exterior maintenance intervals significantly."],
        [("10–12 mm", "Panel\nThickness"), ("Any", "Wall\nSurface"), 
         ("Inside/Out", "Interior &\nExterior"), ("Dual", "Aesthetic &\nProtective")],
        [("◈", "Architectural Focal Points",        "Stone cladding instantly transforms a plain wall into the architectural focal point of any room — commanding attention and communicating permanence, quality, and premium design intent."),
         ("◇", "Lightweight Thin Panels",           "At 10–12 mm thickness and 26–32 kg/m², the panels are structurally much lighter than full-thickness stone — suitable for lightweight walls, upper floors, and retrofitting existing buildings."),
         ("◉", "Thermal Insulation Benefit",        "Applied to exterior facades, Kota Stone panels provide meaningful thermal mass that moderates daily temperature swings — reducing building heating and cooling loads by 8–12% in Indian conditions."),
         ("✦", "Weather & Moisture Barrier",        "Kota Stone's low porosity (<0.5% absorption) makes it resistant to moisture penetration, salt attack, biological growth, and UV degradation on external building facades."),
         ("▲", "Full Finish Range",                 "All six surface finishes are available for cladding — from mirror-polished feature walls and contemporary honed panels to rustic natural and tactile leather surfaces."),
         ("□", "Simple Installation System",        "Applied with standard C2 flexible tile adhesive using the same installation method as large-format ceramic tiles — accessible to any experienced tiling contractor."),],
        [["Specification", "Value", "Notes"],
         ["Panel Thickness", "10–12 mm", "Standard cladding panels"],
         ["Panel Weight", "26–32 kg/m²", "Structural check for upper floors"],
         ["Standard Panel Sizes", "300×600 mm", "Custom lengths available"],
         ["Available Finishes", "All Six Finishes", "Polished to Sandblasted"],
         ["Adhesive Type", "C2 Flexible Tile Adhesive", "BS EN 12004 compliant"],
         ["Joint Width — Interior", "2–3 mm", "Matching grout colour"],
         ["Joint Width — Exterior", "3–5 mm", "Flexible weatherproof grout"],
         ["Frost Resistance", "Yes — Class F4", "External use approved"],
         ["Sealer (Interior)", "Optional — Penetrating", "For stain-prone areas"],
         ["Sealer (Exterior)", "Recommended — Breathable", "Annual inspection advised"],],
        [CW*0.30, CW*0.35, CW*0.35],
        None,
        [("◈", "Residential Feature Walls",         "Behind sofas, at bed heads, in dining rooms, and in entrance foyers — Kota Stone feature walls create the most dramatic interior focal points available to residential designers."),
         ("◇", "Hospitality & Restaurant Design",   "Hotel lobby walls, restaurant interiors, bar back panels, and boutique hotel corridors — Kota Stone cladding creates a distinctive, memorable spatial character for hospitality venues."),
         ("◉", "Commercial Building Facades",       "Office building exterior cladding in natural Kota Stone projects a prestigious, architecturally considered image that outlasts paint or render by decades with minimal maintenance."),
         ("✦", "Luxury Retail Environments",        "Premium retail flagship stores, jewellery boutiques, and luxury brand showrooms use Kota Stone cladding as a brand signature — communicating quality, durability, and premium positioning."),
         ("▲", "Heritage & Government Facades",     "Government buildings, educational institutions, civic facilities, and heritage conservation projects specify Kota Stone cladding for authentic character and minimal lifetime maintenance cost."),
         ("□", "Bathroom & Spa Interior Walls",     "Full-height Kota Stone wall cladding in bathrooms and spas creates a luxurious wellness environment — cool to the touch, naturally moisture-resistant, and organically beautiful."),],
        "Request free cladding panel samples in the finish and stone variant of your choice. Our technical team "
        "can provide CAD drawings, fixing specifications, adhesive recommendations, and project support for "
        "interior and exterior cladding installations of any scale.",
    ))

    # ── 11. POOL ─────────────────────────────────────────────────
    paths.append(make_application(
        "application-pool.pdf",
        dict(title_lines=["Kota Stone Pool Surrounds"],
             subtitle="India's Safest & Most Beautiful Pool Decking Material",
             tagline="Anti-slip when wet. Cool underfoot in summer. Chlorine-resistant. UV-stable. Visually stunning. Kota Stone is the only pool decking material that compromises nothing.",
             img_name="pool.jpg",
             cat_type="Application Guide"),
        "Kota Stone Pool Surrounds — Application Guide",
        "The Complete Pool Decking Solution — No Compromises",
        ["Pool surrounds are one of the most demanding surface environments in any construction project. The "
         "material must simultaneously deliver excellent slip resistance when continuously wet, stay comfortable "
         "underfoot in direct sunlight above 45°C, resist chlorine and pool chemical attack, remain UV-stable "
         "for decades without colour change, and look beautiful in an outdoor setting. Very few materials "
         "meet all of these requirements. Kota Stone meets every single one.",
         "Natural and leather finish Kota Stone achieves R10–R12 wet slip resistance — the highest safety "
         "rating achievable for pool environments — dramatically reducing the risk of slipping accidents at pool "
         "edges, steps, and wet walkways. This compares directly with polished granite or marble (R9 or below), "
         "which become genuinely dangerous surfaces when wet.",
         "Kota Stone also exhibits a critical thermal comfort advantage — its light colour and lower thermal "
         "conductivity keep the surface measurably cooler than dark natural stones, dark pavers, or standard "
         "ceramic pool tiles in direct Indian summer sunlight. Barefoot comfort around the pool on a peak summer "
         "day is a fundamental luxury — and Kota Stone delivers it naturally."],
        [("R10–R12", "Pool-Safe Wet\nSlip Rating"), ("Cool", "Underfoot in\nSummer Sun"),
         ("Chlorine", "Chemical\nResistant"), ("UV", "Colour\nStable")],
        [("◈", "R10–R12 Wet Slip Resistance",       "The maximum wet slip resistance classification. Maintains safe grip even under continuous water splash from pool jets, rain, and barefoot wet traffic around pool edges."),
         ("◇", "Thermally Cool Underfoot",           "Kota Stone's light colour and lower thermal mass keep the surface significantly cooler than granite, dark marble, or dark-coloured ceramic tiles in direct Indian summer sunlight."),
         ("◉", "Full Chlorine Resistance",           "Completely unaffected by pool water chemistry, chlorine splash, salt chlorination systems, and common pool treatment chemicals — maintains colour and structural integrity indefinitely."),
         ("✦", "Proven UV Colour Stability",         "The natural stone colour does not fade, bleach, or shift tonally under sustained UV exposure — maintaining the same rich blue-green or brown tones for decades of poolside service."),
         ("▲", "Natural Aesthetic Excellence",       "The organic stone texture and natural colour palette complement pool water beautifully — creating the resort-like luxury atmosphere that ceramic tiles, pavers, and coatings simply cannot match."),
         ("□", "Low Cleaning Maintenance",           "Resists algae and mould growth when properly sealed with a penetrating impregnator. Simple pressure washing maintains a pristine pool deck appearance — no specialist cleaning products needed."),],
        [["Pool Specification", "Natural Finish", "Leather Finish"],
         ["Slip Resistance (Wet)", "R11–R12", "R10–R11"],
         ["Thermal Comfort", "Excellent", "Excellent"],
         ["Recommended Thickness", "25 mm", "25 mm"],
         ["Chlorine Resistance", "Excellent", "Excellent"],
         ["UV Stability", "Excellent", "Excellent"],
         ["Maintenance Level", "Low", "Low"],
         ["Best For", "Lap pools, public pools", "Luxury pools, resort spas"],
         ["Sealer Recommended", "Yes — Penetrating", "Yes — Penetrating"],
         ["Joint Grout", "Flexible Pool Grout", "Flexible Pool Grout"],],
        [CW*0.30, CW*0.35, CW*0.35],
        None,
        [("◈", "Luxury Residential Pool Decks",     "Villa and bungalow private swimming pools — creating a luxury resort aesthetic in private homes with natural Kota Stone surrounds that age beautifully."),
         ("◇", "5-Star Resort & Hotel Pool Decks",  "Premium resorts and boutique hotels use Kota Stone pool surrounds for the natural, organic luxury aesthetic that complements high-end hospitality landscaping and pool design."),
         ("◉", "Apartment & Society Pools",         "Apartment complex club house pools benefit from Kota Stone's exceptional durability and very low collective maintenance requirements — ideal for shared facilities with high daily usage."),
         ("✦", "Spa & Wellness Pools",              "Hydrotherapy pools, heated relaxation pools, hot tubs, and spa wet areas — Kota Stone creates a premium natural wellness environment that synthetic materials cannot replicate."),
         ("▲", "Sports & Athletic Pools",           "Olympic training facilities, fitness club pools, and water sports centres need the extreme durability, slip safety, and easy maintenance of natural Kota Stone around high-use pools."),
         ("□", "Water Features & Ornamental Pools", "Garden reflecting pools, ornamental fountains, koi ponds, and water feature surrounds — Kota Stone creates stunning natural focal points in any landscape design."),],
        "Specify Kota Stone pool surrounds for your residential, resort, or commercial swimming pool project. "
        "We supply anti-slip natural and leather finish Kota Stone with full technical documentation including "
        "DIN 51130 slip resistance test certificates. Free samples and competitive bulk pricing available.",
    ))

    # ── 12. STAIRS ───────────────────────────────────────────────
    paths.append(make_application(
        "application-stairs.pdf",
        dict(title_lines=["Kota Stone Staircases"],
             subtitle="Structural Strength · Natural Safety · Enduring Architecture",
             tagline="Built for a lifetime of confident use. Kota Stone stair treads and risers combine 70+ MPa structural strength with natural anti-slip grip and enduring aesthetic beauty.",
             img_name="kota_blue.jpg",
             cat_type="Application Guide"),
        "Kota Stone Staircases — Application Guide",
        "Kota Stone Staircases — Built to Last the Lifetime of the Building",
        ["Staircases are among the highest-stress elements in any building — subjected to continuous concentrated "
         "point loads at nosing zones, heavy repetitive foot impact, edge abrasion, and the structural demand of "
         "spanning across a void or cantilever. Materials that perform well in these conditions are rare. Kota "
         "Stone, with its exceptional 70+ MPa compressive strength and inherent resistance to edge chipping, "
         "has been the proven material of choice for Indian staircases for centuries.",
         "Kota Stone stair treads are specified at 40–50 mm structural slab thickness — providing the structural "
         "depth required to safely span across a stair nosing without risk of cracking, flexure failure, or "
         "chipping at the leading edge under concentrated heel impact. At this thickness, Kota Stone treads "
         "comfortably meet and exceed all structural staircase requirements in the National Building Code of India.",
         "Beyond structural performance, Kota Stone staircases are chosen by architects for their natural "
         "beauty and enduring aesthetic quality. The distinctive blue-green or warm brown natural stone creates "
         "a staircase element that becomes a architectural feature — complementing premium interior design "
         "across residential, hospitality, and institutional building types."],
        [("70+ MPa", "Compressive\nStrength"), ("40–50 mm", "Structural Tread\nThickness"),
         ("R10–R11", "Anti-Slip\nTraction"), ("Lifetime", "Service\nDuration")],
        [("◈", "Exceptional Structural Strength",   "70+ MPa compressive strength means tread slabs do not crack, split, or deflect under concentrated point loads at nosing zones — even in the highest-traffic commercial staircase applications."),
         ("◇", "Natural Anti-Slip Grip",            "All finishes except mirror-polished provide R10–R11 anti-slip traction on stair treads — naturally meeting and exceeding Indian NBC staircase safety requirements without applied coatings."),
         ("◉", "No Edge Chipping",                  "The dense, fine-grained limestone matrix resists edge chipping at nosing zones under repetitive heel impact — a critical requirement that inferior materials fail to meet over time."),
         ("✦", "Structural Lifetime Serviceability","Unlike timber stairs that warp and loosen, or ceramic tile treads that crack and detach, Kota Stone stair treads maintain their structural integrity and surface condition indefinitely."),
         ("▲", "Architectural Beauty",              "The distinctive natural stone creates staircase elements of genuine architectural quality — complementing luxury interior design and contributing to the building's long-term character."),
         ("□", "Zero Maintenance",                  "Sweep and damp mop only. No polishing, staining, periodic sealing, or retreatment required. Treads can be spot-reground and re-honed on-site if required in the future."),],
        [["Component", "Specification", "Notes"],
         ["Tread Thickness", "40–50 mm", "Structural slab — resists nosing impact"],
         ["Riser Thickness", "20–25 mm", "Vertical face panel"],
         ["Standard Tread Length", "900 mm", "Custom lengths available"],
         ["Standard Tread Depth", "300 mm", "Up to 450 mm on request"],
         ["Recommended Tread Finish", "Honed or Natural", "R10–R11 for safe grip"],
         ["Riser Finish", "Polished or Honed", "Contrast or matching to tread"],
         ["Nosing Profile", "Bullnose, Square, or Chamfered", "As per architect spec"],
         ["Slip Resistance", "R10 – R11", "DIN 51130 (Honed/Natural)"],
         ["Compressive Strength", "≥ 70 MPa", "IS 1121"],
         ["Installation Method", "Full Mortar Bed", "Minimum 25 mm bed"],
         ["Available Variants", "Kota Blue & Kota Brown", "Both in stock"],],
        [CW*0.28, CW*0.35, CW*0.37],
        None,
        [("◈", "Luxury Residential Staircases",     "Grand entrance staircases, internal floor-to-floor staircases, and external approach steps in premium homes and villas — where structural performance meets interior design quality."),
         ("◇", "Hotel & Resort Grand Staircases",   "Sweeping hotel entrance and lobby staircases in polished or honed Kota Blue are a signature architectural element in premium hospitality design across India."),
         ("◉", "Corporate & Commercial Buildings",  "Internal fire escapes, reception-area feature staircases, and mezzanine steps all benefit from Kota Stone's combination of durability, safety, and professional aesthetic."),
         ("✦", "Educational Institutions",          "Schools, colleges, and universities across India have trusted Kota Stone stair treads for generations — safe for children, durable under extreme foot traffic, and easily maintained."),
         ("▲", "Healthcare & Hospital Staircases",  "Non-slip, easy to sanitise, chemical-resistant, and structurally proven under heavy use — Kota Stone stair treads exceed all healthcare facility safety and hygiene requirements."),
         ("□", "Heritage & Temple Staircases",      "Natural Kota Stone steps on temple plinths, haveli entrances, heritage building approaches, and institutional steps carry traditional authenticity and structural longevity."),],
        "Premium Kota Stone stair treads and risers — structurally proven to 70+ MPa, naturally anti-slip to R10–R11, "
        "and architecturally beautiful in both Kota Blue and Kota Brown. Free samples available. Bulk project pricing "
        "provided within 24 hours of enquiry.",
    ))

    # ── 13. KITCHEN ──────────────────────────────────────────────
    paths.append(make_application(
        "application-kitchen.pdf",
        dict(title_lines=["Kota Stone Kitchen", "Applications"],
             subtitle="Heat-Resistant · Hygienic · Scratch-Resistant · Naturally Beautiful",
             tagline="The kitchen demands more from a surface material than any other room. Kota Stone meets every demand — heat, impact, moisture, acids, and daily abrasion — naturally and permanently.",
             img_name="kitchen.jpg",
             cat_type="Application Guide"),
        "Kota Stone Kitchen Applications — Application Guide",
        "Why Kota Stone Excels in the Most Demanding Room in the Home",
        ["The kitchen is the most demanding surface environment in any building. Every day, kitchen surfaces "
         "face direct heat from pots and pans, acidic food spills, mechanical impacts, sharp blade contact, "
         "constant moisture, and cleaning chemicals. Kota Stone's unique physical properties — dense natural "
         "matrix, 70+ MPa strength, Mohs 4 hardness, and sub-0.5% water absorption — make it an outstanding "
         "natural material choice for kitchen countertops and flooring.",
         "Unlike ceramic tiles that chip and crack at grout lines, or engineered stone that can delaminate "
         "over time, Kota Stone is a single-material solid stone slab with no adhesives, resins, or synthetic "
         "binders. Its structural integrity is uniform throughout — meaning there is no subsurface layer to "
         "fail, delaminate, or separate regardless of the surface conditions it faces.",
         "Kota Stone kitchen countertops and floors develop a beautiful character patina with daily use — "
         "becoming progressively richer and more distinguished in appearance over years of use, rather than "
         "simply wearing out and looking tired like manufactured surface materials. This is the quality of "
         "material that becomes better with age."],
        [("300°C", "Heat\nResistance"), ("Mohs 4", "Scratch\nHardness"),
         ("Hygienic", "Food Safe\nSurface"), ("50+", "Year\nLifetime")],
        [("◈", "Withstands Direct Heat",             "Handles temperatures up to 300°C without cracking, surface discolouration, or structural damage. Hot pots, pans, and baking trays placed directly from hob or oven cause no harm."),
         ("◇", "Inherently Hygienic & Food-Safe",    "The dense, low-porosity surface does not harbour bacteria in microscopic surface pores. Sealed correctly, Kota Stone countertops are inherently hygienic for food contact and preparation surfaces."),
         ("◉", "Superior Scratch Resistance",        "Mohs hardness of 4 means Kota Stone countertops resist ordinary knife cuts and kitchen utensil abrasion that permanently mark softer stone and all manufactured surface materials."),
         ("✦", "Stain-Resistant When Sealed",        "A single application of penetrating stone sealer at installation dramatically reduces stain absorption risk from cooking oils, curries, wine, coffee, and coloured kitchen liquids."),
         ("▲", "Minimal Cleaning Effort",            "Wipe clean with a damp cloth and any mild pH-neutral kitchen cleaner. No specialist products, no weekly treatments, no periodic re-sealing needed — simple care for a lifetime of performance."),
         ("□", "Outstanding Cost Advantage",         "Delivers natural stone aesthetics and kitchen performance at 30–50% of the cost of premium granite, imported quartz, or marble countertops — with a longer service life than all of them."),],
        [["Kitchen Application", "Recommended Finish", "Thickness", "Notes"],
         ["Kitchen Countertops", "Honed (preferred)", "20–25 mm", "Matte finish hides fingerprints"],
         ["Countertops — Luxury", "Polished", "20–25 mm", "High-gloss premium aesthetic"],
         ["Kitchen Floor", "Honed or Natural", "20 mm", "R10 slip rating for safety"],
         ["Splashback Panels", "Polished or Honed", "10–12 mm", "Easy clean surface"],
         ["Outdoor Kitchen", "Natural or Leather", "25 mm", "Weather and UV resistant"],
         ["Commercial Kitchen", "Natural", "25–30 mm", "Heavy-duty, max slip safety"],
         ["Open-Plan Dining Floor", "Honed or Polished", "20 mm", "Match to kitchen flooring"],],
        [CW*0.27, CW*0.24, CW*0.18, CW*0.31],
        None,
        [("◈", "Kitchen Countertops & Worktops",     "Primary application — honed or polished Kota Stone countertops that handle daily cooking impact, cutting board use, and all food preparation activities with ease."),
         ("◇", "Kitchen Floor Tiles",                "Honed or natural finish Kota Stone kitchen floors are naturally cool underfoot, non-slip (R10), and completely impervious to cooking grease, food spills, and cleaning chemicals."),
         ("◉", "Splashback & Wall Panels",           "10–12 mm thin Kota Stone panels behind the hob and sink protect walls from moisture and heat splash, and add a premium, distinctive natural stone aesthetic to the kitchen backdrop."),
         ("✦", "Open Kitchen & Dining Floors",       "Extending Kota Stone continuously from the kitchen floor area through to the open-plan dining space creates a seamless, premium aesthetic throughout the combined living area."),
         ("▲", "Outdoor & Alfresco Kitchens",        "Natural or leather finish Kota Stone handles India's outdoor conditions perfectly — ideal for open-air kitchen counters, BBQ surrounds, outdoor bar tops, and garden cooking areas."),
         ("□", "Restaurant & Commercial Kitchens",   "Restaurant back-of-house floors, food processing facilities, and institutional kitchens rely on natural Kota Stone for its combination of slip safety, chemical resistance, and easy industrial cleaning."),],
        "Request free Kota Stone kitchen countertop and floor tile samples. Get a project-specific quote for "
        "your modular kitchen renovation, new kitchen construction, or commercial kitchen flooring project. "
        "Available in honed, polished, and natural finishes for kitchen applications.",
    ))

    # ── 14. PARKING ──────────────────────────────────────────────
    paths.append(make_application(
        "application-parking.pdf",
        dict(title_lines=["Kota Stone Parking Tiles"],
             subtitle="India's Most Trusted Natural Stone for Parking & Driveways",
             tagline="Heavy-load rated. Anti-skid on wet and oily surfaces. Oil and chemical resistant. Virtually indestructible under vehicle traffic. Zero maintenance for 25+ years.",
             img_name="kota_brown.jpg",
             cat_type="Application Guide"),
        "Kota Stone Parking Tiles — Application Guide",
        "The Undisputed Choice for Indian Parking Infrastructure",
        ["Parking surfaces face some of the most demanding conditions of any flooring application — heavy "
         "dynamic axle loads from multiple vehicles, continuous oil and fuel spillage, constant surface "
         "abrasion, monsoon water exposure, and chemical attack from brake fluid, engine degreaser, and "
         "washing detergents. Kota Stone meets all of these challenges simultaneously without any compromise.",
         "At 25–30 mm thickness and 70+ MPa compressive strength, Kota Stone parking tiles support "
         "full vehicle loads from cars and SUVs right through to light commercial vehicles, delivery trucks, "
         "and warehouse forklifts — without cracking, surface spalling, or differential settlement — "
         "when correctly installed over a reinforced concrete substrate.",
         "Unlike concrete pavers that crack under dynamic load cycles, ceramic parking tiles that shatter "
         "under vehicle impact, or epoxy coatings that chip, peel, and require periodic reapplication, "
         "properly installed Kota Stone parking tiles require only occasional hosing for their entire 25+ "
         "year service life. The total cost advantage over alternative materials is substantial."],
        [("70+ MPa", "Load-Bearing\nStrength"), ("25+", "Year Service\nLife"),
         ("Anti-Skid", "Oil & Wet\nSurfaces"), ("Zero", "Periodic\nMaintenance")],
        [("◈", "Heavy Vehicle Load Capacity",       "70+ MPa compressive strength at 25–30 mm thickness safely supports the dynamic load cycles from cars, SUVs, trucks, and forklifts — without cracking or surface distress under repeated loading."),
         ("◇", "Natural Anti-Skid on All Surfaces", "Natural and flamed finish Kota Stone provides excellent friction coefficient on wet, oily, muddy, and clean surfaces — no anti-slip treatment coatings required at installation or maintenance."),
         ("◉", "Oil & Chemical Resistance",         "The dense, low-absorption stone matrix resists oil, diesel, grease, brake fluid, antifreeze, washing detergents, and all common parking area chemicals without staining or structural attack."),
         ("✦", "Total Monsoon Weather Resistance",  "Sub-0.5% water absorption prevents water penetration and frost heave damage. Unaffected by standing water pooling during monsoon season — unlike clay pavers or concrete surfaces."),
         ("▲", "Zero Maintenance Service Life",     "Properly installed Kota Stone parking tiles require only periodic water washing for their entire 25+ year service life — producing a dramatically lower total ownership cost than any alternative."),
         ("□", "Cost-Optimal Infrastructure Choice","Lower material cost than stone alternatives, zero coating replacement cycles, and a 25+ year service life without rehabilitation produce the most cost-effective parking infrastructure investment."),],
        [["Specification", "Residential/Light Duty", "Commercial Heavy Duty"],
         ["Stone Thickness", "25 mm", "30–40 mm"],
         ["Concrete Substrate", "75 mm M20 PCC", "100–150 mm M25 RCC"],
         ["Compressive Strength", "≥ 70 MPa", "≥ 70 MPa"],
         ["Recommended Finish", "Natural", "Natural or Flamed"],
         ["Slip Resistance", "R11", "R12"],
         ["Joint Width", "5 mm", "8–10 mm"],
         ["Joint Fill", "Cement Mortar", "Polymer-Modified Mortar"],
         ["Max Vehicle Load", "2.5 tonnes axle", "8+ tonnes axle"],
         ["Sealer Recommended", "No", "No"],],
        [CW*0.30, CW*0.35, CW*0.35],
        None,
        [("◈", "Commercial Parking Complexes",      "Shopping malls, office parks, multiplexes, and mixed-use commercial developments — high-volume daily traffic across hundreds of vehicles requiring maximum durability and zero maintenance."),
         ("◇", "Industrial & Logistics Facilities", "Factory yards, logistics hub aprons, and warehouse loading bays where forklifts and heavy vehicles require 30–40 mm industrial-grade Kota Stone on reinforced concrete."),
         ("◉", "Luxury Residential Driveways",      "Villa and bungalow driveways — durable, permanently anti-skid, and visually premium. Creates a sophisticated first impression at the entrance to any premium home."),
         ("✦", "Hotel & Resort Entrance Zones",     "Hotel porte-cochère areas, valet parking approach roads, and resort entrance driveways where the parking surface must match the luxury standard of the property."),
         ("▲", "Institutional & Campus Parking",    "Hospital parking facilities with ambulance access and heavy delivery vehicle traffic, school and college campus parking — demanding durability, safety, and long-term economy."),
         ("□", "Government Infrastructure",         "Municipal corporation parking, government building approaches, airport surface roads, and defence establishment parking — where Kota Stone's proven performance record is critical."),],
        "Bulk supply of Kota Stone parking tiles in any quantity, custom sizing, and pan-India delivery with "
        "logistics coordination. Get a project quotation for your residential driveway, commercial parking "
        "complex, or industrial vehicle area within 24 hours of enquiry.",
    ))

    # ── 15. INDUSTRIAL ───────────────────────────────────────────
    paths.append(make_application(
        "application-industrial.pdf",
        dict(title_lines=["Kota Stone Industrial", "Flooring"],
             subtitle="India's Most Durable Industrial Floor Material",
             tagline="70+ MPa strength. R12 slip resistance. Chemical resistant. Frost stable. No replacement cycle. Kota Stone industrial flooring lasts the entire lifetime of the building.",
             img_name="kota_brown.jpg",
             cat_type="Application Guide"),
        "Kota Stone Industrial Flooring — Application Guide",
        "Industrial-Grade Kota Stone — Proven for Over a Century in Indian Facilities",
        ["Industrial flooring is subjected to conditions that rapidly destroy most materials — heavy dynamic "
         "machinery loads, fork truck impact, chemical spills, temperature extremes from -30°C cold stores "
         "to 200°C+ process environments, constant surface abrasion from wheeled traffic, and aggressive "
         "cleaning regimes. Kota Stone, with its exceptional 70+ MPa compressive strength and extremely "
         "low porosity, has been the flooring material of choice for Indian industrial facilities for "
         "well over a century.",
         "Unlike epoxy floor coatings that chip, delaminate, and require full replacement every 5–7 years, "
         "or concrete floors that surface-dust, crack, and harbour contamination in surface pores, Kota Stone "
         "industrial flooring maintains its complete structural integrity and surface quality indefinitely "
         "under continuous heavy industrial use. There is no coating to fail, no surface layer to degrade — "
         "the stone is the floor, all the way through.",
         "Available in 25–30 mm heavy-duty thickness with natural or flamed finish for maximum R12 slip "
         "resistance, Kota Stone is the only industrial flooring solution that combines proven structural "
         "performance with absolute zero maintenance cost throughout the building's operational life."],
        [("70+ MPa", "Compressive\nStrength"), ("R12", "Industrial Slip\nRating"),
         ("Zero", "Replacement\nCycle"), ("Lifetime", "Service\nDuration")],
        [("◈", "Extreme Load Bearing Capacity",     "30 mm Kota Stone on 100 mm RCC substrate safely withstands forklift dynamic loads, heavy machinery point loads, and stacked pallet storage — with no cracking or surface distress."),
         ("◇", "R12 Industrial Slip Safety",        "Natural and flamed finish provide R12 slip resistance — critical for mandatory worker safety compliance in wet process areas, chemical facilities, and food processing environments."),
         ("◉", "Broad Chemical Resistance",         "Resistant to dilute acids, alkalis, oils, greases, diesel, industrial solvents, and most chemical compounds encountered in manufacturing, processing, and storage facility environments."),
         ("✦", "Industrial Cleaning Compatible",    "Can be pressure washed, steam cleaned, scrubbed with industrial detergents, and hosed down repeatedly without any surface degradation — unlike epoxy or polyurethane coated floors."),
         ("▲", "No Replacement Cycle",              "Epoxy coatings require complete strip-and-recoat every 5–7 years (major operational disruption and cost). A correctly installed Kota Stone floor requires no rehabilitation for the building's life."),
         ("□", "Cold Storage Compatible",           "Frost-resistant to Class F4, Kota Stone performs in freeze-thaw cycling conditions inside cold storage facilities and refrigerated warehouses where thermal shock destroys most flooring materials."),],
        [["Specification", "Standard Industrial", "Heavy-Duty Industrial"],
         ["Stone Thickness", "25 mm", "30–40 mm"],
         ["RCC Substrate", "100 mm M25", "150 mm M30"],
         ["Compressive Strength", "≥ 70 MPa", "≥ 70 MPa"],
         ["Recommended Finish", "Natural", "Natural or Flamed"],
         ["Slip Resistance", "R11–R12", "R12"],
         ["Chemical Resistance", "Good to Excellent", "Excellent"],
         ["Frost/Cold Store", "Class F4 — Yes", "Class F4 — Yes"],
         ["Joint Fill", "Epoxy Mortar", "Epoxy Mortar (Flexible)"],
         ["Maintenance Required", "Hose down only", "Hose down only"],],
        [CW*0.30, CW*0.35, CW*0.35],
        None,
        [("◈", "Manufacturing Factories",            "Automobile, textile, pharmaceutical, FMCG, and engineering manufacturing plant primary floor areas — where heavy machinery, fork truck traffic, and chemical exposure demand the best."),
         ("◇", "Warehouses & Logistics Centres",    "Storage and distribution centre floors where continuous forklift traffic, heavy pallet rack loads, and large vehicle movements require structural floor slabs that never need rehabilitation."),
         ("◉", "Cold Storage & Refrigeration",      "Frost-resistant Kota Stone withstands the freeze-thaw thermal cycling inside refrigerated warehouses, cold stores, and blast-freezing facilities where most floor materials fail."),
         ("✦", "Food Processing Plants",            "Meets the hygiene and durability requirements for food processing environments — chemical resistant, easy to pressure wash and sanitise, and smooth enough for FSSC 22000 compliance."),
         ("▲", "Chemical & Pharmaceutical Plants",  "Chemical resistance and structural durability make Kota Stone the industrial floor specification for chemical manufacturing process areas, pharmaceutical production, and laboratory facilities."),
         ("□", "Government & Defence Infrastructure","Military facilities, government depots, ordnance warehouses, defence vehicle yards, and public infrastructure projects where proven long-term performance and zero maintenance are mandatory."),],
        "Get a competitive bulk quotation for industrial Kota Stone flooring for your facility. We supply "
        "and deliver pan-India with complete technical documentation including IS test certificates, "
        "installation specifications, and quality assurance documentation for large-scale industrial projects.",
    ))

    print(f"\n  ✅  All {len(paths)} PDFs complete.\n")
    for p in paths:
        kb = os.path.getsize(p) / 1024
        print(f"     {os.path.basename(p):52s}  {kb:6.0f} KB")
    return paths


if __name__ == "__main__":
    run_all()