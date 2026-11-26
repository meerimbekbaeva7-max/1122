// ---------- mountains behind the house (kitchen view) ----------
{const W=900,D=260,g=new THREE.PlaneGeometry(W,D,240,70);g.rotateX(-Math.PI/2);const pos=g.attributes.position;const col=[];
 const ridge=(x,z)=>{let h=0,a=1,f=.006;for(let o=0;o<5;o++){h+=a*(1-Math.abs(Math.sin(x*f+o*1.7)*Math.cos(z*f*1.3+o)));a*=.5;f*=2.1;}return h;};
 for(let i=0;i<pos.count;i++){const x=pos.getX(i),z=pos.getZ(i);const t=(z+D/2)/D;
  const env=Math.sin(Math.PI*Math.min(1,(1-t)*1.25))*(.7+.3*Math.sin(x*.004+1.2));let y=Math.max(0,ridge(x,z)*150*env-10);pos.setY(i,y);
  const c=new THREE.Color(y>118?'#f2f5f9':y>70?'#6e757c':y>30?'#3f5a3a':'#4d6a37');if(y>104&&y<=118)c.lerp(new THREE.Color('#f2f5f9'),(y-104)/14);if(y>60&&y<=70)c.lerp(new THREE.Color('#3f5a3a'),(70-y)/10);c.lerp(new THREE.Color('#a9b9c9'),.1+.22*(1-t));col.push(c.r,c.g,c.b);}
 g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.computeVertexNormals();
 const mt=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.95,flatShading:true,fog:false}));mt.position.set(0,-2,-230);scene.add(mt);}
scene.fog=new THREE.Fog('#dfe7ee',90,520);

// ---------- site ----------
const site=new THREE.Group();scene.add(site);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(400,400),M.grass);ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;site.add(ground);
const flat=(w,d,x,z,mat,y=.02)=>{const m=box(site,w,.04,d,x,y,z,mat,false);m.receiveShadow=true;return m;};
flat(1.6,8,-1.5,10.2,M.pave,.03);flat(4,9,8,9.5,M.pave);flat(60,1.8,0,15.2,M.pave,.03);
const G=c=>new THREE.MeshStandardMaterial({color:c,roughness:.9});
const leafGeo=new THREE.IcosahedronGeometry(1,0),leafMat=new THREE.MeshStandardMaterial({roughness:.85});
const LEAVES=[];const C=new THREE.Color(),Mx=new THREE.Matrix4(),Q=new THREE.Quaternion(),Sv=new THREE.Vector3(),Pv=new THREE.Vector3(),Ev=new THREE.Euler();
const GREENS=['#3d5f2c','#4a6e33','#567a3a','#2f4f24','#62843f','#45682f'];
function blob(cx,cy,cz,rx,ry,rz,n,ls,seed,pal=GREENS,jit=.08){for(let i=0;i<n;i++){const u=rnd(seed+i*3),v=rnd(seed+i*3+1),w=Math.cbrt(.35+.65*rnd(seed+i*3+2));const th=u*Math.PI*2,ph=Math.acos(2*v-1);
 const x=Math.sin(ph)*Math.cos(th),y=Math.cos(ph),z=Math.sin(ph)*Math.sin(th);C.set(pal[(i+seed)%pal.length]).multiplyScalar((.75+.35*(y*.5+.5))*(1-jit+rnd(seed+i)*jit*2));
 LEAVES.push([cx+x*rx*w,cy+y*ry*w,cz+z*rz*w,ls*(.7+rnd(seed+i*7)*.6),C.clone()]);}}
function tree(x,z,s){const tm=G('#5a4634');const tr=new THREE.Mesh(new THREE.CylinderGeometry(.12*s,.22*s,4.2*s,8),tm);tr.position.set(x,2.1*s,z);tr.castShadow=true;site.add(tr);
 for(let k=0;k<5;k++){const a=k*1.25+z,rr=k?1.3:0;blob(x+Math.cos(a)*rr*s,(4.6+(k?-.3+rnd(k+x)*.9:.9))*s,z+Math.sin(a)*rr*s,1.5*s,1.15*s,1.5*s,70,.32*s,(x*13+z*7+k*101)|0);}}
