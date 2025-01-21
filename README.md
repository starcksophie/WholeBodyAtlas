# Whole Body MRI Atlas Generation

## Overview

This repository contains the code used to generate population-specific whole-body MRI atlases, as described in the paper **"Using UK Biobank Data to Establish Population-Specific Atlases from Whole Body MRI."**

Reliable reference data in medical imaging is largely unavailable. Our work addresses this gap by providing a pipeline to create anatomical and probabilistic atlases from highly heterogeneous whole-body MRI data. This pipeline partitions the population into meaningful subgroups, generates unbiased anatomical atlases, and constructs probabilistic atlases capturing fat and organ distribution variations across the population.

## Data

The code uses magnetic resonance imaging (MRI) data from the UK Biobank dataset. Due to data sharing agreements, the original UK Biobank data cannot be redistributed. However, the generated atlases can be downloaded [here](https://doi.org/10.5281/zenodo.13136891).

## Requirements

- Python 3.11.3
- Install required packages using the `requirements.txt` file:
  ```bash
  pip install -r requirements.txt
  ```

## Citation
```
  @article{starck2024using,
  title={Using UK Biobank data to establish population-specific atlases from whole body MRI},
  author={Starck, Sophie and Sideri-Lampretsa, Vasiliki and Ritter, Jessica JM and Zimmer, Veronika A and Braren, Rickmer and Mueller, Tamara T and Rueckert, Daniel},
  journal={Communications Medicine},
  volume={4},
  number={1},
  pages={237},
  year={2024},
  publisher={Nature Publishing Group UK London}
}
```

## Contact

For any questions you can contact Sophie Starck (sophie.starck@tum.de) or Vasiliki Sideri-Lampretsa (vasiliki.sideri-lampretsa@tum.de).
