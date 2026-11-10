#!/usr/bin/env python3
"""Generate the README visuals for dsh-ota-review-check.

Outputs (all under docs/assets/, idempotent overwrite):

  dsh-ota-review-check-hero-zh-light.webp   1440x576  Pillow poster
  dsh-ota-review-check-hero-zh-dark.webp
  dsh-ota-review-check-hero-en-light.webp
  dsh-ota-review-check-hero-en-dark.webp
  dsh-ota-review-check-flow-v5-light.svg    1100x660  hand-written SVG
  dsh-ota-review-check-flow-v5-dark.svg

Hero -- the register's first row as a seven-column strip. The two cells that
are blank in samples/quickstart/input/OT-001-unsafe.json (总分 / 点评内容) are
ringed in amber and resolve into the one finding the tool really returns
(`OT-001` · warn · 第 1 行 · content), while `OT-006` -- whose category
vocabulary ships empty -- is drawn as the dashed `skipped` slip instead of
being hidden. The chips repeat the real run: warn 1 · info 0 · error 0 ·
skipped 1 (samples/quickstart/expected/result.json).

Flow -- grammar = ANNOTATED LEDGER ROW (nested dimension lines over one row),
not a row of five boxes and not a rule x field matrix. The row carries the nine
canonical columns a rule actually reads (`渠道` / `房型` are read by no check and
are therefore not drawn). Each of the seven rules is a dimension line clamped
onto the cell(s) its `params.check` block names: `presenceAny` (OT-001),
`conditionalPresence` (OT-002), `date` x2 (OT-003, OT-004), `presence` (OT-005),
`enum` (OT-006), `unique` (OT-007, the only across-row check -- hence the
vertical brace over the ghost second row). Amber = severity capped at `warn`
(kind: derived-from-principle); blue = capped at `info` (kind:
institutional-configuration); dashed = declared but not runnable today, because
`values: []` ships empty -> `skipped[]`. One solid arrow leaves the two blank
cells for `issues[]`; the dashed probe leaves the issueType cell for
`skipped[]`. Every string is a repo token (rule id, canonical field, status,
alias) or a value from the quickstart fixture; nothing is invented.

The SVG is language-neutral (English + the register's own tokens), so one
light/dark pair serves all five README languages.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + the Microsoft YaHei / Consolas fonts that ship with
           Windows; the SVG is plain text.
"""
from __future__ import annotations

import math
import os
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# ---------------------------------------------------------------------------
# fonts
# ---------------------------------------------------------------------------
FONT_CANDIDATES = {
    "sans": [r"C:\Windows\Fonts\msyh.ttc",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
             "/System/Library/Fonts/PingFang.ttc"],
    "sans_bold": [r"C:\Windows\Fonts\msyhbd.ttc",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                  "/System/Library/Fonts/PingFang.ttc"],
    "mono": [r"C:\Windows\Fonts\consola.ttf",
             r"C:\Windows\Fonts\cour.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
             "/System/Library/Fonts/Menlo.ttc"],
}
FONT_PATH = {}
for _key, _paths in FONT_CANDIDATES.items():
    _found = next((p for p in _paths if os.path.exists(p)), None)
    if _found is None:
        sys.exit(f"FATAL: no font for {_key!r}; looked for {_paths}. "
                 "Refusing to render tofu boxes.")
    FONT_PATH[_key] = _found

_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(size: int, kind: str = "sans") -> ImageFont.FreeTypeFont:
    key = (kind, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_PATH[kind], size, index=0)
    return _cache[key]


_measure_draw = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def has_cjk(text: str) -> bool:
    """Consolas carries no CJK: such a string is measured and drawn in YaHei."""
    for ch in text:
        code = ord(ch)
        if (0x2E80 <= code <= 0x9FFF or 0x3040 <= code <= 0x30FF
                or 0xF900 <= code <= 0xFAFF or 0xFF00 <= code <= 0xFFEF):
            return True
    return False


def text_width(text: str, size: float, bold: bool = False,
               mono: bool = False) -> float:
    kind = "mono" if mono and not has_cjk(text) else (
        "sans_bold" if bold else "sans")
    return _measure_draw.textlength(text, font=font(round(size), kind))


def assert_fit(text: str, size: float, limit: float, *, bold=False, mono=False,
               where: str = "") -> float:
    """Fail loudly instead of shipping a clipped / overflowing label."""
    width = text_width(text, size, bold, mono)
    if width > limit:
        raise SystemExit(
            f"FATAL: text overflows in {where or '?'} "
            f"({width:.0f}px > {limit:.0f}px at {size}px): {text!r}")
    return width


