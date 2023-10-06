import argparse
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.llms import OpenAI

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--openai_api_key', type=str, default="dummuy")
    parser.add_argument('--model_name', type=str, default="text-davinci-003")
    parser.add_argument('--human_prompt', type=str, default="Hello World!")
    parser.add_argument('--ai_prompt', type=str, default="Hello! How can I assist you today?")
    args = parser.parse_args()

    # メモリ初期化
    memory = ConversationBufferMemory()

    # モデル定義
    llm = OpenAI(
        openai_api_key=args.openai_api_key,
        model_name=args.model_name,
        temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
    )
    print("llm: ", llm)

    # チェーンの初期化（使用する LLM と メモリオブジェクトを渡す）
    conversation = ConversationChain(
        llm=llm, 
        memory=memory
    )

    # LLM推論実行
    try:
        # 会話を開始
        user_input=input("You: ")

        while True: 
            response = conversation.predict(input=user_input)
            print(f"AI: {response}")
            user_input = input("You: ")
            if user_input == "exit":
                break
    except Exception as e:
        print(f"Excception was occurred | {e}")
        exit(1)

    exit(0)
