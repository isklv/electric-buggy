// Экспорт детальной сцены web/buggy_scene.js в Wavefront OBJ + MTL.
// Запуск: node tools/export_model.mjs web/geometry.json buggy_frame_chassis.obj
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';

const here = path.dirname(fileURLToPath(import.meta.url));
const [geoPath, objPath] = process.argv.slice(2);
if (!geoPath || !objPath) {
  console.error('usage: node export_model.mjs <geometry.json> <out.obj>');
  process.exit(1);
}
const G = JSON.parse(fs.readFileSync(geoPath, 'utf8'));
const src = fs.readFileSync(path.join(here, '..', 'web', 'buggy_scene.js'), 'utf8');
const buildBuggy = new Function('module', `${src}\nreturn buildBuggy;`)(undefined);
const { root } = buildBuggy(THREE, G);
root.updateMatrixWorld(true);

const mtlName = path.basename(objPath).replace(/\.obj$/i, '.mtl');
const out = [
  '# Электробагги 2-местный: детальная модель (web/buggy_scene.js + chassis_geometry.py)',
  '# Единицы: мм. X — вправо, Y — вверх, Z — вперед',
  `mtllib ${mtlName}`,
];
const mats = new Map();
let vOff = 1, nOff = 1, objects = 0;
const v = new THREE.Vector3(), n = new THREE.Vector3();
const nm = new THREE.Matrix3();

function emit(geom, matrix, material, name) {
  const pos = geom.attributes.position, nor = geom.attributes.normal;
  const flip = matrix.determinant() < 0;
  nm.getNormalMatrix(matrix);
  out.push(`o ${(name || 'part').replace(/\s+/g, '_')}_${objects++}`);
  out.push(`usemtl ${material.name || 'default'}`);
  mats.set(material.name || 'default', material);
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i).applyMatrix4(matrix);
    out.push(`v ${v.x.toFixed(1)} ${v.y.toFixed(1)} ${v.z.toFixed(1)}`);
    if (nor) {
      n.fromBufferAttribute(nor, i).applyMatrix3(nm).normalize();
      out.push(`vn ${n.x.toFixed(3)} ${n.y.toFixed(3)} ${n.z.toFixed(3)}`);
    }
  }
  const index = geom.index ? geom.index.array : null;
  const count = index ? index.length : pos.count;
  for (let i = 0; i < count; i += 3) {
    let tri = index ? [index[i], index[i + 1], index[i + 2]] : [i, i + 1, i + 2];
    if (flip) tri = [tri[0], tri[2], tri[1]];
    out.push('f ' + tri.map((k) => nor ? `${vOff + k}//${nOff + k}` : `${vOff + k}`).join(' '));
  }
  vOff += pos.count;
  if (nor) nOff += pos.count;
}

const tmp = new THREE.Matrix4();
root.traverse((o) => {
  if (!o.isMesh || !o.visible) return;
  if (o.isInstancedMesh) {
    for (let i = 0; i < o.count; i++) {
      o.getMatrixAt(i, tmp);
      emit(o.geometry, new THREE.Matrix4().multiplyMatrices(o.matrixWorld, tmp), o.material, o.name);
    }
  } else emit(o.geometry, o.matrixWorld, o.material, o.name);
});
fs.writeFileSync(objPath, out.join('\n') + '\n');

const mtl = [];
for (const [name, m] of mats) {
  const c = m.color;
  mtl.push(`newmtl ${name}`, `Kd ${c.r.toFixed(4)} ${c.g.toFixed(4)} ${c.b.toFixed(4)}`,
    `Ks ${(m.metalness * 0.8).toFixed(3)} ${(m.metalness * 0.8).toFixed(3)} ${(m.metalness * 0.8).toFixed(3)}`,
    `Ns ${Math.round((1 - m.roughness) * 200)}`, `d ${m.transparent ? m.opacity : 1}`);
  if (m.emissive && m.emissive.getHex()) mtl.push(`Ke ${m.emissive.r.toFixed(3)} ${m.emissive.g.toFixed(3)} ${m.emissive.b.toFixed(3)}`);
  mtl.push('');
}
fs.writeFileSync(path.join(path.dirname(objPath), mtlName), mtl.join('\n'));
console.log(`OBJ сохранен в: ${objPath} (${objects} деталей, ${vOff - 1} вершин) + ${mtlName}`);
