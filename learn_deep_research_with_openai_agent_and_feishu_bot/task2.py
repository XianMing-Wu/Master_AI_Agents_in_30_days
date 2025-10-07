"""
Task 2: 飞书卡片设计和发送

学习目标：
1. 掌握飞书消息卡片 2.0 规范
2. 设计研究报告卡片模板
3. 实现 Markdown 富文本渲染
4. 添加交互按钮

知识点：
- JSON 数据结构设计
- 卡片 UI/UX 设计
- Markdown 富文本格式化
- 交互组件使用

运行方式：
    python task2.py
"""

import os
import json
import requests
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

# 和 Task 1 一样，先把 .env 中的敏感配置加载进来
load_dotenv()


class FeishuCardClient:
    """飞书卡片消息客户端"""

    def __init__(self):
        # 读取飞书应用相关的凭证
        self.app_id = os.getenv("APP_ID")
        self.app_secret = os.getenv("APP_SECRET")
        self.open_id = os.getenv("OPEN_ID")

        if not all([self.app_id, self.app_secret, self.open_id]):
            raise ValueError("请配置环境变量")

        print(f"✅ 飞书卡片客户端初始化成功")

    def get_token(self) -> Tuple[str, Exception]:
        """获取访问令牌（复用 Task 1 的实现）"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        headers = {"Content-Type": "application/json"}

        try:
            # 和 Task 1 相同：向认证接口发送请求换取 tenant_access_token
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()

            if result.get("code", 0) != 0:
                return "", Exception(result.get("msg"))

            return result["tenant_access_token"], None
        except Exception as e:
            return "", e

    def create_research_card(
        self,
        title: str,
        summary: str,
        content: str,
        follow_up_questions: list = None
    ) -> Dict[str, Any]:
        """
        创建研究报告卡片（这是本任务的核心！）

        卡片结构：
        ┌─────────────────────────────┐
        │  📊 [标题]                  │ <- header
        ├─────────────────────────────┤
        │  摘要：[简短总结]          │ <- body
        │                             │
        │  详细内容：                 │
        │  [Markdown 格式的报告]     │
        │                             │
        │  后续问题：                 │
        │  • 问题1                    │
        │  • 问题2                    │
        │                             │
        │  [查看完整报告] [分享]     │ <- 交互按钮
        └─────────────────────────────┘

        Args:
            title: 报告标题
            summary: 简短摘要（2-3 句话）
            content: 详细内容（Markdown 格式，会嵌入富文本组件）
            follow_up_questions: 后续研究问题列表

        Returns:
            Dict[str, Any]: 卡片 JSON 结构
        """

        # 处理后续问题
        if follow_up_questions is None:
            follow_up_questions = []

        # 规范化文本，使用 Feishu 支持的 Markdown/Lark 语法
        summary_text = (summary or "").strip().replace("\r\n", "\n").replace("\r", "\n")
        content_text = (content or "").strip().replace("\r\n", "\n").replace("\r", "\n")

        if follow_up_questions:
            questions_md = "\n".join([f"- {q.strip()}" for q in follow_up_questions])
        else:
            questions_md = "暂无"

        # 搭建卡片结构：遵循卡片 2.0 的 schema + body 结构
        # 这里保持字段清晰，方便后续 Task 继续扩展
        card = {
            "schema": "2.0",
            "config": {
                "width_mode": "fill"
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": f"📊 {title}",
                    "tag": "plain_text"
                }
            },
            "body": {
                "direction": "vertical",
                "padding": "12px 12px 12px 12px",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"**📝 摘要**\n{summary_text}"
                    },
                    {"tag": "hr"},
                    {
                        "tag": "markdown",
                        "content": f"**📄 详细内容**\n{content_text}"
                    },
                    {"tag": "hr"},
                    {
                        "tag": "markdown",
                        "content": f"**🤔 后续研究方向**\n{questions_md}"
                    },
                    {
                        "tag": "button",
                        "text": {
                            "content": "📚 查看文档",
                            "tag": "plain_text"
                        },
                        "type": "primary",
                        "behaviors": [{"type": "open_url", "default_url": "https://www.feishu.cn/hc/zh-CN"}]
                    }
                ]
            }
        }

        return card

    def send_card(self, token: str, card: Dict[str, Any]) -> Tuple[Dict, Exception]:
        """
        发送卡片消息

        Args:
            token: tenant_access_token
            card: 卡片 JSON 数据

        Returns:
            Tuple[Dict, Exception]: (响应, 错误)
        """
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        params = {"receive_id_type": "open_id"}
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Feishu 卡片消息走 interactive 类型，content 是整体 JSON 字符串
        payload = {
            "receive_id": self.open_id,
            "msg_type": "interactive",  # 交互式卡片类型
            "content": json.dumps(card, ensure_ascii=False)
        }

        try:
            print(f"\n📤 发送卡片...")
            print(f"📋 卡片预览:")
            print(json.dumps(card, indent=2, ensure_ascii=False))

            response = requests.post(url, params=params, headers=headers, json=payload)
            result = response.json()

            if result.get("code", 0) != 0:
                return {}, Exception(result.get("msg"))

            print(f"✅ 卡片发送成功！")
            return result, None

        except Exception as e:
            return {}, e


def demo_research_card(client: FeishuCardClient, token: str):
    """示例：研究报告卡片（核心功能）"""
    print("\n" + "=" * 60)
    print("📌 发送研究报告卡片")
    print("=" * 60)

    # 准备 Markdown 内容（尽量贴近真实的数据展示）
    markdown_content = (
        "## 🔍 主要发现\n\n"
        "### 1. 技术突破\n"
        "- 参数规模突破 1T\n"
        "- 推理速度提升 10x\n"
        "- 成本降低 90%\n\n"
        "### 2. 应用场景\n"
        "- 智能客服：响应准确率 95%\n"
        "- 代码生成：通过率 85%\n"
        "- 内容创作：原创度 80%\n\n"
        "## 📊 数据支撑\n\n"
        "- 用户数：2023年 1M → 2024年 10M（增长900%）\n"
        "- API 调用：2023年 100M → 2024年 1B（增长900%）\n\n"
        "## 💬 关键引用\n\n"
        "\"AI 的发展速度超出所有人预期\" — OpenAI CEO"
    )

    # 调用核心函数生成卡片结构
    card = client.create_research_card(
        title="2024 AI 行业报告",
        summary="AI 行业在 2024 年实现了跨越式发展，用户规模和应用场景大幅扩展。",
        content=markdown_content,
        follow_up_questions=[
            "各行业的 AI 采用率如何？",
            "未来 5 年的发展预测？",
            "主要竞争格局是怎样的？"
        ]
    )

    # 发送卡片演示效果
    client.send_card(token, card)


def main():
    """主函数：发送飞书卡片示例"""

    print("=" * 60)
    print("Task 2: 飞书卡片设计和发送")
    print("=" * 60)

    try:
        # 1. 初始化客户端
        client = FeishuCardClient()

        # 2. 获取 token
        token, err = client.get_token()
        if err:
            print(f"❌ 获取 token 失败: {err}")
            return

        # 3. 发送研究报告卡片
        demo_research_card(client, token)

        print("\n" + "=" * 60)
        print("🎉 Task 2 完成！你已经掌握：")
        print("  ✅ 飞书卡片 JSON 结构设计")
        print("  ✅ Markdown 富文本渲染")
        print("  ✅ 交互按钮配置")
        print("  ✅ 研究报告卡片模板")
        print("\n请在飞书中查看卡片效果")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 程序异常: {e}")


# ============================================================
# 学习要点
# ============================================================

"""
📚 核心概念：

1. 卡片结构
   - config: 全局配置
   - header: 卡片头部（标题、主题色）
   - elements: 主体内容数组

2. 常用元素
   - div: 文本块（支持 lark_md）
   - hr: 分隔线
   - action: 交互按钮
   - note: 高亮提示
   - fields: 字段并排显示

3. Markdown 支持
   - ✅ 支持：飞书 Lark Markdown（加粗、斜体、列表、有限 HTML 标签）
   - ❌ 不支持：自定义脚本、未在文档列出的标签

4. 主题颜色
   - blue: 常规 | green: 成功 | red: 警告 | orange: 提示 | purple: 特殊

💡 练习：创建不同主题的任务卡片，包含状态、进度、负责人等字段

📖 参考：https://open.feishu.cn/document/common-capabilities/message-card
"""


if __name__ == "__main__":
    main()
