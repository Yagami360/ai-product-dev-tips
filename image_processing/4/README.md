## 【Python】OpenCV ↔ Pillow ↔ numpy の変換対応

- OpenCV ↔ Pillow ↔ numpy の変換を行うときは、配列の shape や size の順番に注意すること。
    - OpenCV : ndarray.shape / [height, width, channels(3)]
        ```python
        import cv2

        img = cv2.imread('image/1.jpeg')
        print(type(img))
        # <class 'numpy.ndarray'>
        print(img.shape)
        # (225, 400, 3)
        ```
    - Pillow : image.size / [width, height]
        ```python
        from PIL import Image

        img = Image.open('image/1.jpeg')
        print(type(img))
        # <class 'PIL.JpegImagePlugin.JpegImageFile'>
        print(img.size)
        # (400, 225)
        ```

- OpenCV ↔ Pillow ↔ numpy の変換を行うときは、チャンネルの RGB値の順番に注意すること。
    - OpenCV : BGR
        - `cv2.cvtColor()` の引数 `cv2.COLOR_BGR2RGB` で BGRからRGBへ変換出来る
        - 別の方法としては、numpy の
    - Pillow : RGB


- Pillow → OpenCV へ変換は、`np.asarray()` で、一度 numpy に（参照コピーで）変換してから行う。この際に `cv2.cvtColor()` の引数 `cv2.COLOR_RGB2BGR` で色の順番を RGB → BGR にしておく必要がある。
    ```python
    import numpy as np
    from PIL import Image
    import cv2

    img_pillow = Image.open('image/1.jpeg')
    img_np = np.asarray(img_pillow)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    cv2.imwrite('image/1_cv2.png', img_cv)
    ```
    - `np.asarray()` : 参照 Copy
    - `np.array()` : Deep Copy

- OpenCV → Pillow への変換は、`cv2.cvtColor()` の引数 `cv2.COLOR_BGR2RGB` で色の順番を BGR → RGB にした後に、`Image.fromarray()` で numpy 型から Pillow オブジェクトを生成することで行える。
    ```python
    import numpy as np
    from PIL import Image
    import cv2

    img_cv = cv2.imread('image/1.jpeg')
    img_np = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pillow = Image.fromarray(img_np)
    img_pillow.save('image/1_pillow.png')
    ```
