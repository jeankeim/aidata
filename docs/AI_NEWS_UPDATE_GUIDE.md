# AI技术动态自动更新指南

## 📋 方案概述

采用 **GitHub Actions + 人工审核** 的半自动更新方案：

1. **自动抓取**：每周一早上9点（UTC）自动运行爬虫
2. **生成PR**：抓取到的新数据自动生成Pull Request
3. **人工审核**：您审核PR内容，确认无误后合并
4. **零成本**：完全使用GitHub免费功能

---

## 🗂️ 文件结构

```
llm-handbook/
├── data/
│   └── ai-news.json              # AI新闻数据文件
├── scripts/
│   └── update_ai_news.py         # 爬虫脚本
├── .github/workflows/
│   └── update-ai-news.yml        # GitHub Actions配置
└── docs/
    └── AI_NEWS_UPDATE_GUIDE.md   # 本指南
```

---

## ⚙️ 工作原理

### 1. 定时触发
- **频率**：每周一早上9点（UTC时间，北京时间17点）
- **手动触发**：可随时在Actions页面手动运行

### 2. 数据抓取
脚本会从以下RSS源抓取AI相关新闻：
- OpenAI Blog
- Anthropic
- Google AI Blog
- Hugging Face Blog

### 3. 关键词过滤
只保留包含以下关键词的内容：
- GPT, Claude, Gemini, LLM, 大模型, AI, 模型
- LangChain, LlamaIndex, RAG, Agent, 多模态
- DeepSeek, 文心一言, 通义千问

### 4. 生成PR
- 有新数据时，自动创建Pull Request
- PR标题：`📰 自动更新：AI技术动态数据`
- 包含审核清单和操作说明

---

## ✅ 审核流程

当收到自动生成的PR时：

### 1. 查看PR内容
```bash
# 本地查看
gh pr checkout <PR_NUMBER>
cat data/ai-news.json
```

### 2. 审核清单
- [ ] 新闻内容准确无误
- [ ] 日期格式正确（YYYY-MM-DD）
- [ ] 来源链接可访问
- [ ] 无敏感或不当内容

### 3. 操作选项
| 操作 | 说明 |
|------|------|
| **合并PR** | 审核通过，接受更新 |
| **提交修改** | 在PR上直接修改后合并 |
| **关闭PR** | 放弃本次更新 |

---

## 🔧 手动更新

如需手动更新数据：

```bash
# 1. 运行爬虫脚本
python scripts/update_ai_news.py

# 2. 查看更新的数据
cat data/ai-news.json

# 3. 提交更改
git add data/ai-news.json
git commit -m "update: AI新闻数据"
git push origin main
```

---

## 📝 数据结构

### ai-news.json 格式

```json
{
  "lastUpdated": "2026-02-28",
  "version": "1.0",
  "hotNews": [
    {
      "id": 1,
      "title": "新闻标题",
      "category": "分类",
      "date": "2026-02",
      "summary": "摘要",
      "tags": ["标签1", "标签2"],
      "source": "来源",
      "url": "链接",
      "verified": true
    }
  ],
  "modelTimeline": [...],
  "techTrends": [...],
  "toolUpdates": [...]
}
```

---

## 🛠️ 自定义配置

### 修改抓取频率
编辑 `.github/workflows/update-ai-news.yml`：

```yaml
schedule:
  - cron: '0 9 * * 1'  # 每周一9点
  # 其他示例：
  # - cron: '0 9 * * *'   # 每天9点
  # - cron: '0 9 1 * *'   # 每月1号9点
```

### 添加RSS源
编辑 `scripts/update_ai_news.py`：

```python
RSS_SOURCES = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "新增源": "https://example.com/rss.xml",  # 添加这里
}
```

### 修改关键词
编辑 `scripts/update_ai_news.py` 中的 `KEYWORDS` 列表。

---

## 💰 成本说明

| 项目 | 费用 | 说明 |
|------|------|------|
| GitHub Actions | **免费** | 公共仓库无限制 |
| 存储空间 | **免费** | 无限制 |
| 网络流量 | **免费** | 无限制 |
| **总计** | **¥0** | 完全免费 |

---

## 🚨 常见问题

### Q: PR没有自动生成？
A: 检查：
1. Actions是否启用（Settings > Actions > General）
2. 工作流文件是否有语法错误
3. 是否有新的数据变化

### Q: 如何测试脚本？
A: 本地运行：
```bash
python scripts/update_ai_news.py
```

### Q: 如何禁用自动更新？
A: 删除或重命名 `.github/workflows/update-ai-news.yml`

### Q: 可以抓取更多来源吗？
A: 可以，在 `RSS_SOURCES` 中添加更多RSS链接。

---

## 📞 获取帮助

如有问题，请：
1. 查看GitHub Actions运行日志
2. 检查脚本输出信息
3. 提交Issue到项目仓库

---

**最后更新**: 2026年2月28日
