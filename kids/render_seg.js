// usage: node render_seg.js <page-with-query> <out.mp4> <duration> [fps]
const {chromium}=require("playwright");const {spawn}=require("child_process");const path=require("path");
const [page,out,dur,fpsArg]=process.argv.slice(2);const FPS=+(fpsArg||30),DUR=+dur;
(async()=>{const b=await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]});
const p=await b.newPage({viewport:{width:1920,height:1080}});p.on("pageerror",e=>console.log("ERR",e.message));
const [file,q]=page.split("?");await p.goto("file://"+path.resolve(file)+(q?"?"+q:""));await p.waitForFunction(()=>window.sceneReady,{timeout:60000});await p.evaluate(()=>document.fonts.ready);
const ff=spawn("ffmpeg",["-y","-loglevel","error","-f","image2pipe","-framerate",String(FPS),"-c:v","mjpeg","-i","-","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-r",String(FPS),out],{stdio:["pipe","inherit","inherit"]});
const N=Math.round(FPS*DUR),t0=Date.now();
for(let f=0;f<N;f++){await p.evaluate(t=>renderAt(t),f/FPS);const buf=await p.screenshot({type:"jpeg",quality:93});
  if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once("drain",r));if(f%300===0)console.log(out,f,"/",N,((Date.now()-t0)/1000/(f+1)).toFixed(2),"s/f");}
ff.stdin.end();await new Promise(r=>ff.on("close",r));await b.close();console.log("done",out);})();
