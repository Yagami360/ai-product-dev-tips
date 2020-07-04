# 【シェルスクリプト】conda 環境の自動的に作成する。

## 実現方法

### PyTorch 0.4
- 以下のスクリプトを実行（要 conda インストール済み）
    ```sh
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

    #options
    ```

### PyTorch 1.1
- 以下のスクリプトを実行（要 conda インストール済み）
    ```sh
    # PyTorch 1.1 + Python 3.6
    conda create -y -n pytorch11_py36 opencv tensorflow python=3.6 anaconda

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

    conda activate pytorch11_py36
    conda install -y pytorch=1.1.0 torchvision cuda90 -c pytorch && conda clean -ya

    # basic
    conda install -y pillow==6.2.1 && conda clean -ya
    conda install -y -c conda-forge tensorboardx && conda clean -ya
    conda install -y tqdm && conda clean -ya

    # options
    ```

## TensorFlow

## Keras

## Kaggle