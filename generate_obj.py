#!/usr/bin/env python3
"""
Генератор 3D Wavefront .OBJ файла рамы и шасси электробагги
"""
import os
import math

def write_box_to_obj(f, v_offset, p1, p2, width, height, name="beam"):
    """Создает призматический брус (профильную трубу) между точками p1 и p2"""
    # Вектор направления
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 1e-4:
        return v_offset
    
    # Нормализуем направление
    dir_v = (dx/L, dy/L, dz/L)
    
    # Перпендикулярные векторы для сечения
    up = (0, 1, 0)
    if abs(dir_v[1]) > 0.95:
        up = (1, 0, 0)
    
    # u = dir x up
    ux = dir_v[1]*up[2] - dir_v[2]*up[1]
    uy = dir_v[2]*up[0] - dir_v[0]*up[2]
    uz = dir_v[0]*up[1] - dir_v[1]*up[0]
    u_len = math.sqrt(ux*ux + uy*uy + uz*uz)
    u = (ux/u_len * (width/2), uy/u_len * (width/2), uz/u_len * (width/2))
    
    # v = u x dir
    vx = uy*dir_v[2] - uz*dir_v[1]
    vy = uz*dir_v[0] - ux*dir_v[2]
    vz = ux*dir_v[1] - uy*dir_v[0]
    v_len = math.sqrt(vx*vx + vy*vy + vz*vz)
    v = (vx/v_len * (height/2), vy/v_len * (height/2), vz/v_len * (height/2))
    
    # 8 вершин прямоугольного параллелепипеда
    # 4 на старте (p1)
    c1 = (p1[0] + u[0] + v[0], p1[1] + u[1] + v[1], p1[2] + u[2] + v[2])
    c2 = (p1[0] - u[0] + v[0], p1[1] - u[1] + v[1], p1[2] - u[2] + v[2])
    c3 = (p1[0] - u[0] - v[0], p1[1] - u[1] - v[1], p1[2] - u[2] - v[2])
    c4 = (p1[0] + u[0] - v[0], p1[1] + u[1] - v[1], p1[2] + u[2] - v[2])
    # 4 на финише (p2)
    c5 = (p2[0] + u[0] + v[0], p2[1] + u[1] + v[1], p2[2] + u[2] + v[2])
    c6 = (p2[0] - u[0] + v[0], p2[1] - u[1] + v[1], p2[2] - u[2] + v[2])
    c7 = (p2[0] - u[0] - v[0], p2[1] - u[1] - v[1], p2[2] - u[2] - v[2])
    c8 = (p2[0] + u[0] - v[0], p2[1] + u[1] - v[1], p2[2] + u[2] - v[2])
    
    verts = [c1, c2, c3, c4, c5, c6, c7, c8]
    f.write(f"o {name}\n")
    for vert in verts:
        f.write(f"v {vert[0]:.2f} {vert[1]:.2f} {vert[2]:.2f}\n")
    
    # 6 граней (1-based index)
    vo = v_offset
    faces = [
        (vo+1, vo+2, vo+3, vo+4), # start cap
        (vo+5, vo+8, vo+7, vo+6), # end cap
        (vo+1, vo+5, vo+6, vo+2), # side 1
        (vo+2, vo+6, vo+7, vo+3), # side 2
        (vo+3, vo+7, vo+8, vo+4), # side 3
        (vo+4, vo+8, vo+5, vo+1), # side 4
    ]
    for face in faces:
        f.write(f"f {face[0]} {face[1]} {face[2]} {face[3]}\n")
        
    return v_offset + 8

