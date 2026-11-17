// frame-accurate render of car_scene.html (WebGL via SwiftShader) -> build_car/video_silent.mp4
const {chromium}=require("playwright");const {spawn}=require("child_process");const path=require("path");
const FPS=30,DUR=30;
(async()=>{const b=await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on("pageerror",e=>console.log("ERR",e.message));
await p.goto("file://"+path.resolve("car_scene.html"));await p.waitForFunction(()=>window.sceneReady);await p.evaluate(()=>document.fonts.ready);
const ff=spawn("ffmpeg",["-y","-loglevel","error","-f","image2pipe","-framerate",String(FPS),"-c:v","mjpeg","-i","-","-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p","build_car/video_silent.mp4"],{stdio:["pipe","inherit","inherit"]});
for(let f=0;f<FPS*DUR;f++){await p.evaluate(t=>renderAt(t),f/FPS);const buf=await p.screenshot({type:"jpeg",quality:95});
  if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once("drain",r));if(f%150===0)console.log("frame",f);}
ff.stdin.end();await new Promise(r=>ff.on("close",r));await b.close();console.log("done");})();
