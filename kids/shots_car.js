const {chromium}=require("playwright");const path=require("path");
(async()=>{const b=await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on("pageerror",e=>console.log("ERR",e.message));p.on("console",m=>{if(m.type()==="error")console.log("CONSOLE",m.text())});
await p.goto("file://"+path.resolve("car_scene.html"));await p.waitForFunction(()=>window.sceneReady);await p.evaluate(()=>document.fonts.ready);
const ts=(process.argv[2]||"2,6.5,11,15,19.5,24.5,28.5").split(",").map(Number);
let t0=Date.now();
for(const t of ts){await p.evaluate(t=>renderAt(t),t);await p.screenshot({path:`build/k_${t}.png`});}
console.log("ms/frame",(Date.now()-t0)/ts.length);await b.close();})();
