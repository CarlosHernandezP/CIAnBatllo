from flask import render_template, Response, send_from_directory
import os
import gc
import math
import sys
from typing import List

import clip
import k_diffusion as K
import torch
from torch import nn
from torchvision import utils
from tqdm.notebook import tqdm

# Obtén la ruta del directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Combina la ruta del directorio padre con la carpeta "files"
folder_path = os.path.join(current_dir, '..', 'static')

# Crea el directorio de salida si no existe
output_dir = os.path.join('static', 'images')
os.makedirs(output_dir, exist_ok=True)

from diffusion import get_model  # noqa: E402

def image():
    return render_template('image.html')

def text_to_image(prompt, steps, weight, seed):
    image_path = generate_image(prompt, steps, weight, seed)
    return render_template('image_view.html', image_path=image_path)

def move_to_folder(filename):
    return send_from_directory(folder_path, filename)

class CFGDenoiser(nn.Module):
    """
    Clase para el eliminador de ruido condicional.

    Atributos:
        inner_model (nn.Module): El modelo en el cual se realizará la eliminación de ruido.
        cond_scale (float): La escala para el modelo condicional.
    """
    def __init__(self, model: nn.Module, cond_scale: float):
        """Inicializa el eliminador de ruido condicional."""
        super().__init__()
        self.inner_model = model
        self.cond_scale = cond_scale

    def forward(self, x: torch.Tensor, sigma: torch.Tensor, clip_embed: torch.Tensor) -> torch.Tensor:
        """
        Realiza la operación de eliminación de ruido basada en el modelo interno.

        Parámetros:
            x (torch.Tensor): El tensor de entrada.
            sigma (torch.Tensor): El nivel de ruido para el modelo.
            clip_embed (torch.Tensor): Los embeddings de CLIP para la entrada.

        Retorna:
            torch.Tensor: El tensor de salida sin ruido.
        """
        x_in = torch.cat([x] * 2)
        sigma_in = torch.cat([sigma] * 2)
        clip_embed_in = torch.cat([torch.zeros_like(clip_embed), clip_embed])
        uncond, cond = self.inner_model(x_in, sigma_in, clip_embed=clip_embed_in).chunk(2)
        return uncond + (cond - uncond) * self.cond_scale

def callback(info: dict):
    """
    Función de devolución de llamada para mostrar el progreso durante el muestreo.

    Parámetros:
        info (dict): Un diccionario que contiene metadatos sobre el proceso de muestreo.
    """
    if info['i'] % 10 == 0:
        nrow = math.ceil(info['denoised'].shape[0] ** 0.5)
        grid = utils.make_grid(info['denoised'], nrow, padding=0)
        tqdm.write(f'Step {info["i"]} of 50, sigma {info["sigma"]:g}:')
        filename = os.path.join(output_dir, f'progress_step_{info["i"]}.png')
        K.utils.to_pil_image(grid).save(filename)

def generate_image(prompt: str, steps: int = 50, weight: float = 3.0, seed: int = 0) -> List[str]:
    """
    Genera imágenes basadas en un texto dado como indicación.

    Parámetros:
        prompt (str): El texto de indicación en base al cual se generarán las imágenes.
        pasos (int): El número de pasos para el proceso de muestreo.
        peso (float): El peso para la condición.
        semilla (int): La semilla aleatoria para la inicialización.

    Retorna:
        List[str]: La lista de nombres de archivo donde se guardan las imágenes generadas.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    inner_model = get_model('cc12m_1_cfg')()
    inner_model.to(device)
    _, side_y, side_x = inner_model.shape
    model_path = os.path.join('models', 'v-diffusion-pytorch', 'checkpoints', 'cc12m_1_cfg.pth')
    inner_model.load_state_dict(torch.load(model_path, map_location=device))
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
