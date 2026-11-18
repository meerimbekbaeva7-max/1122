"""Photo-real backlit couple for the bot menu (Realistic Vision v5.1 + LCM-LoRA, CPU). usage: gen.py <seed> [n]"""
import sys, torch, time
from diffusers import StableDiffusionPipeline, LCMScheduler
torch.set_num_threads(4)
pipe = StableDiffusionPipeline.from_pretrained("SG161222/Realistic_Vision_V5.1_noVAE", torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
from diffusers import AutoencoderKL
pipe.vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float32)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5"); pipe.fuse_lora()
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
prompt = ("cinematic studio photo, side profile silhouettes of a man and a woman facing each other, faces close, almost kissing, "
          "both fully clothed, strong pink and red neon backlight between them, rim light on their profiles, dark red background, smoke haze, "
          "fashion editorial, 85mm lens, shallow depth of field, high detail, film grain")
neg = "nudity, nsfw, cleavage, text, watermark, logo, deformed, extra limbs, cartoon, drawing, lowres, blurry face"
seed = int(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
for k in range(n):
    t0 = time.time(); g = torch.Generator().manual_seed(seed + k)
    im = pipe(prompt, negative_prompt=neg, num_inference_steps=6, guidance_scale=1.5, width=640, height=640, generator=g).images[0]
    im.save(f"couple_{seed+k}.png"); print("saved", seed + k, round(time.time() - t0, 1), "s", flush=True)
