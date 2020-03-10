# 【Docker】docker exec を nohup で実行する。

`docker exec` を nohup で実行しようとすると、「the input device is not a TTY」のエラーが出て実行できない。この場合、`-it` オプションを指定せずに実行すればよい。

※ TTY : 疑似ターミナル (pseudo-TTY) 。nohup では疑似ターミナルを割り当てないので、このエラーが出る

```sh
# 「the input device is not a TTY」のエラー発生
$ nohup docker exec -it ${CONTAINER_NAME} /bin/bash
```

```sh
# -it オプションをなくす
$ nohup docker exec ${CONTAINER_NAME} /bin/bash
```
