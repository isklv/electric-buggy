#!/usr/bin/env python3
"""
Генератор подробного технического чертежа (Blueprints / TechDraw) электробагги
Создает векторный чертеж SVG с проекциями, габаритными размерами и спецификацией.
"""

def generate_svg_blueprint(output_path):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" width="1600" height="1100" style="background:#0f172a; font-family:'Roboto', 'Segoe UI', Arial, sans-serif;">
  <defs>
    <!-- Сетка миллиметровки -->
    <pattern id="grid-small" width="10" height="10" patternUnits="userSpaceOnUse">
      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#1e293b" stroke-width="0.5"/>
    </pattern>
    <pattern id="grid-large" width="50" height="50" patternUnits="userSpaceOnUse">
      <rect width="50" height="50" fill="url(#grid-small)"/>
      <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#334155" stroke-width="1"/>
    </pattern>
    
    <!-- Маркеры стрелок для размеров -->
    <marker id="arrow-start" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 10 0 L 0 5 L 10 10 z" fill="#38bdf8"/>
    </marker>
    <marker id="arrow-end" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>

  <!-- Фон -->
  <rect width="100%" height="100%" fill="url(#grid-large)"/>

  <!-- Рамка чертежа по ГОСТ -->
  <rect x="30" y="30" width="1540" height="1040" fill="none" stroke="#38bdf8" stroke-width="2"/>
  <rect x="35" y="35" width="1530" height="1030" fill="none" stroke="#38bdf8" stroke-width="1" opacity="0.6"/>

  <!-- Основная надпись (Штамп чертежа) -->
  <g transform="translate(1160, 930)">
    <rect width="400" height="135" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
    <line x1="0" y1="35" x2="400" y2="35" stroke="#38bdf8" stroke-width="1"/>
    <line x1="0" y1="70" x2="400" y2="70" stroke="#38bdf8" stroke-width="1"/>
    <line x1="0" y1="100" x2="400" y2="100" stroke="#38bdf8" stroke-width="1"/>
    <line x1="120" y1="0" x2="120" y2="135" stroke="#38bdf8" stroke-width="1"/>
    <line x1="260" y1="0" x2="260" y2="70" stroke="#38bdf8" stroke-width="1"/>

    <text x="10" y="24" fill="#94a3b8" font-size="12">Проектировщик</text>
    <text x="130" y="24" fill="#f8fafc" font-size="14" font-weight="bold">Antigravity AI / User</text>
    <text x="270" y="24" fill="#38bdf8" font-size="12">Лист 1 из 1</text>

    <text x="10" y="58" fill="#94a3b8" font-size="12">Наименование</text>
    <text x="130" y="58" fill="#38bdf8" font-size="16" font-weight="bold">ЭЛЕКТРОБАГГИ RWD / IRS</text>

    <text x="10" y="88" fill="#94a3b8" font-size="12">Конструкция</text>
    <text x="130" y="88" fill="#f8fafc" font-size="13">Профтруба 50х50, 40х40 (без трубогиба)</text>

    <text x="10" y="122" fill="#94a3b8" font-size="12">Силовая часть</text>
    <text x="130" y="122" fill="#f8fafc" font-size="13">QS138 70H (13 кВт), 2x АКБ 72V 48Ah, отвал</text>
  </g>

  <!-- ==================== 1. ВИД СБОКУ (SIDE ELEVATION) ==================== -->
  <!-- Масштаб: 1 мм = 0.25 px -->
  <g id="side-view" transform="translate(100, 150)">
    <text x="0" y="-30" fill="#38bdf8" font-size="20" font-weight="bold">ВИД СБОКУ (М 1:15)</text>

    <!-- Линия земли -->
    <line x1="-80" y1="360" x2="750" y2="360" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4"/>
    <text x="-70" y="380" fill="#64748b" font-size="12">УРОВЕНЬ ЗЕМЛИ</text>

    <!-- Колеса (175/70 R13, диаметр 575 мм -> 144px, R=72px) -->
    <!-- Заднее колесо (Z = -950 -> X = 100) -->
    <circle cx="100" cy="288" r="72" fill="#1e293b" stroke="#94a3b8" stroke-width="3"/>
    <circle cx="100" cy="288" r="41" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="100" cy="288" r="8" fill="#f59e0b"/>

    <!-- Переднее колесо (Z = +1050 -> X = 612, база 2050 -> 512px) -->
    <circle cx="612" cy="288" r="72" fill="#1e293b" stroke="#94a3b8" stroke-width="3"/>
    <circle cx="612" cy="288" r="41" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
    <circle cx="612" cy="288" r="8" fill="#f59e0b"/>

    <!-- Рама: Нижний лонжерон 50х50 (Клиренс 280 мм -> Y = 290) -->
    <!-- Длина лонжерона 2100 мм -> 525 px, от X=75 до X=635 -->
    <rect x="75" y="280" width="560" height="14" fill="#d97706" stroke="#f59e0b" stroke-width="1.5" rx="2"/>

    <!-- Каркас безопасности 40х40 (Синий) -->
    <!-- Стойка В (задняя, X=200): вертикально вверх до крыши (высота 1150 мм -> 287px, Y=0) -->
    <line x1="200" y1="280" x2="200" y2="10" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/>
    
    <!-- Стойка А (передняя, наклонная, от X=420 до крыши X=380, Y=10) -->
    <line x1="420" y1="280" x2="380" y2="10" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/>

    <!-- Брус крыши (X=200 до X=380, Y=10) -->
    <line x1="196" y1="10" x2="384" y2="10" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/>

    <!-- Задняя наклонная укосина моторного отсека (от крыши X=200, Y=10 к заднему лонжерону X=75, Y=280) -->
    <line x1="200" y1="10" x2="75" y2="280" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/>

    <!-- Передняя наклонная укосина капота (от стойки А X=420, Y=280 к передку X=635, Y=200) -->
    <line x1="420" y1="280" x2="635" y2="190" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/>
    <line x1="635" y1="190" x2="635" y2="280" stroke="#0284c7" stroke-width="8" stroke-linecap="round"/>

    <!-- Боковой защитный брус (отбойник/порог) -->
    <line x1="200" y1="190" x2="420" y2="190" stroke="#0284c7" stroke-width="6"/>

    <!-- Косынки усиления (3 мм сталь) в узлах запила -->
    <polygon points="200,20 200,60 240,10" fill="#38bdf8" opacity="0.8"/>
    <polygon points="380,20 380,60 340,10" fill="#38bdf8" opacity="0.8"/>
    <polygon points="75,270 120,280 75,240" fill="#38bdf8" opacity="0.8"/>

    <!-- Сиденье водителя -->
    <path d="M 240,270 L 320,270 L 300,160 L 260,160 Z" fill="#334155" stroke="#64748b" stroke-width="2"/>
    <!-- Руль -->
    <line x1="330" y1="210" x2="365" y2="175" stroke="#94a3b8" stroke-width="3"/>
    <circle cx="365" cy="175" r="16" fill="none" stroke="#e2e8f0" stroke-width="3"/>

    <!-- Агрегаты: Мотор QS138 и Редуктор сзади -->
    <rect x="80" y="220" width="55" height="55" rx="8" fill="#dc2626" stroke="#ef4444" stroke-width="2"/>
    <text x="85" y="252" fill="#fff" font-size="10" font-weight="bold">QS138</text>

    <!-- Батарейные отсеки (2 шт по центру днища) -->
    <rect x="250" y="240" width="75" height="38" rx="4" fill="#7e22ce" stroke="#a855f7" stroke-width="1.5"/>
    <text x="255" y="262" fill="#fff" font-size="9">АКБ №2</text>
    <rect x="335" y="240" width="75" height="38" rx="4" fill="#7e22ce" stroke="#a855f7" stroke-width="1.5"/>
    <text x="340" y="262" fill="#fff" font-size="9">АКБ №1</text>

    <!-- Снегоотвал спереди -->
    <rect x="635" y="280" width="40" height="14" fill="#06b6d4" stroke="#0891b2" stroke-width="1.5"/>
    <!-- Дышло лопаты -->
    <line x1="675" y1="287" x2="720" y2="300" stroke="#0891b2" stroke-width="6"/>
    <!-- Сечение ковша лопаты -->
    <path d="M 720,260 Q 735,320 720,355" fill="none" stroke="#06b6d4" stroke-width="8" stroke-linecap="round"/>

    <!-- ================= РАЗМЕРНЫЕ ЛИНИИ (ВИД СБОКУ) ================= -->
    <!-- Колесная база: 2050 мм (между центрами колес X=100 и X=612) -->
    <line x1="100" y1="410" x2="612" y2="410" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <line x1="100" y1="360" x2="100" y2="420" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="612" y1="360" x2="612" y2="420" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="320" y="402" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">2050 (КОЛЕСНАЯ БАЗА)</text>

    <!-- Длина рамы: 2100 мм (X=75 до X=635) -->
    <line x1="75" y1="440" x2="635" y2="440" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <line x1="75" y1="294" x2="75" y2="450" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="635" y1="294" x2="635" y2="450" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="355" y="433" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">2100 (ДЛИНА НИЖНЕЙ РАМЫ)</text>

    <!-- Высота кабины: 1430 мм от земли до крыши (Y=360 до Y=10 -> dy=350 px) -->
    <line x1="30" y1="360" x2="30" y2="10" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <line x1="30" y1="10" x2="190" y2="10" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="30" y1="360" x2="70" y2="360" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="20" y="190" fill="#38bdf8" font-size="14" font-weight="bold" transform="rotate(-90, 20, 190)" text-anchor="middle">1430 (ПОЛНАЯ ВЫСОТА)</text>

    <!-- Клиренс: 280 мм (Y=360 до Y=290 -> dy=70 px) -->
    <line x1="-30" y1="360" x2="-30" y2="290" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <line x1="-30" y1="290" x2="75" y2="290" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="-40" y="330" fill="#38bdf8" font-size="12" font-weight="bold" transform="rotate(-90, -40, 330)" text-anchor="middle">280</text>
  </g>

  <!-- ==================== 2. ВИД СВЕРХУ (PLAN VIEW) ==================== -->
  <g id="top-view" transform="translate(100, 680)">
    <text x="0" y="-20" fill="#38bdf8" font-size="20" font-weight="bold">ВИД СВЕРХУ / КОМПОНОВКА (М 1:15)</text>

    <!-- Рама: внешняя ширина 1100 мм -> 275 px, длина 2100 мм -> 525 px -->
    <!-- Y от 0 до 275 px -->
    <!-- Продольные лонжероны 50х50 -->
    <rect x="75" y="10" width="560" height="12" fill="#d97706" stroke="#f59e0b" stroke-width="1.5"/>
    <rect x="75" y="253" width="560" height="12" fill="#d97706" stroke="#f59e0b" stroke-width="1.5"/>

    <!-- Поперечины рамы 50х50 -->
    <rect x="75" y="22" width="12" height="231" fill="#d97706"/>
    <rect x="623" y="22" width="12" height="231" fill="#d97706"/>
    <rect x="200" y="22" width="10" height="231" fill="#d97706"/>
    <rect x="350" y="22" width="10" height="231" fill="#d97706"/>
    <rect x="490" y="22" width="10" height="231" fill="#d97706"/>

    <!-- Колеса (ширина 175 мм -> 44 px, диаметр 575 мм -> 144 px) -->
    <!-- Колея 1300 мм (центр Y = 137.5, колеса при Y = -25 и Y = 300) -->
    <!-- Задние колеса (X = 100) -->
    <rect x="64" y="-35" width="72" height="42" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>
    <rect x="64" y="268" width="72" height="42" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>
    <!-- Передние колеса (X = 612) -->
    <rect x="576" y="-35" width="72" height="42" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>
    <rect x="576" y="268" width="72" height="42" rx="4" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/>

    <!-- Задняя независимая подвеска IRS: ШРУСы и дифференциал -->
    <circle cx="100" cy="137" r="28" fill="#dc2626" stroke="#ef4444" stroke-width="2"/>
    <!-- Приводные валы (ШРУСы 2108) -->
    <line x1="100" y1="109" x2="100" y2="7" stroke="#cbd5e1" stroke-width="5"/>
    <line x1="100" y1="165" x2="100" y2="268" stroke="#cbd5e1" stroke-width="5"/>

    <!-- А-образные рычаги подвески (Зеленые) -->
    <!-- Слева (низ чертежа) -->
    <line x1="75" y1="260" x2="100" y2="270" stroke="#10b981" stroke-width="4"/>
    <line x1="140" y1="260" x2="100" y2="270" stroke="#10b981" stroke-width="4"/>
    <!-- Справа (верх чертежа) -->
    <line x1="75" y1="15" x2="100" y2="5" stroke="#10b981" stroke-width="4"/>
    <line x1="140" y1="15" x2="100" y2="5" stroke="#10b981" stroke-width="4"/>

    <!-- Передняя подвеска А-рычаги -->
    <line x1="580" y1="15" x2="612" y2="5" stroke="#10b981" stroke-width="4"/>
    <line x1="640" y1="15" x2="612" y2="5" stroke="#10b981" stroke-width="4"/>
    <line x1="580" y1="260" x2="612" y2="270" stroke="#10b981" stroke-width="4"/>
    <line x1="640" y1="260" x2="612" y2="270" stroke="#10b981" stroke-width="4"/>

    <!-- Центральный батарейный тоннель (Ширина 340 мм -> 85 px) -->
    <rect x="230" y="95" width="220" height="85" fill="#1e1b4b" stroke="#6366f1" stroke-width="1.5" stroke-dasharray="4,2"/>
    <rect x="240" y="100" width="95" height="75" rx="3" fill="#7e22ce" stroke="#a855f7" stroke-width="1.5"/>
    <text x="250" y="142" fill="#fff" font-size="11" font-weight="bold">АКБ №2</text>
    <rect x="345" y="100" width="95" height="75" rx="3" fill="#7e22ce" stroke="#a855f7" stroke-width="1.5"/>
    <text x="355" y="142" fill="#fff" font-size="11" font-weight="bold">АКБ №1</text>

    <!-- Сиденья водителя и пассажира (по бокам от тоннеля) -->
    <!-- Водитель (слева по ходу движения) -->
    <rect x="240" y="190" width="100" height="60" rx="6" fill="#334155" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="260" y="225" fill="#f1f5f9" font-size="11">Водитель</text>
    <!-- Пассажир -->
    <rect x="240" y="25" width="100" height="60" rx="6" fill="#334155" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="255" y="60" fill="#f1f5f9" font-size="11">Пассажир</text>

    <!-- Отвал для снега (ширина 1400 мм -> 350 px) спереди под углом -->
    <g transform="rotate(18, 700, 137)">
      <rect x="685" y="-38" width="18" height="350" rx="4" fill="#06b6d4" stroke="#0891b2" stroke-width="2"/>
      <text x="690" y="145" fill="#0f172a" font-size="12" font-weight="bold" transform="rotate(-90, 690, 145)">ОТВАЛ 1400 мм</text>
    </g>

    <!-- ================= РАЗМЕРНЫЕ ЛИНИИ (ВИД СВЕРХУ) ================= -->
    <!-- Ширина рамы: 1100 мм (Y=10 до Y=265 -> dy=255 px) -->
    <line x1="30" y1="10" x2="30" y2="265" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <line x1="30" y1="10" x2="75" y2="10" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="30" y1="265" x2="75" y2="265" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="20" y="145" fill="#38bdf8" font-size="13" font-weight="bold" transform="rotate(-90, 20, 145)" text-anchor="middle">1100 (ШИРИНА РАМЫ)</text>

    <!-- Колея: 1300 мм (между центрами колес Y=-14 и Y=289) -->
    <line x1="720" y1="-14" x2="720" y2="289" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <line x1="648" y1="-14" x2="725" y2="-14" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <line x1="648" y1="289" x2="725" y2="289" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2"/>
    <text x="735" y="145" fill="#38bdf8" font-size="13" font-weight="bold" transform="rotate(90, 735, 145)" text-anchor="middle">1300 (КОЛЕЯ КОЛЕС)</text>
  </g>

  <!-- ==================== 3. ВИД СЗАДИ / ПОДВЕСКА IRS ==================== -->
  <g id="rear-suspension-view" transform="translate(1000, 150)">
    <text x="0" y="-30" fill="#38bdf8" font-size="20" font-weight="bold">ВИД СЗАДИ / КИНЕМАТИКА IRS (М 1:12)</text>

    <!-- Земля -->
    <line x1="-50" y1="360" x2="520" y2="360" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4"/>

    <!-- Колеса (Ширина 175 -> 50 px, Диаметр 575 -> 160 px, Y=280) -->
    <!-- Левое колесо -->
    <rect x="-20" y="200" width="50" height="160" rx="8" fill="#1e293b" stroke="#94a3b8" stroke-width="2.5"/>
    <!-- Правое колесо -->
    <rect x="440" y="200" width="50" height="160" rx="8" fill="#1e293b" stroke="#94a3b8" stroke-width="2.5"/>

    <!-- Поперечина нижней рамы 50х50 (Клиренс 280 мм -> Y = 280) -->
    <!-- Ширина рамы 1100 мм -> 300 px (X от 85 до 385) -->
    <rect x="85" y="265" width="300" height="18" fill="#d97706" stroke="#f59e0b" stroke-width="1.5"/>

    <!-- Верхний ярус рамы под амортизаторы -->
    <line x1="120" y1="180" x2="350" y2="180" stroke="#0284c7" stroke-width="6"/>
    <line x1="120" y1="180" x2="85" y2="265" stroke="#0284c7" stroke-width="6"/>
    <line x1="350" y1="180" x2="385" y2="265" stroke="#0284c7" stroke-width="6"/>

    <!-- Дифференциал ВАЗ по центру (X=235) -->
    <circle cx="235" cy="274" r="32" fill="#dc2626" stroke="#ef4444" stroke-width="2"/>
    <circle cx="235" cy="274" r="10" fill="#fff"/>

    <!-- Приводы ШРУС (от центра к ступицам 2108) -->
    <line x1="205" y1="274" x2="25" y2="280" stroke="#f8fafc" stroke-width="6" stroke-linecap="round"/>
    <line x1="265" y1="274" x2="445" y2="280" stroke="#f8fafc" stroke-width="6" stroke-linecap="round"/>

    <!-- А-образные рычаги подвески (Зеленые) -->
    <!-- Нижний рычаг (от уха рамы X=85, Y=274 к низу кулака X=25, Y=310) -->
    <line x1="85" y1="274" x2="25" y2="310" stroke="#10b981" stroke-width="6" stroke-linecap="round"/>
    <line x1="385" y1="274" x2="445" y2="310" stroke="#10b981" stroke-width="6" stroke-linecap="round"/>

    <!-- Верхний рычаг (от уха X=120, Y=200 к верху кулака X=25, Y=235) -->
    <line x1="120" y1="205" x2="25" y2="235" stroke="#10b981" stroke-width="6" stroke-linecap="round"/>
    <line x1="350" y1="205" x2="445" y2="235" stroke="#10b981" stroke-width="6" stroke-linecap="round"/>

    <!-- Амортизаторы с пружинами -->
    <line x1="135" y1="180" x2="25" y2="290" stroke="#fbbf24" stroke-width="7" stroke-linecap="round"/>
    <line x1="335" y1="180" x2="445" y2="290" stroke="#fbbf24" stroke-width="7" stroke-linecap="round"/>

    <!-- Стойки безопасности задние (В-стойки) -->
    <line x1="85" y1="265" x2="115" y2="20" stroke="#0284c7" stroke-width="8"/>
    <line x1="385" y1="265" x2="355" y2="20" stroke="#0284c7" stroke-width="8"/>
    <line x1="115" y1="20" x2="355" y2="20" stroke="#0284c7" stroke-width="8"/>
    <!-- Задний крест жесткости -->
    <line x1="85" y1="265" x2="355" y2="20" stroke="#0284c7" stroke-width="5" stroke-dasharray="4,2"/>
    <line x1="385" y1="265" x2="115" y2="20" stroke="#0284c7" stroke-width="5" stroke-dasharray="4,2"/>

    <!-- Размеры подвески -->
    <line x1="5" y1="360" x2="465" y2="360" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow-start)" marker-end="url(#arrow-end)"/>
    <text x="235" y="380" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">1300 (КОЛЕЯ ЗАДНИХ КОЛЕС ПО ЦЕНТРАМ)</text>
  </g>

  <!-- ==================== 4. ТАБЛИЦА УГЛОВ ЗАПИЛА ПРОФИЛЬНЫХ ТРУБ ==================== -->
  <g transform="translate(1000, 600)">
    <rect width="560" height="290" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" rx="6"/>
    <text x="20" y="30" fill="#38bdf8" font-size="15" font-weight="bold">УГЛЫ РАСКРОЯ ТРУБ (БЕЗ ТРУБОГИБА):</text>

    <text x="20" y="65" fill="#f8fafc" font-size="12">1. Стойка лобового стекла (А-стойка, 40х40х2):</text>
    <text x="40" y="85" fill="#94a3b8" font-size="11">• Нижний срез к раме: запил под углом 65° (отклонение 25° от вертикали)</text>
    <text x="40" y="103" fill="#94a3b8" font-size="11">• Верхний стык к крыше: угловой запил 45° + косынка 80х80 мм</text>

    <text x="20" y="130" fill="#f8fafc" font-size="12">2. Задняя стойка безопасности (В-стойка, 40х40х2):</text>
    <text x="40" y="150" fill="#94a3b8" font-size="11">• Нижний срез к раме: прямой рез 90° (перпендикулярно полу)</text>
    <text x="40" y="168" fill="#94a3b8" font-size="11">• Верхний стык к крыше: запил 45° + косынка 80х80 мм</text>

    <text x="20" y="195" fill="#f8fafc" font-size="12">3. Наклонные укосины моторного отсека (40х40х2):</text>
    <text x="40" y="215" fill="#94a3b8" font-size="11">• Верхний срез: запил 38° к задней балке крыши</text>
    <text x="40" y="233" fill="#94a3b8" font-size="11">• Нижний срез: запил 52° к заднему лонжерону рамы</text>

    <text x="20" y="260" fill="#38bdf8" font-size="12" font-weight="bold">★ ПРАВИЛО СВАРКИ: Все угловые стыки варить с полным проваром</text>
    <text x="20" y="278" fill="#94a3b8" font-size="11">и усиливать стальной косынкой 3 мм (сопротивление кручению выше, чем у гиба!)</text>
  </g>
</svg>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Чертеж SVG сохранен в: {output_path}")

if __name__ == "__main__":
    generate_svg_blueprint("/home/isklv/orca/neuroflow/electric_buggy/blueprint_drawings.svg")
