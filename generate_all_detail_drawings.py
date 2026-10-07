#!/usr/bin/env python3
"""
Генератор полного комплекта деталировочных чертежей узлов электробагги
1. Передние А-рычаги подвески (02_front_suspension_arms.svg)
2. Задняя независимая подвеска IRS (03_rear_irs_arms.svg)
3. Моторная плита QS138 и узел дифференциала (04_powertrain_motor_plate.svg)
4. Поворотный снегоотвал и пружинная навеска (05_snow_plow_assembly.svg)
5. Съемный термобокс АКБ 72V (06_battery_box_thermal.svg)
"""
import os

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drawings")
os.makedirs(out_dir, exist_ok=True)

def write_svg(filename, content):
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Чертеж сохранен: {path}")

# =========================================================================
# ЧЕРТЕЖ 2: ПЕРЕДНИЕ А-РЫЧАГИ (FRONT SUSPENSION ARMS)
# =========================================================================
svg_front_arms = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950" style="background:#0f172a; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.8"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  <rect x="20" y="20" width="1360" height="910" fill="none" stroke="#38bdf8" stroke-width="2"/>
  
  <!-- Заголовок -->
  <text x="50" y="65" fill="#38bdf8" font-size="22" font-weight="bold">ДЕТАЛИРОВОЧНЫЙ ЧЕРТЁЖ: РЫЧАГИ ПЕРЕДНЕЙ ПОДВЕСКИ</text>
  <text x="50" y="90" fill="#94a3b8" font-size="14">Узлы: ВАЗ-2108 (сайлентблоки ромашки + шаровые опоры 2108). Материал: труба 25х25х2.0 / лист 3 мм</text>

  <!-- Штамп -->
  <g transform="translate(980, 800)">
    <rect width="380" height="110" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="15" y="30" fill="#94a3b8" font-size="12">Узел:</text>
    <text x="100" y="30" fill="#f8fafc" font-size="14" font-weight="bold">Передняя подвеска (А-рычаги)</text>
    <text x="15" y="60" fill="#94a3b8" font-size="12">Материал:</text>
    <text x="100" y="60" fill="#f8fafc" font-size="13">Труба 25х25х2 (Сталь 20) + лист 3мм</text>
    <text x="15" y="90" fill="#94a3b8" font-size="12">Чертеж:</text>
    <text x="100" y="90" fill="#38bdf8" font-size="13">02-SUSP-FRONT-01 / Масштаб 1:2.5</text>
  </g>

  <!-- 1. НИЖНИЙ А-РЫЧАГ (ВИД СВЕРХУ) -->
  <g transform="translate(100, 150)">
    <text x="0" y="0" fill="#10b981" font-size="18" font-weight="bold">1. НИЖНИЙ А-ОБРАЗНЫЙ РЫЧАГ (L = 380 мм, База = 240 мм)</text>
    
    <!-- Втулки сайлентблоков на раме (2 шт) -->
    <!-- Втулка 1 (X=50, Y=60) -->
    <rect x="30" y="35" width="40" height="50" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="50" cy="60" r="16" fill="#1e293b" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="50" cy="60" r="6" fill="#38bdf8"/>
    <text x="15" y="105" fill="#94a3b8" font-size="11">Втулка D=34 (под 2108)</text>

    <!-- Втулка 2 (X=50, Y=300) -->
    <rect x="30" y="275" width="40" height="50" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="50" cy="300" r="16" fill="#1e293b" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="50" cy="300" r="6" fill="#38bdf8"/>

    <!-- Трубы 25х25, сходящиеся к фланцу шаровой -->
    <!-- Луч 1 -->
    <line x1="50" y1="60" x2="430" y2="180" stroke="#10b981" stroke-width="14" stroke-linecap="round"/>
    <!-- Луч 2 -->
    <line x1="50" y1="300" x2="430" y2="180" stroke="#10b981" stroke-width="14" stroke-linecap="round"/>
    <!-- Поперечина жесткости (усилитель под амортизатор) -->
    <line x1="260" y1="125" x2="260" y2="235" stroke="#10b981" stroke-width="12"/>

    <!-- Кронштейн крепления амортизатора (на расстоянии 260 мм от оси рамы) -->
    <rect x="245" y="160" width="30" height="40" rx="3" fill="#f59e0b" stroke="#fbbf24" stroke-width="2"/>
    <circle cx="260" cy="180" r="5" fill="#0f172a"/>
    <text x="210" y="150" fill="#fbbf24" font-size="11" font-weight="bold">Уши амортизатора (отв. 10.5)</text>

    <!-- Фланец шаровой опоры ВАЗ-2108 (треугольная пластина из листа 4 мм) -->
    <polygon points="410,140 470,180 410,220" fill="#475569" stroke="#94a3b8" stroke-width="2"/>
    <!-- Отверстие под палец шаровой D=30 -->
    <circle cx="430" cy="180" r="14" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
    <!-- Крепежные отверстия шаровой М8 (2 шт) -->
    <circle cx="430" cy="155" r="4" fill="#38bdf8"/>
    <circle cx="430" cy="205" r="4" fill="#38bdf8"/>
    <text x="445" y="185" fill="#f8fafc" font-size="11">Шаровая 2108</text>

    <!-- РАЗМЕРНЫЕ ЛИНИИ -->
    <!-- Длина рычага: 380 мм -->
    <line x1="50" y1="350" x2="430" y2="350" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <line x1="50" y1="300" x2="50" y2="360" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="430" y1="180" x2="430" y2="360" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="240" y="342" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">380 мм (ВЫЛЕТ РЫЧАГА)</text>

    <!-- База сайлентблоков: 240 мм -->
    <line x1="0" y1="60" x2="0" y2="300" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <line x1="0" y1="60" x2="40" y2="60" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="0" y1="300" x2="40" y2="300" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="-10" y="185" fill="#38bdf8" font-size="13" font-weight="bold" transform="rotate(-90, -10, 185)" text-anchor="middle">240 мм (БАЗА)</text>
  </g>

  <!-- 2. ВЕРХНИЙ А-РЫЧАГ (L = 310 мм, База = 200 мм) -->
  <g transform="translate(720, 150)">
    <text x="0" y="0" fill="#38bdf8" font-size="18" font-weight="bold">2. ВЕРХНИЙ А-ОБРАЗНЫЙ РЫЧАГ (L = 310 мм, База = 200 мм)</text>
    
    <!-- Втулки сайлентблоков -->
    <rect x="30" y="55" width="40" height="45" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="50" cy="78" r="14" fill="#1e293b" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="50" cy="78" r="5" fill="#38bdf8"/>

    <rect x="30" y="255" width="40" height="45" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="50" cy="278" r="14" fill="#1e293b" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="50" cy="278" r="5" fill="#38bdf8"/>

    <!-- Трубы 25х25 -->
    <line x1="50" y1="78" x2="360" y2="178" stroke="#0284c7" stroke-width="12" stroke-linecap="round"/>
    <line x1="50" y1="278" x2="360" y2="178" stroke="#0284c7" stroke-width="12" stroke-linecap="round"/>

    <!-- Фланец верхней шаровой -->
    <polygon points="340,145 395,178 340,211" fill="#475569" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="360" cy="178" r="12" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="360" cy="158" r="4" fill="#38bdf8"/>
    <circle cx="360" cy="198" r="4" fill="#38bdf8"/>

    <!-- РАЗМЕРНЫЕ ЛИНИИ ВЕРХНЕГО РЫЧАГА -->
    <line x1="50" y1="330" x2="360" y2="330" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <text x="205" y="322" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">310 мм (ВЫЛЕТ ВЕРХНЕГО РЫЧАГА)</text>

    <line x1="0" y1="78" x2="0" y2="278" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <text x="-10" y="178" fill="#38bdf8" font-size="13" font-weight="bold" transform="rotate(-90, -10, 178)" text-anchor="middle">200 мм (БАЗА)</text>

    <!-- Пояснение про кинематику -->
    <g transform="translate(50, 390)">
      <rect width="450" height="130" fill="#1e293b" stroke="#64748b" stroke-width="1" rx="4"/>
      <text x="15" y="25" fill="#38bdf8" font-size="13" font-weight="bold">★ ИНЖЕНЕРНЫЕ ТРЕБОВАНИЯ К ПОДВЕСКЕ:</text>
      <text x="15" y="50" fill="#f8fafc" font-size="11">1. Разница длин (380 мм низ vs 310 мм верх): дает отрицательный развал (-1.5°)</text>
      <text x="15" y="70" fill="#94a3b8" font-size="11">   в поворотах при крене кузова, повышая сцепление колеса с грунтом.</text>
      <text x="15" y="90" fill="#f8fafc" font-size="11">2. Кастер (угол продольного наклона оси поворота): выставлять +4°...+5°</text>
      <text x="15" y="110" fill="#94a3b8" font-size="11">   смещением верхнего рычага назад на 25 мм для самовозврата руля в ноль.</text>
    </g>
  </g>