def fit_size(text: str, limit: float, start: float, floor: float, *,
             bold=False, mono=False) -> float:
    size = float(start)
    while size > floor and text_width(text, size, bold, mono) > limit:
        size -= 0.5
    if text_width(text, size, bold, mono) > limit:
        raise SystemExit(f"FATAL: cannot fit {text!r} into {limit}px "
                         f"(floor {floor}px)")
    return size


# ---------------------------------------------------------------------------
# palette -- family accent #4B67B4 (dark: #8496f5), GitHub-safe page grounds
# ---------------------------------------------------------------------------
THEMES = {
    "light": dict(
        bg_top=(249, 246, 253), bg_bottom=(228, 234, 248),
        ink=(24, 29, 45), ink2=(66, 78, 104), muted=(104, 116, 142),
        faint=(146, 156, 178),
        surface=(255, 255, 255), surface_alt=(244, 247, 253),
        border=(213, 220, 240), grid=(224, 229, 243),
        family=(75, 103, 180), family_soft=(232, 238, 252),
        ok=(26, 130, 92), warn=(168, 112, 24), hot=(186, 66, 44),
        violet=(102, 76, 184), info=(52, 92, 184), teal=(15, 118, 110),
        shadow=(38, 50, 92),
    ),
    "dark": dict(
        bg_top=(19, 26, 42), bg_bottom=(12, 16, 22),
        ink=(238, 242, 255), ink2=(178, 189, 214), muted=(146, 158, 186),
        faint=(112, 124, 152),
        surface=(23, 31, 48), surface_alt=(19, 26, 41),
        border=(43, 54, 82), grid=(35, 45, 68),
        family=(132, 150, 245), family_soft=(35, 45, 74),
        ok=(84, 214, 165), warn=(226, 179, 74), hot=(240, 138, 93),
        violet=(180, 158, 246), info=(122, 162, 247), teal=(94, 210, 198),
        shadow=(0, 0, 0),
    ),
}


def mix(rgb, other, ratio):
    return tuple(round(rgb[i] + (other[i] - rgb[i]) * ratio) for i in range(3))


def over(rgb, theme, alpha):
    """Flatten `rgb` against the theme surface for alpha-style fills."""
    return mix(theme["surface"], rgb, alpha)


# ---------------------------------------------------------------------------
# drawing surface with supersampling
# ---------------------------------------------------------------------------
class Sheet:
    """2x supersampled RGBA canvas; every coordinate is in final pixels."""

    def __init__(self, width: int, height: int, theme: dict, ss: int = 2):
        self.w, self.h, self.ss, self.t = width, height, ss, theme
        base = Image.new("RGB", (1, 2))
        base.putpixel((0, 0), theme["bg_top"])
        base.putpixel((0, 1), theme["bg_bottom"])
        self.img = base.resize((width * ss, height * ss),
                               Image.BILINEAR).convert("RGBA")
        self.d = ImageDraw.Draw(self.img)

    def _box(self, box):
        s = self.ss
        return [round(v * s) for v in box]

    def rounded(self, box, radius, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self._box(box), radius=radius * self.ss,
                                 fill=fill, outline=outline,
                                 width=max(1, round(width * self.ss)))

    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle(self._box(box), fill=fill, outline=outline,
                         width=max(1, round(width * self.ss)))

    def line(self, xy, fill, width=1):
        s = self.ss
        self.d.line([(round(xy[0] * s), round(xy[1] * s)),
                     (round(xy[2] * s), round(xy[3] * s))],
                    fill=fill, width=max(1, round(width * s)))

    def dashed_line(self, x1, y1, x2, y2, fill, width=1.5, dash=5, gap=5):
        length = math.hypot(x2 - x1, y2 - y1)
        if length <= 0:
            return
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0.0
        while pos < length:
            end = min(pos + dash, length)
            self.line((x1 + ux * pos, y1 + uy * pos,
                       x1 + ux * end, y1 + uy * end), fill, width)
            pos += dash + gap

    def dashed_rounded(self, box, radius, outline, width=1.4, dash=6, gap=5):
        """Dashed rounded outline, drawn as four dashed edges + soft corners."""
        x0, y0, x1, y1 = box
        inset = radius / 2
        self.dashed_line(x0 + inset, y0, x1 - inset, y0, outline, width,
                         dash, gap)
        self.dashed_line(x0 + inset, y1, x1 - inset, y1, outline, width,
                         dash, gap)
        self.dashed_line(x0, y0 + inset, x0, y1 - inset, outline, width,
                         dash, gap)
        self.dashed_line(x1, y0 + inset, x1, y1 - inset, outline, width,
                         dash, gap)

    def dot(self, cx, cy, r, fill):
        s = self.ss
        self.d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s,
                        (cy + r) * s], fill=fill)

    def text(self, xy, s, size, fill, *, bold=False, mono=False, anchor="ls"):
        kind = "mono" if mono and not has_cjk(s) else (
            "sans_bold" if bold else "sans")
        self.d.text((xy[0] * self.ss, xy[1] * self.ss), s,
                    font=font(round(size * self.ss), kind),
                    fill=fill, anchor=anchor)

    def shadow(self, box, radius, dy=14, blur=26, alpha=34):
        s = self.ss
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        b = self._box((box[0], box[1] + dy, box[2], box[3] + dy))
        ld.rounded_rectangle(b, radius=radius * s,
                             fill=self.t["shadow"] + (alpha,))
        layer = layer.filter(ImageFilter.GaussianBlur(blur * s))
        self.img.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.img)

    def glow(self, cx, cy, radius, color, alpha):
        s = self.ss
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse([(cx - radius) * s, (cy - radius) * s,
                    (cx + radius) * s, (cy + radius) * s],
                   fill=color + (alpha,))
        layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55 * s))
        self.img.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.img)

    def save(self, path):
        out = self.img.resize((self.w, self.h), Image.LANCZOS)
        out.convert("RGB").save(path, "WEBP", quality=94, method=6)


