# 【Docker】dockerfile の WORKDIR 変更前のデフォルトパス
dockerfile において、`WORKDIR` コマンドで作業ディレクトリを変える前のディレクトリは、ルートディレクトリ `/` である。
従って、Ubuntu 環境の場合は、ユーザーは root ユーザーで、sudo 権限をもつユーザーになっている。

```sh
ubuntu@64e190d002b8:/$ ls -l
drwxr-xr-x   1 root   root   4096 Mar  4 07:00 bin
drwxr-xr-x   2 root   root   4096 Apr 12  2016 boot
drwxr-xr-x   5 root   root    360 Mar 13 07:33 dev
drwxr-xr-x   1 root   root   4096 Mar 13 07:33 etc
drwxr-xr-x   2 root   root   4096 Apr 12  2016 home
drwxr-xr-x   1 root   root   4096 Sep 13  2015 lib
drwxr-xr-x   2 root   root   4096 Nov  8 21:44 lib64
drwxr-xr-x   2 root   root   4096 Nov  8 21:44 media
drwxr-xr-x   2 root   root   4096 Nov  8 21:44 mnt
drwxr-xr-x   2 root   root   4096 Nov  8 21:44 opt
dr-xr-xr-x 163 root   root      0 Mar 13 07:33 proc
drwx------   1 root   root   4096 Mar 13 07:05 root
drwxr-xr-x   1 root   root   4096 Nov  8 21:44 run
drwxr-xr-x   1 root   root   4096 Nov 27 00:22 sbin
drwxr-xr-x   2 root   root   4096 Nov  8 21:44 srv
dr-xr-xr-x  13 root   root      0 Mar 13 07:07 sys
drwxrwxrwt   1 root   root   4096 Mar 13 07:05 tmp
drwxr-xr-x   1 root   root   4096 Nov  8 21:44 usr
drwxr-xr-x   1 root   root   4096 Nov  8 21:44 var
```