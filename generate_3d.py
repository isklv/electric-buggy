#!/usr/bin/env python3
"""
Генератор 3D-модели шасси электробагги: интерактивный просмотрщик viewer.html (Three.js)
и Wavefront OBJ (buggy_frame_chassis.obj). Геометрия подвески, рулевого и силового модуля
берется из chassis_geometry.py — та же, что на чертежах 07-13.

Координаты, мм: X — вправо, Y — вверх, Z — вперед. Начало — на земле посередине базы.
"""
import json
import math
import os

import chassis_geometry as g

ZF = g.WHEELBASE / 2       # передняя ось
ZR = -g.WHEELBASE / 2      # задняя ось
FLOOR_Y = 305              # ось балок пола 50x50 (низ на 280 — клиренс)
FLOOR_Z = ZF - g.FRAME_CROSSBEAM_FROM_AXLE   # поперечины пола: ±625
HW = g.FRAME_HALF_WIDTH
ROOF_Y = 280 + 1150
ROOF_HW = 480
A_Z, B_Z = 300, -550

LAYERS = {
    "cage": ("Каркас безопасности (40х40)", "#38bdf8"),
    "base": ("Рама пола и подрамники (50х50)", "#f59e0b"),
    "suspension": ("Подвеска, колеса, рулевое", "#10b981"),
    "batteries": ("Модули АКБ (2 шт по центру)", "#a855f7"),
    "drivetrain": ("Мотор, цепь, КПП 2108, приводы", "#ef4444"),
    "plow": ("Крепеж снегоотвала", "#06b6d4"),
}
MATERIALS = {
    "base": (0xd97706, 0.4, 0.6), "cage": (0x0284c7, 0.3, 0.7), "arm": (0x10b981, 0.5, 0.5),
    "upper": (0x0ea5e9, 0.5, 0.5), "tire": (0x1e2229, 0.9, 0.1), "rim": (0x94a3b8, 0.2, 0.8),
    "steel": (0x64748b, 0.4, 0.7), "adapter": (0xa78bfa, 0.4, 0.5), "spring": (0xf59e0b, 0.4, 0.6),
    "bat": (0x9333ea, 0.3, 0.4), "motor": (0x1d4ed8, 0.3, 0.8), "gearbox": (0x9ca3af, 0.5, 0.6),
    "red": (0xdc2626, 0.3, 0.8), "plow": (0x06b6d4, 0.4, 0.6), "seat": (0x334155, 0.9, 0.0),
}

parts = []


def beam(layer, a, b, w, h=None, mat="base"):
    parts.append({"t": "beam", "g": layer, "a": a, "b": b, "w": w, "h": h or w, "m": mat})


def box(layer, c, size, mat):
    parts.append({"t": "box", "g": layer, "c": c, "s": size, "m": mat})


def cyl(layer, c, r, length, axis, mat, seg=20):
    parts.append({"t": "cyl", "g": layer, "c": c, "r": r, "l": length, "ax": axis, "m": mat, "seg": seg})