# ---------------------------------------------------------------------------
# hero content -- the register row and the run both come from the quickstart
# ---------------------------------------------------------------------------
HERO_W, HERO_H = 1440, 576

# samples/quickstart/input/OT-001-unsafe.json -- first (only) row.
# (column alias zh, alias en), canonical field, cell width, value
HERO_COLS = [
    (("序号", "No."), "reviewNo", 62, "1"),
    (("入住日期", "Check-in"), "checkIn", 112, "2026-03-01"),
    (("总分", "Score"), "score", 62, ""),
    (("点评内容", "Review text"), "content", 118, ""),
    (("是否回复", "Replied"), "replyStatus", 86, "是"),
    (("回复日期", "Reply date"), "repliedAt", 112, "2026-03-02"),
    (("回复人", "Reply by"), "replier", 100, "张店长"),
]

HERO_COPY = {
    "zh": dict(
        kicker="CHECKER · 在线点评回复台账",
        title="点评台账核对",
        value=("把点评回复台账核成一份差异清单",
               "哪一行、哪一栏、差什么，逐条指认"),
        sub="7 条规则 · 不联网 · 不调用模型 · 不改原件",
        meta="级别随依据封顶 · 未执行检查进 skipped · 空结果 ≠ 没问题",
        footer="dsh-ota-review-check · Apache-2.0 · DSH ≥0.2.1 <0.3.0",
        panel_title="台账第 1 行 → 逐栏判定",
        panel_meta="ota_review_check · ruleset 2026.1",
        empty_tag="空",
        finding_tag="OT-001 · warn · 第 1 行 · content",
        finding_found="content、score 都为空",
        finding_expected="依据：content、score 至少应填写一项",
        skip_tag="OT-006 · skipped",
        skip_body="分类词表出厂为空 → 本条未执行",
        chip_warn="warn 1", chip_info="info 0", chip_error="error 0",
        chip_skip="skipped 1",
        panel_note="每条发现都写明「哪一行、哪一栏」",
        rules_note="7 条规则 · 2026.1",
    ),
    "en": dict(
        kicker="CHECKER · OTA REVIEW REGISTER",
        title="OTA reply audit",
        value=("Audit a review-reply register line by line",
               "Which row, which column, what is missing"),
        sub="7 rules · no network · no model call · read-only",
        meta="Severity capped by evidence · skipped is always reported",
        footer="dsh-ota-review-check · Apache-2.0 · DSH ≥0.2.1 <0.3.0",
        panel_title="Row 1 → verdict per column",
        panel_meta="ota_review_check · ruleset 2026.1",
        empty_tag="empty",
        finding_tag="OT-001 · warn · row 1 · content",
        finding_found="content and score are both empty",
        finding_expected="expected: content or score, at least one",
        skip_tag="OT-006 · skipped",
        skip_body="category vocabulary ships empty → not run",
        chip_warn="warn 1", chip_info="info 0", chip_error="error 0",
        chip_skip="skipped 1",
        panel_note="every finding names its row and its column",
        rules_note="7 rules · 2026.1",
    ),
}

# hero geometry (final pixels)
LX = 72                        # left column x
PANEL = (700, 62, 1408, 522)   # right panel box
PX0, PY0, PX1, PY1 = PANEL