</svg>"""
write_svg("02_front_suspension_arms.svg", svg_front_arms)

# =========================================================================
# ЧЕРТЕЖ 3: ЗАДНЯЯ ПОДВЕСКА IRS И РЕГУЛИРОВКА СХОЖДЕНИЯ
# =========================================================================
svg_rear_irs = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950" style="background:#0f172a; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.8"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  <rect x="20" y="20" width="1360" height="910" fill="none" stroke="#38bdf8" stroke-width="2"/>
  
  <text x="50" y="65" fill="#38bdf8" font-size="22" font-weight="bold">ДЕТАЛИРОВОЧНЫЙ ЧЕРТЁЖ: ЗАДНЯЯ НЕЗАВИСИМАЯ ПОДВЕСКА (IRS)</text>
  <text x="50" y="90" fill="#94a3b8" font-size="14">Схема узла: кулак ВАЗ-2108, привод ШРУС, рулевой сгон для фиксации и регулировки схождения</text>

  <!-- Штамп -->
  <g transform="translate(980, 800)">
    <rect width="380" height="110" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="15" y="30" fill="#94a3b8" font-size="12">Узел:</text>
    <text x="100" y="30" fill="#f8fafc" font-size="14" font-weight="bold">Задняя подвеска IRS</text>
    <text x="15" y="60" fill="#94a3b8" font-size="12">Компоненты:</text>
    <text x="100" y="60" fill="#f8fafc" font-size="13">Кулак 2108 + ШРУС + Сгон М16</text>
    <text x="15" y="90" fill="#94a3b8" font-size="12">Чертеж:</text>
    <text x="100" y="90" fill="#38bdf8" font-size="13">03-SUSP-REAR-IRS / Масштаб 1:2.5</text>
  </g>

  <!-- Схема сбора одного борта (Вид сзади / в плане) -->
  <g transform="translate(80, 160)">
    <!-- Рама (сечение лонжерона 50х50) -->
    <rect x="0" y="100" width="50" height="50" fill="#d97706" stroke="#f59e0b" stroke-width="2"/>
    <text x="12" y="130" fill="#fff" font-size="11" font-weight="bold">50x50</text>
    <rect x="20" y="20" width="40" height="40" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
    <text x="25" y="45" fill="#fff" font-size="10">40x40</text>

    <!-- Приводной вал ШРУС (от центрального дифференциала к ступице) -->
    <line x1="-60" y1="125" x2="420" y2="125" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
    <circle cx="0" cy="125" r="22" fill="#475569" stroke="#cbd5e1" stroke-width="2"/>
    <text x="-45" y="165" fill="#94a3b8" font-size="11">Внутренний ШРУС</text>
    <circle cx="420" cy="125" r="22" fill="#475569" stroke="#cbd5e1" stroke-width="2"/>
    <text x="390" y="165" fill="#94a3b8" font-size="11">Внешний ШРУС</text>

    <!-- Нижний рычаг (от рамы Y=125 к низу кулака Y=160) -->
    <line x1="50" y1="125" x2="420" y2="185" stroke="#10b981" stroke-width="12" stroke-linecap="round"/>
    <!-- Верхний рычаг (от рамы Y=40 к верху кулака Y=65) -->
    <line x1="60" y1="40" x2="420" y2="65" stroke="#10b981" stroke-width="12" stroke-linecap="round"/>

    <!-- Задний поворотный кулак ВАЗ-2108 (вертикальная стойка) -->
    <rect x="410" y="55" width="24" height="140" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <!-- Тормозной диск и ступица -->
    <rect x="434" y="25" width="16" height="200" rx="3" fill="#cbd5e1" stroke="#fff" stroke-width="2"/>
    <!-- Колесо R13 (сечение) -->
    <rect x="450" y="0" width="120" height="250" rx="10" fill="#1e293b" stroke="#64748b" stroke-width="2.5"/>
    <text x="475" y="130" fill="#f8fafc" font-size="14" font-weight="bold">175/70 R13</text>

    <!-- УЗЕЛ ФИКСАЦИИ СХОЖДЕНИЯ (РУЛЕВОЙ СГОН) -->
    <!-- Сошка кулака (направлена вперед/вглубь) -->
    <path d="M 410,125 L 340,195" stroke="#ef4444" stroke-width="8" stroke-linecap="round"/>
    <rect x="330" y="185" width="80" height="16" rx="4" fill="#b91c1c" stroke="#f87171" stroke-width="1.5"/>
    <text x="345" y="198" fill="#fff" font-size="10" font-weight="bold">Тяга схождения</text>
    <!-- Регулировочная резьбовая муфта М16х1.5 (Сгон ВАЗ-2108) -->
    <rect x="230" y="187" width="90" height="12" rx="2" fill="#fbbf24" stroke="#d97706" stroke-width="1"/>
    <text x="240" y="197" fill="#0f172a" font-size="9" font-weight="bold">Сгон М16 L=120</text>
    <!-- Тяга к раме -->
    <line x1="50" y1="140" x2="230" y2="193" stroke="#ef4444" stroke-width="8" stroke-linecap="round"/>

    <!-- Размеры -->
    <line x1="0" y1="280" x2="510" y2="280" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <text x="255" y="272" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">650 мм (ПОЛОВИНА КОЛЕИ ОТ ЦЕНТРА)</text>
  </g>

  <!-- Деталировка регулировочного сгона схождения -->
  <g transform="translate(750, 160)">
    <rect width="550" height="340" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" rx="6"/>
    <text x="20" y="35" fill="#38bdf8" font-size="16" font-weight="bold">ДЕТАЛЬ: ТЯГА РЕГУЛИРОВКИ СХОЖДЕНИЯ (СГОН ВАЗ)</text>

    <!-- Чертёж сгона -->
    <g transform="translate(40, 70)">
      <rect x="20" y="25" width="220" height="30" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
      <!-- Левая и правая резьба -->
      <line x1="20" y1="32" x2="80" y2="32" stroke="#fbbf24" stroke-width="3" stroke-dasharray="3,3"/>
      <line x1="160" y1="32" x2="220" y2="32" stroke="#fbbf24" stroke-width="3" stroke-dasharray="3,3"/>
      <!-- Наконечник ШС или сайлентблок -->
      <circle cx="20" cy="40" r="18" fill="#475569" stroke="#cbd5e1" stroke-width="2"/>
      <circle cx="20" cy="40" r="6" fill="#38bdf8"/>
      <circle cx="220" cy="40" r="18" fill="#475569" stroke="#cbd5e1" stroke-width="2"/>
      <circle cx="220" cy="40" r="6" fill="#38bdf8"/>
      <!-- Контргайки -->
      <rect x="75" y="20" width="16" height="40" rx="2" fill="#f59e0b"/>
      <rect x="149" y="20" width="16" height="40" rx="2" fill="#f59e0b"/>
      <text x="65" y="80" fill="#fbbf24" font-size="11">Контргайка М16</text>
      <text x="140" y="80" fill="#fbbf24" font-size="11">Контргайка М16</text>
    </g>

    <text x="20" y="195" fill="#f8fafc" font-size="13" font-weight="bold">Инструкция по настройке задней колеи:</text>
    <text x="20" y="225" fill="#94a3b8" font-size="12">1. Схождение задних колес выставлять строго в 0° 00' (или до +0° 10' суммарно).</text>
    <text x="20" y="250" fill="#94a3b8" font-size="12">2. Вращением трубной муфты сгона удлинять или укорачивать тягу.</text>
    <text x="20" y="275" fill="#94a3b8" font-size="12">3. После регулировки затянуть обе контргайки моментом 75-80 Нм с фиксатором резьбы.</text>
    <text x="20" y="300" fill="#ef4444" font-size="12" font-weight="bold">ВАЖНО: Люфт в этом узле недопустим — проверяется перед каждым выездом!</text>
  </g>
</svg>"""
write_svg("03_rear_irs_arms.svg", svg_rear_irs)