# =========================================================================
# 1. РАМА ПОЛА И ПОДРАМНИКИ
# =========================================================================
def build_frame():
    for sx in (-1, 1):
        beam("base", [sx * HW, FLOOR_Y, -FLOOR_Z], [sx * HW, FLOOR_Y, FLOOR_Z], 50)
    for z in (-FLOOR_Z, -300, 0, 300, FLOOR_Z):
        beam("base", [-HW, FLOOR_Y, z], [HW, FLOOR_Y, z], 50)

    # Передний подрамник
    lr_x, lr_y = g.LOWER_INNER[0] - 45, g.LOWER_INNER[1] + 25
    ur_x, ur_y = g.UPPER_INNER[0] - 40, g.UPPER_INNER[1] + 10
    front_end = ZF + 375
    for sx in (-1, 1):
        beam("base", [sx * lr_x, lr_y, FLOOR_Z], [sx * lr_x, lr_y, front_end], 50)
        beam("base", [sx * ur_x, ur_y, ZF - 230], [sx * ur_x, ur_y, ZF + 200], 40)
        for z in (ZF - 230, ZF + 200):
            beam("base", [sx * lr_x, lr_y + 25, z], [sx * ur_x, ur_y - 20, z], 40)
        beam("base", [sx * ur_x, ur_y, ZF - 230], [sx * HW, FLOOR_Y, FLOOR_Z], 40)   # укосина к полу
        for z in g.LOWER_ARM_Z:
            box("base", [sx * (g.LOWER_INNER[0] - 5), g.LOWER_INNER[1], ZF + z], [40, 48, 50], "base")
        for z in g.UPPER_ARM_Z:
            box("base", [sx * (g.UPPER_INNER[0] - 5), g.UPPER_INNER[1], ZF + z], [40, 48, 50], "base")
    beam("base", [-lr_x - 25, lr_y, front_end], [lr_x + 25, lr_y, front_end], 50)
    beam("base", [-ur_x, ur_y, ZF + 200], [ur_x, ur_y, ZF + 200], 40)
    sl, su = g.shock_points()
    bar_y = su[1] + 50
    beam("base", [-su[0] - 25, bar_y, ZF + g.SHOCK_Z], [su[0] + 25, bar_y, ZF + g.SHOCK_Z], 40)
    for sx in (-1, 1):
        beam("base", [sx * ur_x, ur_y, ZF + g.SHOCK_Z], [sx * ur_x, bar_y, ZF + g.SHOCK_Z], 40)
    box("base", [0, FLOOR_Y - 20, FLOOR_Z + 110], [700, 3, 200], "steel")   # ниша для ног

    # Задний подрамник: нижние балки опущены под ШРУС, верхняя рама над рычагами
    rear_end = ZR - 300
    ry = g.REAR_RAIL_Y
    for sx in (-1, 1):
        beam("base", [sx * lr_x, ry, -FLOOR_Z], [sx * lr_x, ry, rear_end], 50)
        beam("base", [sx * lr_x, ry, -FLOOR_Z], [sx * HW, FLOOR_Y, -FLOOR_Z], 50)
        beam("base", [sx * 300, 620, -FLOOR_Z], [sx * 300, 620, rear_end], 40)
        beam("base", [sx * lr_x, ry + 25, rear_end], [sx * 300, 600, rear_end], 40)
        beam("base", [sx * lr_x, ry + 25, ZR + 160], [sx * 300, 600, ZR + 160], 40)
        for z in g.REAR_LOWER_ARM_Z:
            box("base", [sx * (g.LOWER_INNER[0] - 5), g.LOWER_INNER[1], ZR + z], [40, 48, 50], "base")
            beam("base", [sx * lr_x, ry, ZR + z], [sx * (g.LOWER_INNER[0] - 15), g.LOWER_INNER[1], ZR + z], 30)
        for z in g.REAR_UPPER_ARM_Z:
            box("base", [sx * (g.UPPER_INNER[0] - 5), g.UPPER_INNER[1], ZR + z], [40, 48, 50], "base")
            beam("base", [sx * 300, 620, ZR + z], [sx * (g.UPPER_INNER[0] + 5), g.UPPER_INNER[1] + 20, ZR + z], 30)
        # опора верхнего уха амортизатора
        beam("base", [sx * 300, 620, ZR + g.REAR_SHOCK_Z], [sx * su[0], su[1] + 20, ZR + g.REAR_SHOCK_Z], 30)
        # кронштейн тяги схождения
        inner, _ = g.ideal_tie_rod_inner()
        beam("base", [sx * lr_x, ry, ZR + g.REAR_TOE_Z], [sx * inner[0], inner[1], ZR + g.REAR_TOE_Z], 30)
    beam("base", [-lr_x - 25, ry, rear_end], [lr_x + 25, ry, rear_end], 50)
    beam("base", [-300, 620, rear_end], [300, 620, rear_end], 40)