def hero(lang: str, theme_name: str) -> Sheet:
    c = HERO_COPY[lang]
    t = THEMES[theme_name]
    zh = lang == "zh"
    s = Sheet(HERO_W, HERO_H, t)

    s.glow(1170, 150, 300, t["family"], 26 if theme_name == "light" else 34)
    s.glow(320, 470, 260, t["violet"], 14 if theme_name == "light" else 18)

    # ---- left column: kicker / title / two value lines / sub / meta ----
    pill_text = c["kicker"]
    psize = fit_size(pill_text, 330, 17, 14, bold=True)
    pw = text_width(pill_text, psize, bold=True) + 54
    s.rounded((LX, 74, LX + pw, 116), 21, fill=over(t["family"], t, 0.10),
              outline=over(t["family"], t, 0.40), width=1.2)
    s.dot(LX + 23, 95, 3.6, t["family"])
    s.text((LX + 38, 95), pill_text, psize, t["family"], bold=True, anchor="lm")

    tsize = fit_size(c["title"], 560, 88, 48, bold=True)
    s.text((LX, 232), c["title"], tsize, t["ink"], bold=True)

    v1, v2 = c["value"]
    vsize = min(fit_size(v1, 628, 27, 22),
                fit_size(v2, 628, 27, 22))
    s.text((LX, 288), v1, vsize, t["ink2"])
    s.text((LX, 326), v2, vsize, t["ink2"])

    assert_fit(c["sub"], 25, 628, where="hero subtitle")
    s.text((LX, 378), c["sub"], 25, t["muted"])

    s.line((LX, 412, LX + 560, 412), over(t["border"], t, 0.95), width=1.2)
    assert_fit(c["meta"], 20, 628, where="hero meta")
    s.text((LX, 452), c["meta"], 20, t["muted"])

    s.line((LX, 508, LX + 560, 508), over(t["border"], t, 0.95), width=1.2)
    assert_fit(c["footer"], 15.5, 628, where="hero footer")
    s.text((LX, 536), c["footer"], 15.5, t["faint"])

    # ---- right panel: the register row, then the two exits --------------
    s.shadow(PANEL, 22, dy=16, blur=28, alpha=42 if theme_name == "light"
             else 130)
    s.rounded(PANEL, 22, fill=t["surface"],
              outline=over(t["border"], t, 0.95), width=1.4)

    il, ir = PX0 + 28, PX1 - 28
    psize = fit_size(c["panel_title"], 330, 18, 15, bold=True)
    s.text((il, 114), c["panel_title"], psize, t["ink"], bold=True)
    s.text((ir, 114), c["panel_meta"], 12.5, t["muted"], mono=True, anchor="rs")
    s.line((il, 130, ir, 130), over(t["border"], t, 0.9), width=1.1)

    # column headers
    x = il + 18
    col_lefts = []
    for (alias, _en), _canon, width, _value in HERO_COLS:
        col_lefts.append(x)
        label = alias if zh else _en
        assert_fit(label, 12.5, width - 16, where=f"hero column {label}")
        s.text((x + 2, 160), label, 12.5, t["muted"])
        x += width

    # the row strip
    row_box = (il, 170, ir, 258)
    s.rounded(row_box, 14, fill=t["surface_alt"],
              outline=over(t["border"], t, 0.95), width=1.2)

    empties = []
    for index, ((alias, _en), canon, width, value) in enumerate(HERO_COLS):
        cx = col_lefts[index]
        if value == "":
            empties.append((cx, width))

    # tint the two blank cells before any text lands on them
    ring = (empties[0][0] + 5, 176, empties[-1][0] + empties[-1][1] - 5, 252)
    s.rounded(ring, 10, fill=over(t["warn"], t, 0.07))

    for index, ((alias, _en), canon, width, value) in enumerate(HERO_COLS):
        cx = col_lefts[index]
        if index:
            s.line((cx, 178, cx, 250), over(t["border"], t, 0.85), width=1.0)
        s.text((cx + 12, 196), canon, 11, t["muted"], mono=True)
        if value == "":
            s.text((cx + 12, 236), c["empty_tag"], 12.5, t["warn"])
        else:
            assert_fit(value, 12.5, width - 20, mono=True,
                       where=f"hero value {canon}")
            s.text((cx + 12, 236), value, 12.5, t["ink"], mono=True)

    # ring the two blank cells (score + content) with one amber caliper
    s.dashed_rounded(ring, 10, over(t["warn"], t, 0.6), width=1.4, dash=7,
                     gap=5)

    # finding card
    card = (il, 274, ir, 366)
    s.rounded(card, 14, fill=over(t["warn"], t, 0.06),
              outline=over(t["warn"], t, 0.38), width=1.2)
    s.rounded((il, 274, il + 5, 366), 2.5, fill=t["warn"])
    assert_fit(c["finding_tag"], 12.5, 560, mono=True, where="hero finding tag")
    s.text((il + 22, 300), c["finding_tag"], 12.5, t["warn"], mono=True,
           bold=True)
    assert_fit(c["finding_found"], 15, 600, where="hero finding found")
    s.text((il + 22, 330), c["finding_found"], 15, t["ink"], bold=True)
    assert_fit(c["finding_expected"], 12.5, 600, where="hero finding expected")
    s.text((il + 22, 354), c["finding_expected"], 12.5, t["muted"])

    # skipped slip (dashed: declared but not executable)
    slip = (il, 380, ir, 428)
    s.rounded(slip, 12, fill=over(t["muted"], t, 0.05))
    s.dashed_rounded(slip, 12, over(t["muted"], t, 0.55), width=1.2)
    s.text((il + 18, 406), c["skip_tag"], 12.5, t["muted"], mono=True,
           bold=True)
    assert_fit(c["skip_body"], 12.5, 350, where="hero skip body")
    s.text((ir - 18, 406), c["skip_body"], 12.5, t["muted"], anchor="rs")

    # summary chips -- the numbers of the real quickstart run
    chips = [(c["chip_warn"], t["warn"]), (c["chip_info"], t["family"]),
             (c["chip_error"], t["muted"]), (c["chip_skip"], t["violet"])]
    cx = il
    for label, color in chips:
        w = text_width(label, 12.5, mono=True) + 26
        s.rounded((cx, 444, cx + w, 476), 16, fill=over(color, t, 0.11),
                  outline=over(color, t, 0.42), width=1.1)
        s.text((cx + 13, 466), label, 12.5, color, mono=True, bold=True)
        cx += w + 10
    s.text((ir, 466), c["rules_note"], 12.5, t["muted"], mono=True, anchor="rs")

    assert_fit(c["panel_note"], 12, 600, where="hero panel note")
    s.text((il, 504), c["panel_note"], 12, t["faint"])
    return s


