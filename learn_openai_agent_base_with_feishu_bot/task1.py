"""
Task 1: 飞书基础认证和消息发送

学习目标：
1. 理解飞书 API 认证流程（tenant_access_token）
2. 掌握基础文本消息发送
3. 实现错误处理和日志输出

知识点：
- HTTP POST 请求
- JSON 数据处理
- 环境变量管理
- 错误处理模式

运行方式：
    python task1.py
"""

import os
import json
import requests
from typing import Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class FeishuClient:
    """飞书客户端基础类"""

    def __init__(self):
        """初始化飞书客户端"""
        self.app_id = os.getenv("APP_ID")
        self.app_secret = os.getenv("APP_SECRET")
        self.open_id = os.getenv("OPEN_ID")

        # 验证配置
        if not all([self.app_id, self.app_secret, self.open_id]):
            raise ValueError("请在 .env 文件中配置 APP_ID, APP_SECRET, OPEN_ID")

        print(f"✅ 飞书客户端初始化成功")
        print(f"📱 APP_ID: {self.app_id[:10]}...")

    def get_tenant_access_token(self) -> Tuple[str, Exception]:
        """
        获取 tenant_access_token（租户访问令牌）

        这是飞书 API 认证的第一步，所有后续 API 调用都需要这个 token

        Returns:
            Tuple[str, Exception]: (access_token, error)
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

        # 准备请求数据
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            print(f"\n🔐 正在获取访问令牌...")
            print(f"📡 请求地址: {url}")

            # 发送 POST 请求
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # 检查 HTTP 错误

            # 解析响应
            result = response.json()
            print(f"📥 响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")

            # 检查业务错误码
            if result.get("code", 0) != 0:
                error_msg = f"获取 token 失败: {result.get('msg', '未知错误')}"
                print(f"❌ {error_msg}")
                return "", Exception(error_msg)

            token = result["tenant_access_token"]
            print(f"✅ Token 获取成功: {token[:20]}...")
            return token, None

        except Exception as e:
            error_msg = f"请求失败: {e}"
            print(f"❌ {error_msg}")
            return "", e

    def send_text_message(self, token: str, text: str) -> Tuple[dict, Exception]:
        """
        发送纯文本消息

        Args:
            token: tenant_access_token
            text: 要发送的文本内容

        Returns:
            Tuple[dict, Exception]: (响应数据, 错误)
        """
        url = "https://open.feishu.cn/open-apis/im/v1/messages"

        # 查询参数：指定接收者 ID 类型
        params = {
            "receive_id_type": "open_id"
        }

        # 请求头：包含认证 token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        # 请求体：消息内容
        payload = {
            "receive_id": self.open_id,  # 接收者 ID
            "msg_type": "text",           # 消息类型
            "content": json.dumps({       # 消息内容（需要 JSON 序列化）
                "text": text
            }, ensure_ascii=False)
        }

        try:
            print(f"\n📤 正在发送消息...")
            print(f"📡 请求地址: {url}")
            print(f"📝 消息内容: {text}")

            # 发送 POST 请求
            response = requests.post(url, params=params, headers=headers, json=payload)
            response.raise_for_status()

            # 解析响应
            result = response.json()
            print(f"📥 响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")

            # 检查业务错误码
            if result.get("code", 0) != 0:
                error_msg = f"发送消息失败: {result.get('msg', '未知错误')}"
                print(f"❌ {error_msg}")
                return {}, Exception(error_msg)

            print(f"✅ 消息发送成功！")
            return result, None

        except Exception as e:
            error_msg = f"发送消息失败: {e}"
            print(f"❌ {error_msg}")
            return {}, e


def main():
    """主函数：演示完整的认证和发送流程"""

    print("=" * 60)
    print("Task 1: 飞书基础认证和消息发送")
    print("=" * 60)

    try:
        # 1. 初始化客户端
        client = FeishuClient()

        # 2. 获取访问令牌
        token, err = client.get_tenant_access_token()
        if err:
            print(f"\n❌ 认证失败，程序退出")
            return

        # 3. 发送测试消息
        test_message = """
🎓 Task 1 学习完成！

你已经掌握：
✅ 飞书 API 认证流程
✅ tenant_access_token 获取
✅ 发送纯文本消息
✅ 错误处理和日志

下一步：Task 2 - 飞书卡片设计
        """.strip()

        _, err = client.send_text_message(token, test_message)
        if err:
            print(f"\n❌ 消息发送失败")
            return

        print("\n" + "=" * 60)
        print("🎉 Task 1 完成！请查看飞书消息")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 程序异常: {e}")


# ============================================================
# 学习要点和练习
# ============================================================

"""
📚 核心概念解析：

1. tenant_access_token
   - 应用级别的访问令牌
   - 有效期：2 小时
   - 用于所有后续 API 调用

2. 消息发送流程
   认证 → 获取 token → 发送消息 → 处理响应

3. 错误处理
   - HTTP 错误：网络、超时等
   - 业务错误：code != 0
   - 都需要妥善处理

💡 练习题：

1. 修改代码，添加 token 缓存（避免重复获取）
2. 实现发送多条消息的批量发送功能
3. 添加消息发送失败的重试机制（最多3次）
4. 记录所有 API 调用日志到文件

🔍 深入思考：

1. 为什么需要 tenant_access_token？直接用 app_secret 不行吗？
   提示：安全性、权限控制、token 轮换

2. 消息内容为什么要 JSON 序列化两次？
   提示：payload 本身是 JSON，content 字段也需要 JSON 字符串

3. 如何优化多次发送消息的性能？
   提示：token 复用、连接池、批量 API

📖 扩展阅读：
- 飞书认证文档: https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
- 飞书消息文档: https://open.feishu.cn/document/server-docs/im-v1/message/create
"""


if __name__ == "__main__":
    main()
