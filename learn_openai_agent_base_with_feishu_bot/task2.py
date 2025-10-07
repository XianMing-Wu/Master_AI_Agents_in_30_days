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

    def create_email_card(
        self,
        subject: str,
        markdown_body: str
    ) -> Dict[str, Any]:
        """
        创建用于发送邮件内容的飞书卡片。

        结构参考 Task 5 中的 send_feishu_email 工具说明：
        - header 显示邮件主题
        - body 承载 Feishu 兼容的 Markdown 正文

        Args:
            subject: 邮件主题
            markdown_body: 已转换为 Feishu Markdown 的正文

        Returns:
            Dict[str, Any]: 卡片 JSON 结构
        """

        subject_text = (subject or "").strip()
        body_text = (markdown_body or "").strip().replace("\r\n", "\n").replace("\r", "\n")

        if not subject_text:
            subject_text = "未设置主题"

        if not body_text:
            body_text = "*No email content provided.*"

        card = {
            "schema": "2.0",
            "config": {
                "width_mode": "fill"
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": f"📬 {subject_text}",
                    "tag": "plain_text"
                }
            },
            "body": {
                "direction": "vertical",
                "padding": "12px 12px 12px 12px",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": body_text
                    },
                    {"tag": "hr"},
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": "Feishu Markdown 格式已按 Task 5 要求准备"
                            }
                        ]
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


def demo_email_card(client: FeishuCardClient, token: str):
    """示例：邮件卡片（核心功能）"""
    print("\n" + "=" * 60)
    print("📌 发送邮件卡片")
    print("=" * 60)

    # 准备符合 Task 5 要求的 Feishu Markdown 内容
    markdown_content = (
        "# Product Momentum Update\n\n"
        "Dear CEO,\n\n"
        "**ComplAI helps compliance teams** uncover risk faster while keeping workflows simple.\n\n"
        "## Why it matters\n"
        "- Automates evidence collection to cut review time by 60%\n"
        "- Surfaces high-priority anomalies with explainable AI\n"
        "- Integrates with existing ticket systems in under 1 week\n\n"
        "## Next steps\n"
        "1. Schedule a 20-minute discovery session this week\n"
        "2. Share your current compliance stack\n"
        "3. Identify one pilot workflow for automation\n\n"
        "Looking forward to your thoughts.\n\n"
        "Best regards,\nAlice"
    )

    # 发送卡片演示效果
    card = client.create_email_card(
        subject="Unlock Faster Compliance Reviews",
        markdown_body=markdown_content
    )

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

        # 3. 发送邮件卡片
        demo_email_card(client, token)

        print("\n" + "=" * 60)
        print("🎉 Task 2 完成！你已经掌握：")
        print("  ✅ 飞书卡片 JSON 结构设计")
        print("  ✅ Markdown 富文本渲染")
        print("  ✅ 交互按钮配置")
        print("  ✅ 邮件内容卡片模板")
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
