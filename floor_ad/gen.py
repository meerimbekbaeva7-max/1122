"""Photo-real illustrative stills for the liquid-floor ad (Realistic Vision 5.1 + LCM, CPU). usage: gen.py [ids...]"""
import sys, torch, time
from diffusers import StableDiffusionPipeline, LCMScheduler, AutoencoderKL
torch.set_num_threads(4)
pipe = StableDiffusionPipeline.from_pretrained("SG161222/Realistic_Vision_V5.1_noVAE", torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
pipe.vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float32)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5"); pipe.fuse_lora()
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
Q = ", professional photo, realistic, natural light, sharp focus, high detail"
P = {
 "1_old":    "old damaged cement floor with deep cracks and broken chipped tiles in an empty apartment room, dusty, worn" + Q,
 "2_water":  "ruined laminate flooring with planks lifted and buckled upward in a peak, swollen edges, water puddle on the floor, flood damage in apartment" + Q,
 "3_shine":  "modern living room with glossy seamless white epoxy self-leveling floor, mirror reflection, minimalist interior" + Q,
 "4_grind":  "close up of a heavy concrete floor grinder machine with a long handle grinding a concrete floor, cloud of dust, sparks, industrial renovation" + Q,
 "5_primer": "worker applying transparent primer on a clean concrete floor with a paint roller on a long handle, renovation" + Q,
 "6_pour":   "close up of hands tilting a large white bucket pouring thick liquid grey epoxy resin onto a concrete floor, resin stream and glossy puddle spreading" + Q,
 "7_roller": "close up of a metal spiked roller on a long handle rolling over fresh wet glossy grey epoxy floor, small air bubbles, renovation work" + Q,
 "8_result": "bright modern kitchen and hallway with glossy grey seamless epoxy floor reflecting light, clean new renovation" + Q,
 "9_3d":     "luxury bathroom with 3D epoxy floor showing realistic ocean waves and sand under glossy transparent resin" + Q,
}
NEG = "text, watermark, logo, people faces close up, deformed hands, cartoon, drawing, lowres, blurry, nsfw"
ids = sys.argv[1:] or list(P)
for k in ids:
    for seed in ((11,) if len(sys.argv) == 1 else (21, 31)):
        t0 = time.time(); g = torch.Generator().manual_seed(seed)
        im = pipe(P[k], negative_prompt=NEG, num_inference_steps=6, guidance_scale=1.5, width=512, height=896, generator=g).images[0]
        im.save(f"img/{k}_s{seed}.png"); print("saved", k, seed, round(time.time() - t0, 1), "s", flush=True)