# =========================================================================
# 2. КАРКАС БЕЗОПАСНОСТИ
# =========================================================================
def build_cage():
    y0 = FLOOR_Y
    for sx in (-1, 1):
        beam("cage", [sx * HW, y0, B_Z], [sx * ROOF_HW, ROOF_Y, B_Z], 40, mat="cage")
        beam("cage", [sx * HW, y0, A_Z], [sx * ROOF_HW, ROOF_Y, A_Z - 100], 40, mat="cage")
        beam("cage", [sx * ROOF_HW, ROOF_Y, B_Z], [sx * ROOF_HW, ROOF_Y, A_Z - 100], 40, mat="cage")
        beam("cage", [sx * ROOF_HW, ROOF_Y, B_Z], [sx * 300, 620, -FLOOR_Z - 250], 40, mat="cage")
        beam("cage", [sx * HW, y0, A_Z], [sx * (g.UPPER_INNER[0] - 40), g.UPPER_INNER[1] + 10, ZF + 200], 40,
             mat="cage")
        beam("cage", [sx * (HW + 80), y0 + 350, B_Z], [sx * (HW + 80), y0 + 350, A_Z], 40, mat="cage")
        beam("cage", [sx * HW, y0, B_Z], [sx * (HW + 80), y0 + 350, B_Z], 40, mat="cage")
        beam("cage", [sx * HW, y0, A_Z], [sx * (HW + 80), y0 + 350, A_Z], 40, mat="cage")
        beam("cage", [sx * HW, y0, B_Z], [-sx * ROOF_HW, ROOF_Y, B_Z], 30, mat="cage")
    for z in (A_Z - 100, B_Z):
        beam("cage", [-ROOF_HW, ROOF_Y, z], [ROOF_HW, ROOF_Y, z], 40, mat="cage")
    ur_x = g.UPPER_INNER[0] - 40
    beam("cage", [-ur_x, g.UPPER_INNER[1] + 10, ZF + 200], [ur_x, g.UPPER_INNER[1] + 10, ZF + 200], 40, mat="cage")


# =========================================================================
# 3. ПОДВЕСКА, КОЛЕСА, РУЛЕВОЕ (геометрия листов 07-10)
# =========================================================================
def build_corner(sx, za, front):
    L = "suspension"
    lz = g.LOWER_ARM_Z if front else g.REAR_LOWER_ARM_Z
    uz = g.UPPER_ARM_Z if front else g.REAR_UPPER_ARM_Z
    ubj_z = -g.CASTER_OFFSET if front else 0.0
    shock_z = g.SHOCK_Z if front else g.REAR_SHOCK_Z
    steer_z = g.STEER_Z if front else g.REAR_TOE_Z

    lbj = [sx * g.LBJ[0], g.LBJ[1], za]
    ubj = [sx * g.UBJ[0], g.UBJ[1], za + ubj_z]
    for z in lz:
        beam(L, [sx * g.LOWER_INNER[0], g.LOWER_INNER[1], za + z], lbj, 30, mat="arm")
    for z in uz:
        beam(L, [sx * g.UPPER_INNER[0], g.UPPER_INNER[1], za + z], ubj, 25, mat="upper")
    sl, su = g.shock_points()
    t = (sl[0] - g.LOWER_INNER[0]) / (g.LBJ[0] - g.LOWER_INNER[0])
    leg_z = [z * (1 - t) for z in lz]
    beam(L, [sx * sl[0], sl[1], za + leg_z[0]], [sx * sl[0], sl[1], za + leg_z[1]], 25, mat="arm")
    if shock_z < min(leg_z):   # сзади ухо амортизатора вынесено за луч
        beam(L, [sx * sl[0], sl[1], za + min(leg_z)], [sx * sl[0], sl[1], za + shock_z], 25, mat="arm")
    a = [sx * sl[0], sl[1], za + shock_z]
    b = [sx * su[0], su[1], za + shock_z]
    mid = [a[i] + (b[i] - a[i]) * 0.55 for i in range(3)]
    beam(L, a, mid, 44, mat="rim")
    beam(L, mid, b, 16, mat="rim")
    beam(L, [a[i] + (b[i] - a[i]) * 0.12 for i in range(3)], [a[i] + (b[i] - a[i]) * 0.86 for i in range(3)],
         64, mat="spring")

    # кулак 2108 + адаптер АД-01 + рулевой рычаг
    knuckle_top = [sx * 525, 380, za]
    beam(L, lbj, [sx * 615, g.WHEEL_RADIUS_STATIC, za], 50, mat="steel")
    beam(L, [sx * 615, g.WHEEL_RADIUS_STATIC, za], knuckle_top, 45, mat="steel")
    beam(L, [sx * 518, 325, za], [ubj[0], ubj[1] + 20, za + ubj_z], 40, 54, mat="adapter")
    kp = g.kingpin_x_at(g.STEER_ARM_Y)
    sp = g.steer_point_front_view()
    tip = [sx * sp[0], g.STEER_ARM_Y, za + steer_z]
    beam(L, [sx * kp, g.STEER_ARM_Y, za + math.copysign(20, steer_z)], tip, 22, mat="adapter")
    inner, _ = g.ideal_tie_rod_inner()
    beam(L, [sx * inner[0], inner[1], za + steer_z], tip, 16, mat="rim")

    # ступица, тормоз, колесо
    cyl(L, [sx * 645, g.WHEEL_RADIUS_STATIC, za], 45, 80, "x", "steel")
    cyl(L, [sx * (g.HUB_FACE_X - 6), g.WHEEL_RADIUS_STATIC, za], 119, 12, "x", "rim", 32)
    box(L, [sx * (g.HUB_FACE_X - 6), g.WHEEL_RADIUS_STATIC + 95, za - 60], [50, 50, 70], "red")
    cyl(L, [sx * g.HALF_TRACK, g.WHEEL_RADIUS_STATIC, za], g.WHEEL_RADIUS_STATIC + 9, g.TIRE_WIDTH, "x", "tire", 32)
    cyl(L, [sx * g.HALF_TRACK, g.WHEEL_RADIUS_STATIC, za], 165, g.TIRE_WIDTH + 2, "x", "rim", 24)


