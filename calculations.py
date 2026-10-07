#!/usr/bin/env python3
"""
Расчет тягово-динамических характеристик, энергобаланса и раскроя рамы
для двухместного утилитарного электробагги (RWD, IRS)
"""
import math

def calculate_powertrain():
    print("=" * 60)
    print(" 1. ТЯГОВО-ДИНАМИЧЕСКИЙ РАСЧЕТ И ТРАНСМИССИЯ")
    print("=" * 60)
    
    # Исходные данные
    wheel_rim_inch = 13
    tire_width_mm = 175
    tire_profile_pct = 70
    
    # Диаметр колеса
    sidewall_m = (tire_width_mm * (tire_profile_pct / 100)) / 1000.0
    rim_m = (wheel_rim_inch * 25.4) / 1000.0
    wheel_diameter_m = rim_m + 2 * sidewall_m
    wheel_radius_m = wheel_diameter_m / 2.0
    wheel_circ_m = math.pi * wheel_diameter_m
    
    print(f"Колесо: 175/70 R13")
    print(f"Диаметр колеса: {wheel_diameter_m*1000:.1f} мм (радиус: {wheel_radius_m*1000:.1f} мм)")
    print(f"Длина окружности колеса: {wheel_circ_m:.3f} м")
    
    # Мотор QS138 70H V3
    motor_rpm_nom = 3800
    motor_rpm_max = 4400
    motor_internal_ratio = 2.35  # внутренний редуктор QS138 V3
    motor_torque_nom_nm = 32.0   # на валу мотора
    motor_torque_peak_nm = 90.0  # на валу мотора
    
    # Выходной вал мотора (после встроенного редуктора)
    shaft_torque_nom = motor_torque_nom_nm * motor_internal_ratio
    shaft_torque_peak = motor_torque_peak_nm * motor_internal_ratio
    print(f"\nМотор: QS138 70H V3 (внутренний редуктор 1:{motor_internal_ratio})")
    print(f"Крутящий момент на выходной звезде мотора: ном. {shaft_torque_nom:.1f} Нм, пик {shaft_torque_peak:.1f} Нм")
    
    # Звезды цепи 520
    sprocket_motor = 14
    sprocket_diff = 47
    chain_ratio = sprocket_diff / sprocket_motor
    total_ratio = motor_internal_ratio * chain_ratio
    chain_efficiency = 0.95
    
    print(f"\nЦепная передача 520:")
    print(f"Ведущая звезда: {sprocket_motor} зубьев")
    print(f"Ведомая звезда: {sprocket_diff} зубьев")
    print(f"Передаточное число цепи: 1:{chain_ratio:.3f}")
    print(f"ОБЩЕЕ передаточное отношение (мотор -> колеса): 1:{total_ratio:.2f}")
    
    # Скорости
    speed_nom_kmh = (motor_rpm_nom / total_ratio) * wheel_circ_m * 60.0 / 1000.0
    speed_max_kmh = (motor_rpm_max / total_ratio) * wheel_circ_m * 60.0 / 1000.0
    
    print(f"\nРасчетные скорости:")
    print(f"Номинальная крейсерская скорость (3800 об/мин): {speed_nom_kmh:.1f} км/ч")
    print(f"Максимальная скорость (4400 об/мин): {speed_max_kmh:.1f} км/ч")
    
    # Тяговое усилие на колесах (2 задних колеса)
    wheel_torque_nom = shaft_torque_nom * chain_ratio * chain_efficiency
    wheel_torque_peak = shaft_torque_peak * chain_ratio * chain_efficiency
    tractive_force_nom_n = wheel_torque_nom / wheel_radius_m
    tractive_force_peak_n = wheel_torque_peak / wheel_radius_m
    tractive_force_peak_kg = tractive_force_peak_n / 9.81
    
    print(f"\nТяговые характеристики (для преодоления снега и подъемов):")
    print(f"Крутящий момент на колесах (суммарный): ном. {wheel_torque_nom:.1f} Нм, пик {wheel_torque_peak:.1f} Нм")
    print(f"Линейная сила тяги на колесах: ном. {tractive_force_nom_n:.0f} Н, пик {tractive_force_peak_n:.0f} Н")
    print(f"Пиковое толкающее усилие: {tractive_force_peak_kg:.1f} кгс (~{tractive_force_peak_kg/1000:.2f} тонны тяги!)")
    print("-> Этого усилия достаточно для толкания снежного вала до 250-300 кг перед отвалом.")

