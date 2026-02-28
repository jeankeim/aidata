# ===================================================================
# 大模型应用完整示例项目
# 集成RAG + 客服 + 代码生成 + 内容分析
# ===================================================================

import os
import json
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv

# LangChain导入
# 注：原OpenAI导入已注释，改用兼容国内大模型的方式
# from langchain.chat_models import ChatOpenAI  # 仅适用于OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 国内大模型适配导入
import requests
from typing import Generator


class QwenChatModel:
    """千问大模型及国内大模型通用适配类"""
    
    def __init__(self, api_key: str, model: str = "qwen-turbo", base_url: str = None, temperature: float = 0.7, max_tokens: int = 1000):
        """
        初始化国内大模型适配器
        
        支持的模型：
        - 千问系列：qwen-turbo, qwen-plus, qwen-max
        - 其他国内模型：通过base_url配置兼容OpenAI接口的模型
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 根据模型选择对应的API端点
        if base_url:
            self.base_url = base_url
        elif "qwen" in model.lower():
            self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        else:
            self.base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    def invoke(self, prompt: str) -> 'Message':
        """同步调用模型"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "result_format": "message"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # 创建兼容LangChain的消息对象
            class Message:
                def __init__(self, content):
                    self.content = content
            
            content = result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
            return Message(content)
            
        except Exception as e:
            print(f"API调用错误: {e}")
            class Message:
                def __init__(self, content):
                    self.content = content
            return Message(f"调用失败: {str(e)}")
    
    def __call__(self, prompt: str) -> str:
        """直接调用返回字符串"""
        return self.invoke(prompt).content


# 兼容其他国内大模型的通用类
class GenericLLMModel:
    """通用国内大模型适配类 - 兼容OpenAI接口格式"""
    
    def __init__(self, api_key: str, model: str, base_url: str, temperature: float = 0.7, max_tokens: int = 1000):
        """
        初始化通用大模型适配器
        
        适用于：
        - 智谱AI (GLM系列)
        - 文心一言
        - 讯飞星火
        - 其他兼容OpenAI接口的国内模型
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def invoke(self, prompt: str) -> 'Message':
        """同步调用模型"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 标准OpenAI兼容接口格式
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            class Message:
                def __init__(self, content):
                    self.content = content
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return Message(content)
            
        except Exception as e:
            class Message:
                def __init__(self, content):
                    self.content = content
            return Message(f"调用失败: {str(e)}")
    
    def __call__(self, prompt: str) -> str:
        """直接调用返回字符串"""
        return self.invoke(prompt).content

class LLMApplicationSuite:
    """大模型应用集合类 - 包含多个应用实例
    
    适配国内大模型（千问、智谱、文心等）
    """
    
    def __init__(self, api_key: str, model: str = "qwen-turbo", provider: str = "qwen"):
        """
        初始化应用套件
        
        Args:
            api_key: API密钥
            model: 模型名称
                - 千问: qwen-turbo, qwen-plus, qwen-max
                - 智谱: glm-4, glm-4-flash
                - 文心: 通过GenericLLMModel配置
            provider: 提供商类型 (qwen, zhipu, baidu, generic)
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        
        # 根据提供商选择对应的模型适配器
        if provider == "qwen":
            # 千问大模型（阿里云灵积平台）
            self.llm = QwenChatModel(
                api_key=api_key,
                model=model,
                temperature=0.7,
                max_tokens=1000
            )
        elif provider == "zhipu":
            # 智谱AI (GLM系列) - 使用OpenAI兼容接口
            self.llm = GenericLLMModel(
                api_key=api_key,
                model=model,
                base_url="https://open.bigmodel.cn/api/paas/v4",
                temperature=0.7,
                max_tokens=1000
            )
        elif provider == "baidu":
            # 文心一言
            self.llm = GenericLLMModel(
                api_key=api_key,
                model=model,
                base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
                temperature=0.7,
                max_tokens=1000
            )
        else:
            # 通用适配器 - 可配置任意兼容OpenAI接口的模型
            self.llm = GenericLLMModel(
                api_key=api_key,
                model=model,
                base_url=os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
                temperature=0.7,
                max_tokens=1000
            )
        
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志系统"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    # ============ 应用1: 智能客服系统 ============
    def create_customer_service_bot(self, company_context: Dict) -> ConversationChain:
        """创建客服机器人"""
        self.logger.info("初始化客服系统...")
        
        system_prompt = f"""你是{company_context['company_name']}的专业客服代表。

