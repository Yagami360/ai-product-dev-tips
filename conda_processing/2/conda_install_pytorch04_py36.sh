#!/bin/sh
set -eu

# PyTorch 0.4 + Python 3.6
conda create -y -n pytorch04_py36 opencv tensorflow python=3.6 anaconda

# ~~~~~~~~~~~~
# >>> conda init >>>
__conda_setup="$(CONDA_REPORT_ERRORS=false '$HOME/anaconda3/bin/conda' shell.bash hook 2> /dev/null)"
if [ $? -eq 0 ]; then
    \eval "$__conda_setup"
else
    if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        . "$HOME/anaconda3/etc/profile.d/conda.sh"
        CONDA_CHANGEPS1=false conda activate base
    else
        \export PATH="$PATH:$HOME/anaconda3/bin"
    fi
fi
unset __conda_setup
# <<< conda init <<<

conda activate pytorch04_py36
conda install -y pytorch=0.4.1 torchvision cuda90 -c pytorch && conda clean -ya

# basic
conda install -y pillow==6.2.1 && conda clean -ya
conda install -y -c conda-forge tensorboardx && conda clean -ya
conda install -y tqdm && conda clean -ya

# options
conda install -y -c anaconda scipy && conda clean -ya
conda install -y -c conda-forge imageio && conda clean -ya
conda install -y -c anaconda seaborn && conda clean -ya
conda install -y -c conda-forge nvidia-apex && conda clean -ya
conda install -y -c conda-forge kaggle && conda clean -ya
conda install -y -c anaconda flask && conda clean -ya
conda install -y -c anaconda flask-cors && conda clean -ya
conda install -y -c anaconda requests && conda clean -ya
conda install -y -c anaconda networkx && conda clean -ya
conda install -y -c conda-forge dominate && conda clean -ya
conda install -y -c conda-forge visdom && conda clean -ya
conda install -y -c conda-forge pycocotools && conda clean -ya
conda install -y -c conda-forge ipdb && conda clean -ya