def calculate_battery():
    print("\n" + "=" * 60)
    print(" 2. РАСЧЕТ АККУМУЛЯТОРА И ЭНЕРГОПОТРЕБЛЕНИЯ")
    print("=" * 60)
    
    cells_s = 20  # 20S NMC (номинал 72V, макс 84V, мин 60V)
    v_nom = cells_s * 3.65  # 73V
    
    # Блок 1 (базовый)
    capacity_ah_mod1 = 48.0
    energy_wh_mod1 = v_nom * capacity_ah_mod1
    usable_energy_mod1 = energy_wh_mod1 * 0.85  # 85% полезной емкости (DOD 10-95%)
    
    # Расход энергии
    consumption_summer_wh_km = 65.0  # лето, умеренная езда 40-45 км/ч
    consumption_winter_wh_km = 85.0  # зима / рыхлый грунт / толкание снега
    
    range_mod1_summer = usable_energy_mod1 / consumption_summer_wh_km
    range_mod1_winter = usable_energy_mod1 / consumption_winter_wh_km
    
    # Блок 1 + Блок 2 (расширенная)
    capacity_ah_total = capacity_ah_mod1 * 2
    usable_energy_total = usable_energy_mod1 * 2
    range_total_summer = usable_energy_total / consumption_summer_wh_km
    range_total_winter = usable_energy_total / consumption_winter_wh_km
    
    print(f"Химия: 20S Li-ion/NMC (Номинал: {v_nom:.1f} В, Полный: 84.0 В, Отсечка: 60.0 В)")
    print(f"\n--- МОДУЛЬ №1 (Базовый комплект) ---")
    print(f"Емкость: {capacity_ah_mod1} А·ч ({energy_wh_mod1/1000:.2f} кВт·ч брутто, {usable_energy_mod1/1000:.2f} кВт·ч полезных)")
    print(f"Примерный вес модуля: ~22-24 кг (с BMS и корпусом)")
    print(f"Запас хода летом: {range_mod1_summer:.1f} км")
    print(f"Запас хода зимой / по снегу: {range_mod1_winter:.1f} км")
    
    print(f"\n--- МОДУЛЬ №1 + МОДУЛЬ №2 (Параллельная связка) ---")
    print(f"Суммарная емкость: {capacity_ah_total} А·ч ({usable_energy_total/1000:.2f} кВт·ч полезных)")
    print(f"Суммарный вес двух модулей: ~45 кг")
    print(f"Запас хода летом: {range_total_summer:.1f} км")
    print(f"Запас хода зимой / по снегу: {range_total_winter:.1f} км")
    
    # Токи
    i_peak_controller = 160.0  # Ампер пик контроллера
    c_rate_single = i_peak_controller / capacity_ah_mod1
    c_rate_dual = (i_peak_controller / 2) / capacity_ah_mod1
    print(f"\nНагрузка на ячейки при пиковом токе контроллера {i_peak_controller}А:")
    print(f"С одной батареей: разряд {c_rate_single:.2f}C (допустимо для качественных призматиков NMC)")
    print(f"С двумя батареями: разряд всего {c_rate_dual:.2f}C (максимальный ресурс и отсутствие просадки напряжения!)")