def build_suspension():
    for sx in (-1, 1):
        build_corner(sx, ZF, True)
        build_corner(sx, ZR, False)
    inner, _ = g.ideal_tie_rod_inner()
    cyl("suspension", [0, inner[1], ZF + g.STEER_Z], 22, 2 * inner[0] - 50, "x", "steel")
    # колонка: шестерня -> 2 кардана -> руль (лист 10, координаты от передней оси)
    pts = [(-110, g.STEER_Z - 10, inner[1] - 30), (-200, -430, 560), (-260, -760, 690), (-275, -1060, 820)]
    for (x1, z1, y1), (x2, z2, y2) in zip(pts, pts[1:]):
        beam("suspension", [x1, y1, ZF + z1], [x2, y2, ZF + z2], 20, mat="rim")
    x, z, y = pts[-1]
    parts.append({"t": "cyl", "g": "suspension", "c": [x, y, ZF + z], "r": 175, "l": 25, "ax": "steer",
                  "m": "seat", "seg": 28})


# =========================================================================
# 4. АКБ, СИДЕНЬЯ
# =========================================================================
def build_interior():
    for z in (100, -350):
        box("batteries", [0, FLOOR_Y + 130, z], [320, 220, 420], "bat")
        box("batteries", [0, FLOOR_Y + 10, z], [340, 10, 440], "base")
    for sx in (-280, 280):
        box("base", [sx, FLOOR_Y + 160, -100], [420, 50, 440], "seat")
        box("base", [sx, FLOOR_Y + 430, -330], [420, 550, 50], "seat")


