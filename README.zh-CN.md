# Reddit 客户线索雷达

[English README](README.md)

一个本地优先的 Reddit 痛点研究 CLI，适合独立开发者、自动化接单者和小工具创作者用来发现真实需求。

它会扫描 Reddit 的公开 JSON 页面，按实用机会信号给帖子排序，并把值得验证的线索整理成一张张“小项目机会卡片”。

这个项目不是骚扰式获客工具。它的定位是需求研究：帮你从公开讨论里理解用户痛点，然后构建真正有用的小产品。

## 它能发现什么

雷达会识别这些信号：

- 痛点信号：`manual`、`takes too long`、`looking for a tool`、`can't find`
- 购买意图：`client`、`customer`、`budget`、`Shopify`、`business`
- 紧急程度：`today`、`this week`、`ASAP`、`deadline`
- 自动化适配：`workflow`、`CSV`、`CRM`、`email`、`Zapier`、`dashboard`
- 互动热度：帖子分数和评论数

每个结果会生成一张机会卡片，包含：

- 目标用户
- 原始痛点
- MVP 想法
- 推荐 GitHub 项目名
- 24 小时第一版构建方式
- 可能的变现路径

## 安装

```bash
git clone https://github.com/YOUR_USER/reddit-lead-radar.git
cd reddit-lead-radar
python -m pip install -e .
```

基础公开 JSON 模式不需要 Reddit API key。

不过要注意：不同网络环境下，Reddit 可能返回 403 或触发限流。CLI 会跳过被阻断的搜索并继续写出已收集到的结果。如果要做更高频或更稳定的版本，建议接入 Reddit 官方 API，同时复用本项目的分析和报告层。

## 快速开始

先运行本地示例：

```bash
python -m reddit_lead_radar.cli analyze examples/sample_posts.json --out reports/sample.md --json-out reports/sample.json
```

运行测试：

```bash
python -m unittest discover -s tests
```

扫描 Reddit：

```bash
reddit-lead-radar scan \
  --subreddits SideProject,SaaS,nocode,automation \
  --keywords "looking for tool,need a tool,manual workflow,shopify automation" \
  --limit 10 \
  --days 30 \
  --comments 3 \
  --out reports/latest.md \
  --json-out reports/latest.json
```

Windows PowerShell 写法：

```powershell
reddit-lead-radar scan --subreddits SideProject,SaaS,nocode,automation --keywords "looking for tool,need a tool,manual workflow,shopify automation" --limit 10 --days 30 --comments 3 --out reports/latest.md --json-out reports/latest.json
```

## 示例输出

完整示例见：[examples/sample_report.md](examples/sample_report.md)

```markdown
## 1. Looking for a tool to automate Shopify product page audits

Score: 89/100
Subreddit: r/SideProject

### Opportunity Card

- Target user: Small ecommerce operators and Shopify store owners
- Pain point: Store owners need faster ways to audit listings, pages, copy, and conversion gaps.
- MVP idea: A Shopify store roaster that turns a store URL into a practical conversion checklist.
- GitHub project name: `shopify-store-roaster`
- First build: Fetch one public store page, extract copy and metadata, then generate a Markdown audit.
- Monetization: Paid audits, template packs, or a small monthly monitoring plan.
```

## 负责任使用

请把这个项目用于研究和验证：

- 遵守 Reddit 规则和访问频率限制
- 控制请求量
- 不收集私人信息
- 不生成骚扰、垃圾营销或未经请求的私信
- 优先从公开模式里学习需求，而不是针对个人

默认请求间隔是 2 秒。如果你扫描更多 subreddit 和关键词组合，建议把间隔调大。

## 路线图

- 电商、SaaS、本地商家、自动化接单等关键词预设
- GitHub Actions 每日报告模式
- CSV 导出
- 更好的评论摘要
- 可选的 LLM 机会分析

