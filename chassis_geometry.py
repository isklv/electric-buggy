#!/usr/bin/env python3
"""
Единый источник геометрии шасси электробагги: координаты шарниров подвески,
кинематика (развал, центр крена, подруливание), подбор пружин, рулевая трапеция,
тормоза и передаточные числа трансмиссии (мотор QS138 -> цепь -> КПП ВАЗ-2108).

Система координат (вид спереди на правый борт):
  X — поперёк, от оси симметрии наружу, мм
  Y — вверх от земли, мм
  Z — вдоль, вперёд от оси колеса, мм

Размеры донорских деталей ВАЗ-2108 (положение шаровой на кулаке, толщина
прилива под стойку и т.п.) — РАСЧЁТНЫЕ. Перед резкой металла снять с донора
и при расхождении поправить константы ниже: чертежи перестроятся сами.
"""
import math

# =========================================================================
# 1. ИСХОДНЫЕ ДАННЫЕ
# =========================================================================
TRACK = 1300                 # колея по центрам пятен контакта
WHEELBASE = 2050
WHEEL_RADIUS_STATIC = 280    # статический радиус 175/70 R13 под нагрузкой
TIRE_WIDTH = 175
RIM_ET = 35                  # диск 13x5J ET35, 4x98, DIA 58.6

HALF_TRACK = TRACK / 2
HUB_FACE_X = HALF_TRACK + RIM_ET  # привалочная плоскость ступицы

# --- Угол подвески (одинаковый спереди и сзади, правый борт) ---
# Нижняя шаровая 2108 (штатная, на кулаке)
LBJ = (595.0, 165.0)
# Верхний шарнир — ШС-наконечник M16 на адаптере АД-01 (вместо стойки McPherson)
UBJ = (525.0, 470.0)
# Внутренние оси качания рычагов (на подрамнике)
LOWER_INNER = (205.0, 230.0)
UPPER_INNER = (245.0, 490.0)
# Положение сайлентблоков вдоль Z (от оси колеса, + вперед).
# Верхний рычаг смещен назад на CASTER_OFFSET -> продольный наклон шкворня (кастер).
CASTER_OFFSET = 25
LOWER_ARM_Z = (120.0, -120.0)
UPPER_ARM_Z = (130.0 - CASTER_OFFSET, -130.0 - CASTER_OFFSET)
SHOCK_Z = -CASTER_OFFSET     # амортизатор проходит между лучами верхнего рычага

# Задняя ось: X/Y шарниров те же, по Z узлы разнесены, чтобы амортизатор не
# пересекал привод, а тяга схождения и верхние рычаги — корпус КПП (назад-вверх).
REAR_LOWER_ARM_Z = (80.0, -200.0)
REAR_UPPER_ARM_Z = (200.0, 20.0)
REAR_SHOCK_Z = -100.0
REAR_TOE_Z = 120.0           # АД-01 переставлены Л<->П, рычаг смотрит вперед
REAR_RAIL_Y = 205.0          # нижние балки заднего подрамника опущены под ШРУС

# Адаптер АД-01 на прилив кулака 2108 под стойку (замерить на доноре!)
LUG_BOLTS = ((520.0, 345.0), (511.0, 405.0))  # центры болтов M12x1.25
LUG_THICKNESS = 28.0
ADAPTER_PLATE = 6.0
# Контур щеки АД-01 (вид вдоль оси машины, X/Y правого борта)
ADAPTER_OUTLINE = ((492, 322), (546, 322), (543, 428), (547, 470), (538, 494), (512, 494),
                   (503, 470), (486, 428))
OUTER_CV_CENTER = (575.0, 280.0)  # центр наружного ШРУС (задние, ведущие)
INNER_CV_X = 130.0                # центр внутреннего ШРУС от оси машины (по КПП)

# Рама: широкая часть (1100) обрывается перед колесами
FRAME_HALF_WIDTH = 550
FRAME_CROSSBEAM_FROM_AXLE = 400   # поперечина пола от оси колес
STEER_LOCK_INNER = 38.0           # угол внутреннего колеса, °

