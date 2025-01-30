import torch
from torch import Tensor
import yaml
import json
import sys
import os
import torch
from tqdm import tqdm

import deepali.spatial as spatial
from deepali.spatial import DisplacementFieldTransform
from deepali.modules import TransformImage
from deepali.losses import functional as L
from deepali.data import FlowField, Image
from deepali.core import Axes, Grid

from data_utils import load_and_preprocess, save_sitk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from deepali.examples.ffd.pairwise import register_pairwise

def load_config(config_path):
    r"""Load registration parameters from configuration file."""
    config_text = config_path.read_text()
    if config_path.suffix == ".json":
        return json.loads(config_text)
    return yaml.safe_load(config_text)

def register_deformable(target_path, source_path, config, device, source_seg, target_seg, save=None, verbose=1):

    transform = register_pairwise(
        target={"img": target_path, "seg":target_seg},
        source={"img": source_path, "seg":source_seg},
        config=config,
        outdir=None,
        device=device,
        verbose=verbose,
    )

    # transform image
    target_grid = Grid.from_file(target_path)
    source_image = Image.read(source_path, device=device)
    warp_image = TransformImage(
        target=target_grid,
        source=source_image.grid(),
        sampling='linear',
        padding=source_image.min(),
    ).to(device)

    warped_deformable: Tensor = warp_image(transform[0].tensor(), source_image)
    warped = warped_deformable.detach().cpu().squeeze()
    if source_seg:
        warp_label = TransformImage(
            target=target_grid,
            source=source_image.grid(),
            sampling='nearest',
            padding=source_image.min(),
        ).to(device)
        source_seg_data = Image.read(source_seg, device=device)
        warped_seg: Tensor = warp_label(transform[0].tensor(), source_seg_data)
        warped_seg = warped_seg.detach().cpu().squeeze()
    if save:
        save_path, sitk_arr = save
        transform[0].flow()[0].write(save_path.joinpath('D_trf.nii.gz'))
        save_sitk(save_path.joinpath('D_wat.nii.gz'), warped, sitk_arr)
        save_sitk(save_path.joinpath('D_label.nii.gz'), warped_seg, sitk_arr)
    return warped_deformable, warped_seg, transform

def register_affine(ref, source_path, source_seg, target_grid, iterations=200, lr=0.01, save=None, device='cuda'):
    
    #load images
    mov, _ = load_and_preprocess(path=source_path)    
    mov_label, _ = load_and_preprocess(path=source_seg, pp=False)
    
    transform = spatial.AffineTransform(target_grid)
    optimizer = torch.optim.Adam(transform.parameters(), lr=lr)
    loss = L.mse_loss
    transformer = spatial.ImageTransformer(transform).to(device)
    pbar = tqdm(range(iterations))
    loss_list = []
    for _ in pbar:
        warped_batch = transformer(Image(mov.unsqueeze(0), grid=target_grid, device=device))
        l = loss(warped_batch, ref.unsqueeze(0).to('cuda')) 
        loss_list.append(l.item())
        optimizer.zero_grad()
        l.backward()
        optimizer.step()
    
    warp_image = TransformImage(
        target=target_grid,
        source=target_grid,
        sampling="linear",
        padding=0,
    ).to(device)

    warp_label = TransformImage(
        target=target_grid,
        source=target_grid,
        sampling="nearest",
        padding=0,
    ).to(device)
    
    with torch.inference_mode():
        warped = warp_image(transform.tensor(), mov.unsqueeze(0).to('cuda'))
        warped_label = warp_label(transform.tensor(), torch.Tensor(mov_label).unsqueeze(0).to('cuda'))
    
    if save:
        save_path, sitk_arr = save
        save_sitk(save_path.joinpath('A_wat.nii.gz'), warped.squeeze().detach().cpu().numpy(), sitk_arr)
        save_sitk(save_path.joinpath('A_label.nii.gz'), warped_label.squeeze().detach().cpu().numpy(), sitk_arr)
    return loss_list, transform, warped, warped_label

def load_transform(path: str, target_grid: Grid) -> DisplacementFieldTransform:
    flow = FlowField.read(path, axes=Axes.WORLD)
    flow = flow.axes(Axes.from_grid(target_grid))
    flow = flow.sample(target_grid)
    return DisplacementFieldTransform(target_grid, params=flow.tensor().unsqueeze(0))