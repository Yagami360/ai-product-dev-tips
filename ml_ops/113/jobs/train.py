import argparse
import os
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Subset

from models.networks import ResNet18
from PIL import Image
from tensorboardX import SummaryWriter
from torch.utils.data import DataLoader, TensorDataset
from torchvision.utils import save_image
from tqdm import tqdm
from utils.utils import (
    board_add_image,
    board_add_images,
    load_checkpoint,
    save_checkpoint,
    save_image_historys_gif
)

if __name__ == "__main__":
    """
    ResNet-18 によるクラス分類
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--exper_name", default="ResNet18_train", help="実験名")
    parser.add_argument(
        "--device",
        choices=["cpu", "gpu"],
        default="gpu",
        help="使用デバイス (CPU or GPU)",
    )
    # parser.add_argument('--gpu_ids', type=str, default='0', help='gpu ids: e.g. 0  0,1,2, 0,2. use -1 for CPU')
    parser.add_argument(
        "--dataset",
        choices=["mnist", "cifar-10"],
        default="mnist",
        help="データセットの種類",
    )
    parser.add_argument(
        "--dataset_dir", type=str, default="dataset", help="データセットのディレクトリ"
    )
    parser.add_argument(
        "--results_dir", type=str, default="results", help="生成画像の出力ディレクトリ"
    )
    parser.add_argument(
        "--save_checkpoints_dir",
        type=str,
        default="checkpoints",
        help="モデルの保存ディレクトリ",
    )
    parser.add_argument(
        "--load_checkpoints_dir",
        type=str,
        default="",
        help="モデルの読み込みディレクトリ",
    )
    parser.add_argument(
        "--tensorboard_dir",
        type=str,
        default="tensorboard",
        help="TensorBoard のディレクトリ",
    )
    parser.add_argument(
        "--n_train", type=int, default=10000, help="train dataset の最大数"
    )
    parser.add_argument(
        "--n_test", type=int, default=10000, help="test dataset の最大数"
    )
    parser.add_argument("--n_epoches", type=int, default=10, help="エポック数")
    parser.add_argument("--batch_size", type=int, default=64, help="バッチサイズ")
    parser.add_argument(
        "--batch_size_test", type=int, default=4, help="test データのバッチサイズ"
    )
    parser.add_argument("--lr", type=float, default=0.001, help="学習率")
    parser.add_argument("--beta1", type=float, default=0.5, help="学習率の減衰率")
    parser.add_argument("--beta2", type=float, default=0.999, help="学習率の減衰率")
    parser.add_argument(
        "--image_size", type=int, default=224, help="入力画像のサイズ（pixel単位）"
    )
    parser.add_argument(
        "--n_fmaps", type=int, default=64, help="１層目の特徴マップの枚数"
    )
    parser.add_argument("--n_classes", type=int, default=10)
    parser.add_argument(
        "--n_display_step", type=int, default=50, help="tensorboard への表示間隔"
    )
    parser.add_argument(
        "--n_display_test_step",
        type=int,
        default=500,
        help="test データの tensorboard への表示間隔",
    )
    parser.add_argument(
        "--n_save_step",
        type=int,
        default=5000,
        help="モデルのチェックポイントの保存間隔",
    )
    parser.add_argument("--seed", type=int, default=8, help="乱数シード値")
    parser.add_argument("--debug", action="store_true", help="デバッグモード有効化")
    args = parser.parse_args()

    # 実行条件の出力
    print("----------------------------------------------")
    print("実行条件")
    print("----------------------------------------------")
    print("開始時間：", datetime.now())
    print("PyTorch version :", torch.__version__)
    for key, value in vars(args).items():
        print("%s: %s" % (str(key), str(value)))

    # 実行 Device の設定
    if args.device == "gpu":
        use_cuda = torch.cuda.is_available()
        if use_cuda == True:
            device = torch.device("cuda")
            # torch.cuda.set_device(args.gpu_ids[0])
            print("実行デバイス :", device)
            print("GPU名 :", torch.cuda.get_device_name(device))
            print("torch.cuda.current_device() =", torch.cuda.current_device())
        else:
            print("can't using gpu.")
            device = torch.device("cpu")
            print("実行デバイス :", device)
    else:
        device = torch.device("cpu")
        print("実行デバイス :", device)

    print("-------------- End ----------------------------")

    # 各種出力ディレクトリ
    if not (os.path.exists(args.results_dir)):
        os.mkdir(args.results_dir)
    if not (os.path.exists(os.path.join(args.results_dir, args.exper_name))):
        os.mkdir(os.path.join(args.results_dir, args.exper_name))
    if not (os.path.exists(args.tensorboard_dir)):
        os.mkdir(args.tensorboard_dir)
    if not (os.path.exists(args.save_checkpoints_dir)):
        os.mkdir(args.save_checkpoints_dir)
    if not (os.path.exists(os.path.join(args.save_checkpoints_dir, args.exper_name))):
        os.mkdir(os.path.join(args.save_checkpoints_dir, args.exper_name))

    # for visualation
    board_train = SummaryWriter(
        log_dir=os.path.join(args.tensorboard_dir, args.exper_name)
    )
    board_test = SummaryWriter(
        log_dir=os.path.join(args.tensorboard_dir, args.exper_name + "_test")
    )

    # seed 値の固定
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # ======================================================================
    # データセットを読み込み or 生成
    # データの前処理
    # ======================================================================
    if args.dataset == "mnist":
        transform = transforms.Compose(
            [
                transforms.Resize(args.image_size, interpolation=Image.LANCZOS),
                transforms.ToTensor(),  # Tensor に変換]
                transforms.Normalize((0.5,), (0.5,)),  # 1 channel 分
            ]
        )

        # data と label をセットにした TensorDataSet の作成
        ds_train = torchvision.datasets.MNIST(
            root=args.dataset_dir,
            train=True,
            transform=transform,  # transforms.Compose(...) で作った前処理の一連の流れ
            target_transform=None,
            download=True,
        )

        ds_test = torchvision.datasets.MNIST(
            root=args.dataset_dir,
            train=False,
            transform=transform,
            target_transform=None,
            download=True,
        )
    elif args.dataset == "cifar-10":
        transform = transforms.Compose(
            [
                transforms.Resize(args.image_size, interpolation=Image.LANCZOS),
                transforms.ToTensor(),  # Tensor に変換
                transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
            ]
        )

        ds_train = torchvision.datasets.CIFAR10(
            root=args.dataset_dir,
            train=True,
            transform=transform,  # transforms.Compose(...) で作った前処理の一連の流れ
            target_transform=None,
            download=True,
        )

        ds_test = torchvision.datasets.CIFAR10(
            root=args.dataset_dir,
            train=False,
            transform=transform,
            target_transform=None,
            download=True,
        )
    else:
        raise NotImplementedError("dataset %s not implemented" % args.dataset)

    indices_train = torch.randperm(len(ds_train))[:min(args.n_train, len(ds_train))]
    indices_test = torch.randperm(len(ds_test))[:min(args.n_test, len(ds_test))]
    ds_train = Subset(ds_train, indices_train)
    ds_test = Subset(ds_test, indices_test)

    # TensorDataset → DataLoader への変換
    dloader_train = DataLoader(
        dataset=ds_train, batch_size=args.batch_size, shuffle=True
    )

    dloader_test = DataLoader(
        dataset=ds_test, batch_size=args.batch_size_test, shuffle=False
    )

    if args.debug:
        print("len(ds_train) :\n", len(ds_train))
        print("len(ds_test) :\n", len(ds_test))

    # ======================================================================
    # モデルの構造を定義する。
    # ======================================================================
    if args.dataset == "mnist":
        model = ResNet18(
            n_in_channels=1, n_fmaps=args.n_fmaps, n_classes=args.n_classes
        ).to(device)
    else:
        model = ResNet18(
            n_in_channels=3, n_fmaps=args.n_fmaps, n_classes=args.n_classes
        ).to(device)

    if args.debug:
        print("model :\n", model)

    # モデルを読み込む
    if not args.load_checkpoints_dir == "" and os.path.exists(
        args.load_checkpoints_dir
    ):
        init_step = load_checkpoint(
            model, device, os.path.join(args.load_checkpoints_dir, "model_final.pth")
        )

    # ======================================================================
    # optimizer の設定
    # ======================================================================
    optimizer = optim.Adam(
        params=model.parameters(), lr=args.lr, betas=(args.beta1, args.beta2)
    )

    # ======================================================================
    # loss 関数の設定
    # ======================================================================
    loss_fn = nn.CrossEntropyLoss()

    # ======================================================================
    # モデルの学習処理
    # ======================================================================
    print("Starting Training Loop...")
    iterations = 0  # 学習処理のイテレーション回数
    n_print = 1

    # -----------------------------
    # エポック数分トレーニング
    # -----------------------------
    for epoch in tqdm(range(args.n_epoches), desc="Epoches"):
        # DataLoader から 1minibatch 分取り出し、ミニバッチ処理
        for step, (images, targets) in enumerate(
            tqdm(dloader_train, desc="minbatch iters")
        ):
            model.train()

            # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する
            # （後の計算で、shape の不一致をおこすため）
            if images.size()[0] != args.batch_size:
                break

            iterations += args.batch_size

            # ミニバッチデータを GPU へ転送
            images = images.to(device)
            targets = targets.to(device)

            # ====================================================
            # モデル の fitting 処理
            # ====================================================
            # ----------------------------------------------------
            # 学習用データをモデルに流し込む
            # model(引数) で呼び出せるのは、__call__ をオーバライトしているため
            # ----------------------------------------------------
            output = model(images)
            if args.debug and n_print > 0:
                print("output.shape :", output.shape)

            # ----------------------------------------------------
            # 損失関数を計算する
            # ----------------------------------------------------
            loss = loss_fn(output, targets)

            # ----------------------------------------------------
            # ネットワークの更新処理
            # ----------------------------------------------------
            # 勾配を 0 に初期化（この初期化処理が必要なのは、勾配がイテレーション毎に加算される仕様のため）
            optimizer.zero_grad()

            # 勾配計算
            loss.backward()

            # backward() で計算した勾配を元に、設定した optimizer に従って、重みを更新
            optimizer.step()

            # ====================================================
            # 学習過程の表示
            # ====================================================
            if step == 0 or (step % args.n_display_step == 0):
                board_train.add_scalar("Model/loss", loss.item(), iterations)
                print("epoch={}, iters={}, loss={:.5f}".format(epoch, iterations, loss))

                # ----------------------------------------------------
                # 正解率を計算する。（バッチデータ）
                # ----------------------------------------------------
                # 確率値が最大のラベル 0~9 を予想ラベルとする。
                # dim = 1 ⇒ 列方向で最大値をとる
                # Returns : (Tensor, LongTensor)
                _, predicts = torch.max(output.data, dim=1)
                if args.debug and n_print > 0:
                    print("predicts.shape :", predicts.shape)

                # 正解数のカウント
                n_tests = targets.size(0)

                # ミニバッチ内で一致したラベルをカウント
                n_correct = (predicts == targets).sum().item()

                accuracy = n_correct / n_tests
                print(
                    "epoch={}, iters={}, accuracy={:.5f}".format(
                        epoch, iterations, accuracy
                    )
                )
                board_train.add_scalar("Model/accuracy_batch", accuracy, iterations)

            # ====================================================
            # test loss の表示
            # ====================================================
            if step == 0 or (step % args.n_display_test_step == 0):
                model.eval()

                n_test_loop = 0
                test_iterations = 0
                test_loss_total = 0
                n_correct = 0
                n_tests = 0
                for test_images, test_targets in dloader_test:
                    if test_images.size()[0] != args.batch_size_test:
                        break

                    test_iterations += args.batch_size_test
                    n_test_loop += 1

                    # ----------------------------------------------------
                    # 入力データをセット
                    # ----------------------------------------------------
                    test_images = test_images.to(device)
                    test_targets = test_targets.to(device)

                    # ----------------------------------------------------
                    # テスト用データをモデルに流し込む
                    # ----------------------------------------------------
                    with torch.no_grad():
                        test_output = model(test_images)

                    # ----------------------------------------------------
                    # 損失関数を計算する
                    # ----------------------------------------------------
                    test_loss = loss_fn(test_output, test_targets)

                    # total
                    test_loss_total += test_loss.item()

                    # ----------------------------------------------------
                    # 正解率を計算する。
                    # ----------------------------------------------------
                    # 確率値が最大のラベル 0~9 を予想ラベルとする。
                    # dim = 1 ⇒ 列方向で最大値をとる
                    # Returns : (Tensor, LongTensor)
                    _, test_predicts = torch.max(test_output.data, dim=1)

                    # 正解数のカウント
                    n_tests += test_targets.size(0)

                    # ミニバッチ内で一致したラベルをカウント
                    n_correct += (test_predicts == test_targets).sum().item()

                    if test_iterations > args.n_test:
                        break

                board_test.add_scalar(
                    "Model/loss", (test_loss_total / n_test_loop), iterations
                )

                test_accuracy = n_correct / n_tests
                board_test.add_scalar("Model/accuracy", test_accuracy, iterations)

            # ====================================================
            # モデルの保存
            # ====================================================
            if step % args.n_save_step == 0:
                save_checkpoint(
                    model,
                    device,
                    os.path.join(
                        args.save_checkpoints_dir, args.exper_name, "model_final.pth"
                    ),
                    iterations,
                )
                print("saved checkpoints")

            n_print -= 1

        # ====================================================
        # 各 Epoch 終了後の処理
        # ====================================================
        # ----------------------------------------------------
        # 正解率を計算する。（全学習用データ）
        # ----------------------------------------------------
        model.eval()
        n_correct = 0
        n_tests = 0
        for images, targets in dloader_train:
            if images.size()[0] != args.batch_size:
                break

            images = images.to(device)
            targets = targets.to(device)
            with torch.no_grad():
                output = model(images)

            # 確率値が最大のラベル 0~9 を予想ラベルとする。
            # dim = 1 ⇒ 列方向で最大値をとる
            # Returns : (Tensor, LongTensor)
            _, predicts = torch.max(output.data, dim=1)

            # 正解数のカウント
            n_tests += targets.size(0)

            # ミニバッチ内で一致したラベルをカウント
            n_correct += (predicts == targets).sum().item()

        accuracy = n_correct / n_tests
        board_train.add_scalar("Model/accuracy", accuracy, iterations)

    save_checkpoint(
        model,
        device,
        os.path.join(args.save_checkpoints_dir, args.exper_name, "model_final.pth"),
        iterations,
    )
    print("Finished Training Loop.")
