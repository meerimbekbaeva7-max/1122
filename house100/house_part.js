// ---------- house: 12.5 x 8 m, one storey on a concrete strip foundation ----------
const FL=.5,H=2.8,XO=6.25,ZO=4,T=.3;
const bld=new THREE.Group(),INT=new THREE.Group(),WIN=new THREE.Group(),ROOF=new THREE.Group();scene.add(bld);bld.add(INT,WIN,ROOF);
// concrete strip foundation with a stone-faced plinth (0.5 m above ground)
const stoneT=ctex(512,512,(g,w,h)=>{g.fillStyle='#6b6560';g.fillRect(0,0,w,h);let y=0;while(y<h){const rh=50+rnd(y)*40;let x=-rnd(y+1)*80;while(x<w){const rw=90+rnd(x+y)*120;g.fillStyle=['#7a736c','#6a635c','#847c74','#5f5852','#736b63'][((x+y)|0)%5];g.fillRect(x+3,y+3,rw-6,rh-6);x+=rw;}y+=rh;}},[1/1.5,1/1.5]);
const plM=new THREE.MeshStandardMaterial({map:stoneT,bumpMap:stoneT,bumpScale:2,roughness:.85});
wallRun(bld,'x',ZO-.15,-XO-.04,XO+.04,0,FL,.38,plM,[],true);wallRun(bld,'x',-ZO+.15,-XO-.04,XO+.04,0,FL,.38,plM,[],true);
wallRun(bld,'z',XO-.15,-ZO,ZO,0,FL,.38,plM,[],true);wallRun(bld,'z',-XO+.15,-ZO,ZO,0,FL,.38,plM,[],true);
box(bld,2*XO-.3,FL-.02,2*ZO-.3,0,(FL-.02)/2,0,M.slab,false);
// strip footing below grade (visible only in plan cut as concrete)
const concM=new THREE.MeshStandardMaterial({color:'#b8b4ac',roughness:.9});
for(const z of[-ZO+.2,ZO-.2,-.4])box(bld,2*XO,.6,.5,0,-.3,z,concM,false);for(const x of[-XO+.2,XO-.2,-1.0,1.0])box(bld,.5,.6,2*ZO,x,-.3,0,concM,false);
// drainage apron (отмостка) around the house
const apronM=new THREE.MeshStandardMaterial({color:'#a9a59d',roughness:.9});
box(bld,2*XO+1.6,.05,.8,0,.025,ZO+.4,apronM,false);box(bld,2*XO+1.6,.05,.8,0,.025,-ZO-.4,apronM,false);box(bld,.8,.05,2*ZO,XO+.4,.025,0,apronM,false);box(bld,.8,.05,2*ZO,-XO-.4,.025,0,apronM,false);
const V=(a,b)=>[FL+a,FL+b];
const HOLES={
 front:[[-4.6,-2.6,...V(.85,2.4),'w'],[-.5,.5,...V(0,2.3),'d'],[2.0,5.3,...V(.3,2.45),'p']],
 back:[[-5.3,-4.0,...V(.85,2.4),'w'],[-2.8,-1.5,...V(.85,2.4),'w'],[-.35,.35,...V(1.6,2.25),'w'],[2.6,4.4,...V(.85,2.4),'w']],
 right:[[-2.9,-1.3,...V(.85,2.4),'w'],[.4,3.2,...V(.3,2.45),'p']],
 left:[[1.4,2.9,...V(.85,2.4),'w'],[-2.6,-1.4,...V(.85,2.4),'w']]};
const zc=ZO-T/2,xc=XO-T/2;
wallRun(bld,'x',zc,-XO,XO,FL,FL+H,T,M.brick,HOLES.front,true,4);wallRun(bld,'x',-zc,-XO,XO,FL,FL+H,T,M.brick,HOLES.back,true,5);
wallRun(bld,'z',xc,-ZO+T,ZO-T,FL,FL+H,T,M.brick,HOLES.right,true,0);wallRun(bld,'z',-xc,-ZO+T,ZO-T,FL,FL+H,T,M.brick,HOLES.left,true,1);
for(const [f,ax,c,inn] of[['front','x',zc,-1],['back','x',-zc,1],['right','z',xc,-1],['left','z',-xc,1]])HOLES[f].forEach(h=>win(WIN,ax,c,h[0],h[1],h[2],h[3],h[4],inn));
for(const sx of[-1,1])for(const sz of[-1,1])box(WIN,.14,H,.14,sx*(XO+.01),FL+H/2,sz*(ZO+.01),M.graph);
box(WIN,2*XO+.1,.12,.12,0,FL+.06,ZO+.04,M.graph);box(WIN,2*XO+.1,.12,.12,0,FL+.06,-ZO-.04,M.graph);box(WIN,.12,.12,2*ZO+.1,XO+.04,FL+.06,0,M.graph);box(WIN,.12,.12,2*ZO+.1,-XO-.04,FL+.06,0,M.graph);

