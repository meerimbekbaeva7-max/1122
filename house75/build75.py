import pathlib,re
s=pathlib.Path('/home/user/1122/house150/house150.html').read_text()
def rep(a,b):
    global s
    assert a in s,a[:90]; s=s.replace(a,b)
rep("<title>Хай-тек дом 150 м²</title>","<title>Дом 75 м² с видом на горы</title>")
rep('<h1>Хай-тек дом <span>150 м²</span></h1>','<h1>Дом <span>75 м²</span> с видом на горы</h1>')
rep('<div class="chips"><span class="chip">15 × 10 м</span><span class="chip">3 спальни</span><span class="chip">2 санузла</span><span class="chip">зал 5 × 8 м</span><span class="chip">гардеробная</span></div>',
    '<div class="chips"><span class="chip">10 × 7,5 м</span><span class="chip">кухня 20 м²</span><span class="chip">зал + веранда</span><span class="chip">шатровая крыша</span></div>')
rep('<span class="lbl">Кирпич</span><span id="brick"','<span class="lbl">Фасад</span><span id="brick"')
rep("--accent:#9a4a33;","--accent:#3f6b5c;")
rep("--accent:#e08a6c;--accent-fg:#1f0d07;","--accent:#7cc3a8;--accent-fg:#06201a;")
rep("const BRICKS={red:{name:'Красный клинкер'","""const woodBoards=ctex(1024,1024,(g,w,h)=>{const n=13,bw=w/n;for(let k=0;k<n;k++){g.fillStyle=['#c19d78','#b38f6b','#caa680','#b9946f','#c09a74','#ad8966'][k%6];g.fillRect(k*bw,0,bw,h);
 for(let i=0;i<14;i++){g.strokeStyle=`rgba(${95+rnd(k*19+i)*30|0},${66+rnd(k*7+i)*20|0},42,${.1+rnd(k+i)*.14})`;g.lineWidth=1+rnd(i+k)*1.5;g.beginPath();const x=k*bw+4+rnd(k*31+i)*(bw-8);g.moveTo(x,0);g.bezierCurveTo(x+6,h*.3,x-6,h*.7,x+3,h);g.stroke();}
 g.fillStyle='rgba(40,28,18,.5)';g.fillRect(k*bw,0,3,h);}},[1/1.6,1/1.6]);
const plasterT=ctex(512,512,(g,w,h)=>{g.fillStyle='#ecebe6';g.fillRect(0,0,w,h);for(let i=0;i<9000;i++){g.fillStyle=`rgba(${190+rnd(i)*50|0},${190+rnd(i)*50|0},${185+rnd(i)*50|0},.3)`;g.fillRect(rnd(i+1)*w,rnd(i+2)*h,2,2);}},[1/2,1/2]);
const BRICKS={wood:{name:'Светлое дерево',ui:'#c19d78',tex:woodBoards},plaster:{name:'Белая штукатурка',ui:'#ecebe6',tex:plasterT},red:{name:'Красный клинкер'""")
rep("const M={brick:cm({map:BRICKS.red.tex,bumpMap:BRICKS.red.tex,bumpScale:1.6,","const M={brick:cm({map:BRICKS.wood.tex,bumpMap:BRICKS.wood.tex,bumpScale:1.0,")
rep("aria-pressed=\"${k==='red'}\"","aria-pressed=\"${k==='wood'}\"")
a=s.index("// ---------- site ----------");b=s.index("// ---------- labels ----------")
NEW=pathlib.Path('/tmp/claude-0/-home-user-1122/baafca0a-3286-5745-8381-c2f1cff59929/scratchpad/new75.js').read_text()
s=s[:a]+NEW+s[b:]
s2=re.sub(r"const VIEWS=\{facade:\[\[14,6\.5,19\],\[1,2,0\]\],plan:\[\[3,19,12\],\[0,FL,0\]\]\};","const VIEWS={facade:[[11,5.5,15],[0,2.2,0]],plan:[[2,14,9],[0,FL,0]]};",s);assert s2!=s;s=s2
rep("const LEG={facade:'<b>Фасад:</b> клинкерный кирпич, панорамные окна в зале и кухне, плоская кровля хай-тек с выносом над террасой и входом, деревянная подшивка и LED-подсветка.',",
    "const LEG={facade:'<b>Дом 75 м²:</b> шатровая крыша из фальцевого металла, веранда вдоль фасада, кухня в задней части с угловыми панорамными окнами на горы. Цвет фасада — кнопками ниже.',")
s2=re.sub(r" plan:'<b>Планировка ≈ 136 м² комнат:</b>[^']*'"," plan:'<b>Планировка ≈ 66 м² комнат:</b> кухня-столовая 20 м² с панорамой на горы, зал с выходом на веранду, спальня, санузел, прихожая. Выберите комнату или нажмите на пол.'",s);assert s2!=s;s=s2
rep("flyTo([cx+1.2,FL+7,cz+4.5],[cx,FL+.3,cz],portrait()?1.35:1);","flyTo([cx+1,FL+6,cz+3.8],[cx,FL+.3,cz],portrait()?1.35:1);")
rep(".sort((a,b)=>Math.hypot(a[0]-.5,a[1])-Math.hypot(b[0]-.5,b[1]));",".sort((a,b)=>Math.hypot(a[0],a[1])-Math.hypot(b[0],b[1]));")
pathlib.Path('/home/user/1122/house75/house75.html').write_text(s)
print('written')
