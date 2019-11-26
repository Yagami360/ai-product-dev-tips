# 【Python】 OpenPose の関節点情報に基づき、人物画像が正面を向いているか後ろを向いているか判定する。

## 機械学習の文脈での用途

- 背面を向いている人物画像が、考えれいる機械学習モデルの出力に悪影響を及ぼすので、データから背面画像をクレンジングしたい場合など。

## 実現方法

- OpenPose での肩 or お尻 or 膝の関節点座標の x 座標（横軸方向）が反転しているかで判定する。
    - 具体的には肩の場合、正面を向いている場合は 「右肩の x 座標 > 左肩の x 座標」、背面を向いている場合は 「右肩の x 座標 < 左肩の x 座標」の関係が成り立つので、この反転関係から判定できる。
- 別の基準として、鼻座標が取れていない「鼻座標値 (0.0, 0.0) 」からからも一部判定可能。

## 入出力データ

- 判定結果 OK（肩）<br>
    ![1FI22O00J-A11@11](https://user-images.githubusercontent.com/25688193/69626569-3e01e980-108c-11ea-8209-6e687e42c78b.png)<br>
    ![1FI22O00N-L11@8](https://user-images.githubusercontent.com/25688193/69626570-3e9a8000-108c-11ea-9373-2550d54caddb.png)<br>
    ![1FI22O00N-Q11@11](https://user-images.githubusercontent.com/25688193/69626571-3e9a8000-108c-11ea-996e-7db279345523.png)<br>


- 判定結果 NG（肩）<br>
    ![1FI22O00A-A11@9](https://user-images.githubusercontent.com/25688193/69626578-41957080-108c-11ea-9699-4aa28ced7843.png)<br>
    ![1FI22O00J-Q11@12](https://user-images.githubusercontent.com/25688193/69626580-41957080-108c-11ea-88c2-720c10d2685c.png)<br>
