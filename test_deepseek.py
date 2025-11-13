#!/usr/bin/env python3
"""
DeepSeek LLM Provider 测试脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from resoftai.config import Settings
from resoftai.llm.factory import LLMFactory


async def test_deepseek():
    """测试DeepSeek provider"""
    print("=" * 60)
    print("DeepSeek LLM Provider 测试")
    print("=" * 60)

    # 加载配置
    settings = Settings()
    llm_config = settings.get_llm_config()

    print(f"\n配置信息:")
    print(f"  Provider: {llm_config.provider.value}")
    print(f"  Model: {llm_config.model_name}")
    print(f"  Max Tokens: {llm_config.max_tokens}")
    print(f"  Temperature: {llm_config.temperature}")
    print(f"  API Base: {llm_config.api_base}")

    # 创建provider
    try:
        provider = LLMFactory.create(llm_config)
        print(f"\n✓ Provider创建成功: {provider.__class__.__name__}")
    except Exception as e:
        print(f"\n✗ Provider创建失败: {e}")
        return False

    # 测试1: 简单的文本生成
    print("\n" + "-" * 60)
    print("测试1: 简单对话")
    print("-" * 60)

    try:
        response = await provider.generate(
            prompt="请用一句话介绍一下你自己",
            system_prompt="你是一个友好的AI助手"
        )

        print(f"\n请求: 请用一句话介绍一下你自己")
        print(f"\n回复:\n{response.content}")
        print(f"\nToken使用: {response.total_tokens}")
        print(f"模型: {response.model}")
        print("\n✓ 测试1通过")

    except Exception as e:
        print(f"\n✗ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试2: 代码生成
    print("\n" + "-" * 60)
    print("测试2: 代码生成")
    print("-" * 60)

    try:
        response = await provider.generate(
            prompt="写一个Python函数，实现斐波那契数列的前n项",
            system_prompt="你是一个专业的Python开发工程师"
        )

        print(f"\n请求: 写一个Python函数，实现斐波那契数列的前n项")
        print(f"\n回复:\n{response.content}")
        print(f"\nToken使用: {response.total_tokens}")
        print(f"模型: {response.model}")
        print("\n✓ 测试2通过")

    except Exception as e:
        print(f"\n✗ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试3: 流式响应
    print("\n" + "-" * 60)
    print("测试3: 流式响应")
    print("-" * 60)

    try:
        print(f"\n请求: 用三句话介绍一下中国的长城")
        print(f"\n流式回复:")

        full_content = ""
        async for content in provider.generate_stream(
            prompt="用三句话介绍一下中国的长城",
            system_prompt="你是一个旅游向导"
        ):
            if content:
                print(content, end="", flush=True)
                full_content += content

        print(f"\n\n完整内容长度: {len(full_content)}字符")
        print("\n✓ 测试3通过")

    except Exception as e:
        print(f"\n✗ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("所有测试通过! DeepSeek集成正常工作 ✓")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = asyncio.run(test_deepseek())
    sys.exit(0 if success else 1)
