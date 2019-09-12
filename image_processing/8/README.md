# 【Python】画像の上下 or 左右対称性を検出する。

- 画像の対称性を検出するには、以下の手順で検出出来る。
    1. 対象画像のバイナリマスク画像（0 or 1）`original_mask` を生成する。
    1. バイナリマスク画像の（上下 or 左右）反転画像 `flipped_mask` を生成する。
    1. バイナリマスク画像 `original_mask` とその反転画像 `flipped_mask` に対して、`==` 演算子で比較したもの sum を取り、画像の高さ H と 幅 Wで正規化し、シンメトリー値 `symmetry_rate` とする。<br> 
        `symmetry_rate = ( sum(sum(original_mask == flipped_mask) ) )/ H / W`
    1. このシンメトリー値は、1.0 に近いほど画像の対称性が高いことを示しているので、あるスレッショルド値の以上 or 以下で、画像の対称 or 非対称を検出することが出来る。

    ```python
    parser = argparse.ArgumentParser()
    parser.add_argument('--symmetry_rate_threshold', type=float, default=0.915 )
    args = parser.parse_args()

    # バイナリマスクの生成
    original_mask = create_binary_mask(original_img)

    # 1 : y軸を中心に反転（=左右反転）
    flipped_mask = cv2.flip(original_mask, 1)

    # バイナリマスク値 (0 or 1) なので、0 or 1 のサムで対称性を計算可能（1.0に近いほど対称性が高い）
    symmetry_rate = ( sum(sum(original_mask == flipped_mask) ) )/ H / W

    # ある閾値以上 or 以下判定で、画像の対称 or 非対称を判定
    if( symmetry_rate >= args.symmetry_rate_threshold ):
        print("対称画像 : symmetry_rate={}".format(symmetry_rate) )
    else:
        print("非対称画像 : symmetry_rate={}".format(symmetry_rate) )
    ```

- 或いはマスク画像にしなくても、以下の手順でも検出出来る。
    1. 元の画像 `original_img` の反転画像 `flipped_img` に対して、`==` 演算子で比較したもの sum を取り、画像の高さ H と 幅 W、及びチャンネル数 C で正規化し、シンメトリー値 `symmetry_rate` とする。<br> 
        `symmetry_rate = sum(sum(sum(original_img == flipped_img)))/ H / W / C`
    1. このシンメトリー値は、1.0 に近いほど画像の対称性が高いことを示しているので、あるスレッショルド値の以上 or 以下で、画像の対称 or 非対称を検出することが出来る。