# ---------------------------------------------------------------------------
# flow SVG -- annotated ledger row, 1100x660
# ---------------------------------------------------------------------------
FLOW_W, FLOW_H = 1100, 660

FLOW_TITLE = "One ledger row · seven annotations · two outlets"
FLOW_SUB = ("Each rule is clamped onto the columns of the same row; a rule that "
            "cannot run reports itself in skipped — never a silent pass.")
FLOW_META = "rules 2026.1 · OT-001..OT-007 · sample 1 row"

ROW_X0, ROW_X1 = 56, 1060
ROW_TOP, ROW_BOT = 360, 440
CELL = (ROW_X1 - ROW_X0) / 9.0


def cell_x(i: int) -> float:
    """Left edge of 1-based cell `i`."""
    return ROW_X0 + (i - 1) * CELL


# (rule, severity colour key, span (first cell, last cell), label tail)
RULE_SPANS = [
    ("OT-001", "warn", (3, 4), "content | score"),
    ("OT-002", "family", (5, 6), "replyStatus → repliedAt"),
    ("OT-005", "family", (8, 8), "replier"),
    ("OT-004", "family", (2, 6), "checkIn ≤ repliedAt"),
    ("OT-003", "family", (2, 7), "checkIn ≤ replyDeadline"),
]

ROW_CELLS = [
    ("序号", "reviewNo", "1"),
    ("入住日期", "checkIn", "2026-03-01"),
    ("总分", "score", ""),
    ("点评内容", "content", ""),
    ("是否回复", "replyStatus", "是"),
    ("回复日期", "repliedAt", "2026-03-02"),
    ("回复期限", "replyDeadline", "2026-03-04"),
    ("回复人", "replier", "张店长"),
    ("问题类型", "issueType", "噪音"),
]

SANS = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
        "'Source Han Sans SC',sans-serif")
MONO = "Consolas,'Cascadia Mono','SFMono-Regular',ui-monospace,monospace"


def hexs(rgb):
    return "#%02x%02x%02x" % tuple(rgb)


def col(value):
    """SVG colour: hex for RGB tuples, pass literal strings through."""
    if isinstance(value, (tuple, list)):
        return hexs(value)
    return value


