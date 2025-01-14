from pathlib import Path
from deepali.data import Image
from reg_utils import register_affine, register_deformable
from data_utils import load_config, load_and_preprocess
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_data', type=str, default='/vol/aimspace/projects/ukbb/data/whole_body/nifti/', help='Path to the dataset')
    parser.add_argument('--path_labels', type=str, default='/vol/aimspace/projects/ukbb/data/whole_body/total_segmentator', help='Path to the dataset labels')

    args = parser.parse_args()
    
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parents[1]
    PATH_CONFIG = project_root / "cfg" / "deformable_config.yaml"
    PATH_DATA = Path(args.path_data)
    PATH_SEG = Path(args.path_labels)

    base_path = Path.cwd().joinpath('temp')
    base_path.mkdir(parents=True, exist_ok=True)

    ref_eid = '1197096'

    fixed_path = base_path.joinpath('ref_pp.nii.gz')
    ref, sitk_arr = load_and_preprocess(path=PATH_DATA.joinpath(ref_eid, 'wat.nii.gz'), save_path=fixed_path,)
    fixed_seg_path = PATH_SEG.joinpath(ref_eid, f'{ref_eid}_total_seg.nii.gz')

    target_grid = Image.read(fixed_path).grid()

    moving_eids = [3876123, 1028117, 1510595, 1041727, 1395210, 1657033]

    config = load_config(PATH_CONFIG)
    device='cuda'

    for mov_eid in moving_eids:
        # create working directory
        cur_path = base_path.joinpath(str(mov_eid))
        cur_path.mkdir(parents=True, exist_ok=True)

        # affine reg
        _, transform, warped, warped_label = register_affine(ref,
                                                            source_path=PATH_DATA.joinpath(str(mov_eid), 'wat.nii.gz'),
                                                            source_seg=PATH_SEG.joinpath(str(mov_eid), f'{str(mov_eid)}_total_seg.nii.gz'),
                                                            target_grid=target_grid,
                                                            iterations=200,
                                                            save = (cur_path, sitk_arr),
                                                            device=device)

        # deformable reg
        warped, warped_seg, deformable_trf = register_deformable(target_path=fixed_path,
                                                                source_path=cur_path.joinpath('A_wat.nii.gz'),
                                                                config=config,
                                                                device='cuda',
                                                                source_seg=cur_path.joinpath('A_label.nii.gz'),
                                                                target_seg=fixed_seg_path,
                                                                save = (cur_path, sitk_arr),
                                                                verbose=1)