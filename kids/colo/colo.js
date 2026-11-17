// Tiko — the Rainbow Tots chameleon (original character). makeColo(THREE, color) -> {g, body, mouth, eyes, tail, setColor}
export function makeColo(THREE, color = '#2fd65a') {
  const std = (c, r = .3, e = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0, ...e });
  const skin = std(color, .28), skinDark = std(color, .35);
  const g = new THREE.Group(), body = new THREE.Group(); g.add(body);
  // chibi body+head blob
  const blob = new THREE.Mesh(new THREE.SphereGeometry(1.1, 64, 48), skin); blob.scale.set(1.12, 1.0, 1.0); blob.position.y = 1.15; body.add(blob);
  const snout = new THREE.Mesh(new THREE.SphereGeometry(.48, 40, 28), skin); snout.scale.set(1.15, .8, .9); snout.position.set(0, .95, .82); body.add(snout);
  // heart belly
  // cream belly patch with a tiny heart
  const belly = new THREE.Mesh(new THREE.SphereGeometry(.62, 40, 28), std('#fff6e8', .5)); belly.scale.set(1, .85, .35); belly.position.set(0, .55, .9); belly.rotation.x = -.25; body.add(belly);
  const hs = new THREE.Shape(); hs.moveTo(0, -.5); hs.bezierCurveTo(-.8, 0, -.55, .6, 0, .25); hs.bezierCurveTo(.55, .6, .8, 0, 0, -.5);
  const heart = new THREE.Mesh(new THREE.ExtrudeGeometry(hs, { depth: .04, bevelEnabled: true, bevelThickness: .03, bevelSize: .03, bevelSegments: 2 }), std('#ff5fa2', .4));
  heart.scale.setScalar(.22); heart.position.set(0, .5, 1.12); heart.rotation.x = -.25; body.add(heart);
  // crest: three soft bumps
  for (let i = 0; i < 3; i++) { const c = new THREE.Mesh(new THREE.SphereGeometry(.2 - i * .03, 20, 14), skinDark); c.scale.set(.7, 1.2, .9); c.position.set(0, 2.2 - i * .12, -.15 - i * .32); body.add(c); }
  // turret eyes
  const eyes = [];
  for (const sx of [-1, 1]) {
    const tur = new THREE.Mesh(new THREE.SphereGeometry(.42, 32, 24), skin); tur.position.set(sx * .58, 1.62, .55); body.add(tur);
    const e = new THREE.Group(); e.position.set(sx * .6, 1.66, .86);
    const w = new THREE.Mesh(new THREE.SphereGeometry(.33, 32, 24), std('#ffffff', .15)); w.scale.z = .7; e.add(w);
    const p = new THREE.Mesh(new THREE.SphereGeometry(.19, 24, 16), std('#1b1b2f', .15)); p.position.set(-sx * .03, -.02, .17); p.scale.z = .6; e.add(p);
    const h1 = new THREE.Mesh(new THREE.SphereGeometry(.07, 12, 8), std('#ffffff', .1)); h1.position.set(.06, .08, .3); e.add(h1);
    const h2 = new THREE.Mesh(new THREE.SphereGeometry(.035, 10, 8), std('#ffffff', .1)); h2.position.set(-.06, -.07, .3); e.add(h2);
    body.add(e); eyes.push(e);
  }
  // cheeks
  for (const sx of [-1, 1]) { const ch = new THREE.Mesh(new THREE.SphereGeometry(.15, 16, 10), std('#ff8fb1', .6)); ch.scale.z = .35; ch.position.set(sx * .62, 1.0, .98); ch.rotation.y = sx * .5; body.add(ch); }
  // mouth (opens for singing)
  const mouth = new THREE.Group(); mouth.position.set(0, .82, 1.2);
  const m = new THREE.Mesh(new THREE.SphereGeometry(.2, 24, 16), std('#5a0f1f', .4)); m.scale.set(1.5, 1, .45); mouth.add(m);
  const tg = new THREE.Mesh(new THREE.SphereGeometry(.11, 16, 10), std('#ff6b8a', .5)); tg.position.set(0, -.08, .05); tg.scale.set(1.3, .6, .4); mouth.add(tg);
  body.add(mouth);
  // little feet
  for (const [x, z] of [[-.55, .55], [.55, .55], [-.6, -.35], [.6, -.35]]) { const f = new THREE.Mesh(new THREE.SphereGeometry(.24, 20, 14), skinDark); f.scale.set(1.2, .6, 1.3); f.position.set(x, .12, z); body.add(f); }
  // rainbow spiral tail (the signature: never changes colour)
  // spiral on the right-back side so it reads from the front
  const pts = []; const cx = 1.32, cy = 1.0, a0 = -2.3;
  for (let i = 0; i <= 140; i++) { const t = i / 140, a = a0 - t * Math.PI * 2.5, r = .7 * (1 - t * .78);
    pts.push(new THREE.Vector3(cx + Math.cos(a) * r, cy + Math.sin(a) * r, -.55 - t * .25)); }
  pts.unshift(new THREE.Vector3(.55, .6, -.7));
  const curve = new THREE.CatmullRomCurve3(pts);
  const tg2 = new THREE.TubeGeometry(curve, 260, .2, 20, false);
  const cols = ['#ff2a2a', '#ff8a00', '#ffc400', '#2fd65a', '#2f8bff', '#7b5bff'].map(h => { const c = new THREE.Color(h); return [c.r, c.g, c.b]; }); const ca = [];
  const pos = tg2.attributes.position, uvs = tg2.attributes.uv;
  for (let i = 0; i < pos.count; i++) { const u = uvs.getX(i); const k = Math.floor(u * 14) % 6; ca.push(...cols[k]); }
  tg2.setAttribute('color', new THREE.Float32BufferAttribute(ca, 3));
  // taper the tail
  for (let i = 0; i < pos.count; i++) { const u = uvs.getX(i); const c = curve.getPoint(u); const v = new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i)).sub(c).multiplyScalar(1 - u * .55).add(c); pos.setXYZ(i, v.x, v.y, v.z); }
  const tail = new THREE.Mesh(tg2, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .3 })); body.add(tail);
  const setColor = c => { skin.color.set(c); skinDark.color.set(new THREE.Color(c).multiplyScalar(.82)); };
  setColor(color);
  return { g, body, mouth, eyes, tail, setColor };
}
