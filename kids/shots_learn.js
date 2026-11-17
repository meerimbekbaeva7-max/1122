const {chromium}=require("playwright");const path=require("path");
(async()=>{const id=process.argv[2];const b=await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]});
const p=await b.newPage({viewport:{width:1920,height:1080}});p.on("pageerror",e=>console.log("ERR",id,e.message));p.on("console",m=>{if(m.type()==="error")console.log("CONSOLE",id,m.text())});
await p.goto("file://"+path.resolve("learn.html")+"?d=build_"+id);await p.waitForFunction(()=>window.sceneReady,{timeout:60000});await p.evaluate(()=>document.fonts.ready);
const L=await p.evaluate(()=>SONG.lines.map(l=>[l.tag,l.t0,l.t1]));const seen=new Set();const ts=[2];
for(const [tag,t0,t1] of L){if(!seen.has(tag)){seen.add(tag);ts.push(+(t0+(t1-t0)*.45).toFixed(2));}}
const files=[];for(const t of ts){await p.evaluate(t=>renderAt(t),t);const f=`build_${id}/k_${t}.png`;await p.screenshot({path:f});files.push(f);}
console.log(files.join(" "));await b.close();})();