# =========================================================================
# 5. СИЛОВОЙ МОДУЛЬ (лист 11): КПП корпусом назад-вверх
# =========================================================================
def build_drivetrain():
    L = "drivetrain"
    R = g.WHEEL_RADIUS_STATIC
    cyl(L, [0, R, ZR], 100, 240, "x", "gearbox")
    box(L, [-120, 430, ZR - 135], [360, 260, 180], "gearbox")
    box(L, [90, 390, ZR - 135], [60, 260, 200], "gearbox")
    box(L, [125, 420, ZR - 135], [10, 400, 260], "base")              # плита-адаптер
    inp = [130, 430, ZR - 135]
    cyl(L, [inp[0] + 75, inp[1], inp[2]], 12, 150, "x", "rim")       # промвал
    for dx in (30, 100):
        box(L, [inp[0] + dx, inp[1], inp[2]], [30, 80, 80], "steel")  # UCF205
    cyl(L, [inp[0] + 125, inp[1], inp[2]], 62, 8, "x", "spring")      # звезда 15T
    cyl(L, [inp[0] + 140, inp[1], inp[2]], 100, 6, "x", "rim", 32)    # диск ручника
    cd = g.chain_center_distance()
    cyl(L, [inp[0] + 60, inp[1] + cd, inp[2]], 103, 140, "x", "motor", 28)
    cyl(L, [inp[0] + 125, inp[1] + cd, inp[2]], 62, 8, "x", "spring")
    for dz in (-62, 62):
        beam(L, [inp[0] + 125, inp[1], inp[2] + dz], [inp[0] + 125, inp[1] + cd, inp[2] + dz], 8, mat="spring")
    for sx in (-1, 1):
        beam(L, [sx * g.INNER_CV_X, R, ZR], [sx * g.OUTER_CV_CENTER[0], R, ZR], 26, mat="rim")
        cyl(L, [sx * g.INNER_CV_X, R, ZR], 45, 80, "x", "seat")
        cyl(L, [sx * (g.OUTER_CV_CENTER[0] - 30), R, ZR], 42, 70, "x", "seat")
    box(L, [0, ROOF_Y - 450, B_Z], [200, 90, 280], "rim")             # контроллер


# =========================================================================
# 6. КРЕПЕЖ СНЕГООТВАЛА
# =========================================================================
def build_plow():
    L = "plow"
    y = g.LOWER_INNER[1] + 25
    zf = ZF + 375
    beam(L, [0, y, zf], [0, y, zf + 250], 60, mat="plow")
    for sx in (-1, 1):
        beam(L, [sx * 350, 200, zf + 600], [0, y, zf + 250], 50, mat="plow")
    # лопата 1400 x 450: дуга R350, вогнутостью вперед, из 8 сегментов
    cz, cy, r = zf + 950, 330, 350
    pts = [(cz - r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
           for a in range(-60, 21, 10)]
    for (z1, y1), (z2, y2) in zip(pts, pts[1:]):
        beam(L, [0, y1, z1], [0, y2, z2], 1400, 5, mat="plow")
    beam(L, [-700, 20, pts[0][0]], [700, 20, pts[0][0]], 20, mat="seat")   # резиновый нож
    cyl(L, [0, y + 60, zf - 40], 55, 140, "x", "rim")


# =========================================================================
# ЭКСПОРТ OBJ
# =========================================================================
def _basis(d):
    up = (0, 1, 0) if abs(d[1]) < 0.95 else (1, 0, 0)
    u = (d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0])
    ul = math.sqrt(sum(c * c for c in u))
    u = tuple(c / ul for c in u)
    v = (u[1] * d[2] - u[2] * d[1], u[2] * d[0] - u[0] * d[2], u[0] * d[1] - u[1] * d[0])
    return u, v


def _prism(a, b, ring):
    """Призма между точками a и b; ring — список (cu, cv) сечения."""
    d = [b[i] - a[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in d))
    d = [c / ln for c in d]
    u, v = _basis(d)
    verts = []
    for p in (a, b):
        for cu, cv in ring:
            verts.append(tuple(p[i] + u[i] * cu + v[i] * cv for i in range(3)))
    n = len(ring)
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    faces.append(tuple(range(n - 1, -1, -1)))
    faces.append(tuple(range(n, 2 * n)))
    return verts, faces


def part_mesh(p):
    if p["t"] == "beam":
        w, h = p["w"] / 2, p["h"] / 2
        return _prism(p["a"], p["b"], [(-w, -h), (w, -h), (w, h), (-w, h)])
    if p["t"] == "box":
        c, s = p["c"], p["s"]
        return _prism([c[0], c[1], c[2] - s[2] / 2], [c[0], c[1], c[2] + s[2] / 2],
                      [(-s[0] / 2, -s[1] / 2), (s[0] / 2, -s[1] / 2), (s[0] / 2, s[1] / 2), (-s[0] / 2, s[1] / 2)])
    if p["t"] == "cyl":
        c, half = p["c"], p["l"] / 2
        ax = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}.get(p["ax"], (0, 0.34, 0.94))
        ring = [(p["r"] * math.cos(2 * math.pi * i / p["seg"]), p["r"] * math.sin(2 * math.pi * i / p["seg"]))
                for i in range(p["seg"])]
        return _prism([c[i] - ax[i] * half for i in range(3)], [c[i] + ax[i] * half for i in range(3)], ring)
    raise ValueError(p["t"])


