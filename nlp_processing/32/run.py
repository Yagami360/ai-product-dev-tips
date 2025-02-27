import argparse
from nemo.collections.nlp.models.language_modeling.megatron_gpt_model import MegatronGPTModel
import lightning as L


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, default="cuda", choices=["cpu", "cuda"])
    args = parser.parse_args()

    trainer = L.Trainer(
        accelerator=args.device,
        devices=1,
    )

    # 事前学習済みLLMモデルを読み込む
    model = MegatronGPTModel.from_pretrained(
        model_name="megatron_gpt_345m",
        map_location=args.device,
        trainer=trainer
        # trainer=None
    )
    # model.set_trainer(trainer)

    # LLMの推論処理
    model.freeze()  # LLMを推論モードにする
    try:
        response = model.generate(
            "AIについて教えてください", 
            max_length=100
        )
        print(response)
    except Exception as e:
        print(f"An exception is occurred: {e}")
