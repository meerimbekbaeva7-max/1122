"""Photo-real 2-storey wooden cottage concepts (Realistic Vision 5.1 + LCM, CPU). usage: gen.py [ids...]"""
import sys, torch, time
from diffusers import StableDiffusionPipeline, LCMScheduler, AutoencoderKL
torch.set_num_threads(4)
pipe = StableDiffusionPipeline.from_pretrained("SG161222/Realistic_Vision_V5.1_noVAE", torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
pipe.vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float32)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5"); pipe.fuse_lora()
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
Q = ", exterior architectural photography, wide angle, full house in frame, green lawn, blue sky, golden hour sunlight, realistic, sharp focus, high detail, 8k"
P = {
 "1_chalet":  "modern two-storey cottage house, facade fully clad with warm golden natural light pine wood horizontal planks, light wooden walls, grey metal gable roof, large panoramic windows, wooden balcony on second floor, paved stone driveway leading to the front entrance" + Q,
 "2_scandi":  "scandinavian two-storey house, facade of vertical natural honey orange cedar wood boards, warm wooden walls, steep dark grey gable roof, big windows, covered porch with wooden steps, gravel driveway with a car parked in front" + Q,
 "3_classic": "classic two-storey wooden cottage, dark walnut brown timber log siding facade, brown roof, white window frames, wooden balcony on the second floor, red brick paved driveway to the entrance" + Q,
 "4_modern":  "modern two-storey house with flat roof, facade of warm teak brown wooden slats, natural wood texture walls, white plaster accents, floor to ceiling glass, wooden garage door, wide concrete driveway" + Q,
}
NEG = "black facade, black walls, dark painted house, black house, grey walls, text, watermark, logo, people, cartoon, drawing, 3d render, lowres, blurry, distorted, cropped house, ruined, construction site, nsfw"
ids = sys.argv[1:] or list(P)
SEEDS = (3, 11, 27)
for k in ids:
    for seed in (SEEDS):
        t0 = time.time(); g = torch.Generator().manual_seed(seed)
        im = pipe(P[k], negative_prompt=NEG, num_inference_steps=6, guidance_scale=2.0, width=768, height=512, generator=g).images[0]
        im.save(f"img/{k}_s{seed}.png"); print("saved", k, seed, round(time.time() - t0, 1), "s", flush=True)