// ---------- rooms ----------
const IX=XO-T,IZ=ZO-T;
const ROOMS=[
 {name:'Прихожая',kind:'hall',xa:-1.0,xb:1.0,za:.8,zb:IZ},
 {name:'Зал',kind:'living',xa:1.0,xb:IX,za:-.4,zb:IZ},
 {name:'Кухня-столовая',kind:'kitchen',xa:-IX,xb:-1.0,za:.8,zb:IZ},
 {name:'Коридор',kind:'corr',xa:-IX,xb:1.0,za:-.4,zb:.8},
 {name:'Детская 1',kind:'kid1',xa:-IX,xb:-3.4,za:-IZ,zb:-.4},
 {name:'Детская 2',kind:'kid2',xa:-3.4,xb:-.85,za:-IZ,zb:-.4},
 {name:'Санузел',kind:'bath',xa:-.85,xb:1.0,za:-IZ,zb:-.4},
 {name:'Спальня',kind:'bed',xa:1.0,xb:IX,za:-IZ,zb:-.4}];
const floors=[];
ROOMS.forEach(rm=>{rm.area=(rm.xb-rm.xa)*(rm.zb-rm.za);const tile=['bath','hall'].includes(rm.kind);
 const m=box(INT,rm.xb-rm.xa,.02,rm.zb-rm.za,(rm.xa+rm.xb)/2,FL+.04,(rm.za+rm.zb)/2,(tile?M.porc:M.parquet).clone(),false);m.receiveShadow=true;m.userData.room=rm;rm.mesh=m;floors.push(m);});
const P=(ax,c,a0,a1,holes=[])=>wallRun(INT,ax,c,a0,a1,FL,FL+H,.12,M.plaster,holes.map(([s,e,dh])=>[s,e,FL,FL+(dh||2.2)]));
P('x',.8,-IX,-1.0,[[-2.4,-1.3,2.3]]);            // kitchen | corridor (wide opening)
P('z',-1.0,.8,IZ,[[1.8,2.8,2.3]]);                // kitchen | hall (opening)
P('z',1.0,-.4,IZ,[[1.4,3.0,2.4],[-.3,.7]]);       // hall/corridor | living (double door + corridor door)
P('x',-.4,-IX,1.0,[[-5.0,-4.2],[-2.4,-1.6],[-.45,.35]]); // corridor | kids + bath
P('x',-.4,1.0,IX,[[1.3,2.2]]);                    // living | bedroom
P('z',-3.4,-IZ,-.4);P('z',-.85,-IZ,-.4);
const put=(x,z,w,d,h,col,y=0)=>box(INT,w,h,d,x,FL+y+h/2,z,typeof col==='string'?F(col):col);
// living room
put(3.5,.4,2.8,1.0,.45,'#7c6a5a');put(3.5,.05,2.8,.22,.85,'#6f5e50');put(5.4,1.0,1.0,1.6,.45,'#7c6a5a');put(3.5,1.6,1.2,.7,.38,'#8a6a4a');put(3.5,1.5,3.4,2.4,.02,'#d6cdbf');
put(3.5,IZ-.25,2.4,.4,.5,'#3a2f28');put(3.5,IZ-.3,1.5,.05,.85,'#111214',.8);put(1.5,3.0,.8,.8,.45,'#b8a48c');
// kitchen
put(-3.4,IZ-.32,3.2,.62,.9,'#efe9df');put(-3.4,IZ-.32,3.22,.64,.04,'#3a2f28',.9);put(-IX+.32,2.2,.62,1.6,.9,'#efe9df');put(-IX+.32,2.2,.64,1.62,.04,'#3a2f28',.9);put(-1.4,IZ-.33,.65,.62,2.2,'#e7e1d6');
put(-3.2,1.9,1.6,.9,.75,'#7b5a3f');for(const [x,z] of[[-3.7,1.3],[-2.7,1.3],[-3.7,2.5],[-2.7,2.5]])put(x,z,.42,.42,.48,'#5a4636');
// kids rooms
for(const [xa,xb,c] of[[-IX,-3.4,'#b9d3e6'],[-3.4,-.85,'#f0c7cf']]){const cx=(xa+xb)/2;put(xa+.5,-2.6,.95,1.95,.4,'#ece7de');put(xa+.5,-2.6,.9,1.85,.12,c,.4);put(xb-.45,-IZ+.35,.8,.55,.75,'#c9b39a');put(xb-.35,-1.3,.6,1.2,2.0,'#e3ddd3');put(cx+.2,-2.0,1.2,1.2,.02,c);}
// bath
put(-.1,-IZ+.42,1.6,.75,.55,'#ffffff');put(.65,-1.2,.4,.55,.42,'#ffffff');put(-.55,-1.1,.5,.45,.85,'#ffffff');
// bedroom
put(3.6,-2.4,1.8,2.0,.42,'#ece7de');put(3.6,-2.35,1.7,1.9,.12,'#c7a98c',.42);put(IX-.08,-2.4,.1,1.9,1.0,'#5b4334');put(IX-.35,-3.6+.2,.45,.45,.5,'#7b5a3f');put(IX-.35,-1.2,.45,.45,.5,'#7b5a3f');put(1.45,-2.4,.6,1.8,2.2,'#e3ddd3');
// hall + corridor
put(-.7,2.6,.5,1.6,2.3,'#d9d2c6');put(.7,3.2,.4,.9,.45,'#7b5a3f');put(-5.2,.2,.35,.8,.8,'#3a2f28');
INT.traverse(o=>{if(o.isMesh)o.castShadow=o.receiveShadow=true;});
const roomLights=[[3.5,1.5,H],[-3.4,2.2,H],[0,2.2,H],[-4.6,-2,H],[-2.1,-2,H],[3.5,-2.2,H],[-2.5,.2,H]].map(([x,z,h])=>{const l=new THREE.PointLight('#ffcf94',0,8,1.6);l.position.set(x,FL+h-.4,z);scene.add(l);return l;});