def calculate_frame_cuts():
    print("\n" + "=" * 60)
    print(" 3. ВЕДОМОСТЬ РАСКРОЯ ПРОФИЛЬНОЙ ТРУБЫ (БЕЗ ТРУБОГИБА)")
    print("=" * 60)
    
    cuts = [
        # Назначение, Профиль, Длина (мм), Кол-во (шт), Торцы / Запил
        ("Нижние продольные лонжероны рамы", "50х50х2.5", 2200, 2, "Торцы 45° спереди / 90° сзади"),
        ("Нижние поперечины днища", "50х50х2.5", 1100, 4, "Прямой рез 90°"),
        ("Передний силовой брус (под отвал)", "50х50х2.5", 1100, 1, "Прямой рез 90° + приемный квадрат 50x50"),
        ("Задний подрамник редуктора", "50х50х2.5", 800, 2, "Прямой рез 90°"),
        
        ("Главные дуги безопасности (А-стойки)", "40х40х2.0", 1150, 2, "Запил 25° внизу / 45° вверху"),
        ("Главные дуги безопасности (В-стойки задние)", "40х40х2.0", 1100, 2, "Прямой рез 90° внизу / 45° вверху"),
        ("Верхние продольные брусья крыши", "40х40х2.0", 950, 2, "Запилы 45° по краям"),
        ("Верхние поперечины крыши", "40х40х2.0", 1000, 3, "Прямой рез 90°"),
        ("Боковые защитные брусья (пороги/отбойники)", "40х40х2.0", 1250, 2, "Запил 30° спереди / 90° сзади"),
        ("Диагональные укосины заднего креста", "40х40х2.0", 1300, 2, "Угловой запил по месту (~38°)"),
        ("Передние укосины капота к ступицам", "40х40х2.0", 750, 2, "Запил 45°"),
        
        ("Каркас тоннеля АКБ (продольные)", "40х20х2.0", 900, 4, "Прямой рез 90°"),
        ("Поперечины под сиденья", "40х20х2.0", 1100, 3, "Прямой рез 90°"),
        ("Стойки крепления амортизаторов (перед)", "40х20х2.0", 450, 4, "Срез под угол рычага"),
        ("Стойки крепления амортизаторов (зад)", "40х20х2.0", 500, 4, "Срез под угол рычага"),
    ]
    
    total_50x50 = 0
    total_40x40 = 0
    total_40x20 = 0
    
    print(f"{'Узел':<40} | {'Профиль':<10} | {'Длина, мм':<10} | {'Кол-во':<6} | {'Обработка'}")
    print("-" * 95)
    for name, prof, length, qty, desc in cuts:
        print(f"{name:<40} | {prof:<10} | {length:<10} | {qty:<6} | {desc}")
        meters = (length * qty) / 1000.0
        if "50х50" in prof:
            total_50x50 += meters
        elif "40х40" in prof:
            total_40x40 += meters
        elif "40х20" in prof:
            total_40x20 += meters
            
    print("-" * 95)
    print(f"ИТОГО ПОТРЕБНОСТЬ В МЕТАЛЛЕ (с запасом 10% на раскрой):")
    print(f"  • Профильная труба 50х50х2.5 мм: {total_50x50 * 1.10:.1f} м (примерно {(total_50x50 * 1.10) / 6:.1f} хлыстов по 6м)")
    print(f"  • Профильная труба 40х40х2.0 мм: {total_40x40 * 1.10:.1f} м (примерно {(total_40x40 * 1.10) / 6:.1f} хлыстов по 6м)")
    print(f"  • Профильная труба 40х20х2.0 мм: {total_40x20 * 1.10:.1f} м (примерно {(total_40x20 * 1.10) / 6:.1f} хлыстов по 6м)")
    print(f"  • Листовая сталь 3.0 мм (на косынки, уши амортизаторов, площадки): ~1.5 м²")

if __name__ == "__main__":
    calculate_powertrain()
    calculate_battery()
    calculate_frame_cuts()
