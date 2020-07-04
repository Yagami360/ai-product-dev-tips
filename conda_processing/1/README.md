# 【シェルスクリプト】シェルスクリプト内で conda 環境を切り替える。
シェルスクリプト内で、conda 環境を activate して、python スクリプトを実行すようにしておけば、毎回手動で `conda activate` しなくて済むので便利。但し、シェルスクリプト内で単純に `conda activate` すると、以下のエラーが出る。

```sh
CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'.
To initialize your shell, run
```

これは、以下の「実現方法」項記載の方法で回避出来る

## 実現方法

- `conda activate ${conda環境名}` の前に、以下のスクリプトを挿入
    ```sh
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

    # シェルスクリプト内で conda activate 出来るようになる
    conda activate ${conda環境名}
    # or source activate ${conda環境名}

    # 毎回手動で conda activate しなくくて済む
    python ${PYTHONスクリプト}
    ```

## 参照サイト
- https://qiita.com/tori_taro/items/ad3a4f488a49400fd457