def write_obj(path):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Электробагги 2-местный: шасси (генерируется generate_3d.py из chassis_geometry.py)\n")
        fh.write("# Единицы: мм. X — вправо, Y — вверх, Z — вперед\n")
        offset = 1
        for layer in LAYERS:
            fh.write(f"o {layer}\n")
            for p in (p for p in parts if p["g"] == layer):
                verts, faces = part_mesh(p)
                for vx in verts:
                    fh.write(f"v {vx[0]:.1f} {vx[1]:.1f} {vx[2]:.1f}\n")
                for fc in faces:
                    fh.write("f " + " ".join(str(offset + i) for i in fc) + "\n")
                offset += len(verts)
    print(f"OBJ сохранен в: {path} ({offset - 1} вершин)")


# =========================================================================
# ЭКСПОРТ HTML (Three.js)
# =========================================================================
def write_html(path):
    gears = {gname: (v, f) for gname, _, _, v, _, f in g.gearbox_table()[2]}
    specs = [
        ("База / Колея:", f"{g.WHEELBASE} мм / {g.TRACK} мм"),
        ("Клиренс (пол / подрамник):", f"280 / {g.REAR_RAIL_Y - 25:.0f} мм"),
        ("Подвеска:", "2 поперечных рычага, кулак 2108"),
        ("Мотор:", "QS138 70H (пик 13 кВт)"),
        ("Трансмиссия:", "цепь 15/15 → КПП 2108"),
        ("Скорость:", f"{gears['4'][0]:.0f} км/ч (4-я), {gears['5'][0]:.0f} (5-я)"),
        ("Тяга (2-я передача):", f"~{gears['2'][1] / 9.81:.0f} кгс"),
        ("Батареи:", "72V 48Ah + 48Ah"),
    ]
    spec_html = "\n".join(f'            <div class="spec-item"><span>{a}</span><span class="spec-val">{b}</span></div>'
                          for a, b in specs)
    btn_html = "\n".join(
        f'            <button class="toggle-btn active" onclick="toggleLayer(\'{k}\')">\n'
        f'                <span><span class="color-dot" style="background:{c}"></span>{n}</span>'
        f'<span id="st-{k}">ВКЛ</span>\n            </button>' for k, (n, c) in LAYERS.items())
    mats = ",\n            ".join(
        f'{k}: new THREE.MeshStandardMaterial({{ color: 0x{c:06x}, roughness: {r}, metalness: {m} }})'
        for k, (c, r, m) in MATERIALS.items())
    html = HTML_TEMPLATE.replace("%SPECS%", spec_html).replace("%BUTTONS%", btn_html) \
        .replace("%MATERIALS%", mats).replace("%PARTS%", json.dumps(parts, separators=(",", ":")))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"HTML 3D Viewer сохранен в: {path}")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Модель: Двухместный Электробагги</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background: #13171f; font-family: 'Segoe UI', Tahoma, sans-serif; color: #fff; }
        #canvas-container { width: 100vw; height: 100vh; display: block; }
        #ui-panel {
            position: absolute; top: 15px; left: 15px; width: 330px; max-width: calc(100vw - 62px);
            max-height: calc(100vh - 66px); overflow-y: auto;
            background: rgba(20, 24, 32, 0.92); backdrop-filter: blur(8px);
            padding: 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 100; font-size: 13px;
        }
        h2 { margin: 0 0 8px 0; font-size: 17px; color: #38bdf8; font-weight: 600; }
        .badge { display: inline-block; background: #0284c7; color: #fff; padding: 2px 7px; border-radius: 4px; font-size: 11px; margin-bottom: 12px; }
        .specs { margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; }
        .spec-item { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 4px; color: #94a3b8; }
        .spec-val { color: #f1f5f9; font-weight: 500; text-align: right; }
        .toggle-btn {
            display: flex; align-items: center; justify-content: space-between;
            background: #27303f; border: 1px solid #3b4758; color: #e2e8f0;
            padding: 7px 12px; border-radius: 6px; margin-bottom: 6px; cursor: pointer; width: 100%; box-sizing: border-box;
        }
        .toggle-btn:hover { background: #334155; }
        .toggle-btn.active { border-color: #38bdf8; background: #1e293b; }
        .color-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .legend { margin-top: 15px; font-size: 11px; color: #64748b; line-height: 1.5; }
        .legend a { color: #38bdf8; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui-panel">
        <h2>⚡ Электробагги 2-местный</h2>
        <span class="badge">RWD • IRS • Без трубогиба</span>
        <div class="specs">
%SPECS%
        </div>
        <div class="controls-group">
%BUTTONS%
        </div>
        <div class="legend">
            💡 ЛКМ — вращение, ПКМ — перемещение, колесо — масштаб.<br>
            Геометрия подвески и рулевого — по листам 07–13.
            <a href="drawings/07_suspension_corner_assembly.svg">Чертежи</a> ·
            <a href="buggy_frame_chassis.obj">OBJ</a>
        </div>
    </div>
    <div id="canvas-container"></div>
    <script>
        const PARTS = %PARTS%;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x13171f);
        scene.fog = new THREE.FogExp2(0x13171f, 0.00012);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 10, 12000);
        camera.position.set(2900, 1900, 3300);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(0, 450, 0);

        scene.add(new THREE.GridHelper(6000, 60, 0x334155, 0x1e293b));
        scene.add(new THREE.HemisphereLight(0xffffff, 0x334155, 0.7));
        const sun = new THREE.DirectionalLight(0xffffff, 0.9);
        sun.position.set(2000, 4000, 2000);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        Object.assign(sun.shadow.camera, { left: -2500, right: 2500, top: 2500, bottom: -2500, far: 9000 });
        scene.add(sun);
        const fill = new THREE.DirectionalLight(0x38bdf8, 0.4);
        fill.position.set(-2000, 2000, -2000);
        scene.add(fill);

        const MAT = {
            %MATERIALS%
        };
        MAT.tire.side = THREE.DoubleSide;
        const groups = {};

        function addMesh(p, geom, pos) {
            const mesh = new THREE.Mesh(geom, MAT[p.m]);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            if (pos) mesh.position.set(...pos);
            if (!groups[p.g]) { groups[p.g] = new THREE.Group(); scene.add(groups[p.g]); }
            groups[p.g].add(mesh);
            return mesh;
        }

        for (const p of PARTS) {
            if (p.t === 'beam') {
                const a = new THREE.Vector3(...p.a), b = new THREE.Vector3(...p.b);
                const mesh = addMesh(p, new THREE.BoxGeometry(p.w, p.h, a.distanceTo(b)));
                mesh.position.copy(a.clone().add(b).multiplyScalar(0.5));
                mesh.lookAt(b);
            } else if (p.t === 'box') {
                addMesh(p, new THREE.BoxGeometry(...p.s), p.c);
            } else if (p.t === 'cyl') {
                const geom = new THREE.CylinderGeometry(p.r, p.r, p.l, p.seg);
                if (p.ax === 'x') geom.rotateZ(Math.PI / 2);
                else if (p.ax === 'z') geom.rotateX(Math.PI / 2);
                else if (p.ax === 'steer') geom.rotateX(Math.PI / 2 - 0.35);
                addMesh(p, geom, p.c);
            }
        }

        window.toggleLayer = function(name) {
            const grp = groups[name];
            if (!grp) return;
            grp.visible = !grp.visible;
            const st = document.getElementById('st-' + name);
            st.innerText = grp.visible ? 'ВКЛ' : 'ВЫКЛ';
            st.parentElement.classList.toggle('active', grp.visible);
        };

        (function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        })();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""


def generate(output_dir):
    parts.clear()
    build_frame()
    build_cage()
    build_suspension()
    build_interior()
    build_drivetrain()
    build_plow()
    write_obj(os.path.join(output_dir, "buggy_frame_chassis.obj"))
    write_html(os.path.join(output_dir, "viewer.html"))


if __name__ == "__main__":
    generate(os.path.dirname(os.path.abspath(__file__)))