# =========================================================================
# ЧЕРТЕЖ 4: МОТОРНАЯ ПЛИТА QS138 И УЗЕЛ ДИФФЕРЕНЦИАЛА
# =========================================================================
svg_motor_plate = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950" style="background:#0f172a; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.8"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  <rect x="20" y="20" width="1360" height="910" fill="none" stroke="#38bdf8" stroke-width="2"/>
  
  <text x="50" y="65" fill="#38bdf8" font-size="22" font-weight="bold">ДЕТАЛИРОВОЧНЫЙ ЧЕРТЁЖ: МОТОРНАЯ ПЛИТА QS138 И НАТЯЖИТЕЛЬ ЦЕПИ 520</text>
  <text x="50" y="90" fill="#94a3b8" font-size="14">Плита с продольными пазами для перемещения мотора и регулировки натяжки цепи 520</text>

  <!-- Штамп -->
  <g transform="translate(980, 800)">
    <rect width="380" height="110" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="15" y="30" fill="#94a3b8" font-size="12">Деталь:</text>
    <text x="100" y="30" fill="#f8fafc" font-size="14" font-weight="bold">Моторная плита QS138</text>
    <text x="15" y="60" fill="#94a3b8" font-size="12">Материал:</text>
    <text x="100" y="60" fill="#f8fafc" font-size="13">Лист сталь 09Г2С / Ст3, t = 6-8 мм</text>
    <text x="15" y="90" fill="#94a3b8" font-size="12">Чертеж:</text>
    <text x="100" y="90" fill="#38bdf8" font-size="13">04-PWR-PLATE-QS138 / М 1:2</text>
  </g>

  <!-- ПЛИТА (ВИД СВЕРХУ) Габариты 300 х 240 мм -->
  <g transform="translate(100, 160)">
    <!-- Контур плиты 300х240 (масштаб: 1 мм = 1.6 px -> 480 x 384 px) -->
    <rect x="40" y="40" width="480" height="384" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="3"/>

    <!-- Центральное посадочное окно под мотор QS138 (D = 110 мм -> 176 px) -->
    <circle cx="280" cy="232" r="88" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
    <text x="280" y="238" fill="#94a3b8" font-size="14" font-weight="bold" text-anchor="middle">Окно D = 110 мм</text>

    <!-- 4 крепежных отверстия мотора QS138 (М10 по радиусу 135 мм) -->
    <circle cx="280" cy="120" r="10" fill="#ef4444"/>
    <circle cx="280" cy="344" r="10" fill="#ef4444"/>
    <circle cx="168" cy="232" r="10" fill="#ef4444"/>
    <circle cx="392" cy="232" r="10" fill="#ef4444"/>
    <text x="280" y="105" fill="#ef4444" font-size="11" text-anchor="middle">Отв. 4х М10 (R=85)</text>

    <!-- 4 ПРОДОЛЬНЫХ ПАЗА ДЛЯ НАТЯЖКИ ЦЕПИ К РАМЕ (12 х 55 мм -> 19 x 88 px) -->
    <!-- Паз 1 (вверху слева) -->
    <rect x="70" y="70" width="88" height="19" rx="9" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>
    <!-- Паз 2 (внизу слева) -->
    <rect x="70" y="375" width="88" height="19" rx="9" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>
    <!-- Паз 3 (вверху справа) -->
    <rect x="400" y="70" width="88" height="19" rx="9" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>
    <!-- Паз 4 (внизу справа) -->
    <rect x="400" y="375" width="88" height="19" rx="9" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="445" y="60" fill="#38bdf8" font-size="11" text-anchor="middle">Пазы 12х55 под М10</text>

    <!-- Размеры плиты -->
    <!-- Длина 300 мм -->
    <line x1="40" y1="460" x2="520" y2="460" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <line x1="40" y1="424" x2="40" y2="470" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="520" y1="424" x2="520" y2="470" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="280" y="452" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">300 мм (ДЛИНА ПЛИТЫ)</text>

    <!-- Ширина 240 мм -->
    <line x1="0" y1="40" x2="0" y2="424" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <line x1="0" y1="40" x2="40" y2="40" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="0" y1="424" x2="40" y2="424" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="-12" y="232" fill="#38bdf8" font-size="14" font-weight="bold" transform="rotate(-90, -12, 232)" text-anchor="middle">240 мм (ШИРИНА ПЛИТЫ)</text>
  </g>

  <!-- СХЕМА УЗЛА НАТЯЖИТЕЛЯ ЦЕПИ И ОПОР ПОДШИПНИКОВ -->
  <g transform="translate(720, 160)">
    <rect width="580" height="480" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" rx="6"/>
    <text x="25" y="35" fill="#38bdf8" font-size="16" font-weight="bold">УЗЕЛ ПРИВОДА: ЦЕПЬ 520 И ПОДШИПНИКИ UCP206</text>

    <g transform="translate(40, 70)">
      <!-- Звезда ведущая 14T на моторе (вверху) -->
      <circle cx="100" cy="60" r="32" fill="#ef4444" stroke="#f87171" stroke-width="2"/>
      <circle cx="100" cy="60" r="12" fill="#0f172a"/>
      <text x="100" y="65" fill="#fff" font-size="11" font-weight="bold" text-anchor="middle">14T</text>

      <!-- Звезда ведомая 47T на дифференциале (внизу) -->
      <circle cx="100" cy="250" r="95" fill="#334155" stroke="#94a3b8" stroke-width="3"/>
      <circle cx="100" cy="250" r="40" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
      <text x="100" y="255" fill="#fff" font-size="16" font-weight="bold" text-anchor="middle">47T (дифференциал)</text>

      <!-- Цепь 520 -->
      <line x1="68" y1="60" x2="5" y2="250" stroke="#fbbf24" stroke-width="8"/>
      <line x1="132" y1="60" x2="195" y2="250" stroke="#fbbf24" stroke-width="8"/>
      <text x="215" y="150" fill="#fbbf24" font-size="12" font-weight="bold">Цепь 520 O-Ring</text>

      <!-- Натяжной болт М10 с упором в раму -->
      <rect x="250" y="45" width="140" height="18" fill="#475569" stroke="#cbd5e1" stroke-width="1"/>
      <circle cx="390" cy="54" r="14" fill="#f59e0b"/>
      <text x="260" y="35" fill="#f8fafc" font-size="11">Упорный винт натяжки М10</text>
    </g>

    <g transform="translate(30, 390)">
      <text x="0" y="20" fill="#f8fafc" font-size="12" font-weight="bold">Опоры вала дифференциала:</text>
      <text x="0" y="40" fill="#94a3b8" font-size="11">• 2 корпусных подшипника UCP206 (диаметр вала 30 мм, динамич. нагрузка 19.5 кН).</text>
      <text x="0" y="60" fill="#94a3b8" font-size="11">• Привариваются к нижней раме через стальные проставки 10 мм с болтами М14.</text>
    </g>
  </g>