[[-13,-4,1.2],[-15,7,1],[16,11,.9],[-11,13,.8]].forEach(a=>tree(...a));
function fir(x,z,s){const tm=G('#4a3626');const tr=new THREE.Mesh(new THREE.CylinderGeometry(.08*s,.14*s,1.2*s,6),tm);tr.position.set(x,.6*s,z);site.add(tr);
 for(let k=0;k<4;k++){const c=new THREE.Mesh(new THREE.ConeGeometry((1.3-k*.25)*s,1.7*s,9),G(['#2c4f2c','#335a31','#2a4a29','#3a6236'][k]));c.position.set(x,(1.4+k*.85)*s,z);c.castShadow=true;site.add(c);}}
[[-20,-14,1.3],[-26,-6,1.5],[22,-15,1.6],[30,-10,1.2],[-30,-12,1.4],[-28,-24,1.7],[28,-24,1.5]].forEach(a=>fir(...a));
let si=0;function shrub(x,z,s,bloom){blob(x,s*.55,z,s*.75,s*.55,s*.75,Math.round(40*s+18),.13+s*.06,(si++)*37+5,['#3f6a30','#4d7a38','#35592a','#5b8742']);
 if(bloom)for(let k=0;k<5;k++){const a=k*1.3+si;blob(x+Math.cos(a)*s*.45,s*.95,z+Math.sin(a)*s*.45,.16,.12,.16,22,.045,si*53+k*7,['#f4f2ec','#e8e6dc','#ffffff'],.04);}}
for(let k=0;k<12;k++)shrub(-7+rnd(k*3)*4.5,7.2+rnd(k*5)*6,.35+rnd(k)*.4,k%4===0);for(let k=0;k<10;k++)shrub(1+rnd(k*7)*4.5,7.6+rnd(k*9)*5.5,.35+rnd(k+2)*.4,k%3===0);
const blades=new THREE.InstancedMesh(new THREE.ConeGeometry(.012,.7,3).translate(0,.35,0),new THREE.MeshStandardMaterial({color:'#9a9f6a',roughness:.9}),24*22);let bi=0;
for(let t=0;t<24;t++){const tx=-7+rnd(t*3)*12,tz=6.8+rnd(t*5)*6.5;for(let k=0;k<22;k++){Ev.set((rnd(t*31+k)-.5)*.9,rnd(t*17+k)*6,(rnd(t*13+k)-.5)*.9);Q.setFromEuler(Ev);
 Mx.compose(Pv.set(tx,0,tz),Q,Sv.set(1,.6+rnd(t+k)*.6,1));blades.setMatrixAt(bi,Mx);blades.setColorAt(bi,C.set(['#a7aa72','#8f9660','#b9b27c','#7d8a55'][k%4]));bi++;}}
blades.castShadow=true;site.add(blades);
{const im=new THREE.InstancedMesh(leafGeo,leafMat,LEAVES.length);LEAVES.forEach(([x,y,z,sz,col],i)=>{Ev.set(rnd(i)*3,rnd(i+1)*3,rnd(i+2)*3);Q.setFromEuler(Ev);
 Mx.compose(Pv.set(x,y,z),Q,Sv.set(sz,sz*.55,sz));im.setMatrixAt(i,Mx);im.setColorAt(i,col);});im.castShadow=true;im.receiveShadow=true;site.add(im);}
for(const z of[8,10,12]){box(site,.1,.6,.1,-2.5,.3,z,M.graph);box(site,.11,.08,.11,-2.5,.62,z,M.led,false);}

