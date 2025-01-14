import torch
import yaml
import json
import torch
from pathlib import Path
import SimpleITK as sitk

def np2sitk(np_image, sitk_img):
    """
    This function takes a numpy array and casts it to a SimpleItk image.

    Args:
        np_image (np.array): numpy image to convert.
        sitk_img (sitk.Image): sitk Image containing params.

    Returns:
        sitk.Image: Corresponding sitk.Image
    """
    new_sitk_img = sitk.GetImageFromArray(np_image)
    new_sitk_img.SetOrigin(sitk_img.GetOrigin())
    new_sitk_img.SetSpacing(sitk_img.GetSpacing())
    new_sitk_img.SetDirection(sitk_img.GetDirection())
    return new_sitk_img

def load_sitk(path):
    """
    Loads sitk.Image from disk.

    Args:
        path (str): path to the image.

    Returns:
        sitk.Image, np.array: tuple image
    """
    im = sitk.ReadImage(path)
    return im, sitk.GetArrayFromImage(im)


def save_sitk(outpath, arr, sitk_arr):
    """
    Save image to disk.

    Args:
        outpath (str): path to file.
        arr (np.array): image array to save.
        sitk_arr (sitk.Image): sitk Image object corresponding.
    """
    sitk_im = np2sitk(arr, sitk_arr)
    sitk.WriteImage(sitk_im, outpath)

def load_config(path):
    r"""Load registration parameters from configuration file."""
    config_path = Path(path).absolute()
    config_text = config_path.read_text()
    if config_path.suffix == ".json":
        return json.loads(config_text)
    return yaml.safe_load(config_text)

def normalise(im):
    return (im-im.min())/(im.max()-im.min())

def load_and_preprocess(path, pp=True, save_path=None):
    sitk_arr = sitk.ReadImage(path)
    im = sitk.DICOMOrient(sitk_arr, 'LPS')
    im = sitk.GetArrayFromImage(im)
    # preprocess
    if pp:
        im = normalise(im)
        min_in = 0
        im = torch.clip(torch.Tensor(im), min=min_in, max=0.6)
        im = normalise(im)
    if save_path:
        save_sitk(save_path, im.numpy(), sitk_arr)
    return im, sitk_arr