</svg>"""
write_svg("04_powertrain_motor_plate.svg", svg_motor_plate)

# =========================================================================
# ЧЕРТЕЖ 5: ПОВОРОТНЫЙ СНЕГООТВАЛ 1400 ММ
# =========================================================================
svg_snow_plow = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950" style="background:#0f172a; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.8"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  <rect x="20" y="20" width="1360" height="910" fill="none" stroke="#38bdf8" stroke-width="2"/>
  
  <text x="50" y="65" fill="#38bdf8" font-size="22" font-weight="bold">СБОРОЧНЫЙ ЧЕРТЁЖ: СНЕГООТВАЛ 1400 ММ С ПОВОРОТНЫМ МЕХАНИЗМОМ</text>
  <text x="50" y="90" fill="#94a3b8" font-size="14">Ширина 1400 мм, поворот на 25° вправо/влево, предохранительные пружины откидывания, быстросъем 50х50</text>

  <!-- Штамп -->
  <g transform="translate(980, 800)">
    <rect width="380" height="110" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="15" y="30" fill="#94a3b8" font-size="12">Узел:</text>
    <text x="100" y="30" fill="#f8fafc" font-size="14" font-weight="bold">Снегоотвал поворотный 1.4м</text>
    <text x="15" y="60" fill="#94a3b8" font-size="12">Материал:</text>
    <text x="100" y="60" fill="#f8fafc" font-size="13">Лист 2.5 мм, труба 50х50, резина 20мм</text>
    <text x="15" y="90" fill="#94a3b8" font-size="12">Чертеж:</text>
    <text x="100" y="90" fill="#38bdf8" font-size="13">05-PLOW-SNOW-1400 / М 1:5</text>
  </g>

  <!-- 1. ВИД СБОКУ (СЕЧЕНИЕ КОВША И ПРУЖИННЫЙ МЕХАНИЗМ) -->
  <g transform="translate(100, 160)">
    <text x="0" y="0" fill="#38bdf8" font-size="18" font-weight="bold">1. ВИД СБОКУ (МЕХАНИЗМ ОТКИДЫВАНИЯ ПРИ УДАРЕ)</text>

    <!-- Земля -->
    <line x1="-30" y1="360" x2="450" y2="360" stroke="#64748b" stroke-width="2" stroke-dasharray="4,4"/>
    <text x="-20" y="380" fill="#64748b" font-size="11">Грунт / Снег</text>

    <!-- Дышло отвала из трубы 50х50 (горизонтальное) -->
    <rect x="-30" y="270" width="220" height="24" rx="2" fill="#d97706" stroke="#f59e0b" stroke-width="2"/>
    <text x="30" y="260" fill="#f59e0b" font-size="11" font-weight="bold">Дышло 50х50х2.5</text>

    <!-- Шарнир качания лопаты (палец Ф16) -->
    <circle cx="190" cy="282" r="14" fill="#334155" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="190" cy="282" r="5" fill="#38bdf8"/>
    <text x="145" y="325" fill="#38bdf8" font-size="11">Шарнир откидывания</text>

    <!-- Изогнутый профиль ковша (радиус R=400, высота 450 мм -> 225 px) -->
    <path d="M 190,282 L 180,350 L 220,350 Q 280,240 220,125" fill="none" stroke="#06b6d4" stroke-width="12" stroke-linecap="round"/>

    <!-- Резиновая демпферная кромка по низу ковша (толщина 20 мм) -->
    <rect x="180" y="350" width="40" height="15" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="230" y="362" fill="#94a3b8" font-size="11">Резина ТМКЩ t=20</text>

    <!-- Предохранительная пружина откидывания (2 шт) -->
    <line x1="80" y1="270" x2="220" y2="150" stroke="#fbbf24" stroke-width="8" stroke-dasharray="8,4"/>
    <circle cx="80" cy="270" r="6" fill="#f59e0b"/>
    <circle cx="220" cy="150" r="6" fill="#f59e0b"/>
    <text x="110" y="195" fill="#fbbf24" font-size="12" font-weight="bold">Пружина L=200</text>

    <!-- Проушина для троса лебедки -->
    <polygon points="120,270 120,230 140,270" fill="#475569" stroke="#94a3b8" stroke-width="1.5"/>
    <circle cx="125" cy="245" r="5" fill="#ef4444"/>
    <text x="65" y="235" fill="#ef4444" font-size="11">Трос лебедки 12V</text>

    <!-- Размеры -->
    <line x1="280" y1="125" x2="280" y2="365" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <text x="295" y="245" fill="#38bdf8" font-size="13" font-weight="bold" transform="rotate(90, 295, 245)" text-anchor="middle">450 мм (ВЫСОТА ЛОПАТЫ)</text>
  </g>

  <!-- 2. ВИД СВЕРХУ (СЕКТОР ПОВОРОТА 0° / 25°) -->
  <g transform="translate(680, 160)">
    <text x="0" y="0" fill="#38bdf8" font-size="18" font-weight="bold">2. ВИД СВЕРХУ (СЕКТОР РЕГУЛИРОВКИ УГЛА СБРОСА)</text>

    <!-- Быстросъемный хвостовик под американский фаркоп 50х50 -->
    <rect x="0" y="180" width="120" height="40" rx="3" fill="#334155" stroke="#94a3b8" stroke-width="2"/>
    <circle cx="60" cy="200" r="8" fill="#38bdf8"/>
    <text x="15" y="170" fill="#94a3b8" font-size="11">Палец Ф16 в раму</text>

    <!-- Центральная поворотная балка -->
    <line x1="120" y1="200" x2="260" y2="200" stroke="#d97706" stroke-width="18" stroke-linecap="round"/>

    <!-- Центральный палец поворота Ф24 мм -->
    <circle cx="260" cy="200" r="16" fill="#ef4444" stroke="#fff" stroke-width="2"/>

    <!-- Секторная пластина с 3 отверстиями фиксации (-25°, 0°, +25°) -->
    <path d="M 210,130 A 90 90 0 0 1 210,270 L 260,200 Z" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
    <circle cx="180" cy="155" r="7" fill="#fbbf24"/>
    <text x="110" y="150" fill="#fbbf24" font-size="11">+25° (Вправо)</text>
    <circle cx="170" cy="200" r="7" fill="#fbbf24"/>
    <text x="115" y="205" fill="#fbbf24" font-size="11">0° (Прямо)</text>
    <circle cx="180" cy="245" r="7" fill="#fbbf24"/>
    <text x="110" y="260" fill="#fbbf24" font-size="11">-25° (Влево)</text>

    <!-- Ковш в повернутом положении (1400 мм -> 420 px) -->
    <g transform="rotate(25, 260, 200)">
      <rect x="250" y="-10" width="20" height="420" rx="4" fill="#06b6d4" stroke="#0891b2" stroke-width="3"/>
      <!-- Ребра жесткости ковша (4 шт) -->
      <line x1="230" y1="40" x2="250" y2="40" stroke="#fff" stroke-width="6"/>
      <line x1="230" y1="150" x2="250" y2="150" stroke="#fff" stroke-width="6"/>
      <line x1="230" y1="250" x2="250" y2="250" stroke="#fff" stroke-width="6"/>
      <line x1="230" y1="360" x2="250" y2="360" stroke="#fff" stroke-width="6"/>
      <text x="260" y="210" fill="#0f172a" font-size="14" font-weight="bold" transform="rotate(-90, 260, 210)" text-anchor="middle">ШИРИНА ЛОПАТЫ 1400 мм</text>
    </g>

    <!-- Описание работы -->
    <g transform="translate(0, 390)">
      <rect width="600" height="130" fill="#1e293b" stroke="#64748b" stroke-width="1" rx="4"/>
      <text x="15" y="25" fill="#38bdf8" font-size="13" font-weight="bold">★ ОСОБЕННОСТИ ЭКСПЛУАТАЦИИ ЗИМОЙ:</text>
      <text x="15" y="50" fill="#f8fafc" font-size="11">1. При наезде на вмерзший камень или люк: лопата поворачивается на нижнем шарнире,</text>
      <text x="15" y="70" fill="#94a3b8" font-size="11">   растягивая пружины, перескакивает препятствие и возвращается назад без удара в раму.</text>
      <text x="15" y="90" fill="#f8fafc" font-size="11">2. Поворот отвала на 25° вправо позволяет сбрасывать снег на обочину при непрерывном ходе.</text>
      <text x="15" y="110" fill="#10b981" font-size="11" font-weight="bold">3. Подъем/опускание: тумблером на панели багги через квадроциклетную лебедку 12V 2000 lbs.</text>
    </g>
  </g>
</svg>"""
write_svg("05_snow_plow_assembly.svg", svg_snow_plow)

