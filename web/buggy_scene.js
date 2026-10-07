/*
 * Детальная 3D-сцена электробагги. Используется и в браузере (viewer.html),
 * и в Node (tools/export_model.mjs -> OBJ/MTL). Без import: THREE передается аргументом.
 *
 * buildBuggy(THREE, G) -> { root, layers, lights, setLights(on) }
 *   G — геометрия из chassis_geometry.py (см. generate_3d.py)
 * Единицы — мм. X — вправо, Y — вверх, Z — вперед.
 */
function buildBuggy(THREE, G) {
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const root = new THREE.Group();
  root.name = 'buggy';
  const layers = {};
  const lights = [];
  const emissives = [];
  let LAYER = 'base';
  let LABEL = '';

  // ---------------------------------------------------------------- материалы
  const M = (color, rough, metal, extra) =>
    new THREE.MeshStandardMaterial(Object.assign({ color, roughness: rough, metalness: metal }, extra || {}));
  const MAT = {
    frame: M(0xc2410c, 0.45, 0.35),           // порошковая краска рамы
    cage: M(0x1e40af, 0.4, 0.35),             // каркас
    arm: M(0x15803d, 0.4, 0.35),              // рычаги
    upper: M(0x0e7490, 0.4, 0.35),
    steel: M(0x6b7280, 0.45, 0.85),
    darkSteel: M(0x374151, 0.5, 0.8),
    zinc: M(0xc7cdd4, 0.3, 0.9),              // оцинкованный крепеж
    chrome: M(0xe5e7eb, 0.12, 1.0),
    alu: M(0xb8bec6, 0.35, 0.9),
    cast: M(0x9ca3af, 0.7, 0.6),              // литье КПП
    rubber: M(0x18181b, 0.92, 0.0),
    tire: M(0x1c1c1f, 0.95, 0.0),
    boot: M(0x111113, 0.75, 0.0),
    rim: M(0xd1d5db, 0.25, 0.95),
    disc: M(0x8a8f96, 0.55, 0.9),
    caliper: M(0xb91c1c, 0.4, 0.5),
    spring: M(0xfacc15, 0.35, 0.6),
    damper: M(0x111827, 0.4, 0.6),
    motor: M(0x1e293b, 0.35, 0.7),
    motorFin: M(0x334155, 0.4, 0.8),
    battery: M(0x6d28d9, 0.35, 0.5),
    batteryLid: M(0x9ca3af, 0.3, 0.9),
    orangeCable: M(0xea580c, 0.6, 0.1),
    redPlastic: M(0xdc2626, 0.5, 0.1),
    blackPlastic: M(0x1f2937, 0.7, 0.05),
    seat: M(0x27272a, 0.85, 0.0),
    seatAccent: M(0x52525b, 0.8, 0.0),
    sheet: M(0x3f3f46, 0.6, 0.5),             // листовой металл пола
    plow: M(0x0891b2, 0.4, 0.4),
    plowEdge: M(0x0f0f10, 0.9, 0.0),
    copper: M(0xb45309, 0.35, 0.9),
    hose: M(0x0b0b0c, 0.8, 0.0),
    roof: M(0x0f172a, 0.2, 0.1, { transparent: true, opacity: 0.55 }),
    glassClear: M(0xffffff, 0.05, 0.0, { transparent: true, opacity: 0.35 }),
    lampWhite: M(0xffffff, 0.2, 0.0, { emissive: 0xfff7e0, emissiveIntensity: 0 }),
    lampRed: M(0x7f1d1d, 0.3, 0.0, { emissive: 0xff1a1a, emissiveIntensity: 0 }),
    lampAmber: M(0x92400e, 0.3, 0.0, { emissive: 0xffa000, emissiveIntensity: 0 }),
    screen: M(0x020617, 0.2, 0.0, { emissive: 0x0ea5e9, emissiveIntensity: 0.6 }),
    reflector: M(0xf1f5f9, 0.08, 1.0),
  };
  for (const [k, m] of Object.entries(MAT)) m.name = k;
  emissives.push([MAT.lampWhite, 2.2], [MAT.lampRed, 1.6], [MAT.lampAmber, 0.5]);

  // ---------------------------------------------------------------- базовые функции
  function layer(name) {
    if (!layers[name]) {
      layers[name] = new THREE.Group();
      layers[name].name = name;
      root.add(layers[name]);
    }
    return layers[name];
  }
  function add(geom, mat, parent) {
    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = LABEL;
    mesh.userData.label = LABEL;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    (parent || layer(LAYER)).add(mesh);
    return mesh;
  }
  // ориентировать объект: локальная ось Y -> направление d
  function alignY(obj, a, b) {
    const d = new THREE.Vector3().subVectors(b, a);
    const len = d.length();
    obj.quaternion.setFromUnitVectors(V(0, 1, 0), d.clone().normalize());
    obj.position.copy(a).addScaledVector(d, 0.5);
    return len;
  }
  // локальная ось Z -> направление a->b, локальная Y максимально вверх
  function alignZ(obj, a, b, upHint) {
    const z = new THREE.Vector3().subVectors(b, a).normalize();
    let up = upHint ? upHint.clone() : V(0, 1, 0);
    if (Math.abs(z.dot(up)) > 0.98) up = V(1, 0, 0);
    const x = new THREE.Vector3().crossVectors(up, z).normalize();
    const y = new THREE.Vector3().crossVectors(z, x);
    obj.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
    obj.position.copy(a);
  }
  function roundedRectShape(w, h, r) {
    const s = new THREE.Shape();
    const x = -w / 2, y = -h / 2;
    s.moveTo(x + r, y);
    s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
    s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
    s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
    return s;
  }
  function roundedRectPath(w, h, r) {
    const p = new THREE.Path();
    const x = -w / 2, y = -h / 2;
    p.moveTo(x + r, y);
    p.lineTo(x + r, y); p.quadraticCurveTo(x, y, x, y + r);
    p.lineTo(x, y + h - r); p.quadraticCurveTo(x, y + h, x + r, y + h);
    p.lineTo(x + w - r, y + h); p.quadraticCurveTo(x + w, y + h, x + w, y + h - r);
    p.lineTo(x + w, y + r); p.quadraticCurveTo(x + w, y, x + w - r, y);
    p.lineTo(x + r, y);
    return p;
  }
  const tubeCache = {};
  // Профильная труба с полой торцевой частью и скругленными углами
  function sqTube(a, b, w, h, mat, wall, upHint) {
    h = h || w;
    wall = wall || (w >= 50 ? 2.5 : 2.0);
    const len = a.distanceTo(b);
    if (len < 1) return null;
    const key = `${w}x${h}x${wall}`;
    if (!tubeCache[key]) {
      const s = roundedRectShape(w, h, wall * 1.6);
      s.holes.push(roundedRectPath(w - 2 * wall, h - 2 * wall, wall * 0.8));
      tubeCache[key] = s;
    }
    const geom = new THREE.ExtrudeGeometry(tubeCache[key], { depth: len, bevelEnabled: false, curveSegments: 3 });
    const mesh = add(geom, mat || MAT.frame);
    alignZ(mesh, a, b, upHint);
    return mesh;
  }
  function rod(a, b, r, mat, seg) {
    const geom = new THREE.CylinderGeometry(r, r, 1, seg || 16);
    const mesh = add(geom, mat);
    const len = alignY(mesh, a, b);
    mesh.scale.set(1, len, 1);
    return mesh;
  }
  function cylAt(c, axis, r, len, mat, seg, parent) {
    const geom = new THREE.CylinderGeometry(r, r, len, seg || 24);
    const mesh = add(geom, mat, parent);
    mesh.position.copy(c);
    mesh.quaternion.setFromUnitVectors(V(0, 1, 0), axis.clone().normalize());
    return mesh;
  }
  function tubeAt(c, axis, rOut, rIn, len, mat, seg, parent) {
    const s = new THREE.Shape();
    s.absarc(0, 0, rOut, 0, Math.PI * 2, false);
    const h = new THREE.Path();
    h.absarc(0, 0, rIn, 0, Math.PI * 2, true);
    s.holes.push(h);
    const geom = new THREE.ExtrudeGeometry(s, { depth: len, bevelEnabled: false, curveSegments: seg || 20 });
    geom.translate(0, 0, -len / 2);
    const mesh = add(geom, mat, parent);
    mesh.position.copy(c);
    mesh.quaternion.setFromUnitVectors(V(0, 0, 1), axis.clone().normalize());
    return mesh;
  }
  function lathe(profile, mat, seg, parent) {
    const pts = profile.map(([r, y]) => new THREE.Vector2(Math.max(r, 0.01), y));
    return add(new THREE.LatheGeometry(pts, seg || 32), mat, parent);
  }
  function rbox(c, size, r, mat, parent) {
    const [w, h, d] = size;
    r = Math.min(r, w / 2 - 0.5, h / 2 - 0.5, d / 2 - 0.5);
    const shape = roundedRectShape(w - 2 * r, h - 2 * r, Math.max(0.5, r * 0.2));
    const geom = new THREE.ExtrudeGeometry(shape, {
      depth: d - 2 * r, bevelEnabled: true, bevelThickness: r, bevelSize: r, bevelSegments: 3, curveSegments: 4,
    });
    geom.translate(0, 0, -(d - 2 * r) / 2);
    const mesh = add(geom, mat, parent);
    mesh.position.copy(c);
    return mesh;
  }
  // Пластина по контуру (2D-точки в плоскости базиса u,v), толщина t по нормали u×v
  function plate(points, origin, u, v, t, mat, holes, parent) {
    const s = new THREE.Shape(points.map(([x, y]) => new THREE.Vector2(x, y)));
    for (const [hx, hy, hr] of holes || []) {
      const h = new THREE.Path();
      h.absarc(hx, hy, hr, 0, Math.PI * 2, true);
      s.holes.push(h);
    }
    const geom = new THREE.ExtrudeGeometry(s, { depth: t, bevelEnabled: false, curveSegments: 12 });
    geom.translate(0, 0, -t / 2);
    const mesh = add(geom, mat, parent);
    const uu = u.clone().normalize();
    const n = new THREE.Vector3().crossVectors(uu, v).normalize();
    const vv = new THREE.Vector3().crossVectors(n, uu);
    mesh.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(uu, vv, n));
    mesh.position.copy(origin);
    return mesh;
  }
  // Ухо-кронштейн: полоса от точки a к оси p с полукругом и отверстием (плоскость ⟂ axis)
  function tab(a, p, width, t, holeR, mat, axis, parent) {
    axis = axis || V(0, 0, 1);
    const d = new THREE.Vector3().subVectors(p, a);
    const L = d.length();
    const w = width / 2;
    const pts = [[0, -w], [L, -w]];
    for (let i = 1; i < 12; i++) {
      const ang = -Math.PI / 2 + (Math.PI * i) / 12;
      pts.push([L + w * Math.cos(ang), w * Math.sin(ang)]);
    }
    pts.push([L, w], [0, w]);
    const v = new THREE.Vector3().crossVectors(axis, d).normalize();
    return plate(pts, a, d, v, t, mat || MAT.frame, [[L, 0, holeR || 6.2]], parent);
  }
  function gusset(p, d1, d2, size, t, offset, mat) {
    const o = p.clone().add(offset || V(0, 0, 0));
    return plate([[0, 0], [size, 0], [0, size]], o, d1, d2, t || 3, mat || MAT.frame);
  }
  function hexHead(c, axis, s, h, mat, parent) {
    const geom = new THREE.CylinderGeometry(s / Math.sqrt(3), s / Math.sqrt(3), h, 6);
    const mesh = add(geom, mat || MAT.zinc, parent);
    mesh.position.copy(c);
    mesh.quaternion.setFromUnitVectors(V(0, 1, 0), axis.clone().normalize());
    return mesh;
  }
  // Болт с головкой и гайкой вдоль axis через точку c, общей длиной len
  function bolt(c, axis, d, len, parent) {
    const ax = axis.clone().normalize();
    cylAt(c, ax, d / 2, len, MAT.zinc, 10, parent);
    const s = d * 1.5 + 1;
    hexHead(c.clone().addScaledVector(ax, -len / 2 - d * 0.32), ax, s, d * 0.65, MAT.zinc, parent);
    hexHead(c.clone().addScaledVector(ax, len / 2 - d * 0.6), ax, s, d * 0.8, MAT.zinc, parent);
  }
  function helix(a, b, coilR, wireR, turns, mat) {
    const len = a.distanceTo(b);
    class Helix extends THREE.Curve {
      getPoint(t, target = new THREE.Vector3()) {
        const ang = t * Math.PI * 2 * turns;
        return target.set(coilR * Math.cos(ang), t * len, coilR * Math.sin(ang));
      }
    }
    const geom = new THREE.TubeGeometry(new Helix(), Math.round(turns * 28), wireR, 8, false);
    const mesh = add(geom, mat);
    mesh.quaternion.setFromUnitVectors(V(0, 1, 0), new THREE.Vector3().subVectors(b, a).normalize());
    mesh.position.copy(a);
    return mesh;
  }
  function cable(points, r, mat) {
    const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal');
    return add(new THREE.TubeGeometry(curve, Math.max(16, points.length * 12), r, 8, false), mat);
  }
  // Гофрированный пыльник между a и b
  function bellows(a, b, r1, r2, folds, mat) {
    const len = a.distanceTo(b);
    const prof = [[0, 0], [r1, 0]];
    for (let i = 0; i <= folds * 2; i++) {
      const t = i / (folds * 2);
      const r = r1 + (r2 - r1) * t + (i % 2 ? 4 : 0);
      prof.push([r, t * len]);
    }
    prof.push([0, len]);
    const mesh = lathe(prof, mat || MAT.boot, 20);
    mesh.quaternion.setFromUnitVectors(V(0, 1, 0), new THREE.Vector3().subVectors(b, a).normalize());
    mesh.position.copy(a);
    return mesh;
  }
  function sprocketShape(teeth, pitchR, boreR) {
    const s = new THREE.Shape();
    const outer = pitchR + 5.5, root = pitchR - 5;
    for (let i = 0; i < teeth; i++) {
      const a0 = (i / teeth) * Math.PI * 2;
      const da = (Math.PI * 2) / teeth;
      const pts = [[root, a0], [outer, a0 + da * 0.3], [outer, a0 + da * 0.5], [root, a0 + da * 0.8]];
      pts.forEach(([r, a], k) => {
        const x = r * Math.cos(a), y = r * Math.sin(a);
        if (i === 0 && k === 0) s.moveTo(x, y); else s.lineTo(x, y);
      });
    }
    s.closePath();
    const h = new THREE.Path();
    h.absarc(0, 0, boreR, 0, Math.PI * 2, true);
    s.holes.push(h);
    for (let i = 0; i < 4; i++) {           // облегчающие отверстия
      const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
      const hp = new THREE.Path();
      hp.absarc(Math.cos(a) * (pitchR * 0.55), Math.sin(a) * (pitchR * 0.55), pitchR * 0.16, 0, Math.PI * 2, true);
      if (pitchR > 35) s.holes.push(hp);
    }
    return s;
  }
  // Деталь в группе-«угле» (локальные координаты)
  function vec(arr) { return V(arr[0], arr[1], arr[2]); }

  // ---------------------------------------------------------------- исходные данные
  const ZF = G.wheelbase / 2, ZR = -G.wheelbase / 2;
  const R = G.wheelR;               // высота оси колеса
  const LR = G.lowerRail, UR = G.upperRail;
  const FY = G.floorY, FZ = G.floorZ, HW = G.frameHalfW;
  const ROOF_Y = G.roofY, ROOF_HW = G.roofHalfW, A_Z = G.aZ, B_Z = G.bZ;
  const frontEnd = ZF + 375, rearEnd = ZR - 300;
  const kp = G.kingpinXAtSteer;
  // Ось первичного вала КПП относительно центра дифференциала (Y, Z) и ввод кабелей мотора
  const INP = { y: G.inputAxis[0], z: G.inputAxis[1] };
  const MOTOR_GLAND = V(144 + 60, R + INP.y + G.chainCD + 108, ZR + INP.z - 40);

  // =================================================================== КОЛЕСО
  function buildWheel(parent) {
    LABEL = 'Колесо 175/70 R13, диск 13x5J ET35 4x98';
    const g = new THREE.Group();
    parent.add(g);
    const W = G.tireW, TR = G.tireR - 7, RIM = 165;
    // шина: профиль (радиус, ось), ось вращения Y -> повернём в X
    const tp = [[RIM + 3, -W / 2 + 14], [RIM + 22, -W / 2 - 2], [RIM + 70, -W / 2 - 6], [TR - 26, -W / 2 - 3],
      [TR - 6, -W / 2 + 10], [TR, -W / 2 + 26], [TR, W / 2 - 26], [TR - 6, W / 2 - 10], [TR - 26, W / 2 + 3],
      [RIM + 70, W / 2 + 6], [RIM + 22, W / 2 + 2], [RIM + 3, W / 2 - 14]];
    const tire = lathe(tp, MAT.tire, 64, g);
    tire.rotation.z = -Math.PI / 2;
    // протектор (зимний, шашки)
    const blockGeom = new THREE.BoxGeometry(30, 9, 24);
    const rows = [-52, -18, 18, 52];
    const N = 60;
    const inst = new THREE.InstancedMesh(blockGeom, MAT.tire, rows.length * N);
    inst.name = LABEL; inst.userData.label = LABEL; inst.castShadow = true;
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = V(1, 1, 1);
    let k = 0;
    rows.forEach((x, ri) => {
      for (let i = 0; i < N; i++) {
        const a = ((i + (ri % 2) * 0.5) / N) * Math.PI * 2;
        // блоки ориентированы по касательной
        const p = V(x, (TR + 2) * Math.cos(a), (TR + 2) * Math.sin(a));
        q.setFromAxisAngle(V(1, 0, 0), -a + Math.PI / 2);
        m4.compose(p, q, sc);
        inst.setMatrixAt(k++, m4);
      }
    });
    g.add(inst);
    // обод: закраины + барабан
    const rp = [[RIM + 12, -63.5], [RIM + 12, -58], [RIM - 2, -55], [RIM - 8, -40], [RIM - 18, -30], [RIM - 18, 25],
      [RIM - 8, 40], [RIM - 2, 55], [RIM + 12, 58], [RIM + 12, 63.5], [RIM - 4, 63.5], [RIM - 22, 45],
      [RIM - 30, 30], [RIM - 30, -45], [RIM - 4, -63.5]];
    const rim = lathe(rp, MAT.rim, 48, g);
    rim.rotation.z = -Math.PI / 2;
    // спицы (литой диск, 6 спиц)
    const spokes = new THREE.Shape();
    spokes.absarc(0, 0, RIM - 22, 0, Math.PI * 2, false);
    for (let i = 0; i < 6; i++) {
      const a0 = (i / 6) * Math.PI * 2 + 0.22, a1 = a0 + Math.PI / 3 - 0.44;
      const hole = new THREE.Path();
      hole.moveTo(62 * Math.cos(a0), 62 * Math.sin(a0));
      hole.absarc(0, 0, RIM - 36, a0 - 0.05, a1 + 0.05, false);
      hole.lineTo(62 * Math.cos(a1), 62 * Math.sin(a1));
      hole.absarc(0, 0, 62, a1, a0, true);
      spokes.holes.push(hole);
    }
    const ch = new THREE.Path(); ch.absarc(0, 0, 29.3, 0, Math.PI * 2, true); spokes.holes.push(ch);
    for (let i = 0; i < 4; i++) {
      const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
      const h = new THREE.Path(); h.absarc(49 * Math.cos(a), 49 * Math.sin(a), 7, 0, Math.PI * 2, true);
      spokes.holes.push(h);
    }
    const sg = new THREE.ExtrudeGeometry(spokes, { depth: 14, bevelEnabled: true, bevelThickness: 3, bevelSize: 3, bevelSegments: 2, curveSegments: 24 });
    const sp = add(sg, MAT.rim, g);
    sp.rotation.y = Math.PI / 2;
    sp.position.x = G.rimEt - 2;
    // колпачок и болты колеса
    LABEL = 'Болты колеса M12x1.25 (65-90 Нм)';
    for (let i = 0; i < 4; i++) {
      const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
      const c = V(G.rimEt + 18, 49 * Math.sin(a), 49 * Math.cos(a));
      hexHead(c, V(1, 0, 0), 17, 10, MAT.chrome, g);
      cylAt(c.clone().add(V(-6, 0, 0)), V(1, 0, 0), 11, 6, MAT.chrome, 16, g);
    }
    LABEL = 'Гайка ступицы M20x1.5 + колпачок';
    cylAt(V(G.rimEt + 16, 0, 0), V(1, 0, 0), 27, 10, MAT.darkSteel, 24, g);
    return g;
  }

  // =================================================================== ТОРМОЗ + СТУПИЦА
  function buildHubBrake(parent, wheelCenter, rearSide) {
    const g = new THREE.Group();
    parent.add(g);
    g.position.copy(wheelCenter);
    const hubX = G.rimEt;       // привалочная плоскость относительно центра колеса
    LABEL = 'Ступица 2108 с подшипником';
    cylAt(V(hubX - 7, 0, 0), V(1, 0, 0), 62, 12, MAT.darkSteel, 32, g);
    cylAt(V(hubX - 40, 0, 0), V(1, 0, 0), 38, 55, MAT.darkSteel, 24, g);
    for (let i = 0; i < 4; i++) {
      const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
      cylAt(V(hubX + 4, 49 * Math.sin(a), 49 * Math.cos(a)), V(1, 0, 0), 5.5, 22, MAT.zinc, 8, g);
    }
    LABEL = 'Тормозной диск 2108 Ø238';
    // диск: шапка + рабочее кольцо (вентилируемое)
    const dp = [[34, hubX - 2], [70, hubX - 2], [70, hubX - 8], [66, hubX - 8], [66, hubX - 30],
      [119, hubX - 30], [119, hubX - 42], [66, hubX - 42], [60, hubX - 34], [60, hubX - 14], [34, hubX - 14]];
    const disc = lathe(dp.map(([r, y]) => [r, y]), MAT.disc, 64, g);
    disc.rotation.z = -Math.PI / 2;
    // вентиляционные каналы
    for (let i = 0; i < 36; i++) {
      const a = (i / 36) * Math.PI * 2;
      const m = add(new THREE.BoxGeometry(4, 50, 3), MAT.darkSteel, g);
      m.position.set(hubX - 36, 93 * Math.cos(a), 93 * Math.sin(a));
      m.rotation.x = -a;
    }
    LABEL = 'Суппорт 2108 (поршень Ø48)';
    const ang = rearSide ? 0.45 : Math.PI - 0.45;   // суппорт сзади-сверху колеса
    const cal = new THREE.Group();
    g.add(cal);
    cal.rotation.x = -(ang - Math.PI / 2);
    // корпус-скоба поверх кольца диска
    rbox(V(hubX - 36, 108, 0), [64, 42, 92], 10, MAT.caliper, cal);
    rbox(V(hubX - 66, 100, 0), [26, 48, 70], 8, MAT.caliper, cal);   // цилиндр
    cylAt(V(hubX - 80, 100, 0), V(1, 0, 0), 26, 8, MAT.caliper, 24, cal);
    LABEL = 'Направляющие суппорта и штуцер';
    for (const z of [-40, 40]) cylAt(V(hubX - 62, 82, z), V(1, 0, 0), 7, 34, MAT.zinc, 10, cal);
    cylAt(V(hubX - 82, 130, 10), V(0, 1, 0), 5, 14, MAT.copper, 8, cal);
    // точка для тормозного шланга (в мировых координатах позже)
    const hosePort = new THREE.Object3D();
    hosePort.position.set(hubX - 82, 140, 10);
    cal.add(hosePort);
    return { group: g, hosePort };
  }

  // =================================================================== КУЛАК + АД-01
  // Строится в локальных координатах правого борта: X наружу, Y вверх, Z от оси (вперед)
  function buildUpright(parent, steerZ) {
    const g = new THREE.Group();
    parent.add(g);
    const lbj = V(G.lbj[0], G.lbj[1], 0);
    LABEL = 'Поворотный кулак ВАЗ-2108';
    // корпус подшипника
    tubeAt(V(G.hubFaceX - 60, R, 0), V(1, 0, 0), 62, 38, 54, MAT.cast, 32, g);
    // нижняя часть с бобышкой шаровой
    const legLow = add(new THREE.CylinderGeometry(22, 30, 1, 16), MAT.cast, g);
    legLow.scale.y = alignY(legLow, V(lbj.x + 8, lbj.y + 12, 0), V(G.hubFaceX - 72, R - 40, 0));
    cylAt(V(lbj.x + 6, lbj.y + 14, 0), V(0, 1, 0), 24, 42, MAT.cast, 20, g);
    LABEL = 'Стяжной болт шаровой M10';
    bolt(V(lbj.x + 6, lbj.y + 20, 0), V(0, 0, 1), 10, 62, g);
    // верх: прилив под стойку
    LABEL = 'Поворотный кулак ВАЗ-2108';
    const [b1, b2] = G.lugBolts;
    const lugC = V((b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2, 0);
    const legUp = add(new THREE.CylinderGeometry(24, 34, 1, 16), MAT.cast, g);
    legUp.scale.y = alignY(legUp, V(G.hubFaceX - 80, R + 30, 0), V(lugC.x + 6, b1[1] - 10, 0));
    const lug = rbox(lugC, [38, 112, G.lugThickness], 6, MAT.cast, g);
    lug.rotation.z = Math.atan2(b1[0] - b2[0], b2[1] - b1[1]);
    // ушки крепления суппорта
    for (const y of [R + 75, R - 75]) rbox(V(G.hubFaceX - 66, y, -60), [26, 30, 40], 6, MAT.cast, g);
    // поворотный рычаг стойки 2108 не используется — рулевой рычаг на АД-01

    LABEL = 'Адаптер АД-01 (щеки 6 мм, 09Г2С)';
    const cheek = G.adapterOutline;
    const half = G.lugThickness / 2 + G.adapterPlate / 2;
    const holes = [...G.lugBolts.map(([x, y]) => [x, y, 6.25]), [G.ubj[0], G.ubj[1], 8.1]];
    for (const z of [half, -half]) plate(cheek, V(0, 0, z), V(1, 0, 0), V(0, 1, 0), G.adapterPlate, MAT.upper, holes, g);
    // перемычка П-профиля
    rbox(V(489, 458, 0), [6, 60, G.lugThickness + 2 * G.adapterPlate], 1, MAT.upper, g);
    // шайбы-бобышки
    for (const z of [half + 5.5, -half - 5.5]) tubeAt(V(G.ubj[0], G.ubj[1], z), V(0, 0, 1), 20, 8.1, 5, MAT.upper, 24, g);
    LABEL = 'Болты M12x1.25 10.9 крепления АД-01 к кулаку';
    for (const [x, y] of G.lugBolts) bolt(V(x, y, 0), V(0, 0, 1), 12, G.lugThickness + 2 * G.adapterPlate + 22, g);
    LABEL = 'Ось ШС верхнего рычага M16x1.5 10.9';
    bolt(V(G.ubj[0], G.ubj[1], 0), V(0, 0, 1), 16, G.lugThickness + 2 * G.adapterPlate + 34, g);
    LABEL = 'Шарнир ШС M16 (камберная регулировка)';
    const ubjBall = add(new THREE.SphereGeometry(13, 18, 12), MAT.chrome, g);
    ubjBall.position.set(G.ubj[0], G.ubj[1], 0);
    tubeAt(V(G.ubj[0], G.ubj[1], 0), V(0, 0, 1), 21, 12, 14, MAT.steel, 24, g);

    // рулевой рычаг: вилка из 2 пластин 8 мм
    LABEL = steerZ < 0 ? 'Рулевой рычаг АД-01 (вилка 2x8 мм)' : 'Рычаг тяги схождения АД-01';
    const sgn = Math.sign(steerZ);
    const tip = [G.steerPoint[0], steerZ];
    const rootZ = sgn * (half + G.adapterPlate / 2);
    const armPts = [[496, rootZ], [540, rootZ], [tip[0] + 15, tip[1] - sgn * 4]];
    for (let i = 0; i <= 10; i++) {
      const a = (Math.PI * i) / 10;
      armPts.push([tip[0] + 15 * Math.cos(a), tip[1] + sgn * 15 * Math.sin(a)]);
    }
    armPts.push([tip[0] - 15, tip[1] - sgn * 4]);
    // плоскость X-Z (u = X, v = Z) -> нормаль = X × Z = -Y; смещение по Y
    for (const y of [G.steerArmY + 15, G.steerArmY - 15]) {
      plate(armPts, V(0, y, 0), V(1, 0, 0), V(0, 0, 1), 8, MAT.upper, [[tip[0], tip[1], 6.1]], g);
    }
    plate([[0, 0], [40, 0], [0, 38]], V(540, G.steerArmY - 19, rootZ), V(0, 0, sgn), V(0, 1, 0), 6, MAT.upper, null, g);
    LABEL = 'ШС M12 рулевой тяги / тяги схождения';
    const tipV = V(tip[0], G.steerArmY, tip[1]);
    bolt(tipV, V(0, 1, 0), 12, 52, g);
    const ball = add(new THREE.SphereGeometry(9, 14, 10), MAT.chrome, g);
    ball.position.copy(tipV);
    tubeAt(tipV, V(0, 1, 0), 15, 8, 12, MAT.steel, 20, g);
    LABEL = 'Нижняя шаровая опора 2108';
    lathe([[0, -22], [20, -22], [26, -10], [24, 6], [16, 18], [10, 26], [0, 26]], MAT.boot, 24, g)
      .position.copy(lbj);
    // точки для внешнего мира
    const marks = {};
    for (const [name, p] of Object.entries({
      ubj: V(G.ubj[0], G.ubj[1], 0), tip: tipV, outerCV: V(G.outerCV[0], G.outerCV[1], 0),
    })) {
      const o = new THREE.Object3D(); o.position.copy(p); g.add(o); marks[name] = o;
    }
    return { group: g, marks };
  }

  // =================================================================== УГОЛ ПОДВЕСКИ
  const hosePorts = [];
  const tieRodTips = {};
  const outerCVs = {};

  function buildCorner(sx, za, front) {
    LAYER = 'suspension';
    const side = sx > 0 ? 'П' : 'Л';
    const axle = front ? 'перед' : 'зад';
    const lz = front ? G.lowerArmZ : G.rearLowerArmZ;
    const uz = front ? G.upperArmZ : G.rearUpperArmZ;
    const shockZ = front ? G.shockZ : G.rearShockZ;
    const steerZ = front ? G.steerZ : G.rearToeZ;
    const caster = front ? G.casterDeg * Math.PI / 180 : 0;

    // группа «стойки»: зеркалирование + кастер вокруг нижней шаровой
    const corner = new THREE.Group();
    corner.name = `Угол подвески ${axle} ${side}`;
    layer('suspension').add(corner);
    corner.position.set(0, 0, za);
    corner.scale.x = sx;
    const tilt = new THREE.Group();     // поворот вокруг оси X через нижнюю шаровую
    corner.add(tilt);
    tilt.position.set(G.lbj[0], G.lbj[1], 0);
    tilt.rotation.x = -caster;
    const up = new THREE.Group();
    tilt.add(up);
    up.position.set(-G.lbj[0], -G.lbj[1], 0);

    const upr = buildUpright(up, steerZ);
    const wc = V(G.halfTrack, R, 0);
    const wheel = buildWheel(up);
    wheel.position.copy(wc);
    const hb = buildHubBrake(up, wc, !front);
    hosePorts.push({ port: hb.hosePort, sx, front });
    root.updateMatrixWorld(true);
    const W = (o) => o.getWorldPosition(new THREE.Vector3());
    const ubjW = W(upr.marks.ubj);
    tieRodTips[`${front ? 'F' : 'R'}${sx}`] = W(upr.marks.tip);
    outerCVs[`${sx}`] = front ? null : W(upr.marks.outerCV);

    const P = (x, y, z) => V(sx * x, y, za + z);
    const lbjW = P(G.lbj[0], G.lbj[1], 0);

    // ---------- нижний рычаг
    LABEL = `Нижний рычаг ${axle} ${side} (труба 30x30x2.5)`;
    const plateC = P(G.lbj[0] - 8, G.lbj[1] - 26, 0);
    for (const z of lz) {
      const pin = P(G.lowerInner[0], G.lowerInner[1], z);
      const start = pin.clone().add(V(sx * 22, 0, 0));
      const end = P(G.lbj[0] - 40, G.lbj[1] - 18, z * 0.12);
      sqTube(start, end, 30, 30, MAT.arm);
      LABEL = `Сайлентблок 2108 в обойме (${axle} ${side})`;
      tubeAt(pin, V(0, 0, 1), 22, 15, 42, MAT.arm, 24);
      tubeAt(pin, V(0, 0, 1), 15, 6.5, 46, MAT.rubber, 20);
      LABEL = `Нижний рычаг ${axle} ${side} (труба 30x30x2.5)`;
    }
    // площадка шаровой
    plate([[-48, -40], [24, -30], [24, 30], [-48, 40]], plateC, V(sx, 0, 0), V(0, 0, 1), 6, MAT.arm,
      [[0, -22, 5.5], [0, 22, 5.5]]);
    LABEL = 'Болты шаровой к рычагу M10x1.25';
    for (const z of [-22, 22]) bolt(P(G.lbj[0] - 8, G.lbj[1] - 26, z), V(0, 1, 0), 10, 36);
    // поперечина под амортизатор
    LABEL = `Нижний рычаг ${axle} ${side} (труба 30x30x2.5)`;
    const t = (G.shockLower[0] - G.lowerInner[0]) / (G.lbj[0] - G.lowerInner[0]);
    const legZ = lz.map((z) => z * (1 - t) + z * 0.12 * t);
    const yS = G.lowerInner[1] + (G.lbj[1] - 18 - G.lowerInner[1]) * t;
    sqTube(P(G.shockLower[0], yS, legZ[0] - 15), P(G.shockLower[0], yS, legZ[1] + 15), 25, 25, MAT.arm);
    if (shockZ < Math.min(...legZ)) {
      sqTube(P(G.shockLower[0], yS, Math.min(...legZ)), P(G.shockLower[0], yS, shockZ - 18), 25, 25, MAT.arm);
    }
    LABEL = 'Уши нижнего крепления амортизатора';
    const sl = P(G.shockLower[0], G.shockLower[1], shockZ);
    for (const dz of [-15, 15]) tab(P(G.shockLower[0] + 25, yS, shockZ + dz), sl, 36, 5, 5.2, MAT.arm);
    bolt(sl, V(0, 0, 1), 10, 48);

    // ---------- верхний рычаг
    LABEL = `Верхний рычаг ${axle} ${side} (труба 25x25x2)`;
    const insertBase = ubjW.clone().add(V(-sx * 52, 4, 0));
    for (const z of uz) {
      const pin = P(G.upperInner[0], G.upperInner[1], z);
      sqTube(pin.clone().add(V(sx * 20, 0, 0)), insertBase, 25, 25, MAT.upper);
      LABEL = `Сайлентблок верхнего рычага (${axle} ${side})`;
      tubeAt(pin, V(0, 0, 1), 20, 13, 38, MAT.upper, 24);
      tubeAt(pin, V(0, 0, 1), 13, 6.5, 42, MAT.rubber, 20);
      LABEL = `Верхний рычаг ${axle} ${side} (труба 25x25x2)`;
    }
    LABEL = 'Бобышка M16x1.5 + контргайка, хвостовик ШС';
    cylAt(insertBase.clone().add(V(sx * 4, -1, 0)), V(1, 0, 0), 15, 26, MAT.upper, 20);
    rod(insertBase, ubjW, 8, MAT.chrome);
    hexHead(insertBase.clone().add(V(sx * 20, -1, 0)), V(1, 0, 0), 24, 8, MAT.zinc);

    // ---------- койловер
    LABEL = `Койловер 350 мм (${axle} ${side})`;
    const su = P(G.shockUpper[0], G.shockUpper[1], shockZ);
    const sh = new THREE.Group();
    layer('suspension').add(sh);
    const len = sl.distanceTo(su);
    sh.position.copy(sl);
    sh.quaternion.setFromUnitVectors(V(0, 1, 0), new THREE.Vector3().subVectors(su, sl).normalize());
    tubeAt(V(0, 0, 0), V(0, 0, 1), 13, 5.2, 22, MAT.damper, 20, sh);
    lathe([[0, 8], [22, 14], [23, 22], [23, len * 0.56], [18, len * 0.58], [0, len * 0.58]], MAT.damper, 28, sh);
    lathe([[0, len * 0.56], [8, len * 0.56], [8, len - 12], [0, len - 12]], MAT.chrome, 16, sh);
    tubeAt(V(0, len, 0), V(0, 0, 1), 13, 5.2, 22, MAT.damper, 20, sh);
    lathe([[0, len - 30], [14, len - 30], [14, len - 14], [0, len - 14]], MAT.damper, 16, sh);
    lathe([[23, len * 0.14], [40, len * 0.14], [40, len * 0.14 + 7], [23, len * 0.14 + 7]], MAT.alu, 32, sh);
    lathe([[9, len - 38], [40, len - 38], [40, len - 31], [9, len - 31]], MAT.alu, 32, sh);
    lathe([[8, len * 0.62], [13, len * 0.62], [13, len * 0.7], [8, len * 0.7]], MAT.rubber, 16, sh);
    const springA = sl.clone().addScaledVector(new THREE.Vector3().subVectors(su, sl).normalize(), len * 0.14 + 7);
    const springB = sl.clone().addScaledVector(new THREE.Vector3().subVectors(su, sl).normalize(), len - 38);
    helix(springA, springB, 31, 5.5, 7.5, MAT.spring);
    bolt(su, V(0, 0, 1), 10, 48);

    // ---------- кронштейны сайлентблоков на подрамнике
    LAYER = 'base';
    LABEL = 'П-скоба сайлентблока (5 мм)';
    const railLow = front ? V(sx * LR[0], LR[1], 0) : V(sx * LR[0], G.rearRailY, 0);
    for (const z of lz) {
      const pin = P(G.lowerInner[0], G.lowerInner[1], z);
      for (const dz of [-24, 24]) tab(V(railLow.x + sx * 20, railLow.y, za + z + dz), pin, 46, 5, 6.2, MAT.frame);
      bolt(pin, V(0, 0, 1), 12, 64);
    }
    const railUp = front ? V(sx * UR[0], UR[1], 0) : V(sx * 300, 620, 0);
    for (const z of uz) {
      const pin = P(G.upperInner[0], G.upperInner[1], z);
      for (const dz of [-22, 22]) tab(V(railUp.x + sx * (front ? 18 : 0), railUp.y - (front ? 0 : 20), za + z + dz), pin, 42, 5, 6.2, MAT.frame);
      bolt(pin, V(0, 0, 1), 12, 60);
    }
    LABEL = 'Уши верхнего крепления амортизатора';
    for (const dz of [-15, 15]) {
      tab(V(su.x - sx * 10, front ? G.shockBarY : 620, za + shockZ + dz), su, 34, 5, 5.2, MAT.frame);
    }
    LAYER = 'suspension';
  }

  // =================================================================== РАМА
  function buildFrame() {
    LAYER = 'base';
    LABEL = 'Рама пола: профиль 50x50x2.5';
    for (const sx of [-1, 1]) sqTube(V(sx * HW, FY, -FZ - 25), V(sx * HW, FY, FZ + 25), 50);
    for (const z of [-FZ, -300, 0, 300, FZ]) sqTube(V(-HW + 25, FY, z), V(HW - 25, FY, z), 50, 50, MAT.frame, 2.5, V(0, 1, 0));
    LABEL = 'Косынки 80x80 мм, лист 3 мм';
    for (const sx of [-1, 1]) for (const z of [-FZ, FZ]) {
      gusset(V(sx * (HW - 25), FY, z - Math.sign(z) * 25), V(-sx, 0, 0), V(0, 0, -Math.sign(z)), 80, 3, V(0, 26.5, 0));
    }
    LABEL = 'Лист пола 2 мм (рифленый)';
    rbox(V(0, FY + 27, 0), [2 * HW - 50, 2, 2 * FZ - 50], 0.5, MAT.sheet);

    // ---------- передний подрамник
    LABEL = 'Передний подрамник: балки 50x50, стойки 40x40';
    for (const sx of [-1, 1]) {
      sqTube(V(sx * LR[0], LR[1], FZ - 25), V(sx * LR[0], LR[1], frontEnd + 25), 50);
      sqTube(V(sx * UR[0], UR[1], ZF - 250), V(sx * UR[0], UR[1], ZF + 220), 40);
      for (const z of [ZF - 230, ZF + 200]) sqTube(V(sx * LR[0], LR[1] + 25, z), V(sx * UR[0], UR[1] - 20, z), 40);
      sqTube(V(sx * UR[0], UR[1], ZF - 250), V(sx * (HW - 20), FY + 20, FZ), 40);
      sqTube(V(sx * LR[0], LR[1] + 25, FZ + 25), V(sx * UR[0], UR[1] - 20, ZF - 230), 40);
      // переход пола к подрамнику
      LABEL = 'Переход пола к переднему подрамнику';
      sqTube(V(sx * LR[0], LR[1], FZ + 25), V(sx * LR[0], FY, FZ + 25), 50);
      LABEL = 'Передний подрамник: балки 50x50, стойки 40x40';
    }
    sqTube(V(-LR[0] - 25, LR[1], frontEnd), V(LR[0] + 25, LR[1], frontEnd), 50);
    sqTube(V(-UR[0] - 20, UR[1], ZF + 200), V(UR[0] + 20, UR[1], ZF + 200), 40);
    LABEL = 'Поперечина амортизаторов 40x40';
    const by = G.shockBarY;
    sqTube(V(-G.shockUpper[0] - 30, by, ZF + G.shockZ), V(G.shockUpper[0] + 30, by, ZF + G.shockZ), 40);
    for (const sx of [-1, 1]) {
      sqTube(V(sx * UR[0], UR[1] + 20, ZF + G.shockZ), V(sx * UR[0], by - 20, ZF + G.shockZ), 40);
    }
    LABEL = 'Поперечина рейки 40x40';
    const rackY = G.tieRodInner[1] - 45;
    sqTube(V(-LR[0] - 20, rackY, ZF + G.steerZ), V(LR[0] + 20, rackY, ZF + G.steerZ), 40);
    for (const sx of [-1, 1]) sqTube(V(sx * LR[0], LR[1] + 25, ZF + G.steerZ), V(sx * LR[0], rackY - 20, ZF + G.steerZ), 40);
    LABEL = 'Ниша для ног (лист 2 мм)';
    rbox(V(0, FY - 10, FZ + 110), [2 * LR[0] + 300, 2, 220], 0.5, MAT.sheet);
    LABEL = 'Защита днища (лист 3 мм)';
    rbox(V(0, LR[1] - 27, ZF), [2 * LR[0] + 50, 3, 700], 0.5, MAT.sheet);

    // ---------- задний подрамник
    LABEL = 'Задний подрамник: балки 50x50 / 40x40';
    const ry = G.rearRailY;
    for (const sx of [-1, 1]) {
      sqTube(V(sx * LR[0], ry, -FZ + 25), V(sx * LR[0], ry, rearEnd - 25), 50);
      sqTube(V(sx * LR[0], ry, -FZ + 25), V(sx * (HW - 25), FY, -FZ + 25), 50);
      sqTube(V(sx * 300, 620, -FZ + 20), V(sx * 300, 620, rearEnd - 20), 40);
      for (const z of [rearEnd, ZR + 160, -FZ - 20]) sqTube(V(sx * LR[0], ry + 25, z), V(sx * 300, 600, z), 40);
      for (const z of G.rearLowerArmZ) sqTube(V(sx * LR[0], ry, ZR + z), V(sx * (G.lowerInner[0] - 30), G.lowerInner[1] - 10, ZR + z), 30);
      for (const z of G.rearUpperArmZ) sqTube(V(sx * 300, 600, ZR + z), V(sx * (G.upperInner[0] + 2), G.upperInner[1] + 22, ZR + z), 30);
      sqTube(V(sx * 300, 600, ZR + G.rearShockZ), V(sx * (G.shockUpper[0] - 8), 620, ZR + G.rearShockZ), 40);
      LABEL = 'Кронштейн тяги схождения';
      sqTube(V(sx * LR[0], ry + 25, ZR + G.rearToeZ), V(sx * (G.tieRodInner[0] - 22), G.tieRodInner[1], ZR + G.rearToeZ), 30);
      LABEL = 'Задний подрамник: балки 50x50 / 40x40';
    }
    sqTube(V(-LR[0] - 25, ry, rearEnd), V(LR[0] + 25, ry, rearEnd), 50);
    sqTube(V(-320, 620, rearEnd), V(320, 620, rearEnd), 40);
    sqTube(V(-320, 620, -FZ - 20), V(320, 620, -FZ - 20), 40);
    for (const sx of [-1, 1]) sqTube(V(sx * 300, 620, ZR + G.rearShockZ), V(sx * (G.shockUpper[0] + 30), 620, ZR + G.rearShockZ), 40);
    LABEL = 'Защита КПП (лист 3 мм)';
    rbox(V(0, ry - 28, ZR - 60), [2 * LR[0] + 50, 3, 520], 0.5, MAT.sheet);
    LABEL = 'Задняя перегородка (лист 1.5 мм)';
    rbox(V(0, 640, B_Z - 30), [2 * HW - 60, 640, 1.5], 0.5, MAT.sheet);
  }

  // =================================================================== КАРКАС
  function buildCage() {
    LAYER = 'cage';
    LABEL = 'Каркас безопасности 40x40x2';
    const aTop = A_Z - 100;
    const roof = [];
    for (const sx of [-1, 1]) {
      sqTube(V(sx * HW, FY + 25, B_Z), V(sx * ROOF_HW, ROOF_Y, B_Z), 40, 40, MAT.cage);
      sqTube(V(sx * HW, FY + 25, A_Z), V(sx * ROOF_HW, ROOF_Y, aTop), 40, 40, MAT.cage);
      sqTube(V(sx * ROOF_HW, ROOF_Y, B_Z - 20), V(sx * ROOF_HW, ROOF_Y, aTop + 20), 40, 40, MAT.cage);
      sqTube(V(sx * ROOF_HW, ROOF_Y, B_Z), V(sx * 300, 640, -FZ - 250), 40, 40, MAT.cage);
      sqTube(V(sx * (HW + 80), FY + 350, B_Z), V(sx * (HW + 80), FY + 350, A_Z), 40, 40, MAT.cage);
      sqTube(V(sx * HW, FY + 25, B_Z), V(sx * (HW + 80), FY + 350, B_Z), 40, 40, MAT.cage);
      sqTube(V(sx * HW, FY + 25, A_Z), V(sx * (HW + 80), FY + 350, A_Z), 40, 40, MAT.cage);
      sqTube(V(sx * HW, FY + 25, B_Z), V(-sx * ROOF_HW, ROOF_Y - 20, B_Z), 30, 30, MAT.cage);
      // передняя дуга (кенгурятник) и капотные трубы
      LABEL = 'Передняя дуга с фарами 40x40';
      sqTube(V(sx * UR[0], UR[1] + 20, ZF + 200), V(sx * UR[0], 720, ZF + 150), 40, 40, MAT.cage);
      const dashX = HW - 70 * 0.44, dashZ = A_Z - 100 * 0.44;
      sqTube(V(sx * UR[0], 720, ZF + 150), V(sx * dashX, 800, dashZ), 40, 40, MAT.cage);
      LABEL = 'Каркас безопасности 40x40x2';
    }
    for (const z of [aTop, B_Z, (aTop + B_Z) / 2]) sqTube(V(-ROOF_HW - 20, ROOF_Y, z), V(ROOF_HW + 20, ROOF_Y, z), 40, 40, MAT.cage);
    LABEL = 'Передняя дуга с фарами 40x40';
    sqTube(V(-UR[0] - 20, 720, ZF + 150), V(UR[0] + 20, 720, ZF + 150), 40, 40, MAT.cage);
    LABEL = 'Поперечина панели приборов 40x40';
    const dashX = HW - 70 * 0.44, dashZ = A_Z - 100 * 0.44;
    sqTube(V(-dashX, 800, dashZ), V(dashX, 800, dashZ), 40, 40, MAT.cage);
    LABEL = 'Косынки каркаса 3 мм';
    for (const sx of [-1, 1]) {
      for (const [z, zt] of [[B_Z, B_Z], [A_Z, aTop]]) {
        const p = V(sx * ROOF_HW, ROOF_Y - 20, zt);
        const dDown = new THREE.Vector3().subVectors(V(sx * HW, FY, z), V(sx * ROOF_HW, ROOF_Y, zt)).normalize();
        const dAlong = V(0, 0, z === B_Z ? 1 : -1);
        gusset(p, dDown, dAlong, 75, 3, V(sx * 22, 0, 0), MAT.cage);
      }
    }
    LAYER = 'interior';
    LABEL = 'Крыша: поликарбонат 6 мм';
    rbox(V(0, ROOF_Y + 23, (aTop + B_Z) / 2), [2 * ROOF_HW + 60, 6, aTop - B_Z + 60], 2, MAT.roof);
  }

  // =================================================================== РУЛЕВОЕ
  function buildSteering() {
    LAYER = 'suspension';
    const rz = ZF + G.steerZ;
    const ti = G.tieRodInner;
    LABEL = 'Рулевая рейка с торцевыми тягами';
    cylAt(V(0, ti[1], rz), V(1, 0, 0), 24, 2 * ti[0] - 150, MAT.alu, 28);
    for (const sx of [-1, 1]) {
      LABEL = 'Пыльник рейки';
      bellows(V(sx * (ti[0] - 75), ti[1], rz), V(sx * (ti[0] - 6), ti[1], rz), 22, 13, 6);
      LABEL = 'Рулевая тяга + наконечник ШС M12';
      const tip = tieRodTips[`F${sx}`];
      const inner = V(sx * ti[0], ti[1], rz);
      rod(inner, tip.clone().add(new THREE.Vector3().subVectors(inner, tip).setLength(26)), 8, MAT.steel);
      hexHead(inner.clone().lerp(tip, 0.75), new THREE.Vector3().subVectors(tip, inner), 19, 10, MAT.zinc);
      LABEL = 'Хомут рейки';
      tubeAt(V(sx * (ti[0] - 110), ti[1], rz), V(1, 0, 0), 30, 24, 30, MAT.darkSteel, 24);
      rbox(V(sx * (ti[0] - 110), ti[1] - 32, rz), [30, 16, 80], 2, MAT.darkSteel);
    }
    LABEL = 'Корпус шестерни рейки';
    const cp = G.columnPoints.map(([x, y, z]) => V(x, y, ZF + z));
    cylAt(V(cp[0].x, ti[1] + 10, rz), V(0, 1, 0), 30, 50, MAT.alu, 24);
    LABEL = 'Рулевой вал и карданы';
    for (let i = 0; i < cp.length - 1; i++) rod(cp[i], cp[i + 1], i === cp.length - 2 ? 12 : 10, MAT.steel);
    for (const j of [cp[1], cp[2]]) {
      const s = add(new THREE.SphereGeometry(16, 16, 12), MAT.darkSteel); s.position.copy(j);
      rbox(j.clone().add(V(0, 0, 0)), [36, 14, 14], 3, MAT.steel).lookAt(cp[0]);
    }
    LABEL = 'Опора рулевого вала (2 подшипника)';
    const mid = cp[2].clone().lerp(cp[3], 0.45);
    cylAt(mid, new THREE.Vector3().subVectors(cp[3], cp[2]), 26, 180, MAT.darkSteel, 20);
    LAYER = 'interior';
    LABEL = 'Руль Ø350';
    const wg = new THREE.Group();
    layer('interior').add(wg);
    alignZ(wg, cp[3], cp[3].clone().add(new THREE.Vector3().subVectors(cp[3], cp[2]).normalize()));
    const rimT = add(new THREE.TorusGeometry(175, 14, 14, 56), MAT.seat, wg);
    for (let i = 0; i < 3; i++) {
      const a = Math.PI / 2 + (i * Math.PI * 2) / 3;
      const s = add(new THREE.BoxGeometry(150, 26, 8), MAT.darkSteel, wg);
      s.position.set(Math.cos(a) * 85, Math.sin(a) * 85, -12);
      s.rotation.z = a;
    }
    add(new THREE.CylinderGeometry(42, 46, 40, 24), MAT.seat, wg).rotation.x = Math.PI / 2;
  }

  // =================================================================== ИНТЕРЬЕР
  function bucketSeat(x) {
    LABEL = 'Сиденье ковш с подголовником';
    const g = new THREE.Group();
    layer('interior').add(g);
    g.position.set(x, FY + 40, -110);
    rbox(V(0, 70, 0), [470, 90, 470], 30, MAT.seat, g);                 // подушка
    for (const sx of [-1, 1]) rbox(V(sx * 205, 110, 20), [70, 90, 430], 28, MAT.seatAccent, g);
    const back = new THREE.Group();
    g.add(back);
    back.position.set(0, 100, -230);
    back.rotation.x = -0.22;
    rbox(V(0, 320, 0), [470, 640, 90], 32, MAT.seat, back);
    for (const sx of [-1, 1]) rbox(V(sx * 210, 300, 40), [70, 520, 90], 28, MAT.seatAccent, back);
    rbox(V(0, 640, 10), [280, 90, 80], 30, MAT.seat, back);
    LABEL = 'Ремни безопасности (3 точки)';
    for (const sx of [-1, 1]) rbox(V(sx * 120, 330, 52), [50, 560, 4], 1, MAT.redPlastic, back);
    LABEL = 'Салазки сиденья';
    for (const sx of [-1, 1]) rbox(V(sx * 160, 12, 0), [30, 22, 440], 3, MAT.darkSteel, g);
  }

  function buildInterior() {
    LAYER = 'interior';
    for (const x of [-290, 290]) bucketSeat(x);
    // панель приборов
    const dashX = HW - 70 * 0.44, dashZ = A_Z - 100 * 0.44;
    LABEL = 'Панель приборов (лист 2 мм)';
    const dp = rbox(V(0, 770, dashZ - 60), [2 * dashX - 60, 160, 8], 3, MAT.sheet);
    dp.rotation.x = -0.6;
    LABEL = 'Дисплей контроллера / BMS';
    const sc = rbox(V(-275, 800, dashZ - 90), [190, 110, 12], 4, MAT.screen);
    sc.rotation.x = -0.6;
    LABEL = 'Тумблеры: фары, подогрев АКБ, лебедка';
    for (let i = 0; i < 5; i++) {
      const b = cylAt(V(-40 + i * 50, 770, dashZ - 70), V(0, Math.cos(0.6), -Math.sin(0.6)), 8, 22, i === 0 ? MAT.redPlastic : MAT.blackPlastic, 12);
    }
    // педали
    LABEL = 'Педальный узел: тормоз + газ';
    const pz = FZ + 200, py = 640;
    sqTube(V(-470, py, pz + 30), V(-100, py, pz + 30), 40, 40, MAT.frame);
    sqTube(V(-100, py, pz + 30), V(-UR[0], UR[1], ZF - 250), 40, 40, MAT.frame);
    for (const [x, len, label] of [[-330, 270, 'Педаль тормоза (i=4.5)'], [-200, 230, 'Электронная педаль газа']]) {
      LABEL = label;
      cylAt(V(x, py - 30, pz + 20), V(1, 0, 0), 10, 50, MAT.zinc, 12);
      const arm = rbox(V(x, py - 30 - len / 2, pz + 5), [16, len, 12], 3, MAT.darkSteel);
      arm.rotation.x = 0.25;
      rbox(V(x, py - 30 - len + 10, pz - 30), [80, 50, 10], 4, MAT.rubber).rotation.x = 0.6;
    }
    LABEL = 'ГТЦ 2108 с бачком';
    cylAt(V(-330, py + 10, pz + 160), V(0, 0, 1), 22, 150, MAT.alu, 20);
    rbox(V(-330, py + 70, pz + 160), [70, 60, 90], 8, MAT.glassClear);
    cylAt(V(-330, py + 108, pz + 160), V(0, 1, 0), 18, 14, MAT.blackPlastic, 16);
    // рычаг КПП и ручник
    LABEL = 'Рычаг переключения передач';
    rod(V(0, FY + 40, 180), V(30, FY + 420, 120), 9, MAT.steel);
    const knob = add(new THREE.SphereGeometry(28, 20, 14), MAT.blackPlastic);
    knob.position.set(30, FY + 440, 120);
    lathe([[0, 0], [55, 0], [40, 60], [10, 90], [0, 90]], MAT.boot, 20).position.set(0, FY + 30, 180);
    LABEL = 'Рычаг стояночного тормоза';
    const hb = rbox(V(80, FY + 120, 60), [24, 30, 260], 6, MAT.darkSteel);
    hb.rotation.x = 0.35;
  }

  // =================================================================== АКБ И ЭЛЕКТРИКА
  function buildBatteries() {
    LAYER = 'batteries';
    const boxes = [];
    for (const [z, n] of [[110, 1], [-330, 2]]) {
      LABEL = `Термобокс АКБ №${n}: 72V 48Ah, ЭППС 20 мм`;
      const c = V(0, FY + 28 + 135, z);
      rbox(c, [300, 260, 380], 10, MAT.battery);
      rbox(c.clone().add(V(0, 133, 0)), [310, 10, 390], 4, MAT.batteryLid);
      for (let i = -3; i <= 3; i++) rbox(c.clone().add(V(i * 38, 141, 0)), [12, 6, 340], 2, MAT.batteryLid);
      LABEL = 'Ручки и замки-лягушки';
      for (const sx of [-1, 1]) {
        rbox(c.clone().add(V(sx * 152, 70, 0)), [8, 24, 160], 4, MAT.darkSteel);
        rbox(c.clone().add(V(sx * 153, 115, 120)), [10, 30, 30], 3, MAT.zinc);
        rbox(c.clone().add(V(sx * 153, 115, -120)), [10, 30, 30], 3, MAT.zinc);
      }
      LABEL = 'Разъем Anderson SB175 + автомат 100A';
      rbox(c.clone().add(V(-70, 40, 195)), [60, 34, 26], 3, MAT.redPlastic);
      rbox(c.clone().add(V(60, 40, 193)), [40, 70, 22], 3, MAT.blackPlastic);
      boxes.push(c);
    }
    LABEL = 'Лоток АКБ / тоннель';
    rbox(V(0, FY + 32, -110), [340, 6, 900], 2, MAT.frame);
    // силовая электрика на перегородке
    LABEL = 'Контроллер VOTOL EM150 (радиатор)';
    const ctrl = V(0, 830, B_Z - 90);
    rbox(ctrl, [280, 200, 70], 8, MAT.alu);
    for (let i = -6; i <= 6; i++) rbox(ctrl.clone().add(V(i * 20, 0, -40)), [4, 190, 20], 1, MAT.alu);
    LABEL = 'Главный контактор 200A + предзаряд';
    cylAt(V(-230, 760, B_Z - 70), V(0, 1, 0), 32, 90, MAT.blackPlastic, 20);
    LABEL = 'DC-DC 72V -> 12V 30A';
    rbox(V(230, 760, B_Z - 75), [150, 110, 50], 6, MAT.alu);
    LABEL = 'Силовые кабели 72V (25 мм²)';
    for (const [dx, m] of [[-20, MAT.orangeCable], [20, MAT.orangeCable]]) {
      cable([boxes[0].clone().add(V(-70 + dx, 40, 210)), V(-70 + dx, FY + 230, 300), V(-120 + dx, FY + 60, 0),
        V(-150 + dx, FY + 60, -500), V(-200 + dx, 600, B_Z - 40), V(-230 + dx, 760, B_Z - 75)], 6, m);
    }
    cable([V(-200, 760, B_Z - 90), V(-120, 800, B_Z - 110), ctrl.clone().add(V(-140, -60, 0))], 6, MAT.orangeCable);
    LABEL = 'Фазные провода мотора U/V/W';
    const motorGland = MOTOR_GLAND;
    for (let i = 0; i < 3; i++) {
      cable([ctrl.clone().add(V(60 + i * 20, -100, 0)), V(80 + i * 15, 640, B_Z - 200),
        V(120 + i * 12, motorGland.y + 120, motorGland.z + 80), motorGland.clone().add(V(i * 10 - 10, 0, 0))], 5,
        [MAT.caliper, MAT.spring, MAT.upper][i]);
    }
  }

  // =================================================================== СИЛОВОЙ МОДУЛЬ
  function buildDrivetrain() {
    LAYER = 'drivetrain';
    const gb = new THREE.Group();
    gb.name = 'Силовой модуль';
    layer('drivetrain').add(gb);
    gb.position.set(0, R, ZR);
    const inp = V(0, G.inputAxis[0], G.inputAxis[1]);   // ось первичного вала в группе
    LABEL = 'КПП ВАЗ-2108 (картер дифференциала)';
    const dl = lathe([[0, -125], [60, -125], [78, -112], [104, -90], [108, -40], [108, 60], [96, 100], [62, 118], [0, 118]], MAT.cast, 40, gb);
    dl.rotation.z = -Math.PI / 2;
    LABEL = 'КПП ВАЗ-2108 (картер КПП)';
    const caseC = V(-115, inp.y * 0.55 + 20, inp.z * 0.6);
    rbox(caseC, [360, inp.y + 120, 200], 40, MAT.cast, gb);
    for (let i = 0; i < 5; i++) rbox(caseC.clone().add(V(-150 + i * 70, 0, 100)), [10, inp.y + 60, 10], 3, MAT.cast, gb);
    LABEL = 'Крышка 5-й передачи';
    const c5 = lathe([[0, 0], [82, 0], [86, 12], [78, 48], [50, 70], [0, 72]], MAT.cast, 32, gb);
    c5.rotation.z = Math.PI / 2;
    c5.position.set(-290, inp.y, inp.z);
    LABEL = 'Картер сцепления (окно закрыто крышкой)';
    const bell = lathe([[60, 0], [150, 0], [178, 70], [182, 82], [60, 82]], MAT.cast, 40, gb);
    bell.rotation.z = -Math.PI / 2;
    bell.position.set(50, inp.y, inp.z);
    LABEL = 'Сальники приводов';
    for (const sx of [-1, 1]) cylAt(V(sx * 122, 0, 0), V(1, 0, 0), 46, 14, MAT.rubber, 24, gb);
    LABEL = 'Механизм выбора передач, тяга';
    cylAt(V(-160, inp.y + 110, inp.z - 40), V(0, 1, 0), 22, 50, MAT.cast, 16, gb);
    rod(V(-160, R + inp.y + 150, ZR + inp.z - 40), V(-60, FY + 60, 150), 6, MAT.steel);
    LABEL = 'Подушки КПП';
    for (const [x, z] of [[-250, inp.z - 80], [60, -110]]) {
      cylAt(V(x, -95, z), V(0, 1, 0), 32, 40, MAT.rubber, 20, gb);
      rbox(V(x, -125, z), [90, 8, 90], 2, MAT.darkSteel, gb);
    }
    LABEL = 'Сливная и контрольная пробки';
    hexHead(V(-40, -108, 0), V(0, 1, 0), 22, 12, MAT.zinc, gb);
    hexHead(V(-200, 30, inp.z * 0.6 - 102), V(0, 0, 1), 22, 12, MAT.zinc, gb);
    LABEL = 'Сапун КПП';
    rod(V(-120, R + inp.y + 200, ZR + inp.z * 0.6), V(-120, R + inp.y + 320, ZR + inp.z * 0.6 + 40), 3, MAT.hose);

    // плита-адаптер на фланец картера сцепления
    LABEL = 'Плита-адаптер 10 мм (мотор + промвал)';
    const pX = 136;
    const cd = G.chainCD;
    const plateShape = [[-130, -150], [130, -150], [130, cd + 120], [-130, cd + 120]];
    plate(plateShape.map(([a, b]) => [a + inp.z, b + inp.y]), V(pX, 0, 0), V(0, 0, 1), V(0, 1, 0), 10, MAT.frame,
      [[inp.z, inp.y, 30], [inp.z, inp.y + cd, 40]], gb);
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      bolt(V(pX, inp.y + 158 * Math.sin(a), inp.z + 158 * Math.cos(a)), V(1, 0, 0), 10, 30, gb);
    }
    LABEL = 'Пазы натяжки цепи (мотор)';
    for (const dz of [-95, 95]) for (const dy of [-60, 60]) {
      rbox(V(pX + 6, inp.y + cd + dy, inp.z + dz), [4, 55, 13], 6, MAT.darkSteel, gb);
    }
    // кассета промвала: вторая пластина на стойках
    LABEL = 'Кассета промвала: 2x UCF205';
    const p2X = 250;
    plate([[-75, -75], [75, -75], [75, 75], [-75, 75]].map(([a, b]) => [a + inp.z, b + inp.y]), V(p2X, 0, 0),
      V(0, 0, 1), V(0, 1, 0), 8, MAT.frame, [[inp.z, inp.y, 20]], gb);
    for (const [dy, dz] of [[-62, -62], [-62, 62], [62, -62], [62, 62]]) {
      cylAt(V((pX + p2X) / 2, inp.y + dy, inp.z + dz), V(1, 0, 0), 9, p2X - pX, MAT.zinc, 12, gb);
    }
    for (const x of [pX + 18, p2X - 18]) {
      rbox(V(x, inp.y, inp.z), [20, 96, 96], 10, MAT.darkSteel, gb);
      cylAt(V(x + (x < 200 ? 14 : -14), inp.y, inp.z), V(1, 0, 0), 32, 18, MAT.darkSteel, 24, gb);
      for (const [dy, dz] of [[-36, -36], [-36, 36], [36, -36], [36, 36]]) hexHead(V(x + (x < 200 ? -12 : 12), inp.y + dy, inp.z + dz), V(1, 0, 0), 16, 8, MAT.zinc, gb);
    }
    LABEL = 'Промвал Ø25 + шлицевая муфта на первичный вал';
    cylAt(V(150, inp.y, inp.z), V(1, 0, 0), 12.5, 230, MAT.chrome, 16, gb);
    cylAt(V(105, inp.y, inp.z), V(1, 0, 0), 24, 46, MAT.steel, 20, gb);
    LABEL = 'Звезда 15T, цепь 520';
    const sprX = p2X + 22;
    const pr = 15.875 / (2 * Math.sin(Math.PI / G.sprocketTeeth));
    const spg = new THREE.ExtrudeGeometry(sprocketShape(G.sprocketTeeth, pr, 12.5), { depth: 8, bevelEnabled: false });
    for (const y of [inp.y, inp.y + cd]) {
      const s = add(spg, MAT.steel, gb);
      s.rotation.y = Math.PI / 2;
      s.position.set(sprX - 4, y, inp.z);
    }
    LABEL = 'Цепь 520 O-ring, 52 звена';
    // путь цепи: две звезды равного размера -> прямые ветви + полуокружности
    const pts = [];
    const nLinks = 52;
    const perim = 2 * cd + 2 * Math.PI * pr;
    for (let i = 0; i < nLinks; i++) {
      let s = (i / nLinks) * perim;
      let y, z, ang;
      if (s < cd) { y = inp.y + s; z = inp.z + pr; ang = 0; }
      else if ((s -= cd) < Math.PI * pr) { const a = s / pr; y = inp.y + cd + pr * Math.sin(a); z = inp.z + pr * Math.cos(a); ang = a; }
      else if ((s -= Math.PI * pr) < cd) { y = inp.y + cd - s; z = inp.z - pr; ang = Math.PI; }
      else { s -= cd; const a = s / pr; y = inp.y - pr * Math.sin(a); z = inp.z - pr * Math.cos(a); ang = Math.PI + a; }
      pts.push([y, z, ang]);
    }
    const linkGeom = new THREE.BoxGeometry(14, 15.875 * 0.95, 9);
    const links = new THREE.InstancedMesh(linkGeom, MAT.darkSteel, nLinks);
    links.name = LABEL; links.userData.label = LABEL;
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion();
    pts.forEach(([y, z, ang], i) => {
      q.setFromAxisAngle(V(1, 0, 0), -ang);
      m4.compose(V(sprX, y, z), q, V(1, 1, 1));
      links.setMatrixAt(i, m4);
    });
    gb.add(links);
    LABEL = 'Защита цепи (лист 1.5 мм)';
    rbox(V(sprX + 16, inp.y + cd / 2, inp.z + pr + 20), [4, cd + 120, 40], 2, MAT.sheet, gb);
    LABEL = 'Диск стояночного тормоза Ø200 + мех. суппорт';
    cylAt(V(sprX + 24, inp.y, inp.z), V(1, 0, 0), 100, 4, MAT.disc, 40, gb);
    rbox(V(sprX + 24, inp.y - 92, inp.z - 30), [40, 44, 64], 8, MAT.caliper, gb);

    // мотор QS138
    LABEL = 'Мотор QS138 70H V3 (редуктор 2.35)';
    const mC = V(pX + 8, inp.y + cd, inp.z);
    const mbody = lathe([[0, 0], [70, 0], [104, 6], [104, 108], [96, 118], [60, 124], [0, 124]], MAT.motor, 48, gb);
    mbody.rotation.z = -Math.PI / 2;
    mbody.position.copy(mC);
    for (let i = 0; i < 9; i++) {
      const fin = tubeAt(mC.clone().add(V(16 + i * 10, 0, 0)), V(1, 0, 0), 112, 103, 4, MAT.motorFin, 40, gb);
    }
    cylAt(mC.clone().add(V(-2, 0, 0)), V(1, 0, 0), 112, 10, MAT.darkSteel, 40, gb);
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      hexHead(mC.clone().add(V(-9, 96 * Math.sin(a), 96 * Math.cos(a))), V(1, 0, 0), 14, 6, MAT.zinc, gb);
    }
    cylAt(mC.clone().add(V(125, 0, 0)), V(1, 0, 0), 15, sprX - mC.x - 120, MAT.chrome, 16, gb);
    LABEL = 'Кабельный ввод мотора';
    cylAt(mC.clone().add(V(60, 108, -40)), V(0, 1, 0), 14, 26, MAT.blackPlastic, 16, gb);

    // приводы
    for (const sx of [-1, 1]) {
      LABEL = `Привод ВАЗ-2108 (укороченный) ${sx > 0 ? 'П' : 'Л'}`;
      const inner = V(sx * G.innerCVX, R, ZR);
      const outer = outerCVs[`${sx}`];
      const dir = new THREE.Vector3().subVectors(outer, inner).normalize();
      const ih = cylAt(inner.clone().addScaledVector(dir, -10), dir, 46, 72, MAT.cast, 28);
      bellows(inner.clone().addScaledVector(dir, 26), inner.clone().addScaledVector(dir, 120), 40, 14, 5);
      rod(inner.clone().addScaledVector(dir, 110), outer.clone().addScaledVector(dir, -110), 12, MAT.darkSteel);
      bellows(outer.clone().addScaledVector(dir, -125), outer.clone().addScaledVector(dir, -30), 14, 40, 5);
      cylAt(outer.clone().addScaledVector(dir, -12), dir, 42, 40, MAT.steel, 28);
    }
  }

  // =================================================================== ОТВАЛ
  function buildPlow() {
    LAYER = 'plow';
    const y = LR[1];
    LABEL = 'Приемный квадрат 50x50 + палец Ø20';
    sqTube(V(0, y, frontEnd + 25), V(0, y, frontEnd + 220), 60, 60, MAT.frame, 4);
    cylAt(V(0, y + 50, frontEnd + 150), V(0, 1, 0), 10, 120, MAT.zinc, 12);
    const tor = add(new THREE.TorusGeometry(18, 3, 8, 20), MAT.zinc);
    tor.position.set(0, y - 15, frontEnd + 150);
    LABEL = 'Дышло отвала 50x50x2.5';
    const pivot = V(0, y, frontEnd + 260);
    const bladeZ = frontEnd + 620;
    for (const sx of [-1, 1]) sqTube(pivot, V(sx * 380, 190, bladeZ - 20), 50, 50, MAT.plow);
    sqTube(V(-380, 190, bladeZ - 20), V(380, 190, bladeZ - 20), 50, 50, MAT.plow);
    LABEL = 'Поворотный сектор ±25°';
    plate(Array.from({ length: 13 }, (_, i) => {
      const a = -0.6 + (1.2 * i) / 12;
      return [Math.sin(a) * 220, Math.cos(a) * 220];
    }).concat([[0, 0]]), pivot.clone().add(V(0, 28, 0)), V(1, 0, 0), V(0, 0, 1), 8, MAT.plow);
    cylAt(pivot.clone().add(V(0, 20, 0)), V(0, 1, 0), 20, 60, MAT.zinc, 16);
    LABEL = 'Лопата отвала 1400x450, лист 2.5 мм';
    const cz = bladeZ + 330, cy = 330, r = 350;
    const arc = (rr) => Array.from({ length: 17 }, (_, i) => {
      const a = (-60 + (80 * i) / 16) * Math.PI / 180;
      return [cz - rr * Math.cos(a), cy + rr * Math.sin(a)];
    });
    const outerA = arc(r), innerA = arc(r - 3);
    // профиль в плоскости (Z, Y) -> выдавливание по X
    const bladeProfile = outerA.concat(innerA.reverse());
    plate(bladeProfile, V(-700, 0, 0), V(0, 0, 1), V(0, 1, 0), 1400, MAT.plow).position.x = 0;
    LABEL = 'Ребра жесткости лопаты 5 мм';
    for (const x of [-560, -280, 0, 280, 560]) {
      const prof = arc(r).concat(arc(r).map(([z, yy]) => [z - 70 + (yy - 30) * 0.05, yy]).reverse());
      plate(prof, V(x, 0, 0), V(0, 0, 1), V(0, 1, 0), 6, MAT.plow);
    }
    for (const sx of [-1, 1]) plate(arc(r).concat([[arc(r)[16][0] - 70, arc(r)[16][1]], [arc(r)[0][0] - 70, arc(r)[0][1]]]),
      V(sx * 700, 0, 0), V(0, 0, 1), V(0, 1, 0), 6, MAT.plow);
    LABEL = 'Нож из транспортерной резины 20 мм';
    const e0 = arc(r)[0];
    rbox(V(0, e0[1] - 30, e0[0] + 6), [1400, 80, 20], 3, MAT.plowEdge);
    for (let i = 0; i < 8; i++) hexHead(V(-630 + i * 180, e0[1] - 20, e0[0] + 20), V(0, 0, 1), 16, 6, MAT.zinc);
    LABEL = 'Шарнир откидывания лопаты';
    cylAt(V(0, 190, bladeZ - 20), V(1, 0, 0), 16, 1300, MAT.zinc, 16);
    LABEL = 'Пружины откидывания L=200';
    for (const sx of [-1, 1]) {
      const a = V(sx * 300, 210, bladeZ - 60), b = V(sx * 300, 440, bladeZ + 20);
      helix(a, b, 22, 4, 12, MAT.spring);
      rod(a, b, 3, MAT.zinc);
    }
    LABEL = 'Лебедка 12V 2000 lbs';
    const wc = V(0, UR[1] + 60, ZF + 200);
    cylAt(wc, V(1, 0, 0), 36, 120, MAT.darkSteel, 24);
    cylAt(wc.clone().add(V(-110, 0, 0)), V(1, 0, 0), 40, 110, MAT.blackPlastic, 24);
    cylAt(wc.clone().add(V(85, 0, 0)), V(1, 0, 0), 42, 50, MAT.darkSteel, 24);
    rbox(wc.clone().add(V(0, -45, 0)), [300, 10, 120], 2, MAT.darkSteel);
    LABEL = 'Трос лебедки';
    cable([wc.clone().add(V(0, -20, 40)), V(0, 560, frontEnd + 60), V(0, 520, bladeZ + 40)], 3, MAT.zinc);
  }

  // =================================================================== СВЕТ
  function headlight(c, dir, r, label, mat, depth) {
    LAYER = 'lights';
    LABEL = label;
    const g = new THREE.Group();
    layer('lights').add(g);
    alignZ(g, c, c.clone().add(dir));
    const body = lathe([[0, -depth], [r * 0.55, -depth], [r, -depth * 0.35], [r + 4, 0], [0, 0]], MAT.blackPlastic, 32, g);
    body.rotation.x = Math.PI / 2;
    const refl = lathe([[0, -depth * 0.8], [r * 0.4, -depth * 0.7], [r - 3, -6], [r - 3, -4], [0, -4]], MAT.reflector, 32, g);
    refl.rotation.x = Math.PI / 2;
    const lens = add(new THREE.CylinderGeometry(r - 2, r - 2, 6, 32), mat, g);
    lens.rotation.x = Math.PI / 2;
    lens.position.z = 1;
    const ring = add(new THREE.TorusGeometry(r + 2, 4, 8, 32), MAT.chrome, g);
    ring.position.z = 2;
    return g;
  }
  function lampRect(c, dir, w, h, mat, label) {
    LAYER = 'lights';
    LABEL = label;
    const g = new THREE.Group();
    layer('lights').add(g);
    alignZ(g, c, c.clone().add(dir));
    rbox(V(0, 0, -18), [w + 10, h + 10, 34], 6, MAT.blackPlastic, g);
    rbox(V(0, 0, 0), [w, h, 6], 3, mat, g);
    return g;
  }
  function buildLights() {
    const fwd = V(0, 0, 1), back = V(0, 0, -1);
    const lz = ZF + 150 + 24;
    for (const sx of [-1, 1]) {
      const c = V(sx * 120, 770, lz);
      headlight(c, fwd, 60, 'Фара LED Ø5" (ближний/дальний)', MAT.lampWhite, 70);
      LABEL = 'Кронштейн фары';
      tab(V(sx * 120, 740, lz - 30), V(sx * 120, 770, lz - 30), 30, 4, 4, MAT.darkSteel, V(1, 0, 0));
      lampRect(V(sx * (UR[0] + 40), 720, ZF + 175), fwd, 60, 30, MAT.lampAmber, 'Поворотник передний');
      lampRect(V(sx * 300, 650, rearEnd - 26), back, 110, 60, MAT.lampRed, 'Задний фонарь: габарит + стоп');
      lampRect(V(sx * 300, 585, rearEnd - 26), back, 60, 28, MAT.lampAmber, 'Поворотник задний');
      const L = new THREE.SpotLight(0xfff4e0, 0, 9000, 0.42, 0.5, 1.2);
      L.position.copy(c.clone().add(V(0, 0, 10)));
      L.target.position.copy(c.clone().add(V(sx * 300, -500, 4000)));
      root.add(L, L.target);
      lights.push([L, 3.2e6]);
    }
    LABEL = 'LED-балка на крыше 800 мм';
    lampRect(V(0, ROOF_Y + 60, A_Z - 100 + 20), fwd, 780, 70, MAT.lampWhite, 'LED-балка на крыше 800 мм');
    LAYER = 'lights';
    LABEL = 'Кронштейны LED-балки';
    for (const sx of [-1, 1]) rbox(V(sx * 340, ROOF_Y + 34, A_Z - 100 + 4), [12, 50, 36], 2, MAT.darkSteel);
    const bar = new THREE.SpotLight(0xffffff, 0, 14000, 0.65, 0.6, 1.2);
    bar.position.set(0, ROOF_Y + 60, A_Z - 70);
    bar.target.position.set(0, 0, A_Z + 6000);
    root.add(bar, bar.target);
    lights.push([bar, 2.5e6]);
    lampRect(V(0, 620, rearEnd - 26), back, 70, 30, MAT.lampWhite, 'Фонарь заднего хода');
    lampRect(V(0, ROOF_Y + 50, B_Z - 30), back, 160, 60, MAT.lampWhite, 'Рабочая фара назад (уборка снега)');
    for (const sx of [-1, 1]) {
      const red = new THREE.PointLight(0xff2020, 0, 1500, 2);
      red.position.set(sx * 300, 650, rearEnd - 120);
      root.add(red);
      lights.push([red, 2.0e5]);
    }
  }
  function buildBrakeLines() {
    LAYER = 'suspension';
    LABEL = 'Тормозные трубки Ø4.75 и шланги';
    root.updateMatrixWorld(true);
    const mc = V(-330, 650, FZ + 360);
    const teeF = V(-60, LR[1] + 40, ZF - 300);
    cable([mc, V(-250, 600, FZ + 380), V(-120, LR[1] + 60, FZ + 300), teeF], 2.4, MAT.copper);
    const teeR = V(-40, G.rearRailY + 40, ZR + 200);
    cable([mc, V(-360, 560, FZ + 300), V(-LR[0] + 10, FY - 30, FZ), V(-LR[0] + 10, FY - 30, -FZ),
      V(-80, G.rearRailY + 40, -FZ - 60), teeR], 2.4, MAT.copper);
    for (const hp of hosePorts) {
      const port = hp.port.getWorldPosition(new THREE.Vector3());
      const tee = hp.front ? teeF : teeR;
      const mid = V(hp.sx * 380, port.y + 60, port.z + (hp.front ? -60 : 60));
      cable([tee, V(hp.sx * 160, tee.y + 20, tee.z), mid], 2.4, MAT.copper);
      cable([mid, mid.clone().lerp(port, 0.5).add(V(0, 50, 0)), port], 5, MAT.hose);
    }
  }

  // =================================================================== СБОРКА
  buildFrame();
  for (const sx of [-1, 1]) { buildCorner(sx, ZF, true); buildCorner(sx, ZR, false); }
  buildCage();
  buildSteering();
  buildInterior();
  buildBatteries();
  buildDrivetrain();
  buildPlow();
  buildLights();
  buildBrakeLines();

  function setLights(on) {
    for (const [m, k] of emissives) m.emissiveIntensity = on ? k : 0.05;
    for (const [L, k] of lights) L.intensity = on ? k : 0;
  }
  setLights(false);
  return { root, layers, lights, setLights, materials: MAT };
}

if (typeof module !== 'undefined') module.exports = { buildBuggy };