# Наконечник рулевой тяги / тяги схождения на рычаге адаптера (вид спереди)
STEER_ARM_LENGTH = 120       # вынос рычага назад от оси шкворня (вид сверху)
STEER_ARM_Y = 400
STEER_Z = -STEER_ARM_LENGTH  # рейка (и тяга схождения сзади) — за осью колес
# Рулевая колонка: (X, Y, Z от передней оси) — шестерня, кардан 2, кардан 1, центр руля
COLUMN_POINTS = ((-110, 398, -130), (-200, 560, -430), (-260, 690, -760), (-275, 820, -1060))

# Амортизатор (койловер от квадроцикла 250-300cc)
SHOCK_EYE_TO_EYE = 350
SHOCK_STROKE = 110
SHOCK_LOWER_FRAC = 0.65      # точка крепления на нижнем рычаге (доля от внутренней оси)
SHOCK_INCLINE_DEG = 14       # наклон к вертикали (верх к центру машины)

BUMP_TRAVEL = 100            # ход сжатия колеса
DROOP_TRAVEL = 80            # ход отбоя колеса

# --- Массы ---
CURB_MASS = 490              # снаряженная, без отвала, 1 АКБ
CREW_MASS = 160
PLOW_MASS = 60
FRONT_SHARE = 0.45           # доля полной массы на передней оси (без отвала)
UNSPRUNG_FRONT = 32          # на угол: кулак+ступица+тормоз+колесо+1/2 рычагов
UNSPRUNG_REAR = 36           # + половина привода
RIDE_FREQ_FRONT = 1.45       # Гц (у задней выше — гасит галопирование)
RIDE_FREQ_REAR = 1.60
CG_HEIGHT = 500

# --- Тормоза (4 одинаковых узла ВАЗ-2108) ---
CALIPER_PISTON_D = 48.0      # мм, суппорт 2108
DISC_EFF_RADIUS = 0.098      # м, эффективный радиус трения диска 2108
PAD_MU = 0.38
MASTER_CYL_D = 20.64         # мм, ГТЦ 2108 (сверить маркировку)
PEDAL_RATIO = 4.5            # без вакуумного усилителя
TARGET_DECEL_G = 0.8

# --- Трансмиссия ---
MOTOR_RPM_MAX = 4400
MOTOR_RPM_CRUISE = 3800
MOTOR_TORQUE_PEAK = 90.0     # Нм на роторе QS138 70H V3
QS_REDUCTION = 2.35          # встроенный редуктор QS138 V3
CHAIN_DRIVE = 15             # звезда мотора, цепь 520
CHAIN_DRIVEN = 15            # звезда промвала (на шлицах первичного вала КПП)
GEARBOX_INPUT_TORQUE_LIMIT = 135  # Нм — ограничить током фаз в контроллере
GEARS_2108 = {"1": 3.636, "2": 1.950, "3": 1.357, "4": 0.941, "5": 0.784}
FINAL_DRIVE_2108 = 3.94      # главная пара 2108 (бывает 3.7 / 4.1 — сверить)
GEARBOX_EFF = 0.93
WHEEL_RADIUS_DYN = 0.289


# =========================================================================
# 2. ВСПОМОГАТЕЛЬНАЯ ГЕОМЕТРИЯ
# =========================================================================
def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _add(a, b): return (a[0] + b[0], a[1] + b[1])
def _len(v): return math.hypot(v[0], v[1])
def _rot(v, ang): return (v[0] * math.cos(ang) - v[1] * math.sin(ang),
                          v[0] * math.sin(ang) + v[1] * math.cos(ang))
def _angle(v): return math.atan2(v[1], v[0])


def _line_intersect(p1, p2, p3, p4):
    d = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
    if abs(d) < 1e-9:
        return None
    t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / d
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


