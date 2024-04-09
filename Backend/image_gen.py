import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

class ImageGenerator:
    def __init__(self):
        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        ckpt = "sdxl_lightning_4step_unet.safetensors"

        # Load model.
        self.unet = UNet2DConditionModel.from_config(base, subfolder="unet").to("cuda", torch.float16)
        self.unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))
        self.pipe = StableDiffusionXLPipeline.from_pretrained(base, unet=self.unet, torch_dtype=torch.float16, variant="fp16").to("cuda")

        # Ensure sampler uses "trailing" timesteps.
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(self.pipe.scheduler.config, timestep_spacing="trailing")

    def generate(self, text, num_inference_steps=4, guidance_scale=0):
        # Ensure using the same inference steps as the loaded model and CFG set to 0.
        return self.pipe(text, num_inference_steps=num_inference_steps, guidance_scale=guidance_scale).images[0]