def generate_obj(output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Wavefront OBJ: Electric Buggy 2-seater (RWD, IRS)\n")
        f.write("# Units: mm\n")
        
        vo = 0
        groundClearance = 280
        baseZ_front = 1050
        baseZ_rear = -1050
        halfW = 550
        roofH = groundClearance + 1150
        roofHalfW = 480
        A_pillar_Z = 300
        B_pillar_Z = -550
        
        # 1. Нижняя рама 50х50
        beams_50 = [
            ([-halfW, groundClearance, baseZ_rear], [-halfW, groundClearance, baseZ_front], "Sill_Left"),
            ([halfW, groundClearance, baseZ_rear], [halfW, groundClearance, baseZ_front], "Sill_Right"),
            ([-halfW, groundClearance, baseZ_front], [halfW, groundClearance, baseZ_front], "Cross_Front"),
            ([-halfW, groundClearance, baseZ_rear], [halfW, groundClearance, baseZ_rear], "Cross_Rear"),
            ([-halfW, groundClearance, 0], [halfW, groundClearance, 0], "Cross_Mid"),
            ([-halfW, groundClearance, -500], [halfW, groundClearance, -500], "Cross_SeatRear"),
            ([-halfW, groundClearance, 500], [halfW, groundClearance, 500], "Cross_FrontSusp"),
        ]
        for p1, p2, name in beams_50:
            vo = write_box_to_obj(f, vo, p1, p2, 50, 50, name)
            
        # 2. Каркас безопасности 40х40
        beams_40 = [
            ([-halfW, groundClearance, B_pillar_Z], [-roofHalfW, roofH, B_pillar_Z], "B_Pillar_L"),
            ([halfW, groundClearance, B_pillar_Z], [roofHalfW, roofH, B_pillar_Z], "B_Pillar_R"),
            ([-halfW, groundClearance, A_pillar_Z], [-roofHalfW, roofH, A_pillar_Z - 100], "A_Pillar_L"),
            ([halfW, groundClearance, A_pillar_Z], [roofHalfW, roofH, A_pillar_Z - 100], "A_Pillar_R"),
            ([-roofHalfW, roofH, A_pillar_Z - 100], [roofHalfW, roofH, A_pillar_Z - 100], "Roof_Front"),
            ([-roofHalfW, roofH, B_pillar_Z], [roofHalfW, roofH, B_pillar_Z], "Roof_Rear"),
            ([-roofHalfW, roofH, B_pillar_Z], [-roofHalfW, roofH, A_pillar_Z - 100], "Roof_Side_L"),
            ([roofHalfW, roofH, B_pillar_Z], [roofHalfW, roofH, A_pillar_Z - 100], "Roof_Side_R"),
            ([-roofHalfW, roofH, B_pillar_Z], [-halfW, groundClearance, baseZ_rear], "Engine_Diagonal_L"),
            ([roofHalfW, roofH, B_pillar_Z], [halfW, groundClearance, baseZ_rear], "Engine_Diagonal_R"),
            ([-halfW, groundClearance, B_pillar_Z], [roofHalfW, roofH, B_pillar_Z], "Rear_Cross_Diag1"),
            ([halfW, groundClearance, B_pillar_Z], [-roofHalfW, roofH, B_pillar_Z], "Rear_Cross_Diag2"),
            ([-halfW, groundClearance, A_pillar_Z], [-300, groundClearance + 350, baseZ_front], "Hood_Diag_L"),
            ([halfW, groundClearance, A_pillar_Z], [300, groundClearance + 350, baseZ_front], "Hood_Diag_R"),
            ([-300, groundClearance + 350, baseZ_front], [300, groundClearance + 350, baseZ_front], "Hood_Cross"),
            ([-halfW - 80, groundClearance + 350, B_pillar_Z], [-halfW - 80, groundClearance + 350, A_pillar_Z], "Side_Bar_L"),
            ([halfW + 80, groundClearance + 350, B_pillar_Z], [halfW + 80, groundClearance + 350, A_pillar_Z], "Side_Bar_R"),
        ]
        for p1, p2, name in beams_40:
            vo = write_box_to_obj(f, vo, p1, p2, 40, 40, name)
            
        # 3. Батарейные модули (два бокса в тоннеле)
        vo = write_box_to_obj(f, vo, [-160, groundClearance + 20, 100 - 210], [160, groundClearance + 240, 100 + 210], 320, 220, "Battery_Box_1")
        vo = write_box_to_obj(f, vo, [-160, groundClearance + 20, -350 - 210], [160, groundClearance + 240, -350 + 210], 320, 220, "Battery_Box_2")
        
        # 4. Передний силовой квадрат под отвал (Hitch)
        vo = write_box_to_obj(f, vo, [0, groundClearance, baseZ_front], [0, groundClearance, baseZ_front + 250], 60, 60, "Front_Plow_Hitch")

    print(f"3D OBJ модель сохранена в: {output_file}")

if __name__ == "__main__":
    generate_obj("/home/isklv/orca/neuroflow/electric_buggy/buggy_frame_chassis.obj")
