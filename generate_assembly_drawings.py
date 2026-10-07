#!/usr/bin/env python3
"""
Генератор сборочных чертежей узлов шасси (листы 07-13). Вся геометрия берется
из chassis_geometry.py — после правки координат перезапустить этот скрипт.

07 — Угол подвески в сборе (единый на 4 колеса)
08 — Адаптер верхнего шарнира и рулевого рычага АД-01 на кулак 2108
09 — Передний подрамник, кинематика (развал / подруливание)
10 — Рулевое управление: трапеция, рейка, колонка
11 — Силовой модуль: QS138 -> цепь 520 -> КПП 2108 -> приводы
12 — Тормозная система и педальный узел
13 — Типовые кронштейны, крепеж, моменты затяжки
"""
import math
import os

import chassis_geometry as g

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drawings")

ACC, GRN, AMB, TXT, MUT, RED, VIO = "#38bdf8", "#10b981", "#f59e0b", "#f8fafc", "#94a3b8", "#f87171", "#a78bfa"
STEEL, DARK, PANEL, BG = "#64748b", "#334155", "#1e293b", "#0f172a"


# =========================================================================
# SVG-примитивы
# =========================================================================
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    return f"{v:.1f}"


def text(x, y, s, size=12, color=TXT, anchor="start", weight="normal", rot=None):
    tr = f' transform="rotate({f(rot)},{f(x)},{f(y)})"' if rot else ""
    return (f'<text x="{f(x)}" y="{f(y)}" fill="{color}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{tr}>{esc(s)}</text>')