def _circle_intersect(c0, r0, c1, r1, near):
    d = _len(_sub(c1, c0))
    a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(max(r0 ** 2 - a ** 2, 0.0))
    ex = ((c1[0] - c0[0]) / d, (c1[1] - c0[1]) / d)
    m = (c0[0] + a * ex[0], c0[1] + a * ex[1])
    s1 = (m[0] - h * ex[1], m[1] + h * ex[0])
    s2 = (m[0] + h * ex[1], m[1] - h * ex[0])
    return s1 if _len(_sub(s1, near)) < _len(_sub(s2, near)) else s2


def kingpin_inclination_deg():
    return math.degrees(math.atan2(LBJ[0] - UBJ[0], UBJ[1] - LBJ[1]))


def scrub_radius():
    # пересечение оси шкворня с землей (Y=0)
    k = (LBJ[0] - UBJ[0]) / (UBJ[1] - LBJ[1])
    ground_x = LBJ[0] + LBJ[1] * k
    return HALF_TRACK - ground_x


def steer_point_front_view():
    """Наконечник тяги в проекции на вид спереди: лежит на оси шкворня на высоте
    STEER_ARM_Y, смещён внутрь на величину аккермановского наклона рычага."""
    k = (LBJ[0] - UBJ[0]) / (UBJ[1] - LBJ[1])
    x_kp = LBJ[0] - (STEER_ARM_Y - LBJ[1]) * k
    return (x_kp - STEER_ARM_LENGTH * math.tan(math.radians(ackermann_arm_angle_deg())),
            STEER_ARM_Y)


def ackermann_arm_angle_deg():
    """Угол рычага к продольной оси для 100% Аккермана (рычаг за осью колеса)."""
    k = (LBJ[0] - UBJ[0]) / (UBJ[1] - LBJ[1])
    x_kp = LBJ[0] - (STEER_ARM_Y - LBJ[1]) * k
    return math.degrees(math.atan2(x_kp, WHEELBASE))


def shock_points():
    lower = _add(LOWER_INNER, tuple(SHOCK_LOWER_FRAC * c for c in _sub(LBJ, LOWER_INNER)))
    static_len = SHOCK_EYE_TO_EYE - DROOP_TRAVEL * 0.60  # уточняется ниже по факт. MR
    a = math.radians(SHOCK_INCLINE_DEG)
    upper = (lower[0] - static_len * math.sin(a), lower[1] + static_len * math.cos(a))
    return lower, upper


# =========================================================================
# 3. КИНЕМАТИКА ДВОЙНЫХ ПОПЕРЕЧНЫХ РЫЧАГОВ (вид спереди)
# =========================================================================
def solve_position(theta):
    """Поворот нижнего рычага на theta (рад). Возвращает словарь положений."""
    lower_len = _len(_sub(LBJ, LOWER_INNER))
    upper_len = _len(_sub(UBJ, UPPER_INNER))
    knuckle_len = _len(_sub(UBJ, LBJ))
    b = _add(LOWER_INNER, _rot(_sub(LBJ, LOWER_INNER), theta))
    d = _circle_intersect(UPPER_INNER, upper_len, b, knuckle_len, near=UBJ)
    phi = _angle(_sub(d, b)) - _angle(_sub(UBJ, LBJ))

    def carry(p):  # точка, жестко связанная с кулаком
        return _add(b, _rot(_sub(p, LBJ), phi))

    wheel = carry((HALF_TRACK, WHEEL_RADIUS_STATIC))
    contact = carry((HALF_TRACK, 0.0))
    s_low, s_up = shock_points()
    s_low_new = _add(LOWER_INNER, _rot(_sub(s_low, LOWER_INNER), theta))
    return {
        "lbj": b, "ubj": d, "phi": phi,
        "wheel": wheel, "contact": contact,
        "travel": wheel[1] - WHEEL_RADIUS_STATIC,
        "camber_deg": -math.degrees(phi),
        "shock_len": _len(_sub(s_up, s_low_new)),
        "steer": carry(steer_point_front_view()),
    }


