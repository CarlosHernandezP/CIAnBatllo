import gc
import math
import sys
from typing import List

import clip
import k_diffusion as K
import torch
from torch import nn
from torchvision import utils
from tqdm.notebook import trange, tqdm

import os
import platform
import argparse

"""
This script is for generating images based on a given text prompt.
It leverages a conditional denoiser along with CLIP for text-to-image translation.
"""

# Initialize global variables to set paths
current_path: str = os.path.dirname(os.path.abspath(__file__))
module_path: str = os.path.join(current_path, 'v-diffusion-pytorch')
sys.path.append(module_path)
# Crear el directorio si no existe
output_dir = 'static/images/'
os.makedirs(output_dir, exist_ok=True)
from diffusion import get_model  # noqa: E402


class CFGDenoiser(nn.Module):
    """
    A class for the Conditional denoiser.
    
    Attributes:
        inner_model (nn.Module): The model based on which denoising will be performed.
        cond_scale (float): The scale for the conditional model.
    """

    def __init__(self, model: nn.Module, cond_scale: float):
        """Initialize the conditional denoiser."""
        super().__init__()
        self.inner_model = model
        self.cond_scale = cond_scale

    def forward(self, x: torch.Tensor, sigma: torch.Tensor, clip_embed: torch.Tensor) -> torch.Tensor:
        """
        Perform the denoising operation based on the inner model.
        
        Parameters:
            x (torch.Tensor): The input tensor.
            sigma (torch.Tensor): The noise level for the model.
            clip_embed (torch.Tensor): The CLIP embeddings for the input.
        
        Returns:
            torch.Tensor: The denoised output tensor.
        """
        x_in = torch.cat([x] * 2)
        sigma_in = torch.cat([sigma] * 2)
        clip_embed_in = torch.cat([torch.zeros_like(clip_embed), clip_embed])
        uncond, cond = self.inner_model(x_in, sigma_in, clip_embed=clip_embed_in).chunk(2)
        return uncond + (cond - uncond) * self.cond_scale


def callback(info: dict):
    """
    Callback function to show progress during sampling.
    
    Parameters:
        info (dict): A dictionary containing metadata about the sampling process.
    """
    if info['i'] % 10 == 0:
        nrow = math.ceil(info['denoised'].shape[0] ** 0.5)
        grid = utils.make_grid(info['denoised'], nrow, padding=0)
        tqdm.write(f'Step {info["i"]} of 50, sigma {info["sigma"]:g}:')
        filename = os.path.join(output_dir, f'progress_step_{info["i"]}.png')
        K.utils.to_pil_image(grid).save(filename)


def generate_image(prompt: str, steps: int = 50, weight: float = 3.0, seed: int = 0) -> List[str]:
    """
    Generate images based on a given text prompt.
    
    Parameters:
        prompt (str): The text prompt based on which images will be generated.
        steps (int): The number of steps for the sampling process.
        weight (float): The weight for the conditioning.
        seed (int): The random seed for initialization.
        
    Returns:
        List[str]: The list of filenames where the generated images are saved.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    inner_model = get_model('cc12m_1_cfg')()
    inner_model.to(device)
    _, side_y, side_x = inner_model.shape
    #print working directory
    print("Current working directory: {0}".format(os.getcwd()))

    inner_model.load_state_dict(torch.load('../image_generation/v-diffusion-pytorch/checkpoints/cc12m_1_cfg.pth', map_location=device))
    inner_model = inner_model.eval().requires_grad_(False)
    model = K.external.VDenoiser(inner_model)
    clip_model = clip.load(inner_model.clip_model, jit=False, device=device)[0]

    target_embed = clip_model.encode_text(clip.tokenize(prompt)).float()

    gc.collect()
    torch.manual_seed(seed)


    sigmas = K.sampling.get_sigmas_karras(steps, 1e-2, 160, device=device)
    x = torch.randn([4, 3, side_y, side_x], device=device) * sigmas[0]

    model_wrap = CFGDenoiser(model, weight)
    extra_args = {'clip_embed': target_embed.repeat([4, 1])}
    outs = K.sampling.sample_lms(model_wrap, x, sigmas, extra_args=extra_args, callback=callback)
    tqdm.write('Done!')
    filenames = []

    for i, out in enumerate(outs):
        filename = os.path.join(output_dir, f'out_{i}.png')
        filenames.append(filename)
        K.utils.to_pil_image(out).save(filename)

    return filenames

if __name__ == '__main__':
    parser = argparse.ArgumentParser()


    parser.add_argument('--prompt', type=str, default='A painting of a cat riding a bike',
                        help='Text prompt')
    parser.add_argument('--weight', type=float, default=3,
                    help='Weight of the conditioning')
    parser.add_argument('--steps', type=int, default=50, help='Number of steps')
    parser.add_argument('--seed', type=int, default=0, help='Random seed')
    parser.add_argument('--n_images', type=int, default=4, help='Number of images to generate')
    args = parser.parse_args()

    generate_image(args.prompt, args.steps, args.weight, args.seed)