def line(p1, p2, color=TXT, w=1.5, dash=None, cap="round", op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op < 1 else ""
    return (f'<line x1="{f(p1[0])}" y1="{f(p1[1])}" x2="{f(p2[0])}" y2="{f(p2[1])}" stroke="{color}" '
            f'stroke-width="{f(w)}" stroke-linecap="{cap}"{d}{o}/>')


def poly(pts, fill="none", stroke=TXT, w=1.5, op=1.0, dash=None, closed=True):
    tag = "polygon" if closed else "polyline"
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts_s = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    return (f'<{tag} points="{pts_s}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
            f'stroke-width="{f(w)}" stroke-linejoin="round"{d}/>')


def rect(x, y, w, h, fill=DARK, stroke=MUT, sw=1.5, rx=0, op=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{f(min(x, x + w))}" y="{f(min(y, y + h))}" width="{f(abs(w))}" height="{f(abs(h))}" '
            f'rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def circ(c, r, fill=DARK, stroke=MUT, w=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{d}/>'


def dim(p1, p2, label, off=18, color=ACC, size=12):
    """Линейный размер между p1 и p2 (px) со смещением off перпендикулярно."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / ln * off, dx / ln * off
    a, b = (p1[0] + nx, p1[1] + ny), (p2[0] + nx, p2[1] + ny)
    ext = 4 if off >= 0 else -4
    e1 = (p1[0] + nx + ext * nx / (abs(off) or 1), p1[1] + ny + ext * ny / (abs(off) or 1))
    e2 = (p2[0] + nx + ext * nx / (abs(off) or 1), p2[1] + ny + ext * ny / (abs(off) or 1))
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    tx, ty = mx + (nx / (abs(off) or 1)) * 5, my + (ny / (abs(off) or 1)) * 5
    return "".join([
        line(p1, e1, color, 0.8, "3,2"), line(p2, e2, color, 0.8, "3,2"),
        f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{color}" stroke-width="1.2" '
        f'marker-start="url(#arr)" marker-end="url(#arr)"/>',
        f'<text x="{f(tx)}" y="{f(ty)}" fill="{color}" font-size="{size}" font-weight="bold" text-anchor="middle" '
        f'transform="rotate({f(ang)},{f(tx)},{f(ty)})" dominant-baseline="{"auto" if off <= 0 else "hanging"}">'
        f'{esc(label)}</text>',
    ])


def leader(p, t, label, color=TXT, size=11, anchor="start"):
    return (line(p, t, MUT, 0.9) + circ(p, 2.2, MUT, MUT, 0) +
            text(t[0] + (4 if anchor == "start" else -4), t[1] + 4, label, size, color, anchor))


def note_box(x, y, w, title, lines, color=ACC, size=11, lh=17):
    h = 34 + lh * len(lines)
    out = [rect(x, y, w, h, PANEL, STEEL, 1, 4), text(x + 12, y + 22, title, 13, color, weight="bold")]
    for i, s in enumerate(lines):
        c = TXT
        if s.startswith("!"):
            s, c = s[1:], RED
        elif s.startswith("~"):
            s, c = s[1:], MUT
        out.append(text(x + 12, y + 42 + i * lh, s, size, c))
    return "".join(out), h


def table(x, y, widths, header, rows, size=11, lh=18, color=ACC):
    w = sum(widths)
    out = [rect(x, y, w, lh * (len(rows) + 1) + 6, PANEL, STEEL, 1, 3)]
    cx = x
    for i, hd in enumerate(header):
        out.append(text(cx + 6, y + 14, hd, size, color, weight="bold"))
        cx += widths[i]
    out.append(line((x, y + lh + 2), (x + w, y + lh + 2), STEEL, 1))
    for r, row in enumerate(rows):
        cx = x
        for i, cell in enumerate(row):
            out.append(text(cx + 6, y + lh * (r + 2) - 2, cell, size, TXT if i else MUT))
            cx += widths[i]
    return "".join(out), lh * (len(rows) + 1) + 6


def spring(p1, p2, coils=9, width=26, color=AMB):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    nx, ny = -uy, ux
    pts = [p1]
    n = coils * 2
    for i in range(1, n):
        t = i / n
        s = width / 2 * (1 if i % 2 else -1)
        pts.append((p1[0] + dx * t + nx * s, p1[1] + dy * t + ny * s))
    pts.append(p2)
    return poly(pts, "none", color, 2, closed=False)


def plot(x, y, w, h, series, xr, yr, xt, yt, xlabel, ylabel, title):
    def px(v): return x + (v - xr[0]) / (xr[1] - xr[0]) * w
    def py(v): return y + h - (v - yr[0]) / (yr[1] - yr[0]) * h
    out = [rect(x - 50, y - 34, w + 70, h + 76, PANEL, STEEL, 1, 4),
           text(x - 38, y - 14, title, 13, ACC, weight="bold")]
    for v in yt:
        out.append(line((x, py(v)), (x + w, py(v)), DARK, 1))
        out.append(text(x - 6, py(v) + 4, f"{v:+g}" if v else "0", 10, MUT, "end"))
    for v in xt:
        out.append(line((px(v), y), (px(v), y + h), DARK, 1))
        out.append(text(px(v), y + h + 14, f"{v:+g}" if v else "0", 10, MUT, "middle"))
    out.append(line((x, py(0)), (x + w, py(0)), STEEL, 1.2))
    out.append(line((px(0), y), (px(0), y + h), STEEL, 1.2))
    for i, (xs, ys, color, label) in enumerate(series):
        out.append(poly([(px(a), py(b)) for a, b in zip(xs, ys)], "none", color, 2.2, closed=False))
        out.append(text(x + 8, y + 14 + i * 15, label, 10, color))
    out.append(text(x + w, y + h + 30, xlabel, 10, MUT, "end"))
    out.append(text(x - 38, y + h / 2, ylabel, 10, MUT, "middle", rot=-90))
    return "".join(out)


class View:
    """Проекция мм -> px. Y мм направлен вверх, на листе — вниз."""
    def __init__(self, ox, oy, s, flip_y=True):
        self.ox, self.oy, self.s, self.fy = ox, oy, s, flip_y

    def __call__(self, x, y):
        return (self.ox + x * self.s, self.oy - y * self.s if self.fy else self.oy + y * self.s)

    def p(self, pt):
        return self(*pt)

    def L(self, mm):
        return mm * self.s


def sheet(code, title, subtitle, node, material, scale, body, sheet_no):
    stamp = f"""
  <g transform="translate(980, 812)">
    <rect width="380" height="104" fill="{PANEL}" stroke="{ACC}" stroke-width="1.5"/>
    <line x1="0" y1="34" x2="380" y2="34" stroke="{STEEL}"/><line x1="0" y1="68" x2="380" y2="68" stroke="{STEEL}"/>
    <line x1="90" y1="0" x2="90" y2="104" stroke="{STEEL}"/>
    {text(12, 22, "Узел:", 12, MUT)}{text(100, 22, node, 13, TXT, weight="bold")}
    {text(12, 56, "Материал:", 12, MUT)}{text(100, 56, material, 12, TXT)}
    {text(12, 90, "Чертеж:", 12, MUT)}{text(100, 90, f"{code} / {scale} / лист {sheet_no}", 12, ACC)}
  </g>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950" style="background:{BG}; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="{PANEL}" stroke-width="0.8"/>
    </pattern>
    <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="8" stroke="{STEEL}" stroke-width="1.5"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{ACC}"/>
    </marker>
    <marker id="flow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="{BG}"/>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  <rect x="20" y="20" width="1360" height="910" fill="none" stroke="{ACC}" stroke-width="2"/>
  {text(50, 62, title, 22, ACC, weight="bold")}
  {text(50, 88, subtitle, 14, MUT)}
{body}
{stamp}
</svg>"""


def write(name, content):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Чертеж сохранен: {path}")


# =========================================================================
# Общие элементы угла подвески (вид спереди, правый борт)
# =========================================================================
def draw_corner(v, detail=True, mirror=1):
    """Возвращает SVG угла подвески в виде View v. mirror=-1 — левый борт."""
    def P(x, y):
        return v(mirror * x, y)
    o = []
    hw = g.TIRE_WIDTH / 2
    R = g.WHEEL_RADIUS_STATIC
    # Шина в разрезе: прямоугольник, затем «вырезаем» обод
    x0, x1 = sorted((P(g.HALF_TRACK - hw, 0)[0], P(g.HALF_TRACK + hw, 0)[0]))
    o.append(rect(x0, P(0, R + 289)[1], x1 - x0, v.L(R + 289), PANEL, STEEL, 2, v.L(40)))
    rx0, rx1 = sorted((P(g.HALF_TRACK - 63.5, 0)[0], P(g.HALF_TRACK + 63.5, 0)[0]))
    o.append(rect(rx0, P(0, R + 165)[1], rx1 - rx0, v.L(330), BG, "none", 0))
    for xr in (g.HALF_TRACK - 63.5, g.HALF_TRACK + 63.5):  # закраины обода
        o.append(line(P(xr, R - 165), P(xr, R + 165), MUT, 2.5))
    o.append(line(P(g.HALF_TRACK - 63.5, R + 150), P(g.HALF_TRACK + 63.5, R + 150), MUT, 1.5))
    o.append(line(P(g.HALF_TRACK - 63.5, R - 150), P(g.HALF_TRACK + 63.5, R - 150), MUT, 1.5))
    o.append(line(P(g.HUB_FACE_X, R - 150), P(g.HUB_FACE_X, R + 150), MUT, 3))  # диск колеса
    # Тормозной диск 2108 и суппорт
    dx0 = P(g.HUB_FACE_X - 12, 0)[0]
    o.append(rect(min(dx0, P(g.HUB_FACE_X, 0)[0]), P(0, R + 119)[1], v.L(12), v.L(238), "#cbd5e1", TXT, 1))
    cx0 = P(g.HUB_FACE_X - 35, 0)[0]
    o.append(rect(min(cx0, P(g.HUB_FACE_X + 8, 0)[0]), P(0, R + 128)[1], v.L(43), v.L(45), "#b45309", AMB, 1.2, 3))
    # Ступица / подшипник
    hx0 = P(605, 0)[0]
    o.append(rect(min(hx0, P(g.HUB_FACE_X - 12, 0)[0]), P(0, R + 32)[1], v.L(g.HUB_FACE_X - 617), v.L(64),
                  "#475569", MUT, 1.2))
    # Кулак 2108 (схематично) — сечение
    knuckle = [(583, 148), (614, 160), (630, 235), (630, 322), (602, 336), (540, 330), (530, 422),
               (500, 422), (508, 328), (560, 245), (574, 186)]
    o.append(poly([P(*p) for p in knuckle], "#475569", "#cbd5e1", 1.6, 0.95))
    # Адаптер АД-01 (щека)
    adapter = g.ADAPTER_OUTLINE
    o.append(poly([P(*p) for p in adapter], VIO, VIO, 1.6, 0.35))
    for b in g.LUG_BOLTS:
        o.append(circ(P(*b), v.L(9), BG, TXT, 1.4))
        o.append(circ(P(*b), v.L(3), TXT, TXT, 0))
    # Рулевой рычаг (уходит назад) — торец
    sp = g.steer_point_front_view()
    o.append(rect(P(*sp)[0] - v.L(14), P(*sp)[1] - v.L(15), v.L(28), v.L(30), VIO, VIO, 1.2, 3, 0.6))
    # Рычаги
    o.append(line(P(*g.LOWER_INNER), P(*g.LBJ), GRN, v.L(30), op=0.85))
    o.append(line(P(*g.UPPER_INNER), P(*g.UBJ), "#0ea5e9", v.L(25), op=0.85))
    # Сайлентблоки внутренних осей
    for p in (g.LOWER_INNER, g.UPPER_INNER):
        o.append(circ(P(*p), v.L(22), DARK, TXT, 1.6))
        o.append(circ(P(*p), v.L(7), ACC, ACC, 0))
    # Шаровая 2108 и ШС M16
    o.append(circ(P(*g.LBJ), v.L(17), "#475569", TXT, 1.6))
    o.append(circ(P(*g.LBJ), v.L(6), AMB, AMB, 0))
    o.append(circ(P(*g.UBJ), v.L(16), "#475569", TXT, 1.6))
    o.append(circ(P(*g.UBJ), v.L(8), BG, ACC, 1.5))
    # Амортизатор с пружиной
    s_low, s_up = g.shock_points()
    a, b = P(*s_low), P(*s_up)
    mid = (a[0] + (b[0] - a[0]) * 0.55, a[1] + (b[1] - a[1]) * 0.55)
    o.append(line(a, mid, "#cbd5e1", v.L(40)))
    o.append(line(mid, b, TXT, v.L(14)))
    o.append(spring((a[0] + (b[0] - a[0]) * 0.12, a[1] + (b[1] - a[1]) * 0.12),
                    (a[0] + (b[0] - a[0]) * 0.86, a[1] + (b[1] - a[1]) * 0.86), 8, v.L(62)))
    o.append(circ(a, v.L(9), BG, AMB, 1.6))
    o.append(circ(b, v.L(9), BG, AMB, 1.6))
    # Ось шкворня
    k = (g.LBJ[0] - g.UBJ[0]) / (g.UBJ[1] - g.LBJ[1])
    o.append(line(P(g.LBJ[0] + g.LBJ[1] * k, 0), P(g.LBJ[0] - (560 - g.LBJ[1]) * k, 560), RED, 1.3,
                  "14,4,3,4"))
    # Рулевая тяга (проекция)
    inner, _ = g.ideal_tie_rod_inner()
    o.append(line(P(*inner), P(*sp), VIO, v.L(16), op=0.5))
    o.append(circ(P(*inner), v.L(12), BG, VIO, 1.6))
    # Плоскость колеса
    o.append(line(P(g.HALF_TRACK, -20), P(g.HALF_TRACK, 600), STEEL, 1, "18,4,3,4"))
    return "".join(o)


def draw_subframe_section(v, mirror=1):
    """Сечения рам подрамника в виде спереди (правый/левый борт)."""
    def P(x, y):
        return v(mirror * x, y)
    o = []
    lr = (g.LOWER_INNER[0] - 45, g.LOWER_INNER[1] + 25)   # центр нижней балки 50x50
    ur = (g.UPPER_INNER[0] - 40, g.UPPER_INNER[1] + 10)   # центр верхней балки 40x40
    for c, s in ((lr, 50), (ur, 40)):
        p = P(c[0] - s / 2 * mirror, c[1] + s / 2)
        o.append(rect(p[0], p[1], v.L(s) * mirror, v.L(s), "#d97706", AMB, 1.6))
    # стойка между балками (за плоскостью — штрих)
    p = P(lr[0] - 20 * mirror, ur[1] - 20)
    o.append(rect(p[0], p[1], v.L(40) * mirror, v.L(ur[1] - 20 - lr[1] - 25), "none", MUT, 1, 0, 1, "5,3"))
    # уши сайлентблоков
    for piv, c in ((g.LOWER_INNER, lr), (g.UPPER_INNER, ur)):
        e0 = P(c[0] + 20, piv[1] + 24)
        o.append(rect(e0[0], e0[1], v.L(piv[0] - c[0] + 6) * mirror, v.L(48), "#92400e", AMB, 1, 4, 0.8))
    # поперечина амортизаторов
    s_low, s_up = g.shock_points()
    top = s_up[1] + 30
    p0 = P(0, top + 40)
    o.append(rect(p0[0], p0[1], v.L(s_up[0] + 25) * mirror, v.L(40), "#d97706", AMB, 1.4, 0, 0.9))
    o.append(rect(P(s_up[0] - 12, top)[0], P(0, top)[1], v.L(24) * mirror, v.L(top - s_up[1] + 10),
                  "#92400e", AMB, 1))
    return "".join(o), lr, ur, top


# =========================================================================
# ЛИСТ 07 — УГОЛ ПОДВЕСКИ В СБОРЕ
# =========================================================================
def sheet_07():
    v = View(110, 840, 0.95)
    o = []
    o.append(line(v(-80, 0), v(780, 0), MUT, 2))
    o.append(text(*v(-75, -14), "ЗЕМЛЯ", 10, MUT))
    o.append(line(v(0, -30), v(0, 610), STEEL, 1.2, "18,4,3,4"))
    o.append(text(*v(6, 596), "ОСЬ МАШИНЫ", 10, MUT))
    # мгновенный центр и центр крена
    ic, rc = g.roll_center_height()
    for a, b in ((g.LOWER_INNER, g.LBJ), (g.UPPER_INNER, g.UBJ)):
        t = (-80 - a[0]) / (b[0] - a[0])
        o.append(line(v(*b), v(-80, a[1] + t * (b[1] - a[1])), GRN, 0.8, "4,4", op=0.7))
    o.append(line(v(g.HALF_TRACK, 0), v(-80, rc + (rc - 0) * 80 / g.HALF_TRACK), RED, 0.8, "4,4", op=0.7))
    sub, lr, ur, top = draw_subframe_section(v)
    o.append(sub)
    o.append(draw_corner(v))
    o.append(circ(v(0, rc), 6, RED, TXT, 1))
    o.append(text(*(v(8, rc + 12)), f"Центр крена h = {rc:.0f}", 11, RED, weight="bold"))
    o.append(text(*(v(-75, 300)), f"→ к мгн. центру", 10, GRN))
    o.append(text(*(v(-75, 286)), f"X={ic[0]:.0f}, Y={ic[1]:.0f}", 10, GRN))

    # выноски
    sl, su = g.shock_points()
    inner, tlen = g.ideal_tie_rod_inner()
    sp = g.steer_point_front_view()
    L = [
        (g.LOWER_INNER, (90, 140), "1. Нижний рычаг (сайлентблоки, ось вдоль машины)"),
        (g.UPPER_INNER, (60, 560), "2. Верхний рычаг, база 260 мм"),
        (g.LBJ, (360, 60), "3. Шаровая опора 2108 (штатная)"),
        (g.UBJ, (420, 600), "4. ШС-наконечник M16x1.5 (регулировка развала)"),
        ((515, 380), (230, 360), "5. Адаптер АД-01 (лист 08)"),
        ((600, 300), (700, 520), "6. Кулак 2108"),
        ((g.HUB_FACE_X - 6, 380), (700, 470), "7. Диск 2108 + суппорт"),
        (sl, (300, 120), "8. Койловер 350 мм"),
        (inner, (60, 390), "9. Внутр. шарнир рейки / тяги схожд."),
        ((lr[0], lr[1] - 10), (40, 200), "10. Подрамник 50x50 / 40x40"),
        ((su[0], top + 20), (90, 650), "11. Поперечина амортизаторов 40x40"),
    ]
    for p, t, s in L:
        o.append(leader(v(*p), v(*t), s, TXT, 11))
    # размеры
    o.append(dim(v(0, 0), v(g.HALF_TRACK, 0), f"{g.HALF_TRACK:.0f} (ПОЛУКОЛЕЯ)", 46))
    k = (g.LBJ[0] - g.UBJ[0]) / (g.UBJ[1] - g.LBJ[1])
    gx = g.LBJ[0] + g.LBJ[1] * k
    o.append(dim(v(gx, 0), v(g.HALF_TRACK, 0), f"{g.scrub_radius():.0f}", 22, RED, 11))
    o.append(text(*v(g.UBJ[0] - 70, 545), f"KPI {g.kingpin_inclination_deg():.1f}°", 12, RED, weight="bold"))
    o.append(dim(v(g.HALF_TRACK + 110, 0), v(g.HALF_TRACK + 110, g.WHEEL_RADIUS_STATIC), "R ст. 280", -14))

    # Таблица координат
    rows = [
        ("Ниж. рычаг, внутр. ось", f"{g.LOWER_INNER[0]:.0f}", f"{g.LOWER_INNER[1]:.0f}", "+120 / −120"),
        ("Верх. рычаг, внутр. ось", f"{g.UPPER_INNER[0]:.0f}", f"{g.UPPER_INNER[1]:.0f}",
         f"{g.UPPER_ARM_Z[0]:+.0f} / {g.UPPER_ARM_Z[1]:.0f}"),
        ("Шаровая 2108", f"{g.LBJ[0]:.0f}", f"{g.LBJ[1]:.0f}", "0"),
        ("ШС M16 (верх)", f"{g.UBJ[0]:.0f}", f"{g.UBJ[1]:.0f}", f"{-g.CASTER_OFFSET:.0f}"),
        ("Центр колеса", f"{g.HALF_TRACK:.0f}", f"{g.WHEEL_RADIUS_STATIC}", "0"),
        ("Аморт. нижнее ухо", f"{sl[0]:.0f}", f"{sl[1]:.0f}", f"{g.SHOCK_Z:.0f}"),
        ("Аморт. верхнее ухо", f"{su[0]:.0f}", f"{su[1]:.0f}", f"{g.SHOCK_Z:.0f}"),
        ("Наконечник тяги", f"{sp[0]:.0f}", f"{sp[1]:.0f}", f"{g.STEER_Z:.0f}"),
        ("Внутр. шарнир рейки", f"{inner[0]:.0f}", f"{inner[1]:.0f}", f"{g.STEER_Z:.0f}"),
    ]
    t, h = table(900, 112, [178, 52, 52, 168], ["Точка (правый борт), мм", "X", "Y", "Z (от оси колеса)"], rows)
    o.append(t)
    y = 112 + h + 12
    s = g.sweep(20)
    used, ext, comp = g.shock_stroke_used()
    m = g.corner_sprung_masses()
    _, kf = g.spring_rate(m["front"], g.RIDE_FREQ_FRONT)
    _, kr = g.spring_rate(m["rear"], g.RIDE_FREQ_REAR)
    nb, h = note_box(900, y, 450, "ГЕОМЕТРИЯ (расчет chassis_geometry.py)", [
        f"Наклон шкворня {g.kingpin_inclination_deg():.1f}°, плечо обкатки +{g.scrub_radius():.0f} мм, "
        f"кастер {g.caster_deg():.1f}° (только перед)",
        f"Развал: {s[-1]['camber_deg']:+.1f}° на сжатии +{g.BUMP_TRAVEL}, {s[0]['camber_deg']:+.1f}° на отбое "
        f"−{g.DROOP_TRAVEL}",
        f"Центр крена {rc:.0f} мм; изм. полуколеи {s[-1]['contact'][0] - g.HALF_TRACK:+.0f}/"
        f"{s[0]['contact'][0] - g.HALF_TRACK:+.0f} мм",
        f"Койловер L={g.SHOCK_EYE_TO_EYE} ход {g.SHOCK_STROKE}: работает {used:.0f} мм, "
        f"MR = {g.motion_ratio():.2f}",
        f"Пружина: перед ≈ {kf:.0f} Н/мм, зад ≈ {kr:.0f} Н/мм",
        "~Статическая установка: развал 0°...−0.5°, схождение перед +0°10', зад 0°",
    ])
    o.append(nb)
    y += h + 12
    nb, h = note_box(900, y, 450, "КОЛЕСО И СТУПИЦА", [
        "Диск 13x5J ET35, 4x98, DIA 58.6; шина 175/70 R13",
        "Болты колеса M12x1.25 конус 60° — 65...90 Нм крест-накрест",
        "Гайка ступицы M20x1.5 — 225...250 Нм, закернить бурт",
        "Передние (неведущие): вместо привода — «имитатор ШРУС»:",
        "~ обрезок наружного ШРУС 2108 со шлицевым хвостовиком —",
        "~ стягивает подшипник ступицы. Без него подшипник разрушится!",
    ], GRN)
    o.append(nb)
    o.append(note_box(50, 112, 520, "ЕДИНЫЙ УГОЛ ПОДВЕСКИ НА 4 КОЛЕСА", [
        "Рычаги, кулаки, адаптеры, тормоза — одинаковые спереди и сзади.",
        "Сзади рычаг адаптера тянет тяга схождения (сгон M16) вместо рулевой тяги.",
        "Кулак НЕ варить (термообработка) — только болтовые соединения.",
    ], AMB)[0])
    return sheet("07-SUSP-CORNER", "СБОРОЧНЫЙ ЧЕРТЁЖ: УГОЛ ПОДВЕСКИ (ВИД СПЕРЕДИ, ПРАВЫЙ БОРТ)",
                 "Двойные поперечные рычаги на кулаке ВАЗ-2108; статика, полная нагрузка", "Угол подвески в сборе", "Кулак 2108 + АД-01 + рычаги", "М 1:5 (прибл.)",
                 "".join(o), 7)


# =========================================================================
# ЛИСТ 08 — АДАПТЕР АД-01
# =========================================================================
def balloon(p, n, at):
    """Позиционная выноска: линия от детали к кружку с номером позиции."""
    return (line(p, at, MUT, 0.9) + circ(p, 2.2, MUT, MUT, 0) + circ(at, 11, PANEL, ACC, 1.4) +
            text(at[0], at[1] + 4, str(n), 11, ACC, "middle", "bold"))


def sheet_08():
    o = []
    sc = 1.8
    # --- Вид А: щека в плоскости X-Y (вдоль оси машины) ---
    v = View(210 - 470 * sc, 600 + 300 * sc, sc)
    o.append(text(50, 128, "ВИД А — ЩЕКА (вдоль оси машины), М 2:1", 14, GRN, weight="bold"))
    lug = [(500, 310), (540, 310), (533, 425), (503, 425)]
    o.append(poly([v(*p) for p in lug], "none", MUT, 1.2, dash="5,3"))
    o.append(text(*v(470, 290), "штрих — прилив кулака 2108", 10, MUT))
    adapter = g.ADAPTER_OUTLINE
    o.append(poly([v(*p) for p in adapter], VIO, VIO, 2, 0.28))
    o.append(poly([v(486, 428), v(492, 428), v(498, 488), v(503, 470)], VIO, VIO, 1, 0.6))
    for b in g.LUG_BOLTS:
        o.append(circ(v(*b), v.L(6.25), BG, TXT, 1.5))
        o.append(line(v(b[0] - 11, b[1]), v(b[0] + 11, b[1]), RED, 0.8, "6,2,2,2"))
        o.append(line(v(b[0], b[1] - 11), v(b[0], b[1] + 11), RED, 0.8, "6,2,2,2"))
    o.append(circ(v(*g.UBJ), v.L(20), "none", AMB, 1.4, "4,2"))
    o.append(circ(v(*g.UBJ), v.L(8.1), BG, TXT, 1.6))
    k = (g.LBJ[0] - g.UBJ[0]) / (g.UBJ[1] - g.LBJ[1])
    o.append(line(v(g.LBJ[0] - (300 - g.LBJ[1]) * k, 300), v(g.LBJ[0] - (515 - g.LBJ[1]) * k, 515), RED, 1.2,
                  "14,4,3,4"))
    o.append(text(*v(552, 300), "ось шкворня", 10, RED))
    b1, b2 = g.LUG_BOLTS
    o.append(dim(v(*b1), v(*b2), f"{math.hypot(b2[0] - b1[0], b2[1] - b1[1]):.0f}*", -34, size=11))
    o.append(dim(v(*b2), v(*g.UBJ), f"{math.hypot(g.UBJ[0] - b2[0], g.UBJ[1] - b2[1]):.0f}", -34, size=11))
    o.append(dim(v(492, 322), v(546, 322), "54", 22, size=11))
    o.append(dim(v(470, 322), v(470, 494), "172", -10, size=11))
    o.append(balloon(v(530, 340), 1, v(585, 360)))
    o.append(balloon(v(494, 450), 2, v(585, 520)))
    o.append(balloon(v(g.UBJ[0] + 14, g.UBJ[1] + 12), 3, v(585, 490)))
    o.append(balloon(v(*b1), 6, v(585, 330)))
    o.append(balloon(v(*g.UBJ), 7, v(585, 460)))
    o.append(text(*v(470, 270), "2 отв. Ø12.5 (M12x1.25), Ø16.2 (M16)", 11, TXT))

    # --- Вид Б: сверху (X-Z), Z вниз = назад ---
    vb = View(560 - 470 * sc, 175 + 40 * sc, sc, flip_y=False)
    def B(x, z): return vb(x, -z)
    o.append(text(470, 128, "ВИД Б — СВЕРХУ, М 2:1", 14, GRN, weight="bold"))
    t = g.LUG_THICKNESS / 2
    pl = g.ADAPTER_PLATE
    for z0 in (t, -t - pl):
        p = B(486, z0 + pl)
        o.append(rect(p[0], p[1], vb.L(61), vb.L(pl), VIO, VIO, 1.5, 0, 0.55))
    p = B(500, t)
    o.append(rect(p[0], p[1], vb.L(40), vb.L(2 * t), "none", MUT, 1, 0, 1, "5,3"))
    o.append(circ(B(g.UBJ[0], 0), vb.L(13), "#475569", TXT, 1.4))
    o.append(line(B(g.UBJ[0], t + pl + 12), B(g.UBJ[0], -t - pl - 12), TXT, vb.L(16) * 0.35))
    o.append(line(B(g.UBJ[0] - 12, 0), B(g.UBJ[0] - 60, 0), "#0ea5e9", vb.L(22), op=0.6))
    o.append(text(*B(g.UBJ[0] - 62, 30), "к верх. рычагу", 10, ACC))
    sp = g.steer_point_front_view()
    kp = g.kingpin_x_at(g.STEER_ARM_Y)
    root0, root1 = (496, -t - pl), (540, -t - pl)
    tip = (sp[0], g.STEER_Z)
    o.append(poly([B(*root0), B(*root1), B(tip[0] + 15, tip[1]), B(tip[0] - 15, tip[1])], VIO, VIO, 1.6, 0.45))
    o.append(circ(B(*tip), vb.L(15), VIO, VIO, 1.6))
    o.append(circ(B(*tip), vb.L(6.1), BG, TXT, 1.5))
    o.append(poly([B(540, -t - pl), B(540, -t - pl - 40), B(522, -t - pl)], AMB, AMB, 1, 0.5))
    ang = math.radians(g.ackermann_arm_angle_deg())
    far = (kp - 150 * math.tan(ang), -150)
    o.append(line(B(kp, 0), B(*far), RED, 1, "10,4,2,4"))
    o.append(circ(B(kp, 0), 4, RED, RED, 0))
    o.append(text(*B(far[0] - 6, far[1] + 4), f"{g.ackermann_arm_angle_deg():.1f}° — на центр задней оси", 11, RED, "end"))
    o.append(dim(B(560, 0), B(560, tip[1]), f"{g.STEER_ARM_LENGTH}", -8, size=11))
    o.append(dim(B(548, t + pl), B(548, -t - pl), f"{g.LUG_THICKNESS + 2 * pl:.0f}", -14, size=11))
    o.append(text(*B(472, -t - pl - 30), f"зазор {g.LUG_THICKNESS:.0f}+0.5*", 11, ACC, "end"))
    o.append(balloon(B(500, t + pl / 2), 1, B(470, 45)))
    o.append(balloon(B(510, -70), 4, B(470, -80)))
    o.append(balloon(B(531, -t - pl - 12), 5, B(600, -50)))
    o.append(balloon(B(*tip), 9, B(470, -125)))
    o.append(balloon(B(g.UBJ[0] + 8, 8), 8, B(600, 30)))

    # --- Сечение В-В: вилка рулевого рычага ---
    o.append(text(470, 575, "СЕЧЕНИЕ В-В — ВИЛКА РУЛЕВОГО РЫЧАГА, М 2:1", 14, GRN, weight="bold"))
    cx, cy = 640, 660
    for dy in (-27, 19):
        o.append(rect(cx - 90, cy + dy, 150, 8 * sc / 1.8 * 1.8, VIO, VIO, 1.4, 0, 0.5))
    o.append(circ((cx, cy), 15, "#475569", TXT, 1.4))
    o.append(rect(cx - 9, cy - 19, 18, 38, "#94a3b8", TXT, 1, 2))
    o.append(line((cx, cy - 45), (cx, cy + 45), TXT, 5))
    o.append(line((cx, cy), (cx + 140, cy), VIO, 8, op=0.5))
    o.append(text(cx + 70, cy - 8, "рулевая тяга", 10, VIO))
    o.append(dim((cx - 90, cy - 19), (cx - 90, cy + 19), "22", 14, size=10))
    o.append(text(cx - 200, cy + 70, "ШС M12 между пластинами 8 мм, проставки high-misalignment, болт M12 10.9", 10, MUT))

    rows = [
        ("1", "Щека", "09Г2С / Ст3 t=6", "2"),
        ("2", "Перемычка (стенка П)", "t=6", "1"),
        ("3", "Шайба-бобышка Ø40/Ø16.2", "t=5", "2"),
        ("4", "Пластина рул. рычага", "t=8", "2"),
        ("5", "Косынка", "t=6", "1"),
        ("6", "Болт M12x1.25x70 10.9 + гайка", "вместо болтов стойки", "2"),
        ("7", "Болт M16x1.5x80 10.9 + гайка", "ось ШС", "1"),
        ("8", "ШС M16x1.5 + проставки", "на верх. рычаг", "1"),
        ("9", "ШС M12 + болт M12 10.9", "рул. тяга / схожд.", "1"),
    ]
    tb, h = table(880, 112, [34, 230, 150, 36], ["Поз", "Наименование", "Материал", "Кол"], rows)
    o.append(tb)
    o.append(note_box(880, 112 + h + 14, 470, "ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ", [
        "* Размеры со звездочкой — снять с кулака-донора до резки!",
        "1. Изготовить 4 шт: 2 правых + 2 левых (зеркально).",
        "2. Зазор щек = толщина прилива + 0.3...0.5 мм (без люфта).",
        "3. Варить в кондукторе на кулаке-шаблоне (не рабочем!),",
        "   болты M12 вставлены. Остывание медленное.",
        "4. Швы катет 5, сплошные, без подрезов.",
        "5. Отверстие поз. 4 сверлить после сварки, по кондуктору.",
        "!КУЛАК НЕ ГРЕТЬ И НЕ ВАРИТЬ — только болты.",
        "6. Затяжка: M12 10.9 — 110 Нм; M16 10.9 — 250 Нм, фиксатор.",
        "7. Через 50 км — протяжка, осмотр корня рычага на трещины.",
    ], AMB)[0])
    return sheet("08-SUSP-AD01", "ДЕТАЛИРОВКА: АДАПТЕР АД-01 (ВЕРХНИЙ ШАРНИР + РУЛЕВОЙ РЫЧАГ)",
                 "Заменяет стойку McPherson 2108: крепится на прилив кулака двумя болтами, несёт ШС верхнего "
                 "рычага и рулевой рычаг",
                 "Адаптер АД-01 (Л/П)", "09Г2С t=6/8 мм", "М 2:1", "".join(o), 8)


# =========================================================================
# ЛИСТ 09 — ПЕРЕДНИЙ ПОДРАМНИК И КИНЕМАТИКА
# =========================================================================
def sheet_09():
    o = []
    s = 0.4
    # Вид спереди (обе стороны)
    vf = View(420, 395, s)
    o.append(text(50, 128, "ВИД СПЕРЕДИ (обе стороны), М 1:10", 14, GRN, weight="bold"))
    o.append(line(vf(-780, 0), vf(780, 0), MUT, 1.5))
    for m in (1, -1):
        sub, lr, ur, top = draw_subframe_section(vf, m)
        o.append(sub)
        o.append(draw_corner(vf, False, m))
    inner, _ = g.ideal_tie_rod_inner()
    o.append(rect(vf(-inner[0] + 25, 0)[0], vf(0, inner[1] + 18)[1], vf.L(2 * inner[0] - 50), vf.L(36),
                  "#475569", VIO, 1.5, 6))
    o.append(dim(vf(-g.HALF_TRACK, 0), vf(g.HALF_TRACK, 0), f"{g.TRACK} (КОЛЕЯ)", 26))
    o.append(dim(vf(-g.LOWER_INNER[0], g.LOWER_INNER[1]), vf(g.LOWER_INNER[0], g.LOWER_INNER[1]),
                 f"{2 * g.LOWER_INNER[0]:.0f}", 30, size=11))
    o.append(dim(vf(-g.UPPER_INNER[0], g.UPPER_INNER[1]), vf(g.UPPER_INNER[0], g.UPPER_INNER[1]),
                 f"{2 * g.UPPER_INNER[0]:.0f}", -48, size=11))
    o.append(dim(vf(-inner[0], inner[1]), vf(inner[0], inner[1]), f"{2 * inner[0]:.0f} рейка", 30, VIO, 11))
    o.append(dim(vf(-700, 0), vf(-700, g.LOWER_INNER[1]), f"{g.LOWER_INNER[1]:.0f}", -12, size=10))
    o.append(dim(vf(-740, 0), vf(-740, g.UPPER_INNER[1]), f"{g.UPPER_INNER[1]:.0f}", -12, size=10))

    # Вид сверху
    vt = View(420, 470 + 470 * s, s)   # Z вверх = вперед
    o.append(text(50, 455, "ВИД СВЕРХУ (подрамник + начало рамы), М 1:10", 14, GRN, weight="bold"))
    st = g.steering_geometry()
    cb = g.FRAME_CROSSBEAM_FROM_AXLE
    # рама: поперечина пола и лонжероны
    p = vt(-g.FRAME_HALF_WIDTH - 25, -cb + 25)
    o.append(rect(p[0], p[1], vt.L(2 * g.FRAME_HALF_WIDTH + 50), vt.L(50), "#d97706", AMB, 1.4))
    for m in (1, -1):
        p = vt(m * g.FRAME_HALF_WIDTH - 25, -cb - 25)
        o.append(rect(p[0], p[1], vt.L(50), vt.L(80), "#d97706", AMB, 1.4))
    o.append(text(*vt(120, -cb - 50), "поперечина пола 50x50 (широкая часть 1100)", 10, AMB))
    # продольные балки подрамника
    rail_x = g.LOWER_INNER[0] - 45
    for m in (1, -1):
        p = vt(m * rail_x - 25, 350)
        o.append(rect(p[0], p[1], vt.L(50), vt.L(350 + cb - 25), "#d97706", AMB, 1.4, 0, 0.85))
    p = vt(-rail_x - 25, 375)
    o.append(rect(p[0], p[1], vt.L(2 * rail_x + 50), vt.L(50), "#d97706", AMB, 1.4))
    p = vt(-25, 470)
    o.append(rect(p[0], p[1], vt.L(50), vt.L(95), "none", ACC, 1.4, 0, 1, "5,3"))
    o.append(text(*vt(35, 450), "приемный квадрат отвала 50x50", 10, ACC))
    # колеса, зона поворота
    for m in (1, -1):
        p = vt(m * g.HALF_TRACK - g.TIRE_WIDTH / 2, g.WHEEL_RADIUS_STATIC + 9)
        o.append(rect(p[0], p[1], vt.L(g.TIRE_WIDTH), vt.L(2 * (g.WHEEL_RADIUS_STATIC + 9)), PANEL, STEEL, 1.5, 6))
        o.append(circ(vt(m * st["kingpin_x"], 0), vt.L(st["lock_envelope"]), "none", RED, 1, "6,4"))
        # рычаги (нижний — зеленый, верхний — голубой)
        for z in g.LOWER_ARM_Z:
            o.append(line(vt(m * g.LOWER_INNER[0], z), vt(m * g.LBJ[0], 0), GRN, vt.L(30), op=0.8))
        for z in g.UPPER_ARM_Z:
            o.append(line(vt(m * g.UPPER_INNER[0], z), vt(m * g.UBJ[0], -g.CASTER_OFFSET), "#0ea5e9",
                          vt.L(25), op=0.7))
        # рулевой рычаг и тяга
        sp = g.steer_point_front_view()
        o.append(line(vt(m * g.kingpin_x_at(g.STEER_ARM_Y), 0), vt(m * sp[0], g.STEER_Z), VIO, 4))
        o.append(line(vt(m * inner[0], g.STEER_Z), vt(m * sp[0], g.STEER_Z), VIO, 3))
        o.append(circ(vt(m * sp[0], g.STEER_Z), 3.5, VIO, VIO, 0))
    o.append(text(*vt(g.HALF_TRACK + 40, -cb + 70), f"зона поворота колеса R{st['lock_envelope']:.0f}", 10, RED))
    # поперечина амортизаторов и рейка
    sl, su = g.shock_points()
    p = vt(-su[0] - 25, g.SHOCK_Z + 20)
    o.append(rect(p[0], p[1], vt.L(2 * su[0] + 50), vt.L(40), "#d97706", AMB, 1, 0, 0.5, "4,2"))
    p = vt(-inner[0] + 25, g.STEER_Z + 20)
    o.append(rect(p[0], p[1], vt.L(2 * inner[0] - 50), vt.L(40), "#475569", VIO, 1.5, 8))
    o.append(circ(vt(-110, g.STEER_Z - 30), 5, VIO, TXT, 1))
    o.append(line(vt(-110, g.STEER_Z - 30), vt(-150, -cb - 60), VIO, 2, "6,3"))
    o.append(text(*vt(-170, -cb - 50), "к рулевой колонке", 10, VIO, "end"))
    # размеры
    o.append(dim(vt(g.FRAME_HALF_WIDTH + 70, 0), vt(g.FRAME_HALF_WIDTH + 70, -cb), f"{cb}", -12, size=11))
    o.append(dim(vt(-g.LOWER_INNER[0] - 120, 120), vt(-g.LOWER_INNER[0] - 120, -120), "240", -10, GRN, 10))
    o.append(dim(vt(-rail_x, 250), vt(rail_x, 250), f"{2 * rail_x:.0f}", 14, size=10))
    o.append(text(*vt(0, -280), f"рейка: Z = {g.STEER_Z} от оси, Y = {inner[1]:.0f}", 10, VIO, "middle"))

    # Графики кинематики
    sw = g.sweep(10)
    xs = [p["target"] for p in sw]
    o.append(plot(920, 150, 400, 175,
                  [(xs, [p["camber_deg"] for p in sw], GRN, "развал, °"),
                   (xs, [(p["contact"][0] - g.HALF_TRACK) / 10 for p in sw], AMB, "изм. полуколеи, см")],
                  (-80, 100), (-3, 3), [-80, -40, 0, 40, 80], [-3, -2, -1, 0, 1, 2, 3],
                  "ход колеса, мм (+ сжатие)", "град / см", "РАЗВАЛ И КОЛЕЯ НА ХОДЕ ПОДВЕСКИ"))
    ttr = g.bump_steer_table(*g.ideal_tie_rod_inner())
    o.append(plot(920, 410, 400, 150,
                  [([t for t, _ in ttr], [d for _, d in ttr], VIO, "схождение одного колеса, °")],
                  (-80, 100), (-0.25, 0.25), [-80, -40, 0, 40, 80], [-0.2, -0.1, 0, 0.1, 0.2],
                  "ход колеса, мм", "град", "ПОДРУЛИВАНИЕ (рейка на расчетной точке)"))
    o.append(note_box(880, 625, 470, "ИЗМЕНЕНИЕ РАМЫ (обязательно!)", [
        "!Рама 1100 мм не может проходить мимо колес: колесо (X 563...738)",
        "!пересекается с лонжероном X=525...575. Широкая часть рамы",
        f"обрывается поперечиной в {cb} мм от осей; дальше — узкие подрамники.",
        f"Подрамник: 2 балки 50x50 на X=±{rail_x:.0f}, стойки 40x40, верхние 40x40.",
    ], RED, 11, 16)[0])
    return sheet("09-SUSP-FRONT-SUB", "ПЕРЕДНИЙ ПОДРАМНИК ПОДВЕСКИ И КИНЕМАТИКА",
                 "Координаты осей рычагов, рейки, поперечины амортизаторов. Графики — расчет по фактической "
                 "геометрии", "Передний подрамник", "Труба 50x50x2.5, 40x40x2", "М 1:10", "".join(o), 9)


# =========================================================================
# ЛИСТ 10 — РУЛЕВОЕ УПРАВЛЕНИЕ
# =========================================================================
def sheet_10():
    o = []
    st = g.steering_geometry()
    kp = st["kingpin_x"]
    s = 0.22
    v = View(270, 160 + g.WHEEL_RADIUS_STATIC * s + 10, s, flip_y=True)  # Z вверх = вперед
    o.append(text(50, 128, "РУЛЕВАЯ ТРАПЕЦИЯ (вид сверху), М 1:25", 14, GRN, weight="bold"))
    rz = -g.WHEELBASE
    o.append(line(v(-g.HALF_TRACK - 100, rz), v(g.HALF_TRACK + 100, rz), STEEL, 1, "18,4,3,4"))
    o.append(text(*v(g.HALF_TRACK + 30, rz + 40), "задняя ось", 10, MUT))
    inner_a = math.radians(g.STEER_LOCK_INNER)
    outer_a = math.radians(st["outer_deg"])

    def wheel(cx, ang, color, dash=None):
        # колесо поворачивается вокруг шкворня (cx_kp)
        hw, hl = g.TIRE_WIDTH / 2, g.WHEEL_RADIUS_STATIC + 9
        corners = [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]
        sign = 1 if cx > 0 else -1
        pts = []
        for x, z in corners:
            x0, z0 = x + sign * (g.HALF_TRACK - kp), z
            xr = x0 * math.cos(ang) - z0 * math.sin(ang)
            zr = x0 * math.sin(ang) + z0 * math.cos(ang)
            pts.append(v(sign * kp + xr, zr))
        return poly(pts, PANEL if not dash else "none", color, 1.5, dash=dash)

    for m in (1, -1):
        o.append(wheel(m, 0, STEEL))
        o.append(wheel(m * 1, inner_a if m < 0 else outer_a, VIO, "6,3"))
        o.append(wheel(m, 0, STEEL))
        p = v(m * g.HALF_TRACK - g.TIRE_WIDTH / 2, rz + g.WHEEL_RADIUS_STATIC)
        o.append(rect(p[0], p[1], v.L(g.TIRE_WIDTH), v.L(2 * g.WHEEL_RADIUS_STATIC), PANEL, STEEL, 1.2, 4))
    # поворот влево: левое колесо внутреннее
    o.append(line(v(-kp, 0), v(0, rz), RED, 1, "10,4"))
    o.append(line(v(kp, 0), v(0, rz), RED, 1, "10,4"))
    sp = g.steer_point_front_view()
    inner, tl = g.ideal_tie_rod_inner()
    for m in (1, -1):
        o.append(line(v(m * kp, 0), v(m * sp[0], g.STEER_Z), VIO, 4))
        o.append(line(v(m * inner[0], g.STEER_Z), v(m * sp[0], g.STEER_Z), VIO, 2.5))
    o.append(rect(v(-inner[0], 0)[0], v(0, g.STEER_Z + 18)[1], v.L(2 * inner[0]), v.L(36), "#475569", VIO, 1.2, 4))
    o.append(text(*v(0, rz + 70), "линии рычагов сходятся на центре задней оси = 100% Аккерман", 10, RED,
                  "middle"))
    o.append(text(*v(-g.HALF_TRACK - 160, 330), f"внутр. {g.STEER_LOCK_INNER:.0f}°", 12, VIO, weight="bold"))
    o.append(text(*v(g.HALF_TRACK - 60, 330), f"наруж. {st['outer_deg']:.1f}°", 12, VIO, weight="bold"))
    o.append(dim(v(-g.HALF_TRACK - 120, 0), v(-g.HALF_TRACK - 120, rz), f"{g.WHEELBASE} (БАЗА)", -10, size=11))

    # Колонка — вид сбоку (Z-Y), координаты от передней оси
    vs = View(560 + 1300 * 0.32, 760, 0.32)
    o.append(text(560, 420, "РУЛЕВАЯ КОЛОНКА (вид сбоку слева), М 1:15", 14, GRN, weight="bold"))
    o.append(line(vs(-1300, 0), vs(150, 0), MUT, 1.2))
    o.append(circ(vs(0, g.WHEEL_RADIUS_STATIC), vs.L(g.WHEEL_RADIUS_STATIC), "none", STEEL, 1.5))
    o.append(text(*vs(-40, 20), "перед. ось", 10, MUT, "end"))
    pin, j2, j1, wheel_c = ((z, y) for _, y, z in g.COLUMN_POINTS)  # шестерня, кардан 2, кардан 1, руль
    o.append(line(vs(*pin), vs(*j2), VIO, 4))
    o.append(line(vs(*j2), vs(*j1), VIO, 4))
    o.append(line(vs(*j1), vs(*wheel_c), TXT, 6))
    for j in (j1, j2):
        o.append(circ(vs(*j), 6, AMB, TXT, 1.2))
    o.append(circ(vs(*pin), 7, "#475569", VIO, 1.5))
    rw = (math.cos(math.radians(70)) * 175, math.sin(math.radians(70)) * 175)
    o.append(line(vs(wheel_c[0] - rw[0], wheel_c[1] + rw[1]), vs(wheel_c[0] + rw[0], wheel_c[1] - rw[1]), TXT, 7))
    o.append(rect(vs(-cb_x() - 25, 0)[0], vs(0, 330)[1], vs.L(50), vs.L(50), "#d97706", AMB, 1.2))
    o.append(leader(vs(*wheel_c), vs(-1250, 980), "руль Ø350", TXT, 11))
    o.append(leader(vs((j1[0] + wheel_c[0]) / 2, (j1[1] + wheel_c[1]) / 2), vs(-1150, 600),
                    "вал Ø20 в 2 подшипниках (кронштейн на дуге)", TXT, 11))
    o.append(leader(vs(*j1), vs(-620, 820), "кардан 1 (рулевой ВАЗ)", AMB, 11))
    o.append(leader(vs(*j2), vs(-300, 680), "кардан 2", AMB, 11))
    o.append(leader(vs(*pin), vs(80, 560), "шестерня рейки", VIO, 11))
    o.append(text(*vs(-cb_x() - 30, 300), "поперечина пола", 10, AMB, "end"))
    a1 = math.degrees(math.atan2(wheel_c[1] - j1[1], j1[0] - wheel_c[0]))
    a2 = math.degrees(math.atan2(j1[1] - j2[1], j2[0] - j1[0]))
    a3 = math.degrees(math.atan2(j2[1] - pin[1], pin[0] - j2[0]))
    o.append(text(560, 800, f"Углы в карданах: {abs(a1 - a2):.0f}° и {abs(a2 - a3):.0f}° (допуск ≤ 30°).", 11, AMB))
    o.append(text(560, 818, "Вилки промвала — в одной плоскости.", 11, MUT))
    o.append(text(560, 836, "Положение руля — по сиденью (на месте).", 11, MUT))

    rows = [
        ("Тип", "рейка с торцевым отбором тяг (UTV / багги)"),
        ("Межцентр. внутр. шарниров", f"{2 * inner[0]:.0f} ± 10 мм (в среднем положении)"),
        ("Ход рейки", f"не менее ±{st['rack_travel']:.0f} мм + упоры"),
        ("Высота / положение", f"Y = {inner[1]:.0f} мм, Z = {g.STEER_Z} мм от оси"),
        ("Передаточное", "2.0...2.5 оборота руля от упора до упора"),
        ("Крепление", "2 хомута на поперечину 40x40, болты M10"),
        ("Тяга (проекция)", f"{tl:.0f} мм, наконечник ШС M12"),
    ]
    tb, h = table(880, 112, [180, 290], ["Требование к рейке", "Значение"], rows)
    o.append(tb)
    o.append(note_box(880, 112 + h + 12, 470, "РЕЗУЛЬТАТ РАСЧЕТА", [
        f"Радиус разворота по наружному колесу: {st['turn_radius'] / 1000:.2f} м",
        f"Кастер {g.caster_deg():.1f}° (самовозврат руля), KPI {g.kingpin_inclination_deg():.1f}°",
        "Подруливание на ходе ±0.02° — практически ноль (лист 09)",
        "Упоры угла поворота: болт M10 с контргайкой на нижнем рычаге,",
        f"   ограничить внутреннее колесо {g.STEER_LOCK_INNER:.0f}° (шина не трет раму/рычаг).",
        "!Если высота рейки отличается от расчетной более чем на 10 мм —",
        "!подруливание резко растет. Высоту выставлять проставками хомутов.",
    ], AMB)[0])
    return sheet("10-STEER", "РУЛЕВОЕ УПРАВЛЕНИЕ: ТРАПЕЦИЯ, РЕЙКА, КОЛОНКА",
                 "Рейка за осью колес, рычаги АД-01 назад; колонка с двумя карданами",
                 "Рулевое управление", "Рейка UTV + карданы ВАЗ", "М 1:25 / 1:15", "".join(o), 10)


def cb_x():
    return g.FRAME_CROSSBEAM_FROM_AXLE


# =========================================================================
# ЛИСТ 11 — СИЛОВОЙ МОДУЛЬ
# =========================================================================
def sheet_11():
    o = []
    static, pmin, pmax, ang = g.driveshaft_report()
    o.append(note_box(50, 112, 800, "ПРИВОДЫ И ПОДРАМНИК (по месту)", [
        f"Длина между центрами ШРУС {static:.0f} мм, осевой ход {pmin:+.0f}/{pmax:+.0f} мм, угол ≤ {ang:.0f}° — "
        f"укоротить оба привода 2108 до одинаковой длины (токарная услуга).",
        f"Сзади X/Y шарниров — как на листе 07, кастер 0. Z (от оси): нижний {g.REAR_LOWER_ARM_Z[0]:+.0f}/"
        f"{g.REAR_LOWER_ARM_Z[1]:.0f}, верхний {g.REAR_UPPER_ARM_Z[0]:+.0f}/{g.REAR_UPPER_ARM_Z[1]:+.0f}, "
        f"аморт. {g.REAR_SHOCK_Z:.0f}, тяга схожд. {g.REAR_TOE_Z:+.0f} (АД-01 Л<->П).",
        "!КПП сначала примерить: зазор до рычагов и балок ≥ 15 мм на всех ходах подвески.",
        "Корпус КПП развернуть назад-вверх вокруг оси дифференциала — приводы не меняются.",
        "* — размер по фактическому положению выходов дифференциала.",
    ], RED)[0])
    s = 0.55
    v = View(450, 880, s)
    o.append(text(50, 290, "ВИД СЗАДИ НА СИЛОВОЙ МОДУЛЬ, М 1:8 (компоновка)", 14, GRN, weight="bold"))
    o.append(line(v(-720, 0), v(720, 0), MUT, 1.5))
    o.append(line(v(0, -10), v(0, 800), STEEL, 1, "18,4,3,4"))
    R = g.WHEEL_RADIUS_STATIC
    for m in (1, -1):
        o.append(line(v(m * g.INNER_CV_X, R), v(m * g.OUTER_CV_CENTER[0], R), MUT, v.L(26)))
        for x, r in ((g.INNER_CV_X, 45), (g.OUTER_CV_CENTER[0], 42)):
            o.append(circ(v(m * x, R), v.L(r), "#475569", TXT, 1.4))
        p = v(m * g.HALF_TRACK - g.TIRE_WIDTH / 2, 2 * R)
        o.append(rect(p[0], p[1], v.L(g.TIRE_WIDTH), v.L(2 * R), PANEL, STEEL, 1.5, 10))
    gb = [(-60, 190), (300, 190), (300, 470), (200, 560), (-60, 560), (-120, 470), (-120, 260)]
    o.append(poly([v(-x, y) for x, y in gb], "#334155", ACC, 2, 0.9, "8,4"))
    o.append(text(*v(-170, 500), "КПП 2108", 15, ACC, "middle", "bold"))
    o.append(text(*v(-170, 470), "габарит — снять с донора", 10, MUT, "middle"))
    o.append(circ(v(0, R), v.L(60), "#475569", TXT, 1.5))
    o.append(text(*v(0, R - 8), "диф.", 11, TXT, "middle"))
    bell_x = 120
    o.append(poly([v(-bell_x, 300), v(bell_x - 10, 260), v(bell_x - 10, 520), v(-bell_x, 500)],
                  "#475569", MUT, 1.5, 0.8))
    p = v(bell_x - 10, 580)
    o.append(rect(p[0], p[1], v.L(14), v.L(400), "#d97706", AMB, 1.6))
    inp = (bell_x + 4, 420)
    o.append(line(v(inp[0], inp[1]), v(inp[0] + 150, inp[1]), TXT, v.L(25)))
    for x in (inp[0] + 30, inp[0] + 100):
        p = v(x - 15, inp[1] + 40)
        o.append(rect(p[0], p[1], v.L(30), v.L(80), "#64748b", TXT, 1.2, 3))
    p = v(inp[0] + 125, inp[1] + 85)
    o.append(rect(p[0], p[1], v.L(8), v.L(170), AMB, AMB, 1))
    p = v(inp[0] + 140, inp[1] + 100)
    o.append(rect(p[0], p[1], v.L(6), v.L(200), "#cbd5e1", TXT, 1))
    cd = g.chain_center_distance()
    mot = (inp[0] + 70, inp[1] + cd)
    o.append(rect(*v(mot[0] - 70, mot[1] + 103), v.L(140), v.L(206), "#1d4ed8", ACC, 1.8, 8, 0.75))
    o.append(text(*v(mot[0], mot[1] + 6), "QS138 70H", 12, TXT, "middle", "bold"))
    for dx in (-48, 48):
        o.append(line(v(inp[0] + 129, mot[1] + dx), v(inp[0] + 129, inp[1] + dx), AMB, 3, "6,3"))
    o.append(dim(v(inp[0] + 200, inp[1]), v(inp[0] + 200, mot[1]), f"{cd:.0f}", -14, AMB, 11))
    # выноски (подписи справа и слева от модуля)
    o.append(leader(v(mot[0] + 70, mot[1] + 60), (640, 345), "QS138: пазы 12x55 — натяжка цепи", ACC, 11))
    o.append(leader(v(inp[0] + 129, mot[1] - 60), (640, 375), "звезды 15T/15T, цепь 520 O-ring", AMB, 11))
    o.append(leader(v(bell_x - 3, 560), (640, 405), "плита-адаптер t=10 на фланец картера", AMB, 11))
    o.append(leader(v(inp[0] + 30, inp[1] + 40), (640, 435), "промвал Ø25 в 2x UCF205", TXT, 11))
    o.append(leader(v(inp[0] + 15, inp[1]), (640, 465), "шлицевая муфта на первичный вал", TXT, 11))
    o.append(leader(v(inp[0] + 143, inp[1] + 90), (640, 495), "диск стояночного Ø200", TXT, 11))
    o.append(leader(v(g.OUTER_CV_CENTER[0] - 100, R + 13), (640, 545), f"привод 2108, {static:.0f} между ШРУС",
                    TXT, 11))
    o.append(leader(v(-290, 200), (60, 545), "опоры КПП: штатные подушки 2108", TXT, 11))
    o.append(dim(v(-g.INNER_CV_X, R), v(g.INNER_CV_X, R), f"{2 * g.INNER_CV_X:.0f}*", 60, size=11))

    rpm, tq, rows = g.gearbox_table()
    t_rows = [(f"{gname}-я", f"{r:.3f}", f"{tot:.1f}", f"{vmax:.0f}", f"{wt:.0f}", f"{fz:.0f}")
              for gname, r, tot, vmax, wt, fz in rows]
    tb, h = table(880, 112, [52, 64, 70, 80, 110, 94],
                  ["Перед.", "i КПП", "i общ.", "V max", "M колёс, Нм", "Тяга, Н"], t_rows)
    o.append(tb)
    y = 112 + h + 10
    o.append(text(880, y + 4, f"QS138 2.35 x цепь {g.CHAIN_DRIVE}/{g.CHAIN_DRIVEN} x КПП x {g.FINAL_DRIVE_2108}; "
                  f"вход ≤ {tq:.0f} Нм, ≤ {rpm:.0f} об/мин", 11, MUT))
    o.append(note_box(880, y + 16, 470, "ЭКСПЛУАТАЦИЯ И НАСТРОЙКА", [
        "4-я — основная (55 км/ч), 2-я — отвал / снег, 1-я — тяжелый выезд.",
        f"!Ток фаз контроллера ограничить: момент на входе КПП ≤ {tq:.0f} Нм",
        "!(штатный момент двигателя 2108 ≈ 106 Нм). Задний ход — реверсом мотора.",
        "Переключать на остановке (сцепления нет), педаль газа отпущена.",
        "Сцепление, вилку и выжимной снять; окно картера закрыть крышкой.",
        "Масло 75W-90 по уровню контрольной пробки; сапун вывести вверх.",
        "Провис цепи 15-20 мм; натяжка — сдвигом мотора по пазам плиты.",
        "Мотор, промвал и КПП — на одной плите: цепь не тянет подушки.",
        "Мотор можно развернуть вокруг оси промвала (вбок/вперед) —",
        f"   межосевое {cd:.0f} мм (52 звена) сохраняется.",
    ], AMB)[0])
    return sheet("11-PWR-MODULE", "СИЛОВОЙ МОДУЛЬ: QS138 → ЦЕПЬ 520 → КПП 2108 → ПРИВОДЫ",
                 "Заменяет лист 04 (сплошной вал на UCP206 несовместим с IRS). КПП 2108 = редуктор + "
                 "дифференциал + понижающие передачи",
                 "Силовой модуль", "Плита 10 мм, 2x UCF205", "М 1:8", "".join(o), 11)


# =========================================================================
# ЛИСТ 12 — ТОРМОЗА
# =========================================================================
def sheet_12():
    o = []
    b = g.brake_report()
    o.append(text(50, 128, "ГИДРАВЛИЧЕСКАЯ СХЕМА (раздельные контуры перед / зад)", 14, GRN, weight="bold"))

    def box(x, y, w, h, label, color=ACC, sub=None):
        r = rect(x, y, w, h, PANEL, color, 1.6, 6) + text(x + w / 2, y + h / 2 + (0 if sub else 4), label, 12, TXT,
                                                         "middle", "bold")
        if sub:
            r += text(x + w / 2, y + h / 2 + 16, sub, 10, MUT, "middle")
        return r

    def pipe(pts, color=RED):
        return (f'<polyline points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" fill="none" stroke="{color}" '
                f'stroke-width="2.5" marker-end="url(#flow)"/>')

    o.append(box(70, 330, 120, 60, "ПЕДАЛЬ", AMB, f"i = {g.PEDAL_RATIO}"))
    o.append(box(250, 320, 170, 80, "ГТЦ 2108", ACC, f"Ø{g.MASTER_CYL_D} мм, 2 контура"))
    o.append(box(275, 230, 120, 45, "БАЧОК", MUT))
    o.append(line((335, 275), (335, 320), MUT, 2))
    o.append(line((190, 360), (250, 360), AMB, 4))
    o.append(box(500, 180, 130, 50, "ТРОЙНИК", RED))
    o.append(box(480, 470, 140, 60, "РЕГУЛЯТОР", RED, f"задн. ≈ {b['rear_pressure_ratio'] * 100:.0f}%"))
    o.append(box(640, 475, 80, 50, "ТРОЙН.", RED))
    o.append(pipe([(420, 340), (460, 340), (460, 205), (500, 205)]))
    o.append(pipe([(420, 380), (460, 380), (460, 500), (480, 500)]))
    o.append(pipe([(620, 500), (640, 500)]))
    for i, (yy, lbl) in enumerate(((140, "СУППОРТ ПЛ"), (250, "СУППОРТ ПП"))):
        o.append(box(720, yy - 25, 140, 50, lbl, GRN, "2108, Ø48"))
        o.append(pipe([(630, 205), (680, 205), (680, yy), (720, yy)]))
    for yy, lbl in ((420, "СУППОРТ ЗЛ"), (580, "СУППОРТ ЗП")):
        o.append(box(740, yy - 25, 120, 50, lbl, GRN, "2108, Ø48"))
        o.append(pipe([(720, 500), (730, 500), (730, yy), (740, yy)]))
    o.append(text(560, 160, "КОНТУР 1 — ПЕРЕД", 12, RED, "middle", "bold"))
    o.append(text(550, 455, "КОНТУР 2 — ЗАД", 12, RED, "middle", "bold"))
    o.append(box(70, 470, 150, 55, "Датчик стоп", AMB, "на педали, 12V"))
    o.append(line((130, 390), (130, 470), AMB, 1.5, "4,3"))
    o.append(box(250, 470, 170, 55, "Вход EBS / тормоз", VIO, "контроллер VOTOL"))
    o.append(line((220, 497), (250, 497), VIO, 1.5, "4,3"))
    o.append(text(250, 545, "рекуперация при нажатии на педаль", 10, VIO))

    # Педальный узел (вид сбоку)
    o.append(text(50, 600, "ПЕДАЛЬНЫЙ УЗЕЛ (вид сбоку), М 1:5", 14, GRN, weight="bold"))
    piv = (150, 640)
    rod = 60 * 0.9
    pedal_len = rod * g.PEDAL_RATIO
    pad = (piv[0] + 40, piv[1] + pedal_len)
    o.append(rect(piv[0] - 50, piv[1] - 25, 270, 10, "#d97706", AMB, 1.2))
    o.append(text(piv[0] + 230, piv[1] - 14, "кронштейн на щите / поперечине", 10, AMB))
    o.append(line(piv, pad, TXT, 8))
    o.append(rect(pad[0] - 30, pad[1] - 4, 60, 12, "#475569", TXT, 1.2, 3))
    o.append(circ(piv, 8, BG, ACC, 2))
    rp = (piv[0] + 40 * rod / pedal_len, piv[1] + rod)
    o.append(circ(rp, 5, AMB, AMB, 0))
    o.append(line(rp, (rp[0] + 200, rp[1] - 10), AMB, 4))
    o.append(rect(rp[0] + 200, rp[1] - 30, 90, 40, PANEL, ACC, 1.5, 4))
    o.append(text(rp[0] + 245, rp[1] - 5, "ГТЦ", 11, TXT, "middle"))
    o.append(dim(piv, rp, "60", -22, size=11))
    o.append(dim(piv, pad, f"{60 * g.PEDAL_RATIO:.0f}", 40, size=11))
    o.append(text(330, 880, f"Передаточное педали {g.PEDAL_RATIO}:1 (270/60)", 11, MUT))

    o.append(note_box(880, 112, 470, "РАСЧЕТ (4 тормоза 2108, без усилителя)", [
        f"Полная масса {g.CURB_MASS + g.CREW_MASS} кг, замедление {g.TARGET_DECEL_G} g",
        f"Давление в системе {b['pressure_mpa']:.1f} МПа (у 2108 штатно до ~10 МПа)",
        f"Усилие на педали {b['pedal_force_n']:.0f} Н (~{b['pedal_force_n'] / 9.81:.0f} кгс) — без вакуума",
        f"Нагрузка на перед при торможении {b['front_dyn_share'] * 100:.0f}%",
        "!Одинаковые суппорты по кругу -> зад блокируется первым:",
        "!регулируемый клапан в задний контур обязателен.",
    ])[0])
    o.append(note_box(880, 290, 470, "СТОЯНОЧНЫЙ ТОРМОЗ", [
        "У суппортов 2108 нет ручника. Решение: механический суппорт",
        "(тросовый, ATV/багги) на диске Ø200 на промвале (лист 11).",
        "Работает через КПП: включить передачу + рычаг ручника.",
        "Момент на диске умножается передаточным числом -> малый диск.",
    ], AMB)[0])
    o.append(note_box(880, 430, 470, "МОНТАЖ МАГИСТРАЛЕЙ", [
        "Трубки стальные медненые Ø4.75 (3/16\"), развальцовка DIN.",
        "Крепление к раме хомутами через 300 мм, вдали от цепи и АКБ.",
        "Гибкие шланги 2108 к суппортам: длину проверить на полном ходе",
        "сжатия/отбоя и в крайних положениях руля (не натянут, не трет).",
        "Штуцеры M10x1; прокачка: ЗП -> ЗЛ -> ПП -> ПЛ.",
        "Жидкость DOT-4. Задний регулятор — по месту, на заезде.",
    ], GRN)[0])
    return sheet("12-BRAKES", "ТОРМОЗНАЯ СИСТЕМА: СХЕМА, ПЕДАЛЬНЫЙ УЗЕЛ, СТОЯНОЧНЫЙ ТОРМОЗ",
                 "Дисковые тормоза ВАЗ-2108 на 4 колеса, ГТЦ 2108, разделение перед/зад, рекуперация",
                 "Тормозная система", "Узлы ВАЗ-2108", "схема / М 1:5", "".join(o), 12)


# =========================================================================
# ЛИСТ 13 — КРОНШТЕЙНЫ И КРЕПЕЖ
# =========================================================================
def sheet_13():
    o = []
    # 1. Ухо сайлентблока (П-скоба)
    o.append(text(50, 128, "1. КРОНШТЕЙН САЙЛЕНТБЛОКА (П-скоба), М 1:2", 14, GRN, weight="bold"))
    x0, y0 = 80, 150
    o.append(rect(x0, y0 + 120, 100, 30, "#d97706", AMB, 1.4))
    o.append(text(x0 + 50, y0 + 140, "балка 50x50", 10, BG, "middle", "bold"))
    for dx in (0, 80):
        o.append(poly([(x0 + 5 + dx, y0 + 120), (x0 + 5 + dx, y0 + 30), (x0 + 10 + dx, y0 + 12),
                       (x0 + 15 + dx, y0 + 30), (x0 + 15 + dx, y0 + 120)], "#92400e", AMB, 1.2, 0.9))
    o.append(rect(x0 + 15, y0 + 22, 70, 36, "#475569", TXT, 1.2, 4))
    o.append(line((x0 - 10, y0 + 40), (x0 + 120, y0 + 40), RED, 1, "8,3,2,3"))
    o.append(dim((x0 + 15, y0 + 22), (x0 + 85, y0 + 22), "L втулки + 0.5", -16, size=10))
    o.append(note_box(300, 140, 540, "Требования", [
        "Пластины 5 мм 09Г2С, отв. Ø12.2 (M12 10.9), сверлить парой в сборе.",
        "Втулка рычага: труба Ø под сайлентблок с натягом 0.1...0.2 мм.",
        "Сайлентблок 2108 нижнего рычага (или ПУ) — запрессовка после сварки.",
        "!Болты сайлентблоков тянуть ТОЛЬКО под статической нагрузкой",
        "!(машина на колесах) — иначе резина порвется на ходе.",
        "Оси двух ушей одного рычага — соосно (пруток-оправка при сварке).",
    ], ACC)[0])

    # 2. Вставка ШС в трубу рычага
    o.append(text(50, 350, "2. ВЕРХНИЙ РЫЧАГ: ВСТАВКА ПОД ШС M16x1.5", 14, GRN, weight="bold"))
    y = 380
    o.append(rect(80, y, 170, 40, "#0ea5e9", ACC, 1.4, 0, 0.5))
    o.append(rect(200, y + 5, 70, 30, "#64748b", TXT, 1.2))
    o.append(rect(270, y + 12, 50, 16, "#94a3b8", TXT, 1))
    o.append(rect(275, y + 8, 10, 24, AMB, AMB, 1))
    o.append(circ((345, y + 20), 22, "#475569", TXT, 1.5))
    o.append(circ((345, y + 20), 8, BG, TXT, 1.2))
    o.append(dim((200, y + 40), (270, y + 40), "≥ 24", 14, size=10))
    o.append(text(400, y + 14, "бобышка Ø30 с резьбой M16x1.5 вварена в торец трубы,", 11, TXT))
    o.append(text(400, y + 31, "резьба в зацеплении не менее 24 мм; контргайка (оранж.)", 11, TXT))
    o.append(text(400, y + 48, "1 оборот ШС = 1.5 мм = ~0.28° развала", 11, AMB))

    # 3. Ухо амортизатора
    o.append(text(50, 490, "3. ДВОЙНОЕ УХО АМОРТИЗАТОРА", 14, GRN, weight="bold"))
    y = 510
    for dx in (0, 46):
        o.append(poly([(100 + dx, y + 100), (100 + dx, y + 30), (112 + dx, y + 10), (124 + dx, y + 30),
                       (124 + dx, y + 100)], "#92400e", AMB, 1.2, 0.9))
    o.append(rect(112, y + 22, 46, 18, "#475569", TXT, 1))
    o.append(line((90, y + 31), (190, y + 31), RED, 1, "8,3,2,3"))
    o.append(text(220, y + 30, "пластины 5 мм, зазор = ширина втулки аморт. + 0.5", 11, TXT))
    o.append(text(220, y + 48, "отв. по болту аморт. (обычно M10 / M12), болт в двойном срезе", 11, TXT))
    o.append(text(220, y + 66, "на нижнем рычаге — на поперечину жесткости, не на один луч", 11, AMB))

    # 4. Имитатор ШРУС для передних ступиц
    o.append(text(50, 650, "4. ПЕРЕДНЯЯ (НЕВЕДУЩАЯ) СТУПИЦА: ИМИТАТОР ШРУС", 14, GRN, weight="bold"))
    y = 690
    o.append(rect(150, y, 90, 110, "#475569", MUT, 1.4, 4))
    o.append(text(195, y + 125, "кулак", 10, MUT, "middle"))
    o.append(rect(170, y + 30, 50, 50, "#64748b", TXT, 1.2))
    o.append(text(195, y + 60, "подш.", 10, TXT, "middle"))
    o.append(rect(220, y + 15, 60, 80, "#334155", TXT, 1.2))
    o.append(text(250, y + 108, "ступица", 10, MUT, "middle"))
    o.append(rect(80, y + 25, 70, 60, AMB, AMB, 1.2, 6, 0.6))
    o.append(text(115, y + 100, "обрезок", 10, AMB, "middle"))
    o.append(text(115, y + 113, "корпуса ШРУС", 10, AMB, "middle"))
    o.append(rect(150, y + 45, 160, 20, AMB, AMB, 1, 0, 0.6))
    o.append(rect(285, y + 40, 20, 30, TXT, TXT, 1))
    o.append(text(330, y + 50, "гайка M20x1.5, 225...250 Нм", 11, TXT))
    o.append(text(330, y + 68, "Хвостовик со шлицами и упорный торец — от наружного", 11, TXT))
    o.append(text(330, y + 86, "ШРУС 2108 (б/у); чашку срезать. Стягивает внутренние", 11, TXT))
    o.append(text(330, y + 104, "кольца подшипника — без него подшипник разрушится.", 11, RED))

    rows = [
        ("M8 (8.8)", "25", "кронштейны, хомуты"),
        ("M10 (8.8 / 10.9)", "50 / 70", "аморт., шаровая к рычагу*"),
        ("M12 (8.8 / 10.9)", "85 / 110", "сайлентблоки, АД-01 к кулаку"),
        ("M12x1.25 колесо", "65...90", "болты колеса ВАЗ"),
        ("M14 (10.9)", "180", "подушки КПП, плита"),
        ("M16x1.5 (10.9)", "250", "ось ШС верх. рычага"),
        ("M20x1.5 ступица", "225...250", "гайка ступицы 2108"),
    ]
    tb, h = table(880, 112, [150, 90, 230], ["Резьба (класс)", "Нм", "Где"], rows)
    o.append(tb)
    f_load, arm_rows = g.lower_arm_check()
    a_rows = [(n, f"{sg:.0f}", f"{245 / sg:.2f}") for n, sg in arm_rows]
    tb2, h2 = table(880, 112 + h + 16, [190, 120, 160],
                    ["Труба нижнего рычага", "σ, МПа (3g)", "Запас (Ст20)"], a_rows)
    o.append(tb2)
    yy = 112 + h + 16 + h2 + 10
    o.append(note_box(880, yy, 470, "ВЫВОД ПО РЫЧАГАМ", [
        f"!Труба 25x25x2 (лист 02) на нижнем рычаге — запас {245 / arm_rows[0][1]:.2f} < 1.",
        "Нижний рычаг: 30x30x2.5 или 40x20x2 на ребро + поперечина",
        "   под ухо амортизатора. Верхний: 25x25x2 допустим.",
        "Все крепежные детали — класс 10.9, гайки самоконтрящиеся",
        "   или с фиксатором резьбы. * — шаровую 2108 сверить по донору.",
    ], RED)[0])
    return sheet("13-BRACKETS", "ТИПОВЫЕ КРОНШТЕЙНЫ, КРЕПЕЖ И МОМЕНТЫ ЗАТЯЖКИ",
                 "Уши сайлентблоков и амортизаторов, вставка ШС, имитатор ШРУС, проверка прочности рычага",
                 "Кронштейны и крепеж", "09Г2С t=5, крепеж 10.9", "М 1:2", "".join(o), 13)


if __name__ == "__main__":
    write("07_suspension_corner_assembly.svg", sheet_07())
    write("08_knuckle_adapter_AD01.svg", sheet_08())
    write("09_front_subframe_kinematics.svg", sheet_09())
    write("10_steering_system.svg", sheet_10())
    write("11_power_module_gearbox.svg", sheet_11())
    write("12_brake_system.svg", sheet_12())
    write("13_brackets_hardware.svg", sheet_13())
