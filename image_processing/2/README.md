## 【Python】画像やセマンティックセグメンテーション画像の滑らかさを落とさないようにリサイズする。

- OpenCV や Pillow などの画像処理ライブラリを使って画像をリサイズするときに、補間アルゴリズムを指定しないままリサイズしてしまうと、画像の品質が低下してしまうので、出来るだけ品質の高い補間アルゴリズムで補間を行う必要がある。
- 一方、セマンティックセグメンテーションマスク画像に関しては、品質の高い補間アルゴリズムで補間すると、例えば 0 と 5 の間に 3 が現れたしてマスク画像の境界がぼやけてしまうので、最近傍法で補間する必要がある。

- OpenCV の場合：
    - 画像ファイルは `cv2.INTER_AREA` で補間すること。
        ```python
        import cv2
        img = cv2.imread("image/1.png")
        img = cv2.resize(img, dsize = (width,height), interpolation = cv.INTER_AREA) 
        ```
    - セグメンテーションマスク画像に関しては、`cv.INTER_NEAREST` で補間すること。
        ```python
        import cv2
        img_parse = cv2.imread("image/2.png")
        img_parse = cv2.resize(img_parse, dsize = (width,height), interpolation = cv.INTER_NEAREST) 
        ```
        
- Pillow の場合：
    - 画像ファイルは、`Image.LANCZOS` で補間すること。
        ```python
        from PIL import Image
        img = Image.open('image/1.png')
        img = img.resize((256, 256), Image.LANCZOS)
        ```
    - セグメンテーションマスク画像は、`Image.NEAREST` で補間すること。
        ```python
        from PIL import Image
        img_parse = Image.open("image/2.png")
        img_parse = img.resize((256, 256), Image.NEAREST)
        ```