// ---------- hip roof, light-brown metal tile ----------
const tileT=ctex(256,256,(g,w,h)=>{const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#a06e4c');gr.addColorStop(.7,'#94633f');gr.addColorStop(.86,'#6e4529');gr.addColorStop(1,'#a77554');g.fillStyle=gr;g.fillRect(0,0,w,h);
 for(let x=0;x<w;x+=64){const gx=g.createLinearGradient(x,0,x+64,0);gx.addColorStop(0,'rgba(0,0,0,.18)');gx.addColorStop(.5,'rgba(255,255,255,.12)');gx.addColorStop(1,'rgba(0,0,0,.18)');g.fillStyle=gx;g.fillRect(x,0,64,h);}},[3,1/.35]);
const RM=new THREE.MeshStandardMaterial({map:tileT,bumpMap:tileT,bumpScale:2,roughness:.45,metalness:.35,side:THREE.DoubleSide});
const OV=.6,E=FL+H+.18,PT=Math.tan(27*Math.PI/180),HX=XO+OV,HZ=ZO+OV,RH=HZ*PT,RX=HX-HZ;
function poly(pts,uvs,mat){const g=new THREE.BufferGeometry();const Pp=[],U=[];for(let i=1;i<pts.length-1;i++)for(const k of[0,i,i+1]){Pp.push(...pts[k]);U.push(...uvs[k]);}
 g.setAttribute('position',new THREE.Float32BufferAttribute(Pp,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(U,2));g.computeVertexNormals();const m=new THREE.Mesh(g,mat);m.castShadow=m.receiveShadow=true;ROOF.add(m);return m;}
const SL=Math.hypot(HZ,RH);
for(const s of[1,-1]){poly([[-HX,E,s*HZ],[HX,E,s*HZ],[RX,E+RH,0],[-RX,E+RH,0]],[[-HX,0],[HX,0],[RX,SL],[-RX,SL]],RM);poly([[s*HX,E,-HZ],[s*HX,E,HZ],[s*RX,E+RH,0]],[[-HZ,0],[HZ,0],[0,SL]],RM);}
const capM=new THREE.MeshStandardMaterial({color:'#6b4429',roughness:.4,metalness:.4});
function bar(a,b,rr=.07,mat=capM){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b);const m=new THREE.Mesh(new THREE.CylinderGeometry(rr,rr,A.distanceTo(B),8),mat);
 m.position.copy(A).add(B).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());m.castShadow=true;ROOF.add(m);return m;}
