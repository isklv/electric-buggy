#!/usr/bin/env python3
"""
Скрипт генерации полноценной 3D-сцены и проекта .blend для Blender 5.x
"""
import sys
import math

try:
    import bpy
    import mathutils
except ImportError:
    print("Этот скрипт должен запускаться внутри Blender: blender -b -P build_blender_scene.py")
    sys.exit(1)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Удаляем все коллекции и объекты
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def create_material(name, color, roughness=0.4, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    # Blender 4/5: Base Color, Roughness, Metallic
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

def add_beam(collection, p1, p2, width, height, mat, name="Beam"):
    """Создает призматический брус между точками p1 и p2 (координаты в метрах)"""
    v1 = mathutils.Vector(p1)
    v2 = mathutils.Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-4:
        return None

    mid = (v1 + v2) / 2.0
    
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, height, length)
    obj.location = mid

    # Ориентация вдоль вектора diff
    rot_quat = mathutils.Vector((0, 0, 1)).rotation_difference(diff)
    obj.rotation_euler = rot_quat.to_euler()

    # Применяем трансформации scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if mat:
        obj.data.materials.append(mat)

    # Перемещаем в нужную коллекцию
    bpy.context.scene.collection.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def build_buggy():
    clear_scene()

    # Единицы измерения: метры
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

    # Коллекции
    col_base = bpy.data.collections.new("01_Chassis_Base_50x50")
    col_cage = bpy.data.collections.new("02_RollCage_40x40")
    col_susp = bpy.data.collections.new("03_Suspension_IRS")
    col_pwr  = bpy.data.collections.new("04_Powertrain_QS138")
    col_bat  = bpy.data.collections.new("05_Batteries_72V")
    col_plow = bpy.data.collections.new("06_SnowPlow_Mount")

    for c in [col_base, col_cage, col_susp, col_pwr, col_bat, col_plow]:
        bpy.context.scene.collection.children.link(c)

    # Материалы
    mat_base = create_material("Mat_Frame50x50", (0.85, 0.45, 0.05, 1.0), roughness=0.3, metallic=0.7) # Оранжевый металлик
    mat_cage = create_material("Mat_RollCage40x40", (0.05, 0.5, 0.9, 1.0), roughness=0.3, metallic=0.6) # Синий каркас
    mat_susp = create_material("Mat_Suspension", (0.1, 0.75, 0.4, 1.0), roughness=0.4, metallic=0.5)   # Зеленый
    mat_tire = create_material("Mat_TireRubber", (0.05, 0.05, 0.06, 1.0), roughness=0.9, metallic=0.0) # Резина
    mat_rim  = create_material("Mat_WheelRim", (0.7, 0.72, 0.75, 1.0), roughness=0.2, metallic=0.9)    # Алюминий/Сталь
    mat_bat  = create_material("Mat_BatteryPack", (0.6, 0.15, 0.85, 1.0), roughness=0.3, metallic=0.3) # Фиолетовый
    mat_motor= create_material("Mat_MotorDrive", (0.85, 0.1, 0.1, 1.0), roughness=0.3, metallic=0.8)   # Красный
    mat_plow = create_material("Mat_SnowBlade", (0.05, 0.75, 0.85, 1.0), roughness=0.4, metallic=0.5)  # Бирюзовый

    # Размеры в метрах
    gc = 0.280       # клиренс 280 мм
    half_w = 0.550   # полуширина 550 мм (ширина рамы 1.1 м)
    z_f = 1.050      # передний торец
    z_r = -1.050     # задний торец

    # --- 1. Нижняя рама 50х50х2.5 ---
    add_beam(col_base, (-half_w, gc, z_r), (-half_w, gc, z_f), 0.05, 0.05, mat_base, "Sill_Left")
    add_beam(col_base, (half_w, gc, z_r), (half_w, gc, z_f), 0.05, 0.05, mat_base, "Sill_Right")
    add_beam(col_base, (-half_w, gc, z_f), (half_w, gc, z_f), 0.05, 0.05, mat_base, "Cross_Front")
    add_beam(col_base, (-half_w, gc, z_r), (half_w, gc, z_r), 0.05, 0.05, mat_base, "Cross_Rear")
    add_beam(col_base, (-half_w, gc, 0), (half_w, gc, 0), 0.05, 0.05, mat_base, "Cross_Center")
    add_beam(col_base, (-half_w, gc, 0.50), (half_w, gc, 0.50), 0.05, 0.05, mat_base, "Cross_Front_Susp")
    add_beam(col_base, (-half_w, gc, -0.50), (half_w, gc, -0.50), 0.05, 0.05, mat_base, "Cross_Rear_Susp")

    # --- 2. Каркас безопасности 40х40х2.0 ---
    roof_h = gc + 1.150
    roof_w = 0.480
    z_A = 0.300
    z_B = -0.550

    # Стойки
    add_beam(col_cage, (-half_w, gc, z_B), (-roof_w, roof_h, z_B), 0.04, 0.04, mat_cage, "B_Pillar_L")
    add_beam(col_cage, (half_w, gc, z_B), (roof_w, roof_h, z_B), 0.04, 0.04, mat_cage, "B_Pillar_R")
    add_beam(col_cage, (-half_w, gc, z_A), (-roof_w, roof_h, z_A - 0.1), 0.04, 0.04, mat_cage, "A_Pillar_L")
    add_beam(col_cage, (half_w, gc, z_A), (roof_w, roof_h, z_A - 0.1), 0.04, 0.04, mat_cage, "A_Pillar_R")

    # Крыша
    add_beam(col_cage, (-roof_w, roof_h, z_A - 0.1), (roof_w, roof_h, z_A - 0.1), 0.04, 0.04, mat_cage, "Roof_Front")
    add_beam(col_cage, (-roof_w, roof_h, z_B), (roof_w, roof_h, z_B), 0.04, 0.04, mat_cage, "Roof_Rear")
    add_beam(col_cage, (-roof_w, roof_h, z_B), (-roof_w, roof_h, z_A - 0.1), 0.04, 0.04, mat_cage, "Roof_Side_L")
    add_beam(col_cage, (roof_w, roof_h, z_B), (roof_w, roof_h, z_A - 0.1), 0.04, 0.04, mat_cage, "Roof_Side_R")

    # Задние диагонали моторного отсека
    add_beam(col_cage, (-roof_w, roof_h, z_B), (-half_w, gc, z_r), 0.04, 0.04, mat_cage, "Motor_Bay_Diag_L")
    add_beam(col_cage, (roof_w, roof_h, z_B), (half_w, gc, z_r), 0.04, 0.04, mat_cage, "Motor_Bay_Diag_R")
    add_beam(col_cage, (-half_w, gc, z_B), (roof_w, roof_h, z_B), 0.03, 0.03, mat_cage, "Rear_Cross_Diag_1")
    add_beam(col_cage, (half_w, gc, z_B), (-roof_w, roof_h, z_B), 0.03, 0.03, mat_cage, "Rear_Cross_Diag_2")

    # Передний капот
    add_beam(col_cage, (-half_w, gc, z_A), (-0.3, gc + 0.35, z_f), 0.04, 0.04, mat_cage, "Hood_Diag_L")
    add_beam(col_cage, (half_w, gc, z_A), (0.3, gc + 0.35, z_f), 0.04, 0.04, mat_cage, "Hood_Diag_R")
    add_beam(col_cage, (-0.3, gc + 0.35, z_f), (0.3, gc + 0.35, z_f), 0.04, 0.04, mat_cage, "Hood_Cross")

    # Пороги безопасности
    add_beam(col_cage, (-half_w - 0.08, gc + 0.35, z_B), (-half_w - 0.08, gc + 0.35, z_A), 0.04, 0.04, mat_cage, "Side_Protection_L")
    add_beam(col_cage, (half_w + 0.08, gc + 0.35, z_B), (half_w + 0.08, gc + 0.35, z_A), 0.04, 0.04, mat_cage, "Side_Protection_R")

    # --- 3. Подвеска и Колеса ---
    r_wheel = 0.288
    track_half = 0.650

    def create_wheel(x, z, name):
        # Шина
        bpy.ops.mesh.primitive_cylinder_add(radius=r_wheel, depth=0.175, vertices=32)
        tire = bpy.context.active_object
        tire.name = f"{name}_Tire"
        tire.rotation_euler = (0, 0, math.pi / 2)
        tire.location = (x, r_wheel, z)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        tire.data.materials.append(mat_tire)
        bpy.context.scene.collection.objects.unlink(tire)
        col_susp.objects.link(tire)

        # Диск
        bpy.ops.mesh.primitive_cylinder_add(radius=0.165, depth=0.176, vertices=24)
        rim = bpy.context.active_object
        rim.name = f"{name}_Rim"
        rim.rotation_euler = (0, 0, math.pi / 2)
        rim.location = (x, r_wheel, z)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        rim.data.materials.append(mat_rim)
        bpy.context.scene.collection.objects.unlink(rim)
        col_susp.objects.link(rim)

        # А-образные рычаги
        sign = 1 if x > 0 else -1
        in_x = sign * half_w
        out_x = sign * (track_half - 0.05)
        # Нижний рычаг
        add_beam(col_susp, (in_x, gc, z - 0.12), (out_x, r_wheel - 0.04, z), 0.025, 0.025, mat_susp, f"{name}_Arm_Low1")
        add_beam(col_susp, (in_x, gc, z + 0.12), (out_x, r_wheel - 0.04, z), 0.025, 0.025, mat_susp, f"{name}_Arm_Low2")
        # Верхний рычаг
        add_beam(col_susp, (in_x * 0.7, gc + 0.22, z - 0.10), (out_x, r_wheel + 0.06, z), 0.025, 0.025, mat_susp, f"{name}_Arm_Up1")
        add_beam(col_susp, (in_x * 0.7, gc + 0.22, z + 0.10), (out_x, r_wheel + 0.06, z), 0.025, 0.025, mat_susp, f"{name}_Arm_Up2")
        # Амортизатор
        add_beam(col_susp, (out_x - sign * 0.04, r_wheel, z), (in_x * 0.6, gc + 0.35, z), 0.035, 0.035, mat_rim, f"{name}_Shock")

    create_wheel(track_half, z_f - 0.1, "Front_Right")
    create_wheel(-track_half, z_f - 0.1, "Front_Left")
    create_wheel(track_half, z_r + 0.1, "Rear_Right")
    create_wheel(-track_half, z_r + 0.1, "Rear_Left")

    # Привода заднего моста (ШРУСы)
    add_beam(col_susp, (0, r_wheel, z_r + 0.1), (track_half - 0.06, r_wheel, z_r + 0.1), 0.03, 0.03, mat_rim, "Axle_Shaft_R")
    add_beam(col_susp, (0, r_wheel, z_r + 0.1), (-track_half + 0.06, r_wheel, z_r + 0.1), 0.03, 0.03, mat_rim, "Axle_Shaft_L")

    # --- 4. Модули аккумуляторов (2 шт по центру) ---
    def create_battery(z_pos, name):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        bat = bpy.context.active_object
        bat.name = name
        bat.scale = (0.32, 0.22, 0.42)
        bat.location = (0, gc + 0.13, z_pos)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bat.data.materials.append(mat_bat)
        bpy.context.scene.collection.objects.unlink(bat)
        col_bat.objects.link(bat)

    create_battery(0.10, "Battery_Pack_01_50km")
    create_battery(-0.35, "Battery_Pack_02_Ext50km")

    # --- 5. Силовая установка (QS138 + Дифференциал) ---
    # Редуктор/дифференциал
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.18, vertices=24)
    diff = bpy.context.active_object
    diff.name = "Differential_VAZ2108"
    diff.rotation_euler = (0, 0, math.pi / 2)
    diff.location = (0, r_wheel, z_r + 0.1)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    diff.data.materials.append(mat_motor)
    bpy.context.scene.collection.objects.unlink(diff)
    col_pwr.objects.link(diff)

    # Ведомая звезда 47T
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.01, vertices=32)
    sproc = bpy.context.active_object
    sproc.name = "Sprocket_47T_520"
    sproc.rotation_euler = (0, 0, math.pi / 2)
    sproc.location = (0.04, r_wheel, z_r + 0.1)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    sproc.data.materials.append(mat_rim)
    bpy.context.scene.collection.objects.unlink(sproc)
    col_pwr.objects.link(sproc)

    # Мотор QS138 70H
    bpy.ops.mesh.primitive_cylinder_add(radius=0.105, depth=0.23, vertices=32)
    motor = bpy.context.active_object
    motor.name = "Motor_QS138_70H"
    motor.rotation_euler = (0, 0, math.pi / 2)
    motor.location = (0, r_wheel + 0.23, z_r + 0.25)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    motor.data.materials.append(mat_motor)
    bpy.context.scene.collection.objects.unlink(motor)
    col_pwr.objects.link(motor)

    # Контроллер Votol EM150
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ctrl = bpy.context.active_object
    ctrl.name = "Controller_VOTOL_EM150"
    ctrl.scale = (0.20, 0.09, 0.28)
    ctrl.location = (0, roof_h - 0.45, z_B)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ctrl.data.materials.append(mat_rim)
    bpy.context.scene.collection.objects.unlink(ctrl)
    col_pwr.objects.link(ctrl)

    # --- 6. Отвал для снега ---
    # Приемный квадрат 50х50
    add_beam(col_plow, (0, gc, z_f), (0, gc, z_f + 0.25), 0.06, 0.06, mat_plow, "Plow_Hitch_Receiver")
    # Дышло отвала
    add_beam(col_plow, (-0.35, gc - 0.05, z_f + 0.6), (0, gc, z_f + 0.25), 0.05, 0.05, mat_plow, "Plow_A_Arm_L")
    add_beam(col_plow, (0.35, gc - 0.05, z_f + 0.6), (0, gc, z_f + 0.25), 0.05, 0.05, mat_plow, "Plow_A_Arm_R")

    # Сам отвал (лопата 1.4 м шириной)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    blade = bpy.context.active_object
    blade.name = "Snow_Plow_Blade_1400mm"
    blade.scale = (1.40, 0.45, 0.06)
    blade.location = (0, gc + 0.08, z_f + 0.65)
    blade.rotation_euler = (0, -0.35, 0) # скос для отброса снега вправо
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    blade.data.materials.append(mat_plow)
    bpy.context.scene.collection.objects.unlink(blade)
    col_plow.objects.link(blade)

    # Камера и свет
    cam_data = bpy.data.cameras.new("Main_Camera")
    cam = bpy.data.objects.new("Main_Camera", cam_data)
    cam.location = (2.8, -3.2, 2.2)
    cam.rotation_euler = (math.radians(64), 0, math.radians(40))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    light_data = bpy.data.lights.new(name="Sun_Light", type='SUN')
    light_data.energy = 4.0
    light = bpy.data.objects.new("Sun_Light", light_data)
    light.location = (3, -3, 6)
    light.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))
    bpy.context.scene.collection.objects.link(light)

    print("Построение электробагги в Blender завершено успешно!")

if __name__ == "__main__":
    blend_out = "/home/isklv/orca/neuroflow/electric_buggy/electric_buggy.blend"
    build_buggy()
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"Файл сохранен: {blend_out}")