// ---------- house: 10 x 7.5 m, one storey, kitchen at the back facing the mountains ----------
const FL=.5,H=2.8,XO=5,ZO=3.75,T=.3;
const bld=new THREE.Group(),INT=new THREE.Group(),WIN=new THREE.Group(),ROOF=new THREE.Group();scene.add(bld);bld.add(INT,WIN,ROOF);
// light foundation without concrete: screw piles + steel grillage + timber floor
const pileM=new THREE.MeshStandardMaterial({color:'#9aa1a8',roughness:.35,metalness:.85}),capM2=new THREE.MeshStandardMaterial({color:'#5d636a',roughness:.4,metalness:.7});
function pile(x,z,top){const p=new THREE.Mesh(new THREE.CylinderGeometry(.054,.054,top+.4,10),pileM);p.position.set(x,(top-.4)/2,z);p.castShadow=true;bld.add(p);box(bld,.22,.02,.22,x,top,z,capM2);}
const PX=[-4.85,-2.42,0,2.42,4.85],PZ=[-3.6,-1.2,1.2,3.6];PX.forEach(x=>PZ.forEach(z=>pile(x,z,.3)));
for(const z of PZ)box(bld,2*XO,.16,.1,0,.39,z,capM2);for(const x of PX)box(bld,.1,.16,2*ZO,x,.39,0,capM2);
box(bld,2*XO-.1,.03,2*ZO-.1,0,FL-.02,0,M.wood,false);
// slatted skirt (piles stay visible between the slats)
const skirtTex=ctex(256,64,(g,w,h)=>{g.clearRect(0,0,w,h);for(let x=0;x<w;x+=32){g.fillStyle=['#5b4330','#523b2a','#634a35'][(x/32)%3];g.fillRect(x,0,20,h);}});skirtTex.repeat.set(1/.4*.25,1);
const skirtM=new THREE.MeshStandardMaterial({map:skirtTex,transparent:true,alphaTest:.5,side:THREE.DoubleSide,roughness:.8});
for(const s of[-1,1]){const a=new THREE.Mesh(new THREE.PlaneGeometry(2*XO,.42),skirtM.clone());a.material.map=skirtTex.clone();a.material.map.repeat.set(2*XO/.4,1);a.material.map.needsUpdate=true;a.position.set(0,.25,s*(ZO+.02));bld.add(a);
 const b=new THREE.Mesh(new THREE.PlaneGeometry(2*ZO,.42),skirtM.clone());b.material.map=skirtTex.clone();b.material.map.repeat.set(2*ZO/.4,1);b.material.map.needsUpdate=true;b.rotation.y=Math.PI/2;b.position.set(s*(XO+.02),.25,0);bld.add(b);}
const V=(a,b)=>[FL+a,FL+b];
const HOLES={
 back:[[-3.6,-1.6,...V(.85,2.4),'w'],[-.2,4.45,...V(.05,2.55),'p']],
 right:[[-3.2,.3,...V(.05,2.55),'p'],[1.0,2.8,...V(.85,2.4),'w']],
 front:[[-4.2,-2.9,...V(1.5,2.2),'w'],[-2.1,-1.1,...V(0,2.3),'d'],[.2,4.3,...V(.05,2.4),'p']],
 left:[[-2.6,-1.0,...V(.85,2.4),'w']]};
const zc=ZO-T/2,xc=XO-T/2;
wallRun(bld,'x',zc,-XO,XO,FL,FL+H,T,M.brick,HOLES.front,true,4);wallRun(bld,'x',-zc,-XO,XO,FL,FL+H,T,M.brick,HOLES.back,true,5);
wallRun(bld,'z',xc,-ZO+T,ZO-T,FL,FL+H,T,M.brick,HOLES.right,true,0);wallRun(bld,'z',-xc,-ZO+T,ZO-T,FL,FL+H,T,M.brick,HOLES.left,true,1);
for(const [f,ax,c,inn] of[['front','x',zc,-1],['back','x',-zc,1],['right','z',xc,-1],['left','z',-xc,1]])HOLES[f].forEach(h=>win(WIN,ax,c,h[0],h[1],h[2],h[3],h[4],inn));
box(WIN,4.85,.12,.14,2.1,FL+2.62,-ZO-.06,M.graph);box(WIN,.14,.12,3.65,XO+.06,FL+2.62,-1.45,M.graph);box(WIN,.16,2.7,.16,XO+.02,FL+1.32,-ZO-.02,M.graph);
for(const sx of[-1,1])for(const sz of[-1,1])box(WIN,.12,H,.12,sx*(XO+.01),FL+H/2,sz*(ZO+.01),M.graph);

