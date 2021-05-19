# 【PyTorch】AMP [Automatic Mixed Precision] を使用した学習と推論の高速化

## 単一の optimerzer で構成されるモデルの場合

- 学習スクリプトのコード例
    ```python
    ```

- 推論スクリプトのコード例
    ```python
    ```

ポイントは、以下の通り

- APM の初期化<br>
    ```python
    model_G, optimizer_G = amp.initialize(
        model_G, 
        optimizer_G, 
        opt_level = 'O1',
        num_losses = 1
    )
    ```

- スケーリングされた loss 値での誤差逆伝播法処理<br>
    FP16 にスケーリングされた loss 値で誤差逆伝播法処理を行う
    ```python
    # ネットワークの更新処理
    optimizer_G.zero_grad()
    with amp.scale_loss(loss_G, optimizer_G, loss_id=0) as loss_G_scaled:
        loss_G_scaled.backward()
    optimizer_G.step()
    ```

- 推論時にも AMP を適用する場合は、ダミーの optimizer を設定。
    ```python
    ```

## 複数の optimizer で構成されるモデルの場合
GAN のように複数モデル（生成器 + 識別器）と複数の optimizer（生成器の optimizer + 識別器の optimizer）が存在する場合は、

