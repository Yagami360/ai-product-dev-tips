# 【PyTorch】データローダーでの前処理を GPU 動作させて高速化する（PyTorch 1.7, torchvison 0.8 以降）

Pytorch でのデータローダーにおいて、`transforms.RandomAffine()` などでの前処理や DA 処理は、実装が手軽ではあるものの、Pillow オブジェクトに対して CPU で実行されるために、処理が重いという欠点があった。<br>
PyTorch 1.7 以降に組み込まれている torchvison 0.8 以降では、

- CPU で前処理を行うデータローダーのコード例（torchvison 0.8 以前）
    ```python
    ```

- GPU で前処理を行うコード例（torchvison 0.8 以降）
    ```python
    ```

ポイントは、以下の通り

- `torchvision.io.read_image()` を用いて、画像ファイルを直接 Tensor に変換<br>
    torchvison 0.8 以前のデータローダーで画像ファイルを読み込んで Tensor に変換する場合は、Pillow の `Image.open()` か OpenCV の `cv2.imread()` を用いて画像を読み込み、その後 Tensor に変換する方法が一般的であり、処理効率が悪いという問題があった。
    torchvison 0.8 以降では、`torchvision.io.read_image()` を用いて、画像ファイルを直接 Tensor に変換することが可能になっており、直接 Tensor に変換することで処理速度が向上している。

- `nn.Sequential()` で Transform を構成
    torchvison 0.8 以前のデータローダーでは、`transforms.Compose()` を用いて、



## 参考サイト
- https://buildersbox.corp-sansan.com/entry/2020/11/05/110000