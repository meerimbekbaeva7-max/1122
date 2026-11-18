// Lulu — the Rainbow Tots mascot: a baby rainbow cloud (original character).
// makeLulu(THREE) -> {g, body, mouth, eyes, arms, bow, drops, setMood}
export function makeLulu(THREE) {
  const std = (c, r = .35, e = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0, ...e });
  const fluff = std('#ffffff', .55), shade = std('#e6f3ff', .6);
  const g = new THREE.Group(), body = new THREE.Group(); g.add(body);
  // fluffy cloud body: a big core plus puffs around it
  const core = new THREE.Mesh(new THREE.SphereGeometry(1.0, 64, 48), fluff); core.scale.set(1.25, 1.0, 1.0); core.position.y = 1.25; body.add(core);
  const puffs = [[-1.05, 1.0, .1, .55], [1.05, 1.0, .1, .55], [-.6, 1.95, -.05, .55], [.6, 1.95, -.05, .55], [0, 2.15, -.1, .6],
                 [-1.25, 1.45, -.2, .45], [1.25, 1.45, -.2, .45], [-.55, .45, .2, .5], [.55, .45, .2, .5], [0, .35, .1, .55]];
  puffs.forEach(([x, y, z, r], i) => { const p = new THREE.Mesh(new THREE.SphereGeometry(r, 40, 28), i > 6 ? shade : fluff); p.position.set(x, y, z); body.add(p); });
  // rainbow bow on top of the head
  const bow = new THREE.Group(); bow.position.set(.35, 2.55, .05); bow.rotation.z = -.25;
  ['#ff2a2a', '#ff8a00', '#ffc400', '#2fd65a', '#2f8bff', '#7b5bff'].forEach((c, i) => {
    const r = .62 - i * .085; const arc = new THREE.Mesh(new THREE.TorusGeometry(r, .05, 12, 48, Math.PI), std(c, .3)); bow.add(arc); });
  for (const sx of [-1, 1]) { const end = new THREE.Mesh(new THREE.SphereGeometry(.2, 20, 14), fluff); end.position.set(sx * .45, -.02, 0); bow.add(end); }
  body.add(bow);
  // face
  const eyes = [];
  for (const sx of [-1, 1]) {
    const e = new THREE.Group(); e.position.set(sx * .42, 1.45, .98);
    const w = new THREE.Mesh(new THREE.SphereGeometry(.3, 32, 24), std('#1b1b2f', .15)); w.scale.set(.85, 1.05, .5); e.add(w);
    const h1 = new THREE.Mesh(new THREE.SphereGeometry(.1, 14, 10), std('#ffffff', .1)); h1.position.set(.07, .1, .15); e.add(h1);
    const h2 = new THREE.Mesh(new THREE.SphereGeometry(.05, 10, 8), std('#ffffff', .1)); h2.position.set(-.07, -.08, .15); e.add(h2);
    body.add(e); eyes.push(e);
  }
  for (const sx of [-1, 1]) { const ch = new THREE.Mesh(new THREE.SphereGeometry(.17, 16, 10), std('#ff9ec0', .6)); ch.scale.z = .3; ch.position.set(sx * .78, 1.12, .9); ch.rotation.y = sx * .5; body.add(ch); }
  const mouth = new THREE.Group(); mouth.position.set(0, 1.05, 1.0);
  const m = new THREE.Mesh(new THREE.SphereGeometry(.17, 24, 16), std('#5a0f1f', .4)); m.scale.set(1.3, 1, .45); mouth.add(m);
  const tg = new THREE.Mesh(new THREE.SphereGeometry(.09, 16, 10), std('#ff6b8a', .5)); tg.position.set(0, -.07, .05); tg.scale.set(1.3, .6, .4); mouth.add(tg);
  body.add(mouth);
  // little puff arms
  const arms = [];
  for (const sx of [-1, 1]) { const a = new THREE.Group(); a.position.set(sx * 1.35, 1.05, .35); const h = new THREE.Mesh(new THREE.SphereGeometry(.3, 24, 16), fluff); h.position.set(sx * .15, 0, 0); a.add(h); body.add(a); arms.push(a); }
  // two little puff feet so Lulu can toddle along the path
  const feet = [];
  for (const sx of [-1, 1]) { const fg = new THREE.Group(); fg.position.set(sx * .45, .12, .25); const f = new THREE.Mesh(new THREE.SphereGeometry(.24, 24, 16), shade); f.scale.set(1, .7, 1.2); fg.add(f); body.add(fg); feet.push(fg); }
  // colourful raindrops (shown when happy)
  const drops = new THREE.Group(); body.add(drops);
  ['#ff2a2a', '#ff8a00', '#ffc400', '#2fd65a', '#2f8bff', '#7b5bff', '#ff5fa2'].forEach((c, i) => {
    const d = new THREE.Group(); const s = new THREE.Mesh(new THREE.SphereGeometry(.13, 16, 12), std(c, .2)); d.add(s);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(.115, .22, 16), std(c, .2)); tip.position.y = .14; d.add(tip);
    d.userData = { x: -1 + i * .33, ph: i / 7 }; drops.add(d); });
  const setDrops = t => drops.children.forEach(d => { const q = (t * .9 + d.userData.ph) % 1; d.position.set(d.userData.x, .2 - q * 1.6, .5); d.scale.setScalar(1 - q * .5); });
  setDrops(0);
  const walk = (ph, k = 1) => {
    feet.forEach((f, i) => { const s = Math.sin(ph + i * Math.PI); f.position.z = .25 + s * .28 * k; f.position.y = .12 + Math.max(0, Math.cos(ph + i * Math.PI)) * .2 * k; });
    body.position.y = Math.abs(Math.sin(ph)) * .14 * k; body.rotation.z = Math.sin(ph) * .08 * k;
    arms.forEach((a, i) => a.position.y = 1.05 + Math.sin(ph + i * Math.PI) * .12 * k);
  };
  return { g, body, mouth, eyes, arms, bow, drops, setDrops, feet, walk };
}
