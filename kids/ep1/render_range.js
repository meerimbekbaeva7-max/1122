// node render_range.js <page> <out.mp4> <startSec> <endSec>  (warms up camera smoothing for 1 s before start)
const {chromium}=require("playwright");const {spawn}=require("child_process");const path=require("path");
const [page,out,a,b]=process.argv.slice(2);const FPS=30,F0=Math.round(+a*FPS),F1=Math.round(+b*FPS);
(async()=>{const br=await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]});
const p=await br.newPage({viewport:{width:1920,height:1080}});p.on("pageerror",e=>console.log("ERR",e.message));
p.setDefaultTimeout(180000);await p.goto("file://"+path.resolve(page));await p.waitForFunction(()=>window.sceneReady,{timeout:60000});await p.evaluate(()=>document.fonts.ready);
for(let f=Math.max(0,F0-30);f<F0;f++)await p.evaluate(t=>renderAt(t),f/FPS);
const ff=spawn("ffmpeg",["-y","-loglevel","error","-f","image2pipe","-framerate","30","-c:v","mjpeg","-i","-","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",out],{stdio:["pipe","inherit","inherit"]});
const t0=Date.now();for(let f=F0;f<F1;f++){await p.evaluate(t=>renderAt(t),f/FPS);const buf=await p.screenshot({type:"jpeg",quality:93,timeout:180000});
 if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once("drain",r));if((f-F0)%300===0)console.log(out,f-F0,"/",F1-F0,((Date.now()-t0)/1000/(f-F0+1)).toFixed(2),"s/f");}
ff.stdin.end();await new Promise(r=>ff.on("close",r));await br.close();console.log("done",out);})();