// ---------- rooms ----------
const IX=XO-T,IZ=ZO-T;
const ROOMS=[
 {name:'Кухня-столовая',kind:'kitchen',xa:-.5,xb:IX,za:-IZ,zb:.4},
 {name:'Зал',kind:'living',xa:-.3,xb:IX,za:.4,zb:IZ},
 {name:'Спальня',kind:'bed',xa:-IX,xb:-.5,za:-IZ,zb:.4},
 {name:'Прихожая',kind:'hall',xa:-2.6,xb:-.3,za:.4,zb:IZ},
 {name:'Санузел',kind:'bath',xa:-IX,xb:-2.6,za:.4,zb:IZ}];
const floors=[];
ROOMS.forEach(rm=>{rm.area=(rm.xb-rm.xa)*(rm.zb-rm.za);const tile=['bath','hall'].includes(rm.kind);
 const m=box(INT,rm.xb-rm.xa,.02,rm.zb-rm.za,(rm.xa+rm.xb)/2,FL+.04,(rm.za+rm.zb)/2,(tile?M.porc:M.parquet).clone(),false);m.receiveShadow=true;m.userData.room=rm;rm.mesh=m;floors.push(m);});
const P=(ax,c,a0,a1,holes=[])=>wallRun(INT,ax,c,a0,a1,FL,FL+H,.12,M.plaster,holes.map(([s,e,dh])=>[s,e,FL,FL+(dh||2.2)]));
P('x',.4,-IX,-.5,[[-1.8,-1.0]]);P('x',.4,-.5,IX,[[-.2,.7],[1.0,3.4,2.5]]);P('z',-.5,-IZ,.4);P('z',-2.6,.4,IZ,[[1.2,2.0]]);P('z',-.3,.4,IZ,[[1.4,2.8,2.4]]);
const put=(x,z,w,d,h,col,y=0)=>box(INT,w,h,d,x,FL+y+h/2,z,typeof col==='string'?F(col):col);
put(-.15,-1.6,.62,3.4,.9,'#f3f2ef');put(-.15,-1.6,.64,3.42,.04,'#2b2c2f',.9);put(-.15,.05,.62,.6,2.3,'#e7e5e0');put(.6,-IZ+.32,1.5,.62,.9,'#f3f2ef');put(.6,-IZ+.32,1.52,.64,.04,'#2b2c2f',.9);
put(1.6,-1.2,1.9,.9,.9,'#3f6b5c');put(1.6,-1.2,2.0,.95,.05,'#ecebe7',.9);for(const x of[1.0,1.6,2.2])put(x,-.55,.38,.38,.75,'#b49a7c');
put(3.6,-2.2,1.0,1.6,.75,'#8a6a4a');for(const [x,z] of[[3.0,-2.7],[3.0,-1.7],[4.2,-2.7],[4.2,-1.7]])put(x,z,.44,.44,.48,'#3a3d42');
put(2.4,3.1,2.4,.9,.45,'#7b8a84');put(2.4,3.45,2.4,.2,.85,'#6e7c77');put(2.4,2.2,1.1,.6,.38,'#8a6a4a');put(2.4,2.4,3.2,2.2,.02,'#d6cdbf');put(IX-.25,2.0,.4,1.8,.5,'#2d3034');put(IX-.3,2.0,.05,1.3,.75,'#111214',.8);
put(.4,1.4,.8,.8,.45,'#b8a48c');
put(-2.7,-2.3,1.8,2.0,.42,'#ece7de');put(-2.7,-2.25,1.7,1.9,.12,'#a9b7c3',.42);put(-2.7,-3.3,1.9,.1,1.0,'#6b5646');put(-3.9,-3.0,.45,.45,.5,'#8a6a4a');put(-1.5,-3.0,.45,.45,.5,'#8a6a4a');put(-4.3,-.6,.6,1.6,2.3,'#e3ddd3');
put(-4.2,2.7,.75,1.6,.55,'#ffffff');put(-3.0,3.1,.4,.55,.42,'#ffffff');put(-3.3,1.0,.55,.45,.85,'#ffffff');
put(-2.3,2.2,.5,1.8,2.3,'#d9d2c6');put(-1.0,1.0,.4,1.0,.45,'#8a6a4a');
INT.traverse(o=>{if(o.isMesh)o.castShadow=o.receiveShadow=true;});
const roomLights=[[2,-1.4,H],[2,2.2,H],[-2.6,-1.8,H],[-1.4,2,H],[-3.6,2,H]].map(([x,z,h])=>{const l=new THREE.PointLight('#ffcf94',0,8,1.6);l.position.set(x,FL+h-.4,z);scene.add(l);return l;});

