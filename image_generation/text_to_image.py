import gc
import math
import sys

import clip
from IPython import display
import k_diffusion as K
import torch
from torch import nn
from torchvision import utils
from torchvision.transforms import functional as TF
from tqdm.notebook import trange, tqdm

sys.path.append('/v-diffusion-pytorch')

import ipdb; ipdb.set_trace()
from diffusion import get_model

import argparse


# Load the models



class CFGDenoiser(nn.Module):
    def __init__(self, model, cond_scale):
        super().__init__()
        self.inner_model = model
        self.cond_scale = cond_scale

    def forward(self, x, sigma, clip_embed):
        x_in = torch.cat([x] * 2)
        sigma_in = torch.cat([sigma] * 2)
        clip_embed_in = torch.cat([torch.zeros_like(clip_embed), clip_embed])
        uncond, cond = self.inner_model(x_in, sigma_in, clip_embed=clip_embed_in).chunk(2)
        return uncond + (cond - uncond) * self.cond_scale


def callback(info):
    if info['i'] %  10 == 0:
        nrow = math.ceil(info['denoised'].shape[0] ** 0.5)
        grid = utils.make_grid(info['denoised'], nrow, padding=0)
        tqdm.write(f'Step {info["i"]} of 50 ,lie, sigma {info["sigma"]:g}:')
        display.display(K.utils.to_pil_image(grid))
        tqdm.write(f'')

def run( weight: int = 3, steps: int = 50,
        seed: int = 0,  n_images: int = 4):

    gc.collect()
    torch.cuda.empty_cache()
    torch.manual_seed(seed)
    sigmas = K.sampling.get_sigmas_karras(steps, 1e-2, 160, device='cuda')
    x = torch.randn([n_images, 3, side_y, side_x], device='cuda') * sigmas[0]
    model_wrap = CFGDenoiser(torch.cuda.amp.autocast()(model), weight)
    extra_args = {'clip_embed': target_embed.repeat([n_images, 1])}
    outs = K.sampling.sample_lms(model_wrap, x, sigmas, extra_args=extra_args, callback=callback)
    tqdm.write('Done!')
    for i, out in enumerate(outs):
        filename = f'out_{i}.png'
        K.utils.to_pil_image(out).save(filename)
        display.display(display.Image(filename))

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



    inner_model = get_model('cc12m_1_cfg')()
    _, side_y, side_x = inner_model.shape
    inner_model.load_state_dict(torch.load('v-diffusion-pytorch/checkpoints/cc12m_1_cfg.pth', map_location='cpu'))
    inner_model = inner_model.half().cuda().eval().requires_grad_(False)
    model = K.external.VDenoiser(inner_model)
    clip_model = clip.load(inner_model.clip_model, jit=False, device='cpu')[0]

    prompt = args.prompt
    target_embed = clip_model.encode_text(clip.tokenize(prompt)).float().cuda()

    run(args.weight, args.steps, args.seed, args.n_images)
        



