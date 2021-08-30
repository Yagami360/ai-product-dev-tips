# 音声ファイルの無音部分を取り除く

## 方法１（`pydub` を使用する場合）

python モジュールの `pydub` にある `split_on_silence` で無音部分で音声ファイルを分割する

- 
```python
split_on_silence(sound, min_silence_len=2000, silence_thresh=-40, keep_silence=600)
```

## 方法２（）
