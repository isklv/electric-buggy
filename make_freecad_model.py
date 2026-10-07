# -*- coding: utf-8 -*-
"""
FreeCAD Macro / Script: Построение рамы и шасси электробагги
Создает параметрическую модель рамы из профильных труб 50х50, 40х40, 
подвески IRS, отсека двух АКБ и снежного отвала.

Как запустить:
1. В FreeCAD: Меню 'Макросы' -> 'Макросы...' -> Выбрать 'make_freecad_model.py' -> 'Выполнить'
   ИЛИ: перетащить файл в окно FreeCAD.
2. Либо через FreeCAD MCP execute_code.
"""
import math

try:
    import FreeCAD as App
    import Part
except ImportError:
    print("Этот скрипт запускается внутри FreeCAD!")

def create_beam(doc, p1, p2, width, height, name="Beam"):
    """Создает призматическую балку (профильную трубу) между точками p1 и p2"""
    # Вектор направления
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 1e-3:
        return None
    
    # Создаем базовый бокс по центру оси Z
    box = Part.makeBox(width, height, L)
    # Центрируем сечение относительно начала координат
    box.translate(App.Vector(-width/2.0, -height/2.0, 0))
    
    # Вращаем в направлении вектора (dx, dy, dz)
    v_target = App.Vector(dx, dy, dz)
    v_z = App.Vector(0, 0, 1)
    
    rot = App.Rotation(v_z, v_target)
    box.rotate(App.Vector(0, 0, 0), rot.Axis, rot.Angle * 180.0 / math.pi)
    box.translate(App.Vector(p1[0], p1[1], p1[2]))
    
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = box
    return obj

def build_buggy_freecad():
    doc_name = "Electric_Buggy_Chassis"
    doc = App.newDocument(doc_name)
    App.setActiveDocument(doc_name)
    
    gc = 280.0       # клиренс 280 мм
    half_w = 550.0   # полуширина 550 мм
    z_f = 1050.0     # перед
    z_r = -1050.0    # зад
    
    # 1. Нижний силовой периметр (профиль 50х50х2.5)
    grp_base = doc.addObject("App::DocumentObjectGroup", "01_Base_Frame_50x50")
    
    beams_50 = [
        ((-half_w, gc, z_r), (-half_w, gc, z_f), "Sill_Left"),
        ((half_w, gc, z_r), (half_w, gc, z_f), "Sill_Right"),
        ((-half_w, gc, z_f), (half_w, gc, z_f), "Cross_Front"),
        ((-half_w, gc, z_r), (half_w, gc, z_r), "Cross_Rear"),
        ((-half_w, gc, 0), (half_w, gc, 0), "Cross_Center"),
        ((-half_w, gc, 500), (half_w, gc, 500), "Cross_Susp_F"),
        ((-half_w, gc, -500), (half_w, gc, -500), "Cross_Susp_R"),
    ]
    for p1, p2, name in beams_50:
        b = create_beam(doc, p1, p2, 50.0, 50.0, name)
        if b:
            grp_base.addObject(b)
            if hasattr(b, "ViewObject"):
                b.ViewObject.ShapeColor = (0.85, 0.45, 0.1) # оранжевый
                
    # 2. Каркас безопасности (профиль 40х40х2.0)
    grp_cage = doc.addObject("App::DocumentObjectGroup", "02_RollCage_40x40")
    roof_h = gc + 1150.0
    roof_w = 480.0
    z_A = 300.0
    z_B = -550.0
    
    beams_40 = [
        ((-half_w, gc, z_B), (-roof_w, roof_h, z_B), "B_Pillar_L"),
        ((half_w, gc, z_B), (roof_w, roof_h, z_B), "B_Pillar_R"),
        ((-half_w, gc, z_A), (-roof_w, roof_h, z_A - 100), "A_Pillar_L"),
        ((half_w, gc, z_A), (roof_w, roof_h, z_A - 100), "A_Pillar_R"),
        ((-roof_w, roof_h, z_A - 100), (roof_w, roof_h, z_A - 100), "Roof_Front"),
        ((-roof_w, roof_h, z_B), (roof_w, roof_h, z_B), "Roof_Rear"),
        ((-roof_w, roof_h, z_B), (-roof_w, roof_h, z_A - 100), "Roof_Side_L"),
        ((roof_w, roof_h, z_B), (roof_w, roof_h, z_A - 100), "Roof_Side_R"),
        ((-roof_w, roof_h, z_B), (-half_w, gc, z_r), "Engine_Bay_Diag_L"),
        ((roof_w, roof_h, z_B), (half_w, gc, z_r), "Engine_Bay_Diag_R"),
        ((-half_w, gc, z_B), (roof_w, roof_h, z_B), "Rear_Cross_Diag1"),
        ((half_w, gc, z_B), (-roof_w, roof_h, z_B), "Rear_Cross_Diag2"),
        ((-half_w, gc, z_A), (-300, gc + 350, z_f), "Hood_Diag_L"),
        ((half_w, gc, z_A), (300, gc + 350, z_f), "Hood_Diag_R"),
        ((-300, gc + 350, z_f), (300, gc + 350, z_f), "Hood_Cross"),
    ]
    for p1, p2, name in beams_40:
        b = create_beam(doc, p1, p2, 40.0, 40.0, name)
        if b:
            grp_cage.addObject(b)
            if hasattr(b, "ViewObject"):
                b.ViewObject.ShapeColor = (0.1, 0.45, 0.85) # синий
                
    # 3. Батарейные модули (два бокса 72V 48Ah)
    grp_bat = doc.addObject("App::DocumentObjectGroup", "03_Battery_Packs")
    for z_pos, name in [(100, "Battery_Pack_1_50km"), (-350, "Battery_Pack_2_Ext50km")]:
        box_bat = Part.makeBox(320, 220, 420)
        box_bat.translate(App.Vector(-160, gc + 20, z_pos - 210))
        bat_obj = doc.addObject("Part::Feature", name)
        bat_obj.Shape = box_bat
        grp_bat.addObject(bat_obj)
        if hasattr(bat_obj, "ViewObject"):
            bat_obj.ViewObject.ShapeColor = (0.6, 0.15, 0.85) # фиолетовый
            
    # 4. Снегоотвал и силовой крепеж
    grp_plow = doc.addObject("App::DocumentObjectGroup", "04_Snow_Plow")
    hitch = create_beam(doc, (0, gc, z_f), (0, gc, z_f + 250), 60.0, 60.0, "Plow_Hitch_Receiver")
    if hitch: grp_plow.addObject(hitch)
    
    blade = Part.makeBox(1400, 450, 20)
    blade.translate(App.Vector(-700, gc + 50, z_f + 650))
    blade_obj = doc.addObject("Part::Feature", "Snow_Blade_1400mm")
    blade_obj.Shape = blade
    grp_plow.addObject(blade_obj)
    if hasattr(blade_obj, "ViewObject"):
        blade_obj.ViewObject.ShapeColor = (0.05, 0.75, 0.85) # бирюзовый

    doc.recompute()
    print("FreeCAD: Модель успешно сгенерирована!")
    return doc

if __name__ == "__main__":
    if "App" in globals():
        build_buggy_freecad()