def sweep(step_mm=10):
    """Ход колеса от -DROOP до +BUMP. Подбирает theta под заданный ход."""
    out = []
    for target in range(-DROOP_TRAVEL, BUMP_TRAVEL + 1, step_mm):
        lo, hi = -0.8, 0.8
        for _ in range(60):
            mid = (lo + hi) / 2
            if solve_position(mid)["travel"] < target:
                lo = mid
            else:
                hi = mid
        p = solve_position((lo + hi) / 2)
        p["target"] = target
        out.append(p)
    return out


def roll_center_height():
    ic = _line_intersect(LOWER_INNER, LBJ, UPPER_INNER, UBJ)
    contact = (HALF_TRACK, 0.0)
    if ic is None:
        return None, None
    rc = _line_intersect(contact, ic, (0.0, 0.0), (0.0, 1.0))
    return ic, rc[1]


def ideal_tie_rod_inner():
    """Внутренний шарнир тяги, при котором подруливание на ходе минимально:
    центр окружности, наилучшим образом проходящей через траекторию наконечника."""
    pts = [p["steer"] for p in sweep(10)]
    # МНК-окружность (метод Каса)
    n = len(pts)
    sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
    sxx = sum(p[0] ** 2 for p in pts); syy = sum(p[1] ** 2 for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    sxz = sum(p[0] * (p[0] ** 2 + p[1] ** 2) for p in pts)
    syz = sum(p[1] * (p[0] ** 2 + p[1] ** 2) for p in pts)
    sz = sum(p[0] ** 2 + p[1] ** 2 for p in pts)
    # [sxx sxy sx][a]   [sxz]
    # [sxy syy sy][b] = [syz]
    # [sx  sy  n ][c]   [sz ]
    m = [[sxx, sxy, sx, sxz], [sxy, syy, sy, syz], [sx, sy, n, sz]]
    for i in range(3):
        piv = max(range(i, 3), key=lambda r: abs(m[r][i]))
        m[i], m[piv] = m[piv], m[i]
        for r in range(3):
            if r != i:
                f = m[r][i] / m[i][i]
                m[r] = [m[r][k] - f * m[i][k] for k in range(4)]
    a, b, c = (m[i][3] / m[i][i] for i in range(3))
    cx, cy = a / 2, b / 2
    radius = math.sqrt(c + cx ** 2 + cy ** 2)
    return (cx, cy), radius


def bump_steer_table(inner, length):
    rows = []
    for p in sweep(20):
        err = _len(_sub(p["steer"], inner)) - length  # мм рассогласования
        toe_deg = math.degrees(err / STEER_ARM_LENGTH)
        rows.append((p["target"], toe_deg))
    return rows


# =========================================================================
# 4. ПРУЖИНЫ, ТОРМОЗА, ТРАНСМИССИЯ
# =========================================================================
def motion_ratio():
    pts = sweep(10)
    mid = next(i for i, p in enumerate(pts) if p["target"] == 0)
    d_shock = pts[mid - 1]["shock_len"] - pts[mid + 1]["shock_len"]
    d_wheel = pts[mid + 1]["travel"] - pts[mid - 1]["travel"]
    return d_shock / d_wheel


def shock_stroke_used():
    pts = sweep(10)
    return pts[0]["shock_len"] - pts[-1]["shock_len"], pts[0]["shock_len"], pts[-1]["shock_len"]


def corner_sprung_masses():
    gross = CURB_MASS + CREW_MASS
    front_axle = gross * FRONT_SHARE
    rear_axle = gross - front_axle
    # отвал на вылете ~0.75 м перед передней осью
    plow_front = PLOW_MASS * (WHEELBASE + 750) / WHEELBASE
    return {
        "front": front_axle / 2 - UNSPRUNG_FRONT,
        "rear": rear_axle / 2 - UNSPRUNG_REAR,
        "front_plow": (front_axle + plow_front) / 2 - UNSPRUNG_FRONT,
        "rear_plow": (rear_axle - (plow_front - PLOW_MASS)) / 2 - UNSPRUNG_REAR,
    }


def spring_rate(mass, freq):
    wheel_rate = mass * (2 * math.pi * freq) ** 2 / 1000.0  # Н/мм
    mr = motion_ratio()
    return wheel_rate, wheel_rate / mr ** 2


def brake_report():
    gross = CURB_MASS + CREW_MASS
    a_piston = math.pi * (CALIPER_PISTON_D / 2) ** 2           # мм2
    a_master = math.pi * (MASTER_CYL_D / 2) ** 2
    torque_per_mpa = 2 * PAD_MU * a_piston * DISC_EFF_RADIUS   # Нм на МПа (1 суппорт)
    total_force = gross * 9.81 * TARGET_DECEL_G
    total_torque = total_force * WHEEL_RADIUS_STATIC / 1000
    pressure = total_torque / (4 * torque_per_mpa)
    pedal_force = pressure * a_master / PEDAL_RATIO
    # распределение по осям при торможении
    transfer = gross * TARGET_DECEL_G * CG_HEIGHT / WHEELBASE
    front_dyn = gross * FRONT_SHARE + transfer
    return {
        "pressure_mpa": pressure, "pedal_force_n": pedal_force,
        "front_dyn_share": front_dyn / gross,
        "rear_pressure_ratio": (1 - front_dyn / gross) / (front_dyn / gross),
    }


def gearbox_table():
    chain = CHAIN_DRIVEN / CHAIN_DRIVE
    input_rpm = MOTOR_RPM_MAX / QS_REDUCTION / chain
    input_torque = min(MOTOR_TORQUE_PEAK * QS_REDUCTION * chain, GEARBOX_INPUT_TORQUE_LIMIT)
    rows = []
    for g, ratio in GEARS_2108.items():
        total = QS_REDUCTION * chain * ratio * FINAL_DRIVE_2108
        v = MOTOR_RPM_MAX / total * 2 * math.pi * WHEEL_RADIUS_DYN * 60 / 1000
        wheel_torque = input_torque * ratio * FINAL_DRIVE_2108 * GEARBOX_EFF * 0.97
        rows.append((g, ratio, total, v, wheel_torque, wheel_torque / WHEEL_RADIUS_DYN))
    return input_rpm, input_torque, rows


def caster_deg():
    return math.degrees(math.atan2(CASTER_OFFSET, UBJ[1] - LBJ[1]))


def kingpin_x_at(y):
    k = (LBJ[0] - UBJ[0]) / (UBJ[1] - LBJ[1])
    return LBJ[0] - (y - LBJ[1]) * k


def steering_geometry():
    """Угол наружного колеса, радиус разворота, нужный ход рейки."""
    kp = kingpin_x_at(WHEEL_RADIUS_STATIC)
    inner = math.radians(STEER_LOCK_INNER)
    outer = math.atan(1 / (1 / math.tan(inner) + 2 * kp / WHEELBASE))
    radius = WHEELBASE / math.sin(outer) + (HALF_TRACK - kp)
    a0 = math.radians(ackermann_arm_angle_deg())
    rack_inner = STEER_ARM_LENGTH * (math.sin(a0 + inner) - math.sin(a0))
    rack_outer = STEER_ARM_LENGTH * (math.sin(a0) - math.sin(a0 - outer))
    return {"kingpin_x": kp, "outer_deg": math.degrees(outer),
            "turn_radius": radius, "rack_travel": max(rack_inner, rack_outer),
            "lock_envelope": math.hypot(TIRE_WIDTH / 2, WHEEL_RADIUS_STATIC + 9) + 40}


def driveshaft_report():
    lens = []
    for p in sweep(10):
        phi = p["phi"]
        c = _add(p["lbj"], _rot(_sub(OUTER_CV_CENTER, LBJ), phi))
        lens.append((p["target"], _len(_sub(c, (INNER_CV_X, OUTER_CV_CENTER[1]))),
                     math.degrees(math.atan2(c[1] - OUTER_CV_CENTER[1], c[0] - INNER_CV_X))))
    static = next(l for t, l, a in lens if t == 0)
    return static, min(l for _, l, _ in lens) - static, max(l for _, l, _ in lens) - static, \
        max(abs(a) for _, _, a in lens)


def chain_center_distance(links=52, pitch=15.875):
    # равные звезды: C = (L - z) * p / 2
    assert CHAIN_DRIVE == CHAIN_DRIVEN
    return (links - CHAIN_DRIVE) * pitch / 2


def lower_arm_check(g_load=3.0):
    """Изгиб луча нижнего рычага в точке амортизатора при ударе g_load (на угол)."""
    wheel_force = g_load * (corner_sprung_masses()["rear"] + UNSPRUNG_REAR) * 9.81
    arm = _len(_sub(LBJ, LOWER_INNER))
    moment_per_leg = wheel_force * arm * (1 - SHOCK_LOWER_FRAC) / 2  # Н*мм, 2 луча
    def w_box(b, h, t):
        return (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / (6 * h)
    rows = []
    for name, b, h, t in (("25x25x2.0", 25, 25, 2.0), ("30x30x2.5", 30, 30, 2.5),
                          ("40x20x2.0 (на ребро)", 20, 40, 2.0), ("40x40x2.0", 40, 40, 2.0)):
        rows.append((name, moment_per_leg / w_box(b, h, t)))
    return wheel_force, rows


# =========================================================================
# 5. ОТЧЕТ
# =========================================================================
def report():
    print("=" * 66)
    print(" ГЕОМЕТРИЯ УГЛА ПОДВЕСКИ (единая для всех 4 колес)")
    print("=" * 66)
    ic, rc = roll_center_height()
    print(f"Наклон оси шкворня (KPI): {kingpin_inclination_deg():.1f}°")
    print(f"Плечо обкатки: {scrub_radius():.1f} мм (положительное)")
    print(f"Мгновенный центр: X={ic[0]:.0f}, Y={ic[1]:.0f} мм")
    print(f"Высота центра крена: {rc:.0f} мм")
    print(f"Длина нижнего рычага (проекция): {_len(_sub(LBJ, LOWER_INNER)):.0f} мм")
    print(f"Длина верхнего рычага (проекция): {_len(_sub(UBJ, UPPER_INNER)):.0f} мм")
    print("\nХод   | Развал   | Изм. колеи (полуколея)")
    for p in sweep(20):
        print(f"{p['target']:+5d} | {p['camber_deg']:+6.2f}° | {p['contact'][0] - HALF_TRACK:+6.1f} мм")

    inner, length = ideal_tie_rod_inner()
    print(f"\nНаконечник тяги (вид спереди): X={steer_point_front_view()[0]:.0f}, Y={STEER_ARM_Y}")
    print(f"Угол рычага по Аккерману: {ackermann_arm_angle_deg():.1f}° внутрь")
    print(f"ИДЕАЛЬНЫЙ внутренний шарнир тяги: X={inner[0]:.0f}, Y={inner[1]:.0f} мм; "
          f"длина тяги в проекции {length:.0f} мм")
    print(f"=> расстояние между внутренними шарнирами рейки: {2 * inner[0]:.0f} мм")
    print("Подруливание на ходе (схождение одного колеса):")
    for t, toe in bump_steer_table(inner, length):
        print(f"  {t:+4d} мм: {toe:+.3f}°")

    print("\n" + "=" * 66)
    print(" ПРУЖИНЫ И АМОРТИЗАТОРЫ")
    print("=" * 66)
    mr = motion_ratio()
    used, ext, comp = shock_stroke_used()
    s_low, s_up = shock_points()
    print(f"Кинематическое отношение (амортизатор/колесо): {mr:.3f}")
    print(f"Длина амортизатора: отбой {ext:.0f} / сжатие {comp:.0f} мм, задействовано {used:.0f} мм "
          f"из {SHOCK_STROKE} (L={SHOCK_EYE_TO_EYE})")
    print(f"Нижнее ухо: X={s_low[0]:.0f} Y={s_low[1]:.0f}; верхнее: X={s_up[0]:.0f} Y={s_up[1]:.0f}")
    m = corner_sprung_masses()
    for key, label, f in (("front", "Перед", RIDE_FREQ_FRONT), ("rear", "Зад", RIDE_FREQ_REAR)):
        wr, sr = spring_rate(m[key], f)
        print(f"{label}: подрессоренная на угол {m[key]:.0f} кг, жёсткость колеса {wr:.1f} Н/мм, "
              f"ПРУЖИНА {sr:.0f} Н/мм ({sr / 9.81:.1f} кгс/мм)")
        mp = m[key + "_plow"]
        print(f"   с отвалом: {mp:.0f} кг на угол -> частота {math.sqrt(wr * 1000 / mp) / (2 * math.pi):.2f} Гц")

    print("\nПрочность нижнего рычага (удар 3g на угол, σт Ст20 = 245 МПа, 09Г2С = 325 МПа):")
    f, rows = lower_arm_check()
    for name, sigma in rows:
        print(f"  {name:<22} σ = {sigma:5.0f} МПа  запас {245 / sigma:.2f}")

    print("\n" + "=" * 66)
    print(" РУЛЕВОЕ")
    print("=" * 66)
    st = steering_geometry()
    print(f"Кастер: {caster_deg():.1f}° (верхний рычаг смещен назад на {CASTER_OFFSET} мм)")
    print(f"Внутреннее колесо {STEER_LOCK_INNER:.0f}°, наружное {st['outer_deg']:.1f}° (100% Аккерман)")
    print(f"Радиус разворота по наружному колесу: {st['turn_radius'] / 1000:.2f} м")
    print(f"Ход рейки от центра в каждую сторону: {st['rack_travel']:.0f} мм")

    print("\n" + "=" * 66)
    print(" ТОРМОЗА (4 x ВАЗ-2108, без вакуумного усилителя)")
    print("=" * 66)
    b = brake_report()
    print(f"Давление для {TARGET_DECEL_G} g: {b['pressure_mpa']:.2f} МПа")
    print(f"Усилие на педали (передаточное {PEDAL_RATIO}): {b['pedal_force_n']:.0f} Н "
          f"({b['pedal_force_n'] / 9.81:.0f} кгс)")
    print(f"Динамическая нагрузка на перед при торможении: {b['front_dyn_share'] * 100:.0f}%")
    print(f"Давление в заднем контуре должно быть ~{b['rear_pressure_ratio'] * 100:.0f}% от переднего "
          f"-> регулируемый клапан в задний контур")

    print("\n" + "=" * 66)
    print(" ТРАНСМИССИЯ: QS138 -> цепь 520 -> КПП 2108")
    print("=" * 66)
    rpm, tq, rows = gearbox_table()
    print(f"Цепь 520 {CHAIN_DRIVE}T/{CHAIN_DRIVEN}T, 52 звена -> межосевое {chain_center_distance():.1f} мм")
    static, pmin, pmax, ang = driveshaft_report()
    print(f"Привод: между центрами ШРУС {static:.0f} мм, осевой ход {pmin:+.1f}/{pmax:+.1f} мм, "
          f"угол до {ang:.1f}°")
    print(f"Цепь {CHAIN_DRIVE}T/{CHAIN_DRIVEN}T, обороты первичного вала до {rpm:.0f} об/мин, "
          f"момент ограничен до {tq:.0f} Нм")
    print("Пер. | i КПП | i общ  | V max, км/ч | Момент на колесах, Нм | Тяга, Н")
    for g, r, tot, v, wt, f in rows:
        print(f"  {g}  | {r:5.3f} | {tot:6.2f} | {v:11.1f} | {wt:21.0f} | {f:6.0f}")


if __name__ == "__main__":
    report()
