// Tiko — the Rainbow Tots baby dino (original character). makeTiko(THREE) -> {g, body, mouth, eyes, arms, tail}
export function makeTiko(THREE, color = '#2fc7c0') {
  const std = (c, r = .32, e = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0, ...e });
  const skin = std(color, .3), skinD = std(new THREE.Color(color).multiplyScalar(.8), .35), cream = std('#fff1d6', .5);
  const g = new THREE.Group(), body = new THREE.Group(); g.add(body);
  // pear-shaped body + big chibi head
  const torso = new THREE.Mesh(new THREE.SphereGeometry(.95, 56, 40), skin); torso.scale.set(1.0, 1.05, .95); torso.position.y = .95; body.add(torso);
  const head = new THREE.Mesh(new THREE.SphereGeometry(.95, 56, 40), skin); head.scale.set(1.12, .98, 1.0); head.position.set(0, 2.15, .12); body.add(head);
  const muzzle = new THREE.Mesh(new THREE.SphereGeometry(.6, 40, 28), skin); muzzle.scale.set(1.15, .78, .85); muzzle.position.set(0, 1.92, .72); body.add(muzzle);
  for (const sx of [-1, 1]) { const n = new THREE.Mesh(new THREE.SphereGeometry(.05, 10, 8), skinD); n.position.set(sx * .17, 2.07, 1.22); body.add(n); }
  const belly = new THREE.Mesh(new THREE.SphereGeometry(.72, 40, 28), cream); belly.scale.set(1, 1.05, .45); belly.position.set(0, .9, .62); body.add(belly);
  // belly stripes
  for (let i = 0; i < 3; i++) { const st = new THREE.Mesh(new THREE.TorusGeometry(.42 - i * .03, .025, 8, 40, Math.PI * .8), std('#f2d9ad', .5)); st.rotation.z = Math.PI * 1.1; st.position.set(0, .62 + i * .28, .93); st.scale.set(1, .35, 1); body.add(st); }
  // rainbow back spikes, from head to tail
  const spikeCols = ['#ff2a2a', '#ff8a00', '#ffc400', '#2fd65a', '#2f8bff', '#7b5bff'];
  // place each spike on the surface (head then torso), pointing along the surface normal
  const spikes = [];
  const spots = [[0, 2.15, .12, 1.0, 12], [0, 2.15, .12, 1.0, 48], [0, 2.15, .12, 1.0, 85], [0, .95, 0, 1.0, 58], [0, .95, 0, 1.0, 82], [0, .95, 0, .98, 106]];
  spots.forEach(([cx, cy, cz, r, deg], i) => { const a = deg * Math.PI / 180; const n = new THREE.Vector3(0, Math.cos(a), -Math.sin(a));
    const h = .8 - i * .05; const s = new THREE.Mesh(new THREE.ConeGeometry(.33 - i * .018, h, 24), std(spikeCols[i], .28));
    s.position.set(cx, cy, cz).addScaledVector(n, r * .9 + h * .35); s.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), n); s.scale.set(.7, 1, 1.15); body.add(s); spikes.push(s); });
  // eyes
  const eyes = [];
  for (const sx of [-1, 1]) {
    const e = new THREE.Group(); e.position.set(sx * .4, 2.38, .9);
    const w = new THREE.Mesh(new THREE.SphereGeometry(.28, 32, 24), std('#ffffff', .15)); w.scale.z = .6; e.add(w);
    const p = new THREE.Mesh(new THREE.SphereGeometry(.18, 24, 16), std('#1b1b2f', .15)); p.position.set(0, -.02, .12); p.scale.z = .55; e.add(p);
    const h1 = new THREE.Mesh(new THREE.SphereGeometry(.065, 12, 8), std('#ffffff', .1)); h1.position.set(.06, .07, .22); e.add(h1);
    const h2 = new THREE.Mesh(new THREE.SphereGeometry(.03, 10, 8), std('#ffffff', .1)); h2.position.set(-.06, -.07, .22); e.add(h2);
    body.add(e); eyes.push(e);
  }
  for (const sx of [-1, 1]) { const ch = new THREE.Mesh(new THREE.SphereGeometry(.15, 16, 10), std('#ff8fb1', .6)); ch.scale.z = .3; ch.position.set(sx * .72, 2.0, .92); ch.rotation.y = sx * .55; body.add(ch); }
  const mouth = new THREE.Group(); mouth.position.set(0, 1.78, 1.18);
  const m = new THREE.Mesh(new THREE.SphereGeometry(.18, 24, 16), std('#5a0f1f', .4)); m.scale.set(1.7, 1, .45); mouth.add(m);
  const tg = new THREE.Mesh(new THREE.SphereGeometry(.1, 16, 10), std('#ff6b8a', .5)); tg.position.set(0, -.08, .05); tg.scale.set(1.4, .6, .4); mouth.add(tg);
  for (const sx of [-1, 1]) { const tooth = new THREE.Mesh(new THREE.ConeGeometry(.045, .09, 8), std('#ffffff', .2)); tooth.rotation.x = Math.PI; tooth.position.set(sx * .12, .12, .07); mouth.add(tooth); }
  body.add(mouth);
  // tiny arms, feet, tail
  const arms = [];
  for (const sx of [-1, 1]) { const a = new THREE.Group(); a.position.set(sx * .85, 1.25, .35); const arm = new THREE.Mesh(new THREE.CapsuleGeometry(.13, .28, 8, 16), skin); arm.rotation.z = sx * 1.0; arm.position.set(sx * .12, -.05, 0); a.add(arm); body.add(a); arms.push(a); }
  for (const sx of [-1, 1]) { const f = new THREE.Mesh(new THREE.SphereGeometry(.3, 24, 16), skinD); f.scale.set(1, .55, 1.35); f.position.set(sx * .45, .14, .2); body.add(f);
    for (const t of [-1, 0, 1]) { const c = new THREE.Mesh(new THREE.SphereGeometry(.06, 10, 8), cream); c.position.set(sx * .45 + t * .12, .12, .6); body.add(c); } }
  const tailPts = [new THREE.Vector3(0, .42, -.62), new THREE.Vector3(.3, .25, -1.15), new THREE.Vector3(.8, .22, -1.45), new THREE.Vector3(1.25, .35, -1.55)];
  const tc = new THREE.CatmullRomCurve3(tailPts); const tgeo = new THREE.TubeGeometry(tc, 60, .32, 20, false);
  const pos = tgeo.attributes.position, uv = tgeo.attributes.uv;
  for (let i = 0; i < pos.count; i++) { const u = uv.getX(i); const c = tc.getPoint(u); const v = new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i)).sub(c).multiplyScalar(1 - u * .8).add(c); pos.setXYZ(i, v.x, v.y, v.z); }
  tgeo.computeVertexNormals();
  const tail = new THREE.Mesh(tgeo, skin); body.add(tail);
  const tip = new THREE.Mesh(new THREE.SphereGeometry(.07, 12, 8), skin); tip.position.copy(tailPts[3]); body.add(tip);
  return { g, body, mouth, eyes, arms, tail, spikes };
}
