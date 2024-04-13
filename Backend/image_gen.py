# image_gen.py
# This program uses the Stable Diffusion XL model to generate images from text prompts.
#
# Nithun Selva, Clio Zhu
# CS431 Spring 2024

import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

class ImageGenerator:
    def __init__(self):
        """
        Initializes the ImageGenerator class which loads and configures the 
        components necessary for generating images using the Stable Diffusion XL 
        model.
        """
        # Define the base repository and checkpoint for the model
        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        ckpt = "sdxl_lightning_4step_unet.safetensors"

        # Load model
        self.unet = UNet2DConditionModel.from_config(base, subfolder="unet"
                                                     ).to("cuda", torch.float16)
        self.unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))

        # Initialize the Stable Diffusion XL pipeline with the model
        self.pipe = StableDiffusionXLPipeline.from_pretrained(base, 
                                                              unet=self.unet, 
                                                              torch_dtype=torch.float16, 
                                                              variant="fp16").to("cuda")

        # Ensure sampler uses "trailing" timesteps
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(self.pipe.scheduler.config, 
                                                                 timestep_spacing="trailing")

    def generate(self, text, num_inference_steps=4, guidance_scale=0):
        """
        Generates an image from the provided text prompt using the configured 
        Stable Diffusion XL model.
        
        Args:
            text (str): The prompt based on which the image will be generated.
            num_inference_steps (int, optional): The number of diffusion steps.
                Defaults to 4.
            guidance_scale (float, optional): The classifier free guidance scale. 
                Setting this to 0 disables guidance. Defaults to 0.
        
        Returns:
            PIL.Image: The generated image.
        """
        # Ensure using the same inference steps as the loaded model and CFG set to 0
        return self.pipe(text, 
                         num_inference_steps=num_inference_steps, 
                         guidance_scale=guidance_scale).images[0]
    