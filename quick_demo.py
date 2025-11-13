#!/usr/bin/env python3
"""快速演示DeepSeek的代码审查能力"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from resoftai.config import Settings
from resoftai.llm.factory import LLMFactory


async def main():
    print("=" * 70)
    print("DeepSeek 代码审查演示")
    print("=" * 70)

    code = '''
def get_user(user_id):
    db = connect_db()
    user = db.execute("SELECT * FROM users WHERE id = " + str(user_id))
    return user
'''

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    print(f"\n待审查的代码:\n{code}")
    print("\n正在使用DeepSeek分析代码安全性问题...")
    print("-" * 70)

    response = await llm.generate(
        prompt=f"请审查以下代码的安全性问题并给出改进建议：\n\n```python\n{code}\n```",
        system_prompt="你是一个安全专家。重点分析SQL注入、资源泄露等安全问题，并提供安全的改进代码。"
    )

    print(f"\nDeepSeek的分析结果:\n")
    print(response.content)
    print(f"\n[Token使用: {response.total_tokens}]")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
