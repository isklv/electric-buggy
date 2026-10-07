#!/usr/bin/env python3
"""
Генератор детальной 3D-модели электробагги.

1. Считает геометрию из chassis_geometry.py -> web/geometry.json
2. Собирает автономный viewer.html: web/viewer_template.html + web/buggy_scene.js + геометрия
   (открывается двойным кликом, three.js грузится с CDN)
3. Через Node (tools/export_model.mjs) строит ту же сцену и пишет buggy_frame_chassis.obj + .mtl
   (нужно один раз: cd tools && npm install)

Координаты, мм: X — вправо, Y — вверх, Z — вперед. Начало — на земле посередине базы.
"""
import json
import os
import shutil
import subprocess
import sys

import chassis_geometry as g

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "web")
TOOLS = os.path.join(HERE, "tools")

# Входной вал КПП относительно оси дифференциала (Y, Z): корпус развернут назад-вверх
INPUT_AXIS = (150.0, -135.0)


def geometry():
    inner, _ = g.ideal_tie_rod_inner()
    s_low, s_up = g.shock_points()
    gears = {name: (v, f) for name, _, _, v, _, f in g.gearbox_table()[2]}
    return {
        "wheelbase": g.WHEELBASE, "track": g.TRACK, "halfTrack": g.HALF_TRACK,
        "wheelR": g.WHEEL_RADIUS_STATIC, "tireR": g.WHEEL_RADIUS_STATIC + 9, "tireW": g.TIRE_WIDTH,
        "rimEt": g.RIM_ET, "hubFaceX": g.HUB_FACE_X,
        "lbj": g.LBJ, "ubj": g.UBJ, "lowerInner": g.LOWER_INNER, "upperInner": g.UPPER_INNER,
        "lowerArmZ": g.LOWER_ARM_Z, "upperArmZ": g.UPPER_ARM_Z,
        "rearLowerArmZ": g.REAR_LOWER_ARM_Z, "rearUpperArmZ": g.REAR_UPPER_ARM_Z,
        "casterDeg": g.caster_deg(),
        "shockLower": s_low, "shockUpper": s_up, "shockZ": g.SHOCK_Z, "rearShockZ": g.REAR_SHOCK_Z,
        "shockBarY": s_up[1] + 50,
        "steerZ": g.STEER_Z, "rearToeZ": g.REAR_TOE_Z, "steerArmY": g.STEER_ARM_Y,
        "steerPoint": g.steer_point_front_view(), "kingpinXAtSteer": g.kingpin_x_at(g.STEER_ARM_Y),
        "tieRodInner": inner,
        "lugBolts": g.LUG_BOLTS, "lugThickness": g.LUG_THICKNESS, "adapterPlate": g.ADAPTER_PLATE,
        "adapterOutline": g.ADAPTER_OUTLINE, "outerCV": g.OUTER_CV_CENTER, "innerCVX": g.INNER_CV_X,
        "lowerRail": (g.LOWER_INNER[0] - 45, g.LOWER_INNER[1] + 25),
        "upperRail": (g.UPPER_INNER[0] - 40, g.UPPER_INNER[1] + 10),
        "rearRailY": g.REAR_RAIL_Y,
        "floorY": 305, "floorZ": g.WHEELBASE / 2 - g.FRAME_CROSSBEAM_FROM_AXLE, "frameHalfW": g.FRAME_HALF_WIDTH,
        "roofY": 280 + 1150, "roofHalfW": 480, "aZ": 300, "bZ": -550,
        "columnPoints": g.COLUMN_POINTS,
        "inputAxis": INPUT_AXIS, "chainCD": g.chain_center_distance(), "sprocketTeeth": g.CHAIN_DRIVE,
        # для панели характеристик
        "specs": {
            "speed4": round(gears["4"][0]), "speed5": round(gears["5"][0]),
            "pull2": round(gears["2"][1] / 9.81), "clearanceSub": round(g.REAR_RAIL_Y - 25),
        },
    }


def write_viewer(geo):
    with open(os.path.join(WEB, "viewer_template.html"), encoding="utf-8") as fh:
        html = fh.read()
    with open(os.path.join(WEB, "buggy_scene.js"), encoding="utf-8") as fh:
        scene_js = fh.read()
    html = html.replace("/*%GEOMETRY%*/null", json.dumps(geo, ensure_ascii=False))
    html = html.replace("/*%SCENE_JS%*/", scene_js)
    path = os.path.join(HERE, "viewer.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"HTML 3D Viewer сохранен в: {path}")


def export_obj(geo_path):
    if not shutil.which("node"):
        print("! Node.js не найден — OBJ не обновлен", file=sys.stderr)
        return False
    if not os.path.isdir(os.path.join(TOOLS, "node_modules", "three")):
        print("! Нет tools/node_modules — выполните: cd tools && npm install", file=sys.stderr)
        return False
    subprocess.run(["node", os.path.join(TOOLS, "export_model.mjs"), geo_path,
                    os.path.join(HERE, "buggy_frame_chassis.obj")], check=True)
    return True


def generate():
    geo = geometry()
    geo_path = os.path.join(WEB, "geometry.json")
    with open(geo_path, "w", encoding="utf-8") as fh:
        json.dump(geo, fh, ensure_ascii=False, indent=1)
    write_viewer(geo)
    export_obj(geo_path)


if __name__ == "__main__":
    generate()