class Flow:
    def __init__(self, theme_name: str):
        self.t = THEMES[theme_name]
        self.theme_name = theme_name
        self.lines: list[str] = []
        t = self.t
        self.head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{FLOW_W}" '
            f'height="{FLOW_H}" viewBox="0 0 {FLOW_W} {FLOW_H}" '
            f'role="img" aria-labelledby="flowTitle flowDesc">'
            f'<title id="flowTitle">dsh-ota-review-check — annotated ledger '
            f'row</title>'
            f'<desc id="flowDesc">One register row carries the nine canonical '
            f'columns a rule reads. Each of the seven rules is a dimension line '
            f'clamped onto the cells its check block names; amber means the '
            f'severity is capped at warn, blue at info, and the dashed probe '
            f'marks a rule that cannot run because its vocabulary is empty. '
            f'Findings leave for issues[] and unrunnable rules for '
            f'skipped[].</desc>'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{hexs(t["bg_top"])}"/>'
            f'<stop offset="1" stop-color="{hexs(t["bg_bottom"])}"/>'
            f'</linearGradient></defs>'
            f'<rect width="{FLOW_W}" height="{FLOW_H}" rx="20" fill="url(#bg)"/>'
        )

    # -- primitives -------------------------------------------------------
    def rect(self, x, y, w, h, r=0, fill="none", stroke=None, sw=1.2,
             dash=None):
        out = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
               f'height="{h:.1f}"'
               + (f' rx="{r}"' if r else "")
               + f' fill="{col(fill)}"')
        if stroke:
            out += f' stroke="{col(stroke)}" stroke-width="{sw}"'
        if dash:
            out += f' stroke-dasharray="{dash}"'
        return out + "/>"

    def text(self, x, y, s, size, fill, *, bold=False, mono=False,
             anchor="start", opacity=None):
        fam = MONO if (mono and not has_cjk(s)) else SANS
        weight = 700 if bold else 400
        op = f' opacity="{opacity}"' if opacity is not None else ""
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
                f'font-size="{size}" font-weight="{weight}" '
                f'fill="{col(fill)}" text-anchor="{anchor}"{op}>'
                f'{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke, sw=1.4, dash=None,
             opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                f'y2="{y2:.1f}" stroke="{col(stroke)}" stroke-width="{sw}" '
                f'stroke-linecap="round"{d}{op}/>')

    def arrow(self, x1, y1, x2, y2, stroke, sw=1.6, head=5.0, dash=None):
        stroke = col(stroke)
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
        out = [self.line(x1, y1, bx, by, stroke, sw, dash)]
        p2 = (bx - head * 0.55 * math.sin(ang),
              by + head * 0.55 * math.cos(ang))
        p3 = (bx + head * 0.55 * math.sin(ang),
              by - head * 0.55 * math.cos(ang))
        pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in ((x2, y2), p2, p3))
        out.append(f'<polygon points="{pts}" fill="{stroke}"/>')
        return "".join(out)

    # -- composites -------------------------------------------------------
    def card(self, x0, y0, x1, y1, title, title_kind="sans", title_size=13.5):
        t = self.t
        self.lines.append(self.rect(x0, y0, x1 - x0, y1 - y0, 16, t["surface"],
                                    over(t["border"], t, 0.95), 1.3))
        size = title_size
        while size > 11.5 and text_width(
                title, size, bold=True,
                mono=(title_kind == "mono")) > (x1 - x0) - 28:
            size -= 0.5
        self.lines.append(self.text(x0 + 16, y0 + 24, title, size, t["ink"],
                                    bold=True, mono=(title_kind == "mono")))
        self.lines.append(self.line(x0 + 16, y0 + 34, x1 - 16, y0 + 34,
                                    over(t["border"], t, 0.9), 1.0))

    def body(self, x, y, s, color=None, size=12.5):
        self.lines.append(self.text(x, y, s, size,
                                    color if color is not None else self.t["ink2"]))

    def rule_label(self, x, y, rule, tail, color, anchor="start", limit=None):
        """`OT-00N` in mono, then the plain-language tail in the sans face."""
        id_w = text_width(rule, 13, bold=True, mono=True)
        total = id_w + 6 + text_width(tail, 12)
        if limit is not None and total > limit:
            raise SystemExit(f"FATAL: rule label overflows its span "
                             f"({total:.0f}px > {limit:.0f}px): {rule} {tail}")
        if anchor == "end":
            x -= total
        self.lines.append(self.text(x, y, rule, 13, color, bold=True, mono=True))
        self.lines.append(self.text(x + id_w + 6, y, tail, 12,
                                    self.t["muted"]))
        return total

    def dimension(self, first, last, y, color, rule, tail, dashed=False,
                  anchor="start", label_x=None, limit=None):
        """Extension lines + a capped dimension line + the rule label."""
        t = self.t
        a, b = cell_x(first), cell_x(last + 1)
        dash = "5 4" if dashed else None
        faint = over(t["border"], t, 1.0)
        for edge in (a, b):
            self.lines.append(self.line(edge, y, edge, ROW_TOP - 2, faint, 1.1,
                                        dash=dash))
        self.lines.append(self.line(a, y, b, y, color, 1.6, dash=dash))
        for edge in (a, b):
            self.lines.append(self.line(edge, y - 5, edge, y + 5, color, 1.6,
                                        dash=dash))
        lx = label_x if label_x is not None else a + 6
        span = (b - lx - 8) if anchor == "start" else 300
        self.rule_label(lx, y - 11, rule, tail, color, anchor=anchor,
                        limit=limit if limit is not None else span)
        return a, b

    # -- composition ------------------------------------------------------
    def build(self) -> str:
        t = self.t
        L = self.lines
        L.append(self.head)
        ink, ink2, muted, faint = t["ink"], t["ink2"], t["muted"], t["faint"]
        family, warn = t["family"], t["warn"]

        # header ----------------------------------------------------------
        assert_fit(FLOW_TITLE, 26, 700, bold=True, where="flow title")
        assert_fit(FLOW_SUB, 14, 990, where="flow subtitle")
        assert_fit(FLOW_META, 12.5, 360, mono=True, where="flow meta")
        L.append(self.text(40, 52, FLOW_TITLE, 26, ink, bold=True))
        L.append(self.text(40, 76, FLOW_SUB, 14, muted))
        L.append(self.text(1060, 52, FLOW_META, 12.5, muted, mono=True,
                           anchor="end"))

        # inputs ----------------------------------------------------------
        self.card(40, 92, 372, 190, "MATERIAL · JSON / YAML")
        for i, line in enumerate((
                "header: hotel · period · platform · …",
                "rows[] = 1 · 13 canonical column groups",
                "read-only · no network · no model call")):
            assert_fit(line, 12.5, 300, where=f"material line {i}")
            self.body(56, 140 + i * 18, line,
                      ink2 if i < 2 else muted)

        self.card(388, 92, 700, 190, "parseMaterial", title_kind="mono")
        for i, line in enumerate((
                "alias → canonical (13 groups)",
                "case / space / _ / - ignored",
                "列名保留 → 定位写明读的是哪一栏")):
            assert_fit(line, 12.5, 280, where=f"parse line {i}")
            self.body(404, 140 + i * 18, line, ink2 if i < 2 else muted)

        self.card(716, 92, 1060, 190, "rules/ota-review-check.yaml",
                  title_kind="mono")
        for i, line in enumerate((
                "7 rules · 2026.1 · this run: 6 run, 1 skipped",
                "derived → cap warn · config → cap info",
                "excerpt 未取得 → 不伪造引文")):
            assert_fit(line, 12.5, 316, where=f"rules line {i}")
            self.body(732, 140 + i * 18, line, ink2 if i < 2 else muted)

        # material -> parse, then both sources feed the row itself
        L.append(self.arrow(374, 141, 386, 141, over(muted, t, 0.8), sw=1.4,
                            head=3.6))
        feed = over(muted, t, 0.55)
        L.append(self.line(544, 190, 544, 246, feed, 1.2))
        L.append(self.line(888, 190, 888, 246, feed, 1.2))
        L.append(self.line(100, 246, 888, 246, feed, 1.2))
        L.append(self.arrow(100, 246, 100, 354, over(muted, t, 0.85), sw=1.5,
                            head=4.6))

        # annotations: five above the row --------------------------------
        tiers = {"OT-001": 342, "OT-002": 342, "OT-005": 342,
                 "OT-004": 312, "OT-003": 282}
        for rule, color_key, (first, last), tail in RULE_SPANS:
            self.dimension(first, last, tiers[rule], t[color_key], rule, tail)

        # the row: nine canonical columns, the ones a rule reads -----------
        L.append(self.rect(ROW_X0, ROW_TOP, ROW_X1 - ROW_X0, ROW_BOT - ROW_TOP,
                           14, t["surface"], over(t["border"], t, 0.95), 1.4))
        # the two blank cells the one finding comes from (tinted first, so the
        # cell text stays legible on top of the wash)
        blank = (cell_x(3) + 6, 366, cell_x(5) - 6, 434)
        L.append(self.rect(blank[0], blank[1], blank[2] - blank[0],
                           blank[3] - blank[1], 10, over(warn, t, 0.06)))
        for i in range(1, 9):
            L.append(self.line(cell_x(i), 368, cell_x(i), 432,
                               over(t["border"], t, 0.85), 1.0))

        for i, (alias, canon, value) in enumerate(ROW_CELLS):
            x = cell_x(i + 1) + 12
            assert_fit(alias, 13, CELL - 18, where=f"alias {alias}")
            assert_fit(canon, 11, CELL - 18, mono=True,
                       where=f"canonical {canon}")
            L.append(self.text(x, 382, alias, 13, ink2))
            L.append(self.text(x, 402, canon, 11, muted, mono=True))
            if value == "":
                L.append(self.text(x, 426, "空", 12.5, warn, bold=True))
            else:
                assert_fit(value, 12.5, CELL - 18, mono=True,
                           where=f"value {canon}")
                L.append(self.text(x, 426, value, 12.5, ink, mono=True))

        L.append(self.rect(blank[0], blank[1], blank[2] - blank[0],
                           blank[3] - blank[1], 10, "none",
                           over(warn, t, 0.5), 1.3, dash="6 5"))

        # OT-007: the only across-row rule -- a brace over the row + row 2
        brace_x = 46
        L.append(self.line(brace_x, ROW_TOP, brace_x, 496, t["warn"], 1.6))
        for yy in (ROW_TOP, 496):
            L.append(self.line(brace_x, yy, brace_x + 6, yy, t["warn"], 1.6))
        L.append(self.rect(ROW_X0, 448, CELL, 48, 10,
                           over(t["surface_alt"], t, 0.9),
                           over(t["border"], t, 0.9), 1.1, dash="5 4"))
        L.append(self.text(ROW_X0 + 10, 466, "row 2", 11, muted))
        L.append(self.text(ROW_X0 + 10, 486, "1", 12.5, muted, mono=True))
        self.rule_label(176, 470, "OT-007", "reviewNo unique across rows",
                        t["warn"], limit=280)

        # OT-006: declared, but values[] ships empty -> skipped
        ox0, ox1 = cell_x(9), cell_x(9) + CELL
        L.append(self.line(ox0, 440, ox0, 456, over(t["border"], t, 1.0), 1.1,
                           dash="5 4"))
        L.append(self.line(ox1, 440, ox1, 456, over(t["border"], t, 1.0), 1.1,
                           dash="5 4"))
        L.append(self.line(ox0, 456, ox1, 456, over(muted, t, 0.8), 1.4,
                           dash="5 4"))
        for edge in (ox0, ox1):
            L.append(self.line(edge, 451, edge, 461, over(muted, t, 0.8), 1.4,
                               dash="5 4"))
        self.rule_label(ox0 - 12, 474, "OT-006", "issueType in values[]",
                        over(muted, t, 0.95), anchor="end", limit=300)

        # exits ------------------------------------------------------------
        L.append(self.arrow(445, 446, 445, 512, over(muted, t, 0.9), sw=1.7,
                            head=5.0))
        L.append(self.arrow(ox0 + CELL / 2, 456, ox0 + CELL / 2, 512,
                            over(muted, t, 0.8), sw=1.4, head=4.4,
                            dash="5 4"))

        self.card(40, 516, 660, 616, "issues[] · each finding is locatable")
        issues = (
            ("{ row: 1, column: content } · OT-001 · warn", 12.5, warn),
            ("found · expected · basis · fix — never a verdict", 13, ink2),
            ("id = plugin + rule + locator hash → allow-list key", 13, muted),
        )
        for i, (line, size, color) in enumerate(issues):
            assert_fit(line, size, 580, mono=(i == 0), where=f"issues {i}")
            L.append(self.text(56, 568 + i * 20, line, size, color,
                               mono=(i == 0)))

        self.card(680, 516, 1060, 616, "skipped[] · never a silent pass")
        skips = (
            ("values = [] → cannot run, reason kept", 12.5, t["violet"]),
            ("OT-002 no matching row · OT-003 no deadline", 13, ink2),
            ("an empty list never means nothing is wrong", 13, muted),
        )
        for i, (line, size, color) in enumerate(skips):
            assert_fit(line, size, 344, where=f"skipped {i}")
            L.append(self.text(696, 568 + i * 20, line, size, color))

        # legend -----------------------------------------------------------
        legend1 = ("amber = severity capped at warn (derived-from-principle) · "
                   "blue = capped at info (institutional-configuration)")
        legend2 = ("dashed = declared but not runnable today (values: []) · no "
                   "network, no model call · the report carries the disclaimer")
        assert_fit(legend1, 12, 1020, where="legend 1")
        assert_fit(legend2, 12, 1020, where="legend 2")
        L.append(self.text(40, 636, legend1, 12, muted))
        L.append(self.text(40, 652, legend2, 12, faint))

        L.append("</svg>")
        return "\n".join(L) + "\n"


def flow_svg(theme_name: str) -> str:
    return Flow(theme_name).build()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
LEGACY = ("dsh-ota-review-check-flow-light.svg",
          "dsh-ota-review-check-flow-dark.svg",
          "dsh-ota-review-check-flow.svg")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    written = []
    for lang in ("zh", "en"):
        for theme in ("light", "dark"):
            name = f"dsh-ota-review-check-hero-{lang}-{theme}.webp"
            hero(lang, theme).save(os.path.join(OUT, name))
            written.append(name)
    for theme in ("light", "dark"):
        name = f"dsh-ota-review-check-flow-v5-{theme}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(theme))
        written.append(name)
    for legacy in LEGACY:
        path = os.path.join(OUT, legacy)
        if os.path.exists(path):
            os.remove(path)
            print(f"removed legacy {legacy}")
    print("wrote " + ", ".join(written))


if __name__ == "__main__":
    main()
