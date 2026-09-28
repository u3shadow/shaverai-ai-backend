from app.services.deepseek_client import deepseek_client


def main() -> None:
    response = deepseek_client.complete(
        messages=[
            {
                "role": "system",
                "content": "你是一个连通性测试助手，请简短回答。",
            },
            {
                "role": "user",
                "content": "请只回复：DeepSeek 连接成功",
            },
        ]
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