bar([-RX,E+RH+.03,0],[RX,E+RH+.03,0],.1);for(const sx of[-1,1])for(const sz of[-1,1])bar([sx*HX,E+.03,sz*HZ],[sx*RX,E+RH+.03,0],.08);
const fasM=new THREE.MeshStandardMaterial({color:'#5a3b26',roughness:.5});
for(const s of[1,-1]){box(ROOF,2*HX,.2,.05,0,E-.08,s*HZ,fasM);box(ROOF,.05,.2,2*HZ,s*HX,E-.08,0,fasM);box(ROOF,2*HX,.03,OV,0,E-.17,s*(HZ-OV/2),M.soffit);box(ROOF,OV,.03,2*HZ-2*OV,s*(HX-OV/2),E-.17,0,M.soffit);}
const gutM=new THREE.MeshStandardMaterial({color:'#5a3b26',roughness:.35,metalness:.5});
for(const s of[1,-1]){bar([-HX,E-.12,s*(HZ+.06)],[HX,E-.12,s*(HZ+.06)],.065,gutM);bar([s*(HX+.06),E-.12,-HZ],[s*(HX+.06),E-.12,HZ],.065,gutM);}
for(const sx of[-1,1])for(const sz of[-1,1]){bar([sx*(XO+.08),E-.15,sz*(ZO+.45)],[sx*(XO+.08),E-.5,sz*(ZO+.1)],.05,gutM);bar([sx*(XO+.08),E-.5,sz*(ZO+.1)],[sx*(XO+.08),.2,sz*(ZO+.1)],.05,gutM);}
for(const s of[1,-1]){const d=.9,y=E+d*PT,z=s*(HZ-d);bar([-HX+d+.3,y+.12,z],[HX-d-.3,y+.12,z],.025,gutM);}
box(ROOF,.6,1.1,.6,-3.2,E+RH*.6+.3,-1.2,F('#5a3b26'));box(ROOF,.72,.06,.72,-3.2,E+RH*.6+.88,-1.2,capM);
// entrance porch with its own small hip canopy on wooden posts
const PZ0=ZO,PZ1=ZO+1.8,PX0=-1.7,PX1=1.7,vp=Math.tan(20*Math.PI/180),pTop=E-.05,pEave=pTop-(PZ1+.3-ZO)*vp;
box(bld,PX1-PX0,FL-.05,PZ1-PZ0,0,(FL-.05)/2,(PZ0+PZ1)/2,plM);box(bld,PX1-PX0,.04,PZ1-PZ0,0,FL-.03,(PZ0+PZ1)/2,M.porc);for(let k=0;k<3;k++)box(bld,1.8,.15,.32,0,.075+k*.15,PZ1+.48-k*.32,concM);
for(const x of[PX0+.12,PX1-.12])box(bld,.16,pEave-.45,.16,x,.42+(pEave-.45)/2,PZ1-.12,M.wood);box(bld,PX1-PX0,.18,.16,0,pEave-.08,PZ1-.12,M.wood);
poly([[PX0-.3,pEave,PZ1+.3],[PX1+.3,pEave,PZ1+.3],[PX1+.3-1.2,pTop,ZO],[PX0-.3+1.2,pTop,ZO]],[[-2,0],[2,0],[1,2.2],[-1,2.2]],RM);
for(const [x,s] of[[PX0-.3,1],[PX1+.3,-1]])poly([[x,pEave,PZ1+.3],[x,pEave,ZO],[x+s*1.2,pTop,ZO]],[[0,0],[2.1,0],[2.1,1]],RM);
box(ROOF,PX1-PX0+.5,.02,PZ1-ZO+.25,0,pEave-.02,(ZO+PZ1)/2+.1,M.soffit);
const extGlow=[[0,pEave-.3,ZO+.9],[3.6,FL+2.4,ZO+.8]].map(p=>{const l=new THREE.PointLight('#ffd09a',0,9,1.7);l.position.set(...p);scene.add(l);return l;});
box(WIN,.08,.3,.08,-.85,FL+2.0,ZO+.04,M.led,false);box(WIN,.08,.3,.08,.85,FL+2.0,ZO+.04,M.led,false);