公司信息：
- 产品：{company_context['products']}
- 营业时间：{company_context['hours']}
- 退货政策：{company_context['policy']}

要求：
1. 友好、专业、耐心
2. 准确回答产品和政策问题
3. 记住对话历史
4. 必要时升级至人工客服
"""
        
        memory = ConversationBufferMemory()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("history", "{history}"),
            ("human", "{input}"),
        ])
        
        chain = ConversationChain(
            llm=self.llm,
            memory=memory,
            prompt=prompt,
            verbose=False
        )
        
        self.logger.info("✓ 客服系统已初始化")
        return chain
    
    # ============ 应用2: 内容分析系统 ============
    def analyze_content(self, content: str) -> Dict:
        """分析文本内容"""
        self.logger.info("开始内容分析...")
        
        analysis_prompt = ChatPromptTemplate.from_template("""
请对以下文本进行全面分析：

文本内容：
{content}

分析维度：
1. 摘要（150字以内）
2. 关键词（5个）
3. 情感倾向（积极/中立/消极）
4. 主要观点（3个）

请以JSON格式输出结果。
""")
        
        chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
        response = chain.run(content=content)
        
        self.logger.info("✓ 内容分析完成")
        return {"analysis": response}
    
    # ============ 应用3: 代码生成系统 ============
    def generate_code(self, requirement: str, language: str = "Python") -> str:
        """生成代码"""
        self.logger.info(f"生成{language}代码...")
        
        code_prompt = ChatPromptTemplate.from_template("""
你是一个高级编程专家。

编程语言：{language}
需求：{requirement}

要求：
1. 代码完整、可运行
2. 包含详细注释
3. 遵循最佳实践
4. 包含错误处理
5. 易于维护

直接输出代码，无需额外说明。
""")
        
        chain = LLMChain(llm=self.llm, prompt=code_prompt)
        code = chain.run(language=language, requirement=requirement)
        
        self.logger.info("✓ 代码生成完成")
        return code
    
    # ============ 应用4: 文案生成系统 ============
    def generate_copywriting(self, product_info: Dict) -> Dict:
        """生成营销文案"""
        self.logger.info("生成营销文案...")
        
        copy_prompt = ChatPromptTemplate.from_template("""
你是资深文案撰写专家。

产品信息：
- 名称：{name}
- 特点：{features}
- 目标受众：{audience}
- 价格：{price}

请创建专业营销文案，包括：
1. 吸引眼球的标题（10字以内）
2. 正文（100-150字）
3. 号召性用语

要求简洁、有力、富有说服力。
""")
        
        chain = LLMChain(llm=self.llm, prompt=copy_prompt)
        copywriting = chain.run(
            name=product_info['name'],
            features=product_info['features'],
            audience=product_info['audience'],
            price=product_info.get('price', '未指定')
        )
        
        self.logger.info("✓ 文案生成完成")
        return {"copywriting": copywriting}
    
    # ============ 应用5: 学习内容生成 ============
    def generate_learning_content(self, topic: str, level: str = "中级") -> Dict:
        """生成学习内容"""
        self.logger.info(f"生成{level}级{topic}学习内容...")
        
        content_prompt = ChatPromptTemplate.from_template("""
你是一位经验丰富的教育工作者。

主题：{topic}
难度：{level}

请创建包含以下内容的学习材料：
1. 核心概念解释
2. 3个实际例子
3. 常见误区
4. 练习题（3题）
5. 深入学习建议

