import pathlib,re
base=pathlib.Path('/home/user/1122/house150/house150.html').read_text()
new75=pathlib.Path('/home/user/1122/house75/new75.js').read_text()
site=new75[:new75.index("// ---------- house:")]
house=pathlib.Path('/home/user/1122/house100/house_part.js').read_text()
s=base
def rep(a,b):
    global s
    assert a in s,a[:90]; s=s.replace(a,b)
rep("<title>Хай-тек дом 150 м²</title>","<title>Дом 100 м² в коричневых тонах</title>")
rep('<h1>Хай-тек дом <span>150 м²</span></h1>','<h1>Дом <span>100 м²</span></h1>')
rep('<div class="chips"><span class="chip">15 × 10 м</span><span class="chip">3 спальни</span><span class="chip">2 санузла</span><span class="chip">зал 5 × 8 м</span><span class="chip">гардеробная</span></div>',
    '<div class="chips"><span class="chip">12,5 × 8 м</span><span class="chip">зал 20 м²</span><span class="chip">2 детские + спальня</span><span class="chip">шатровая крыша</span><span class="chip">бетонный фундамент</span></div>')
rep('<span class="lbl">Кирпич</span><span id="brick"','<span class="lbl">Фасад</span><span id="brick"')
rep("--accent:#9a4a33;","--accent:#7a4e32;")
rep("--accent:#e08a6c;--accent-fg:#1f0d07;","--accent:#d9a37c;--accent-fg:#1f1007;")
rep("const BRICKS={red:{name:'Красный клинкер'","""const brownWood=ctex(1024,1024,(g,w,h)=>{for(let y=0;y<h;y+=64){const k=y/64;g.fillStyle=['#6e4a33','#644330','#77513a','#5f402d'][k%4];g.fillRect(0,y,w,64);
 for(let i=0;i<10;i++){g.strokeStyle='rgba(30,16,8,.22)';g.beginPath();const yy=y+5+rnd(k*31+i)*52;g.moveTo(0,yy);g.bezierCurveTo(w*.3,yy+5,w*.6,yy-5,w,yy+2);g.stroke();}g.fillStyle='rgba(20,10,5,.5)';g.fillRect(0,y+60,w,4);}},[1/2,1/2]);
const tanPlaster=ctex(512,512,(g,w,h)=>{g.fillStyle='#b48a68';g.fillRect(0,0,w,h);for(let i=0;i<9000;i++){g.fillStyle=`rgba(${150+rnd(i)*50|0},${110+rnd(i)*40|0},${80+rnd(i)*30|0},.35)`;g.fillRect(rnd(i+1)*w,rnd(i+2)*h,2,2);}},[1/2,1/2]);
const BRICKS={brownWood:{name:'Коричневое дерево (имитация бруса)',ui:'#6e4a33',tex:brownWood},tan:{name:'Светло-коричневая штукатурка',ui:'#b48a68',tex:tanPlaster},red:{name:'Красный клинкер'""")
rep("const M={brick:cm({map:BRICKS.red.tex,bumpMap:BRICKS.red.tex,bumpScale:1.6,","const M={brick:cm({map:BRICKS.brown.tex,bumpMap:BRICKS.brown.tex,bumpScale:1.6,")
rep("aria-pressed=\"${k==='red'}\"","aria-pressed=\"${k==='brown'}\"")
a=s.index("// ---------- site ----------");b=s.index("// ---------- labels ----------")
s=s[:a]+site+house+s[b:]
s2=re.sub(r"const VIEWS=\{facade:\[\[14,6\.5,19\],\[1,2,0\]\],plan:\[\[3,19,12\],\[0,FL,0\]\]\};","const VIEWS={facade:[[12,5,17],[0,2.6,0]],plan:[[2,16,10],[0,FL,0]]};",s);assert s2!=s;s=s2
rep("const LEG={facade:'<b>Фасад:</b> клинкерный кирпич, панорамные окна в зале и кухне, плоская кровля хай-тек с выносом над террасой и входом, деревянная подшивка и LED-подсветка.',",
    "const LEG={facade:'<b>Дом 100 м²:</b> коричневый кирпичный фасад, шатровая крыша из светло-коричневой металлочерепицы, крыльцо с навесом. Бетонный ленточный фундамент, цоколь облицован камнем, отмостка вокруг дома. Цвет фасада — кнопками ниже.',")
s2=re.sub(r" plan:'<b>Планировка ≈ 136 м² комнат:</b>[^']*'"," plan:'<b>Планировка ≈ 88 м² комнат:</b> из прихожей справа большой зал, слева кухня-столовая, за кухней 2 детские, рядом с залом спальня, санузел в центре. Выберите комнату или нажмите на пол.'",s);assert s2!=s;s=s2
rep("flyTo([cx+1.2,FL+7,cz+4.5],[cx,FL+.3,cz],portrait()?1.35:1);","flyTo([cx+1,FL+6,cz+4],[cx,FL+.3,cz],portrait()?1.35:1);")
rep(".sort((a,b)=>Math.hypot(a[0]-.5,a[1])-Math.hypot(b[0]-.5,b[1]));",".sort((a,b)=>Math.hypot(a[0],a[1])-Math.hypot(b[0],b[1]));")
pathlib.Path('/home/user/1122/house100/house100.html').write_text(s);print('written')
