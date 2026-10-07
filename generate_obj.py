#!/usr/bin/env python3
"""
Генератор 3D Wavefront .OBJ шасси электробагги.
Геометрия собирается в generate_3d.py (из chassis_geometry.py), этот скрипт оставлен
для совместимости: пишет тот же OBJ и viewer.html.
"""
import os

from generate_3d import generate

if __name__ == "__main__":
    generate(os.path.dirname(os.path.abspath(__file__)))
