
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1436634.svg)](https://doi.org/10.5281/zenodo.1436634)
[![Licence](https://anaconda.org/openalea/openalea.phenomenal/badges/license.svg)](https://cecill.info/licences/Licence_CeCILL_V1.1-US.txt)
[![Platform](https://anaconda.org/openalea3/openalea.phenomenal/badges/platforms.svg)](https://anaconda.org/openalea3/openalea.phenomenal)
[![Last version](https://anaconda.org/openalea3/openalea.phenomenal/badges/version.svg)](https://anaconda.org/OpenAlea3/openalea.phenomenal/files)
[![GitHub CI](https://github.com/openalea/phenomenal/actions/workflows/conda-package-build.yml/badge.svg)](https://github.com/openalea/phenomenal/actions/workflows/conda-package-build.yml)
[![Documentation Status](https://readthedocs.org/projects/phenomenal/badge/?version=latest)](https://phenomenal.readthedocs.io/en/latest/?badge=latest)
[![Launch interactive phenomenal notebook with myBinder service](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/openalea/phenomenal/master?filepath=examples)


## Phenomenal: An automatic open source library for 3D shoot architecture reconstruction and analysis for image-based plant phenotyping

### Introduction

This work is based on our [biorxiv report](https://doi.org/10.1101/805739)

### Installation

Conda environment : https://docs.conda.io/en/latest/index.html

#### User

##### Create a new environment with phenomenal installed in there :

    mamba create -n phm -c conda-forge -c openalea3 openalea.phenomenal
    mamba activate phm

##### In a existing environment :

    mamba install -c conda-forge -c openalea3 openalea.phenomenal

##### (Optional) Test your installation :

    mamba install -c conda-forge pytest
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal/test; pytest

#### From source

    # Install dependency with conda
    mamba create -n phm -c conda-forge python
    mamba activate phm
    mamba install -c conda-forge cython numpy numba scipy scikit-image scikit-learn networkx opencv matplotlib vtk pytest skan

    # Load phenomenal and install
    git clone https://github.com/openalea/phenomenal.git
    cd phenomenal
    python setup.py develop

    # (Optional) Test your installation
    cd test; pytest


### Usage :

Complete documentation is available at https://phenomenal.readthedocs.io

Tutorials are available in the example folder as a Jupyter Notebook.

You can try online with binder: https://mybinder.org/v2/gh/openalea/phenomenal/master?filepath=examples


### Maintainers

* Artzet	    Simon
* Fournier	    Christian
* Pradal        Christophe

### License

Our code is released under **Cecill-C** (https://cecill.info/licences/Licence_CeCILL_V1.1-US.txt) licence. (see LICENSE file for details).

### Citation

If you find our work useful in your research, please consider citing:

    @article {Artzet805739,
        author = {Artzet, Simon and Chen, Tsu-Wei and Chopard, J{\'e}r{\^o}me and Brichet, Nicolas and Mielewczik, Michael and Cohen-Boulakia, Sarah and Cabrera-Bosquet, Lloren{\c c} and Tardieu, Fran{\c c}ois and Fournier, Christian and Pradal, Christophe},
        title = {Phenomenal: An automatic open source library for 3D shoot architecture reconstruction and analysis for image-based plant phenotyping},
        elocation-id = {805739},
        year = {2019},
        doi = {10.1101/805739},
        publisher = {Cold Spring Harbor Laboratory},
        abstract = {In the era of high-throughput visual plant phenotyping, it is crucial to design fully automated and flexible workflows able to derive quantitative traits from plant images. Over the last years, several software supports the extraction of architectural features of shoot systems. Yet currently no end-to-end systems are able to extract both 3D shoot topology and geometry of plants automatically from images on large datasets and a large range of species. In particular, these software essentially deal with dicotyledons, whose architecture is comparatively easier to analyze than monocotyledons. To tackle these challenges, we designed the Phenomenal software featured with: (i) a completely automatic workflow system including data import, reconstruction of 3D plant architecture for a range of species and quantitative measurements on the reconstructed plants; (ii) an open source library for the development and comparison of new algorithms to perform 3D shoot reconstruction and (iii) an integration framework to couple workflow outputs with existing models towards model-assisted phenotyping. Phenomenal analyzes a large variety of data sets and species from images of high-throughput phenotyping platform experiments to published data obtained in different conditions and provided in a different format. Phenomenal has been validated both on manual measurements and synthetic data simulated by 3D models. It has been also tested on other published datasets to reproduce a published semi-automatic reconstruction workflow in an automatic way. Phenomenal is available as an open-source software on a public repository.},
        URL = {https://www.biorxiv.org/content/early/2019/10/21/805739},
        eprint = {https://www.biorxiv.org/content/early/2019/10/21/805739.full.pdf},
        journal = {bioRxiv}
    }

If you use PhenoTrack3D in your research, cite:

Daviet, B., Fernandez, R., Cabrera-Bosquet, L. et al. PhenoTrack3D: an automatic high-throughput phenotyping pipeline to track maize organs over time. Plant Methods 18, 130 (2022). https://doi.org/10.1186/s13007-022-00961-4
    
```latex
@article {daviet22,
	title={PhenoTrack3D: an automatic high-throughput phenotyping pipeline to track maize organs over time},
	author={Daviet, Benoit and Fernandez, Romain and Cabrera-Bosquet, Lloren{\c{c}} and Pradal, Christophe and Fournier, Christian},
	journal={Plant Methods},
	volume={18},
	number={1},
	pages={1--14},
	year={2022},
	publisher={Springer}
}
```