// ---------- hip roof (шатровая) + veranda ----------
const seamTex=ctex(256,256,(g,w,h)=>{g.fillStyle='#3a3e44';g.fillRect(0,0,w,h);for(let x=0;x<w;x+=64){g.fillStyle='#50555c';g.fillRect(x,0,6,h);g.fillStyle='#2a2d32';g.fillRect(x+6,0,3,h);}},[2,1]);
const RM=new THREE.MeshStandardMaterial({map:seamTex,roughness:.38,metalness:.55,side:THREE.DoubleSide});
const OV=.6,E=FL+H+.18,PT=Math.tan(27*Math.PI/180),HX=XO+OV,HZ=ZO+OV,RH=HZ*PT,RX=HX-HZ;
function poly(pts,uvs,mat){const g=new THREE.BufferGeometry();const Pp=[],U=[];for(let i=1;i<pts.length-1;i++)for(const k of[0,i,i+1]){Pp.push(...pts[k]);U.push(...uvs[k]);}
 g.setAttribute('position',new THREE.Float32BufferAttribute(Pp,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(U,2));g.computeVertexNormals();const m=new THREE.Mesh(g,mat);m.castShadow=m.receiveShadow=true;ROOF.add(m);return m;}
const SL=Math.hypot(HZ,RH);
for(const s of[1,-1]){poly([[-HX,E,s*HZ],[HX,E,s*HZ],[RX,E+RH,0],[-RX,E+RH,0]],[[-HX,0],[HX,0],[RX,SL],[-RX,SL]],RM);poly([[s*HX,E,-HZ],[s*HX,E,HZ],[s*RX,E+RH,0]],[[-HZ,0],[HZ,0],[0,SL]],RM);}
const capM=new THREE.MeshStandardMaterial({color:'#2c2f34',roughness:.4,metalness:.6});
function bar(a,b,rr=.07,mat=capM){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b);const m=new THREE.Mesh(new THREE.CylinderGeometry(rr,rr,A.distanceTo(B),8),mat);
 m.position.copy(A).add(B).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());m.castShadow=true;ROOF.add(m);return m;}
