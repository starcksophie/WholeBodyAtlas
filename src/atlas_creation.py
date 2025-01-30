import os
import argparse
import random
import torch
from tqdm import tqdm
from pathlib import Path
from typing import List
import deepali.spatial as spatial
from deepali.data import Image
import sys
# from reg_utils import load_transform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from deepali.examples.ffd.pairwise import register_pairwise, load_transform
from data_utils import load_and_preprocess, save_sitk

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path to the directory containing the images')
    parser.add_argument('--discard_list', default=[], type=List, help='list of subject to discard')
    parser.add_argument('--path_out', type=str, help='Path to the directory to save the results')
    
    args = parser.parse_args()
    
    base_dir = Path(args.path)
    save_dir = Path(args.path_out)
   
    eids = sorted(os.listdir(base_dir))
    
    l = random.randint(0, len(eids))
    random_path = base_dir.joinpath(eids[l], 'D_wat.nii.gz')
    # load the grid and metadata of the first image as an example
    target_grid = Image.read(random_path).grid()
    _, sitk_arr = load_and_preprocess(random_path)

    naive_atlas = torch.empty(1, *target_grid.shape)
    avg_transform = torch.empty(1, 3, *target_grid.shape)
    
    i = 0
    for subject_dir in tqdm(base_dir.iterdir()):
        image = Image.read(subject_dir.joinpath('D_wat.nii.gz'))
        transform = load_transform(subject_dir.joinpath('D_trf.nii.gz'), target_grid)

        naive_atlas += image
        avg_transform += transform.data()
        i+=1
        
    naive_atlas /=i
    avg_transform/=i

    avg_transform = spatial.DisplacementFieldTransform(image.grid(), params=-avg_transform)
    unbiaser= spatial.ImageTransformer(avg_transform, sampling='linear')
    
    unbiased_vat = unbiaser(naive_atlas)
    save_sitk(save_dir.joinpath('final_atlas.nii.gz'), unbiased_vat.squeeze().numpy(), sitk_arr)
    save_sitk(save_dir.joinpath('initial_atlas.nii.gz'), naive_atlas.squeeze().numpy(), sitk_arr)