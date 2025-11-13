#!/usr/bin/env python3
"""
使用DeepSeek进行实际软件开发任务的演示
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from resoftai.config import Settings
from resoftai.llm.factory import LLMFactory


async def demo_requirement_analysis():
    """演示：需求分析"""
    print("\n" + "=" * 70)
    print("演示1: 使用DeepSeek进行需求分析")
    print("=" * 70)

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    requirement = """
    我需要开发一个在线图书管理系统，功能包括：
    1. 用户注册和登录
    2. 图书的增删改查
    3. 图书借阅和归还
    4. 查看借阅历史
    5. 管理员后台管理
    """

    system_prompt = """你是一个专业的需求分析师。
请分析用户需求，提供详细的功能模块划分和技术建议。
输出格式要清晰，包括：功能模块、技术栈建议、数据库设计要点。"""

    response = await llm.generate(
        prompt=f"请分析以下需求并给出专业建议：\n{requirement}",
        system_prompt=system_prompt
    )

    print(f"\n{response.content}")
    print(f"\n[Token使用: {response.total_tokens}]")


async def demo_architecture_design():
    """演示：系统架构设计"""
    print("\n" + "=" * 70)
    print("演示2: 使用DeepSeek进行系统架构设计")
    print("=" * 70)

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    system_prompt = """你是一个资深的系统架构师。
请设计一个可扩展、高性能的微服务架构。
考虑：服务拆分、数据库设计、缓存策略、消息队列等。"""

    prompt = """
    为一个电商系统设计微服务架构，需要包含：
    - 用户服务
    - 商品服务
    - 订单服务
    - 支付服务
    - 库存服务

    请提供详细的架构图说明和技术选型。
    """

    print("\n正在设计架构...")
    print("-" * 70)

    full_response = ""
    async for chunk in llm.generate_stream(
        prompt=prompt,
        system_prompt=system_prompt
    ):
        print(chunk, end="", flush=True)
        full_response += chunk

    print(f"\n\n[完整回复长度: {len(full_response)}字符]")


async def demo_code_generation():
    """演示：代码生成"""
    print("\n" + "=" * 70)
    print("演示3: 使用DeepSeek生成生产级代码")
    print("=" * 70)

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    system_prompt = """你是一个专业的Python高级工程师。
请编写生产级代码，包含：
- 完整的类型注解
- 详细的文档字符串
- 异常处理
- 单元测试
- 性能优化"""

    prompt = """
    请实现一个RESTful API的用户认证系统，包括：
    1. 用户注册（邮箱验证）
    2. 用户登录（JWT Token）
    3. Token刷新
    4. 密码重置

    使用FastAPI框架，包含完整的错误处理和数据验证。
    """

    response = await llm.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=4000
    )

    print(f"\n{response.content}")
    print(f"\n[Token使用: {response.total_tokens}]")


async def demo_code_review():
    """演示：代码审查"""
    print("\n" + "=" * 70)
    print("演示4: 使用DeepSeek进行代码审查")
    print("=" * 70)

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    code_to_review = '''
def get_user(user_id):
    db = connect_db()
    user = db.execute("SELECT * FROM users WHERE id = " + str(user_id))
    return user
'''

    system_prompt = """你是一个资深的代码审查专家。
请从以下方面审查代码：
1. 安全性问题（SQL注入、XSS等）
2. 性能问题
3. 代码规范
4. 最佳实践
5. 改进建议"""

    response = await llm.generate(
        prompt=f"请审查以下代码并提供改进建议：\n\n```python\n{code_to_review}\n```",
        system_prompt=system_prompt
    )

    print(f"\n{response.content}")
    print(f"\n[Token使用: {response.total_tokens}]")


async def demo_bug_fixing():
    """演示：Bug修复"""
    print("\n" + "=" * 70)
    print("演示5: 使用DeepSeek进行Bug分析和修复")
    print("=" * 70)

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    buggy_code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# 问题：当传入空列表时会出现 ZeroDivisionError
'''

    system_prompt = """你是一个专业的调试专家。
请分析代码bug，提供：
1. Bug的根本原因
2. 修复后的完整代码
3. 测试用例
4. 预防类似问题的建议"""

    response = await llm.generate(
        prompt=f"以下代码有bug，请分析并修复：\n\n```python\n{buggy_code}\n```",
        system_prompt=system_prompt
    )

    print(f"\n{response.content}")
    print(f"\n[Token使用: {response.total_tokens}]")


async def demo_test_generation():
    """演示：测试用例生成"""
    print("\n" + "=" * 70)
    print("演示6: 使用DeepSeek生成测试用例")
    print("=" * 70)

    settings = Settings()
    llm = LLMFactory.create(settings.get_llm_config())

    code_to_test = '''
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item, quantity=1):
        self.items.append({"item": item, "quantity": quantity})

    def remove_item(self, item_name):
        self.items = [i for i in self.items if i["item"] != item_name]

    def get_total(self, prices):
        total = 0
        for item in self.items:
            price = prices.get(item["item"], 0)
            total += price * item["quantity"]
        return total
'''

    system_prompt = """你是一个测试工程师专家。
请为代码编写完整的pytest测试套件，包括：
1. 正常流程测试
2. 边界条件测试
3. 异常情况测试
4. Mock和Fixture的使用
5. 测试覆盖率要求"""

    response = await llm.generate(
        prompt=f"为以下代码编写完整的pytest测试：\n\n```python\n{code_to_test}\n```",
        system_prompt=system_prompt
    )

    print(f"\n{response.content}")
    print(f"\n[Token使用: {response.total_tokens}]")


async def main():
    """运行所有演示"""
    print("\n" + "🚀" * 35)
    print(" DeepSeek AI 软件开发全流程演示")
    print("🚀" * 35)

    demos = [
        ("需求分析", demo_requirement_analysis),
        ("架构设计", demo_architecture_design),
        ("代码生成", demo_code_generation),
        ("代码审查", demo_code_review),
        ("Bug修复", demo_bug_fixing),
        ("测试生成", demo_test_generation),
    ]

    print("\n请选择要运行的演示：")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. 运行所有演示")

    try:
        choice = input("\n请输入选项 (0-6): ").strip()

        if choice == "0":
            # 运行所有演示
            for name, demo_func in demos:
                await demo_func()
                await asyncio.sleep(1)  # 避免请求过快
        elif choice in ["1", "2", "3", "4", "5", "6"]:
            # 运行选中的演示
            idx = int(choice) - 1
            await demos[idx][1]()
        else:
            print("无效的选项")
            return

    except KeyboardInterrupt:
        print("\n\n演示已取消")
        return

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
    print("\n总结:")
    print("✓ DeepSeek在软件开发各个环节都表现出色")
    print("✓ 支持需求分析、架构设计、代码生成、审查、测试等")
    print("✓ 响应速度快，代码质量高")
    print("✓ 性价比优秀，适合大规模应用")


if __name__ == "__main__":
    asyncio.run(main())
