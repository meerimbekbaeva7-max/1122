#!/bin/bash
cd /home/user/1122/kids
node -e '
const {chromium}=require("playwright");const path=require("path");const {spawn}=require("child_process");
(async()=>{const b=await chromium.launch({args:["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"]});
const U="file://"+path.resolve("../sip_house/house.html");
let p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:2});
await p.goto(U+"?mode=hero");await p.waitForFunction(()=>window.ready,{timeout:60000});await p.screenshot({path:"../sip_house/sip_house_render_4k.png"});
await p.goto(U+"?mode=detail");await p.waitForFunction(()=>window.ready,{timeout:60000});await p.evaluate(()=>renderAt(3));await p.screenshot({path:"../sip_house/sip_panel_layers_4k.png"});
await p.close();p=await b.newPage({viewport:{width:1920,height:1080}});p.setDefaultTimeout(180000);
await p.goto(U+"?mode=build");await p.waitForFunction(()=>window.ready,{timeout:60000});
const ff=spawn("ffmpeg",["-y","-loglevel","error","-f","image2pipe","-framerate","30","-c:v","mjpeg","-i","-","-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart","../sip_house/sip_house_build.mp4"],{stdio:["pipe","inherit","inherit"]});
for(let f=0;f<450;f++){await p.evaluate(t=>renderAt(t),f/30);const buf=await p.screenshot({type:"jpeg",quality:93,timeout:180000});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once("drain",r));if(f%90===0)console.log("frame",f);}
ff.stdin.end();await new Promise(r=>ff.on("close",r));await b.close();console.log("done");})()'