# =========================================================================
# ЧЕРТЕЖ 6: ТЕРМОБОКС АККУМУЛЯТОРА 72V 48Ah
# =========================================================================
svg_battery_box = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950" style="background:#0f172a; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.8"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  <rect x="20" y="20" width="1360" height="910" fill="none" stroke="#38bdf8" stroke-width="2"/>
  
  <text x="50" y="65" fill="#38bdf8" font-size="22" font-weight="bold">ДЕТАЛИРОВОЧНЫЙ ЧЕРТЁЖ: СЪЕМНЫЙ ТЕРМОБОКС АКБ 72V 48Ah</text>
  <text x="50" y="90" fill="#94a3b8" font-size="14">Модульный герметичный бокс: 20S NMC ячейки, Smart BMS 100A, греющий слой 12V, разъем Anderson SB175</text>

  <!-- Штамп -->
  <g transform="translate(980, 800)">
    <rect width="380" height="110" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="15" y="30" fill="#94a3b8" font-size="12">Узел:</text>
    <text x="100" y="30" fill="#f8fafc" font-size="14" font-weight="bold">Термобокс АКБ (1 из 2)</text>
    <text x="15" y="60" fill="#94a3b8" font-size="12">Материал:</text>
    <text x="100" y="60" fill="#f8fafc" font-size="13">Лист АМг2 1.5 мм + ЭППС 20 мм</text>
    <text x="15" y="90" fill="#94a3b8" font-size="12">Чертеж:</text>
    <text x="100" y="90" fill="#38bdf8" font-size="13">06-BAT-THERMO-72V / М 1:2</text>
  </g>

  <!-- 1. СХЕМА СЛОЕВ И СБОРКИ ВНУТРИ (РАЗРЕЗ) -->
  <g transform="translate(100, 160)">
    <text x="0" y="0" fill="#38bdf8" font-size="18" font-weight="bold">1. СЕЧЕНИЕ ТЕРМОБОКСА (УТЕПЛЕНИЕ И ПОДОГРЕВ)</text>

    <!-- Внешний металлический корпус (360 х 240 мм) -->
    <rect x="40" y="30" width="380" height="260" rx="8" fill="#1e293b" stroke="#94a3b8" stroke-width="3"/>
    <text x="50" y="55" fill="#94a3b8" font-size="11">Внешний корпус: алюминий 1.5 мм / сталь 1.0 мм</text>

    <!-- Слой термоизоляции ЭППС 20 мм (Розовый/Оранжевый) -->
    <rect x="65" y="65" width="330" height="200" rx="4" fill="#fbcfe8" stroke="#ec4899" stroke-width="2" opacity="0.4"/>
    <text x="75" y="85" fill="#ec4899" font-size="11" font-weight="bold">Слой утеплителя ЭППС 20 мм</text>

    <!-- Нагревательный мат 12V 40W (по дну и стенкам) -->
    <line x1="90" y1="245" x2="370" y2="245" stroke="#ef4444" stroke-width="6"/>
    <text x="140" y="240" fill="#ef4444" font-size="11" font-weight="bold">Греющий мат 12V 40W (под ячейками)</text>

    <!-- 20 ячеек NMC (2 ряда по 10 шт) -->
    <g transform="translate(90, 100)">
      <rect width="280" height="130" fill="#7e22ce" stroke="#a855f7" stroke-width="2" rx="4"/>
      <text x="25" y="55" fill="#fff" font-size="14" font-weight="bold">20S ПРИЗМАТИКИ NMC</text>
      <text x="25" y="80" fill="#f8fafc" font-size="12">72V 48Ah (~3.5 кВт·ч, вес 22 кг)</text>
      <!-- Контакты/шины ячеек -->
      <line x1="20" y1="20" x2="260" y2="20" stroke="#fbbf24" stroke-width="6"/>
      <text x="100" y="15" fill="#fbbf24" font-size="10">Медные никелированные шины</text>
    </g>

    <!-- Smart BMS 100A (сверху блока) -->
    <rect x="130" y="35" width="200" height="25" rx="3" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="150" y="52" fill="#fff" font-size="11" font-weight="bold">JK / ANT Smart BMS 100A</text>

    <!-- Размеры бокса -->
    <line x1="40" y1="320" x2="420" y2="320" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <text x="230" y="312" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">380 мм (ДЛИНА БОКСА)</text>

    <line x1="0" y1="30" x2="0" y2="290" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arr)" marker-end="url(#arr)"/>
    <text x="-12" y="160" fill="#38bdf8" font-size="13" font-weight="bold" transform="rotate(-90, -12, 160)" text-anchor="middle">260 мм (ВЫСОТА БОКСА)</text>
  </g>

  <!-- 2. ТОРЦЕВАЯ ПАНЕЛЬ ПОДКЛЮЧЕНИЯ И РАЗЪЕМОВ -->
  <g transform="translate(680, 160)">
    <text x="0" y="0" fill="#38bdf8" font-size="18" font-weight="bold">2. ТОРЦЕВАЯ ПАНЕЛЬ (БЫСТРОСЪЕМНЫЕ РАЗЪЕМЫ)</text>

    <rect x="40" y="30" width="300" height="260" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>

    <!-- Силовой разъем Anderson SB175 (Главный силовой выход 72V) -->
    <rect x="80" y="60" width="90" height="60" rx="6" fill="#dc2626" stroke="#f87171" stroke-width="2"/>
    <circle cx="105" cy="90" r="12" fill="#0f172a"/>
    <circle cx="145" cy="90" r="12" fill="#0f172a"/>
    <text x="85" y="140" fill="#ef4444" font-size="11" font-weight="bold">Anderson SB175 (72V)</text>

    <!-- Разъем подогрева 12V (Anderson SB50 или авиационный GX16) -->
    <rect x="220" y="65" width="55" height="50" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
    <text x="210" y="135" fill="#38bdf8" font-size="11">Подогрев 12V</text>

    <!-- Автомат постоянного тока 100A (ручной выключатель массы на боксе) -->
    <rect x="80" y="160" width="70" height="90" rx="4" fill="#334155" stroke="#cbd5e1" stroke-width="2"/>
    <rect x="100" y="195" width="30" height="40" fill="#fbbf24"/>
    <text x="80" y="270" fill="#fbbf24" font-size="11" font-weight="bold">DC Автомат 100A</text>

    <!-- Порт зарядки (XT90 / GX16) -->
    <circle cx="245" cy="205" r="22" fill="#059669" stroke="#34d399" stroke-width="2"/>
    <text x="215" y="245" fill="#34d399" font-size="11">Зарядка 84V</text>

    <!-- Схема логики работы терморегулятора -->
    <g transform="translate(0, 310)">
      <rect width="600" height="150" fill="#1e293b" stroke="#64748b" stroke-width="1" rx="4"/>
      <text x="15" y="25" fill="#38bdf8" font-size="13" font-weight="bold">★ АВТОНОМНЫЙ ЗИМНИЙ ТЕРМОКОНТРОЛЬ:</text>
      <text x="15" y="50" fill="#f8fafc" font-size="11">1. Термостат KSD9700 закреплен на центральной ячейке.</text>
      <text x="15" y="70" fill="#94a3b8" font-size="11">   • Температура ниже +5°C: термостат включает мат подогрева 12V 40W.</text>
      <text x="15" y="90" fill="#94a3b8" font-size="11">   • Температура достигает +20°C: термостат отключает питание подогрева.</text>
      <text x="15" y="110" fill="#10b981" font-size="11">2. Энергопотребление подогрева: всего ~35-40 Вт (съедает менее 1% емкости за 2 часа).</text>
      <text x="15" y="130" fill="#f8fafc" font-size="11">3. Быстросъемность: 2 защелки-замка лягушки позволяют за 1 минуту вынуть бокс и унести в тепло.</text>
    </g>
  </g>
</svg>"""
write_svg("06_battery_box_thermal.svg", svg_battery_box)

print("Все деталировочные чертежи успешно сгенерированы в папку drawings!")