bar([-RX,E+RH+.03,0],[RX,E+RH+.03,0],.09);for(const sx of[-1,1])for(const sz of[-1,1])bar([sx*HX,E+.03,sz*HZ],[sx*RX,E+RH+.03,0]);
for(const s of[1,-1]){box(ROOF,2*HX,.2,.05,0,E-.08,s*HZ,M.graph);box(ROOF,.05,.2,2*HZ,s*HX,E-.08,0,M.graph);box(ROOF,2*HX,.03,OV,0,E-.17,s*(HZ-OV/2),M.soffit);box(ROOF,OV,.03,2*HZ-2*OV,s*(HX-OV/2),E-.17,0,M.soffit);}
for(const s of[1,-1]){bar([-HX,E-.12,s*(HZ+.06)],[HX,E-.12,s*(HZ+.06)],.065);bar([s*(HX+.06),E-.12,-HZ],[s*(HX+.06),E-.12,HZ],.065);}
for(const sx of[-1,1])for(const sz of[-1,1]){bar([sx*(XO+.08),E-.15,sz*(ZO+.45)],[sx*(XO+.08),E-.5,sz*(ZO+.1)],.05);bar([sx*(XO+.08),E-.5,sz*(ZO+.1)],[sx*(XO+.08),.2,sz*(ZO+.1)],.05);}
for(let k=0;k<5;k++)box(ROOF,.12,.02,.12,-4+k*2,E-.19,-HZ+.3,M.led,false);
// veranda along the front: deck, wooden posts, low shed roof with hipped ends
const VZ0=ZO,VZ1=ZO+2.6,VX0=-2.7,VX1=XO+.3,vp=Math.tan(12*Math.PI/180),VE=E-.05-(VZ1+.35-ZO)*vp-.22;
box(bld,VX1-VX0,.05,VZ1-VZ0,(VX0+VX1)/2,.4,(VZ0+VZ1)/2,M.deck);for(const x of[VX0+.15,-.2,2.4,VX1-.15])for(const z of[ZO+1.2,VZ1-.15])pile(x,z,.25);box(bld,VX1-VX0,.12,.08,(VX0+VX1)/2,.32,ZO+1.2,capM2);box(bld,VX1-VX0,.12,.08,(VX0+VX1)/2,.32,VZ1-.15,capM2);for(let k=0;k<2;k++)box(bld,1.8,.14,.3,-1.6,.07+k*.14,VZ1+.3-k*.3,M.deck);
[VX0+.15,-.2,2.4,VX1-.15].forEach(x=>box(bld,.16,VE-.42,.16,x,.42+(VE-.42)/2,VZ1-.15,M.wood));box(bld,VX1-VX0,.22,.18,(VX0+VX1)/2,VE+.1,VZ1-.15,M.wood);
const vEave=VE+.22,vTop=vEave+(VZ1+.35-ZO)*vp;
poly([[VX0-.35,vEave,VZ1+.35],[VX1+.35,vEave,VZ1+.35],[VX1+.35,vTop,ZO+.05],[VX0-.35,vTop,ZO+.05]],[[VX0,0],[VX1,0],[VX1,3],[VX0,3]],RM);
for(const x of[VX0-.35,VX1+.35])poly([[x,vEave,VZ1+.35],[x,vTop,ZO+.05],[x,vEave,ZO+.05]],[[0,0],[2.9,1],[2.9,0]],RM);
box(ROOF,VX1-VX0+.6,.02,VZ1-ZO+.2,(VX0+VX1)/2,vEave-.02,(ZO+VZ1)/2+.1,M.soffit);
box(ROOF,VX1-VX0+.7,.18,.05,(VX0+VX1)/2,vEave-.06,VZ1+.36,M.graph);
box(bld,1.8,.4,.75,2.4,.62,ZO+1.8,F('#d8d2c8'));box(bld,1.8,.35,.18,2.4,.8,ZO+2.15,F('#d8d2c8'));box(bld,.8,.38,.5,2.4,.61,ZO+1.0,F('#8a6a4a'));box(bld,.6,.45,.6,4.4,.65,ZO+1.4,F('#5a5d61'));
const extGlow=[[1,VE-.3,ZO+1.3],[2,FL+2.2,-ZO-1.5]].map(p=>{const l=new THREE.PointLight('#ffd09a',0,9,1.7);l.position.set(...p);scene.add(l);return l;});
// small deck behind the kitchen glass (mountain view)
box(bld,5.2,.05,2.2,2.2,.33,-ZO-1.1,M.deck);for(const x of[-.3,2.2,4.7])pile(x,-ZO-2.05,.22);box(bld,5.2,.1,.08,2.2,.26,-ZO-2.05,capM2);box(bld,1.6,.04,.8,2.6,1.05,-ZO-1.2,F('#2e3135'));for(const x of[1.9,3.3])box(bld,.45,.45,.45,x,.58,-ZO-1.2,F('#3a3d42'));

