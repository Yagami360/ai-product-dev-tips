from langchain.chat_models import ChatOpenAI

if __name__ == '__main__':
    # モデル定義
    llm = ChatOpenAI()
    print("llm: ", llm)

    # LLM推論実行
    try:
        llm.predict("Hello, world!")
    except Exception as e:
        print(f"Excception was occurred | {e}")
        exit(1)

    exit(0)