格式清晰，易于理解。
""")
        
        chain = LLMChain(llm=self.llm, prompt=content_prompt)
        content = chain.run(topic=topic, level=level)
        
        self.logger.info("✓ 学习内容生成完成")
        return {"content": content}
    
    # ============ 通用方法 ============
    def quick_ask(self, question: str, context: Optional[str] = None) -> str:
        """快速问答"""
        if context:
            prompt = f"背景信息：{context}\n\n问题：{question}"
        else:
            prompt = question
            
        response = self.llm.invoke(prompt)
        return response.content
    
    def batch_process(self, tasks: List[Dict]) -> List[Dict]:
        """批量处理任务"""
        self.logger.info(f"开始批量处理{len(tasks)}个任务...")
        results = []
        
        for i, task in enumerate(tasks, 1):
            self.logger.info(f"处理任务 {i}/{len(tasks)}")
            
            task_type = task.get('type')
            if task_type == 'analysis':
                result = self.analyze_content(task['content'])
            elif task_type == 'copywriting':
                result = self.generate_copywriting(task['product_info'])
            elif task_type == 'code':
                result = self.generate_code(task['requirement'], task.get('language', 'Python'))
            else:
                result = {"error": "未知的任务类型"}
            
            results.append({
                "task_id": task.get('id', i),
                "result": result
            })
        
        self.logger.info("✓ 批量处理完成")
        return results


# ===================================================================
# 使用示例
# ===================================================================

def main():
    """主函数 - 演示所有功能"""
    
    # 设置API密钥（实际使用时从环境变量读取）
    # 千问API密钥获取：https://dashscope.aliyun.com/
    api_key = "your-qwen-api-key"  # 替换为你的千问API密钥
    
    # 初始化应用套件 - 使用千问大模型
    suite = LLMApplicationSuite(
        api_key=api_key,
        model="qwen-turbo",  # 可选: qwen-turbo, qwen-plus, qwen-max
        provider="qwen"
    )
    
    # 其他国内大模型配置示例：
    # suite = LLMApplicationSuite(api_key, model="glm-4", provider="zhipu")  # 智谱AI
    # suite = LLMApplicationSuite(api_key, model="ernie-bot", provider="baidu")  # 文心一言
    
    print("="*60)
    print("大模型应用完整示例项目")
    print("="*60)
    
    # 示例1：快速问答
    print("\n【示例1：快速问答】")
    question = "请解释什么是大语言模型？"
    answer = suite.quick_ask(question)
    print(f"Q: {question}")
    print(f"A: {answer}\n")
    
    # 示例2：文案生成
    print("【示例2：生成营销文案】")
    product = {
        "name": "AI智能助手",
        "features": "24小时可用、多语言支持、快速响应",
        "audience": "企业和个人用户",
        "price": "¥99/月"
    }
    copy_result = suite.generate_copywriting(product)
    print(copy_result["copywriting"][:200] + "...\n")
    
    # 示例3：内容分析
    print("【示例3：内容分析】")
    sample_text = "人工智能正在改变我们的生活方式。从医疗到教育，从交通到娱乐，AI无处不在。"
    analysis = suite.analyze_content(sample_text)
    print(f"分析结果: {analysis['analysis'][:200]}...\n")
    
    # 示例4：代码生成
    print("【示例4：代码生成】")
    code = suite.generate_code(
        "创建一个简单的Flask API来返回当前时间",
        "Python"
    )
    print(f"生成的代码:\n{code[:300]}...\n")
    
    # 示例5：学习内容生成
    print("【示例5：学习内容生成】")
    content = suite.generate_learning_content("机器学习基础", "入门")
    print(f"生成的内容:\n{content['content'][:300]}...\n")
    
    print("="*60)
    print("✓ 所有示例执行完成！")
    print("="*60)


if __name__ == "__main__":
    # 实际运行时取消注释
    # main()
    
    # 或者手动测试各功能
    print("此为完整可运行的示例代码框架")
    print("使用时请：")
    print("1. 安装依赖：pip install langchain python-dotenv requests")
    print("2. 获取千问API密钥：https://dashscope.aliyun.com/")
    print("3. 将 'your-qwen-api-key' 替换为实际的API密钥")
    print("4. 取消main()的注释并运行")