#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

GROUPS = [
    ("ai-data", "AI 与数据智能", "AI & Data Intelligence", [
        ("machine-learning", "机器学习", "Machine Learning", "https://pytorch.org/docs/stable/"),
        ("natural-language-processing", "自然语言处理", "Natural Language Processing", "https://huggingface.co/docs/transformers/"),
        ("computer-vision", "计算机视觉", "Computer Vision", "https://docs.opencv.org/"),
        ("multimodal-ai", "多模态人工智能", "Multimodal AI", "https://openai.github.io/openai-agents-python/"),
    ]),
    ("agent-engineering", "Agent 工程", "Agent Engineering", [
        ("agent-design", "Agent 设计", "Agent Design", "https://openai.github.io/openai-agents-python/agents/"),
        ("tool-use-mcp", "工具调用与 MCP", "Tool Use & MCP", "https://modelcontextprotocol.io/specification/"),
        ("workflow-orchestration", "工作流编排", "Workflow Orchestration", "https://openai.github.io/openai-agents-python/handoffs/"),
        ("evaluation-observability", "评估与可观测性", "Evaluation & Observability", "https://openai.github.io/openai-agents-python/tracing/"),
    ]),
    ("software", "软件工程", "Software Engineering", [
        ("backend-engineering", "后端工程", "Backend Engineering", "https://docs.python.org/3/"),
        ("frontend-engineering", "前端工程", "Frontend Engineering", "https://developer.mozilla.org/"),
        ("mobile-engineering", "移动端工程", "Mobile Engineering", "https://developer.android.com/docs"),
        ("devops-cloud", "DevOps 与云工程", "DevOps & Cloud", "https://docs.github.com/en/actions"),
    ]),
    ("data-systems", "数据与系统", "Data & Systems", [
        ("data-engineering", "数据工程", "Data Engineering", "https://spark.apache.org/docs/latest/"),
        ("database-engineering", "数据库工程", "Database Engineering", "https://www.postgresql.org/docs/"),
        ("distributed-systems", "分布式系统", "Distributed Systems", "https://kubernetes.io/docs/"),
        ("cybersecurity", "网络安全", "Cybersecurity", "https://owasp.org/www-project-top-ten/"),
    ]),
    ("fundamental-science", "基础科学", "Fundamental Science", [
        ("mathematics", "数学", "Mathematics", "https://www.ams.org/"),
        ("statistics", "统计学", "Statistics", "https://www.itl.nist.gov/div898/handbook/"),
        ("physics", "物理学", "Physics", "https://www.aps.org/"),
        ("chemistry", "化学", "Chemistry", "https://iupac.org/"),
    ]),
    ("life-health", "生命与健康", "Life & Health", [
        ("bioinformatics", "生物信息学", "Bioinformatics", "https://www.ncbi.nlm.nih.gov/"),
        ("multi-omics", "多组学", "Multi-omics", "https://www.ebi.ac.uk/training/"),
        ("spatial-omics", "空间组学", "Spatial Omics", "https://commonfund.nih.gov/hubmap"),
        ("clinical-research", "临床研究", "Clinical Research", "https://clinicaltrials.gov/"),
    ]),
    ("engineering", "工程技术", "Engineering", [
        ("robotics", "机器人", "Robotics", "https://docs.ros.org/"),
        ("control-engineering", "控制工程", "Control Engineering", "https://www.ieee.org/"),
        ("electronics", "电子工程", "Electronics", "https://www.ieee.org/"),
        ("mechanical-engineering", "机械工程", "Mechanical Engineering", "https://www.asme.org/"),
    ]),
    ("business", "商业与管理", "Business & Management", [
        ("product-management", "产品管理", "Product Management", "https://www.pmi.org/"),
        ("market-research", "市场研究", "Market Research", "https://www.esomar.org/"),
        ("financial-analysis", "金融分析", "Financial Analysis", "https://www.cfainstitute.org/"),
        ("operations-management", "运营管理", "Operations Management", "https://www.iso.org/standards.html"),
    ]),
    ("humanities", "人文学科", "Humanities", [
        ("history", "历史学", "History", "https://www.loc.gov/"),
        ("philosophy", "哲学", "Philosophy", "https://plato.stanford.edu/"),
        ("linguistics", "语言学", "Linguistics", "https://www.linguisticsociety.org/"),
        ("literature", "文学研究", "Literary Studies", "https://www.mla.org/"),
    ]),
    ("social-science", "社会科学", "Social Science", [
        ("sociology", "社会学", "Sociology", "https://www.asanet.org/"),
        ("economics", "经济学", "Economics", "https://www.oecd.org/economy/"),
        ("psychology", "心理学", "Psychology", "https://www.apa.org/"),
        ("education", "教育研究", "Education Research", "https://ies.ed.gov/"),
    ]),
    ("creative-communication", "创意与传播", "Creative & Communication", [
        ("ux-design", "用户体验设计", "UX Design", "https://www.w3.org/WAI/"),
        ("data-visualization", "数据可视化", "Data Visualization", "https://www.w3.org/TR/WCAG22/"),
        ("technical-writing", "技术写作", "Technical Writing", "https://developers.google.com/tech-writing"),
        ("digital-media", "数字媒体", "Digital Media", "https://www.w3.org/standards/"),
    ]),
    ("responsible-public", "公共与负责任技术", "Responsible & Public Technology", [
        ("law-compliance", "法律与合规", "Law & Compliance", "https://eur-lex.europa.eu/"),
        ("public-policy", "公共政策", "Public Policy", "https://www.oecd.org/"),
        ("sustainability", "可持续发展", "Sustainability", "https://www.ipcc.ch/"),
        ("ai-safety-governance", "AI 安全与治理", "AI Safety & Governance", "https://www.nist.gov/itl/ai-risk-management-framework"),
    ]),
]

TASKS = [
    ("problem-framing", "问题界定", "Problem Framing", "把模糊需求转化为可验证的问题、边界、假设与停止条件", "需求说明、利益相关者目标、约束", "问题陈述、假设清单、范围边界", "由领域专家检查问题是否可证伪且没有偷换目标", "medium"),
    ("literature-scan", "文献与知识扫描", "Literature & Knowledge Scan", "系统检索权威资料，建立概念、方法、争议与证据地图", "关键词、时间范围、来源层级", "检索式、证据表、研究空白", "复核检索覆盖率、来源层级与反例", "low"),
    ("source-verification", "来源核验", "Source Verification", "追溯事实、数字和引文到一手来源并标记不确定性", "候选事实、网页、论文或制度文本", "逐条证据链、发布日期与可信度", "随机抽查原文位置和语义一致性", "medium"),
    ("data-acquisition", "数据获取", "Data Acquisition", "制定合法、可复现的数据采集与版本固定方案", "数据需求、许可、接口或实验条件", "数据清单、采集脚本说明、许可记录", "重放采集流程并核对样本量与哈希", "high"),
    ("data-cleaning", "数据清洗", "Data Cleaning", "识别缺失、异常、重复、泄漏和编码问题，保留审计轨迹", "原始数据、质量规则", "清洗数据、变更日志、异常报告", "差分检查、统计分布检查和人工抽样", "medium"),
    ("schema-design", "结构与模式设计", "Schema Design", "为数据、知识或任务状态设计清晰且可演进的模式", "实体、关系、约束、查询需求", "模式定义、字段字典、迁移策略", "用典型和极端样例验证约束", "medium"),
    ("exploratory-analysis", "探索性分析", "Exploratory Analysis", "在不夸大因果的前提下发现分布、关联、分层和异常", "已质控数据、分析问题", "图表、描述统计、候选解释", "检查多重比较、分层偏差和替代解释", "medium"),
    ("baseline-construction", "基线构建", "Baseline Construction", "建立简单、强健、可复现的比较基线，避免只和弱方法比较", "任务定义、数据拆分、历史方法", "基线实现、参数、运行记录", "独立复现并核对数据泄漏", "medium"),
    ("experiment-design", "实验设计", "Experiment Design", "事前定义变量、对照、样本量、随机化和失败判据", "假设、资源、伦理与现实约束", "实验协议、功效分析、预注册要点", "由独立审阅者检查混杂与可重复性", "high"),
    ("metric-selection", "指标选择", "Metric Selection", "选择与真实目标一致的主指标、护栏指标和分层指标", "目标函数、失败成本、用户或科学需求", "指标卡、计算方式、阈值理由", "用反例测试指标是否可被投机优化", "medium"),
    ("tool-selection", "工具选择", "Tool Selection", "依据能力、权限、成本、可观测性和锁定风险选择工具", "任务、可用工具、权限和预算", "工具比较矩阵、选型结论、回退方案", "用小样本基准验证关键能力", "medium"),
    ("workflow-orchestration", "工作流编排", "Workflow Orchestration", "把检索、计算、写作、审阅和人工决策组合成可恢复流程", "任务图、工具契约、状态与依赖", "工作流图、接口、重试和检查点", "注入故障并验证恢复、幂等与审计", "high"),
    ("protocol-prompt-design", "协议与提示设计", "Protocol & Prompt Design", "把意图写成结构化指令、输入输出契约和拒绝条件", "角色、输入、输出模式、失败案例", "协议模板、示例、边界测试", "用对抗样例和跨模型测试稳定性", "medium"),
    ("human-review", "人工复核设计", "Human Review Design", "明确哪些节点必须由具备责任和资质的人批准", "风险等级、决策影响、审阅者能力", "复核清单、升级路径、责任矩阵", "演练误报、漏报和意见冲突", "high"),
    ("error-analysis", "误差分析", "Error Analysis", "对失败样本分型并定位数据、方法、工具或目标层面的根因", "预测、输出、日志、人工标注", "错误分类、根因假设、修复优先级", "盲审样本并验证分类一致性", "medium"),
    ("uncertainty-assessment", "不确定性评估", "Uncertainty Assessment", "量化数据、模型、测量与外推不确定性，避免伪精确", "估计值、分布假设、样本与模型", "区间、敏感性分析、适用边界", "覆盖率、校准和极端情景检查", "high"),
    ("reproducibility", "复现与可重复性", "Reproducibility", "固定环境、数据、随机性和运行元数据，使第三方可重放", "代码、数据、依赖、参数", "锁定文件、运行清单、复现说明", "在干净环境完整重跑", "medium"),
    ("risk-assessment", "风险评估", "Risk Assessment", "识别技术、社会、法律、安全和组织风险及其触发条件", "系统边界、使用者、威胁与影响", "风险登记册、严重度、缓解与责任人", "红队评审并检查剩余风险", "high"),
    ("privacy-review", "隐私审查", "Privacy Review", "最小化个人数据，检查同意、用途限制、保留与再识别风险", "数据流、身份字段、权限和政策", "数据保护影响清单、删除与访问策略", "隐私负责人和领域负责人联合批准", "critical"),
    ("security-review", "安全审查", "Security Review", "建立威胁模型，验证身份、授权、输入边界、供应链和日志安全", "架构、资产、信任边界和攻击者模型", "威胁模型、测试结果、修复门槛", "安全负责人批准且高危问题清零", "critical"),
    ("cost-optimization", "成本优化", "Cost Optimization", "在不牺牲质量与安全护栏的前提下降低计算、时间和人工成本", "成本明细、质量曲线、服务级目标", "成本模型、优化方案、回退阈值", "用同一评估集比较质量成本前沿", "medium"),
    ("performance-optimization", "性能优化", "Performance Optimization", "定位延迟、吞吐、内存或实验效率瓶颈，避免无证据调参", "性能基线、剖析日志、负载模型", "瓶颈报告、优化补丁、基准结果", "重复基准并报告方差和回归", "medium"),
    ("report-drafting", "报告撰写", "Report Drafting", "把方法、证据、局限和建议组织成可审计的专业报告", "分析产物、证据表、读者需求", "结构化报告、图表说明、引用", "事实核验、反向大纲和局限检查", "low"),
    ("decision-brief", "决策简报", "Decision Brief", "把多方案的收益、成本、风险和不可逆性压缩为可行动决策", "方案、证据、约束、利益相关者", "一页简报、推荐方案、触发器与退出条件", "由最终责任人签字并记录异议", "high"),
    ("maintenance-handoff", "维护与交接", "Maintenance & Handoff", "定义所有权、监控、更新节奏、失效信号和退役流程", "交付物、依赖、运行风险、团队结构", "维护手册、值班与变更流程、退役标准", "交接演练和恢复演练通过", "medium"),
]

HIGH_STAKES = {"cybersecurity", "clinical-research", "financial-analysis", "law-compliance", "public-policy", "ai-safety-governance", "psychology"}
FIELDS = ["id", "record_type", "maturity", "group_slug", "group_zh", "group_en", "domain_slug", "domain_zh", "domain_en", "task_slug", "title_zh", "title_en", "description_zh", "inputs", "outputs", "validation", "risk_level", "human_gate", "source_url"]


def write(path: str | Path, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n", encoding="utf-8")


def risk_for(domain_slug: str, task_slug: str, base: str) -> str:
    risk = base
    if domain_slug in HIGH_STAKES and task_slug in {"data-acquisition", "experiment-design", "uncertainty-assessment", "human-review", "risk-assessment", "decision-brief"}:
        risk = "critical" if task_slug in {"human-review", "decision-brief"} else "high"
    return risk


def human_gate(risk: str) -> str:
    if risk == "critical":
        return "必须由具备资质的领域负责人批准；禁止无人值守自动执行，并记录批准人、证据与回滚条件。"
    if risk == "high":
        return "提交领域负责人复核；在影响外部人员、资金、健康、安全或合规前必须显式批准。"
    return "按抽样规则复核；发现越界、低置信度或来源冲突时升级人工处理。"


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group_slug, group_zh, group_en, domains in GROUPS:
        for domain_slug, domain_zh, domain_en, source_url in domains:
            for index, (task_slug, task_zh, task_en, purpose, inputs, outputs, validation, base_risk) in enumerate(TASKS, start=1):
                risk = risk_for(domain_slug, task_slug, base_risk)
                rows.append({
                    "id": f"rof-{domain_slug}-{index:02d}",
                    "record_type": "workflow-blueprint",
                    "maturity": "blueprint",
                    "group_slug": group_slug,
                    "group_zh": group_zh,
                    "group_en": group_en,
                    "domain_slug": domain_slug,
                    "domain_zh": domain_zh,
                    "domain_en": domain_en,
                    "task_slug": task_slug,
                    "title_zh": f"{domain_zh}：{task_zh}",
                    "title_en": f"{domain_en}: {task_en}",
                    "description_zh": f"面向{domain_zh}场景，{purpose}。该条目是任务工作流蓝图，不代表已安装或完成安全审计的插件。",
                    "inputs": inputs,
                    "outputs": outputs,
                    "validation": validation,
                    "risk_level": risk,
                    "human_gate": human_gate(risk),
                    "source_url": source_url,
                })
    return rows


def render_domain(rowset: list[dict[str, str]]) -> str:
    first = rowset[0]
    lines = [
        f"# {first['domain_zh']} / {first['domain_en']}", "",
        f"> 所属主题群：**{first['group_zh']}**。共 25 条可组合的任务工作流蓝图。", "",
        f"权威入口：<{first['source_url']}>", "",
        "这些条目强调输入、输出、验证、风险和 Human Gate；它们不是未经验证的自动化承诺。", "",
        "| ID | Skill 蓝图 | 风险 | 核心验证 |", "|---|---|---|---|",
    ]
    for row in rowset:
        lines.append(f"| `{row['id']}` | **{row['title_zh']}**<br>{row['description_zh']} | `{row['risk_level']}` | {row['validation']} |")
    lines += ["", "## 组合建议", "", "先从问题界定、来源核验和基线构建开始；再按任务需要组合工具选择、工作流编排、误差分析与复现。任何高风险或关键风险步骤都不得绕过人工批准。"]
    return "\n".join(lines)


def render_group(rows: list[dict[str, str]]) -> str:
    first = rows[0]
    domains = sorted({(r['domain_slug'], r['domain_zh'], r['domain_en']) for r in rows})
    lines = [f"# {first['group_zh']} / {first['group_en']}", "", f"本主题群包含 **{len(rows)}** 条蓝图，覆盖四个专业方向。", ""]
    for slug, zh, en in domains:
        lines.append(f"- [{zh} / {en}](../categories/{slug}.md)")
    return "\n".join(lines)


def generate_catalog(rows: list[dict[str, str]]) -> None:
    path = ROOT / "skills/catalog.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    grouped: dict[str, list[dict[str, str]]] = {}
    group_rows: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["domain_slug"], []).append(row)
        group_rows.setdefault(row["group_slug"], []).append(row)
    for slug, rowset in grouped.items():
        write(f"skills/categories/{slug}.md", render_domain(rowset))
    for slug, rowset in group_rows.items():
        write(f"skills/groups/{slug}.md", render_group(rowset))
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(rows),
        "domain_count": len(grouped),
        "group_count": len(group_rows),
        "record_type": "workflow-blueprint",
        "maturity": "blueprint",
        "risk_distribution": dict(Counter(r["risk_level"] for r in rows)),
        "truth_boundary": "Catalog records are workflow blueprints, not claims that 1,200 plugins are installed, executable, or audited.",
    }
    write("skills/catalog_metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    index = ["# Skill 知识地图", "", "RoadOfFlower 将 1,200 条任务蓝图按 12 个主题群、48 个专业方向组织。", "", "## 主题群", ""]
    for group_slug, group_zh, group_en, _ in GROUPS:
        index.append(f"- [{group_zh} / {group_en}](groups/{group_slug}.md) — 100 条")
    index += ["", "## 本地搜索", "", "```bash", "python scripts/skill_finder.py '空间组学 质控' --limit 8", "python scripts/skill_finder.py --domain cybersecurity --risk critical", "```", "", "> 真实性边界：目录中的条目均为 `workflow-blueprint / blueprint`，不冒充已安装插件。"]
    write("skills/README.md", "\n".join(index))


def generate_scripts() -> None:
    finder = r'''#!/usr/bin/env python3
import argparse, csv, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def tokens(text): return [t for t in re.split(r"[^\w\u4e00-\u9fff]+", text.lower()) if t]
def main():
    p=argparse.ArgumentParser(description="Search RoadOfFlower Agent Skill blueprints")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--domain")
    p.add_argument("--risk", choices=["low","medium","high","critical"])
    p.add_argument("--limit", type=int, default=10)
    args=p.parse_args()
    with (ROOT/"skills/catalog.csv").open(encoding="utf-8") as f: rows=list(csv.DictReader(f))
    q=tokens(args.query); ranked=[]
    for row in rows:
        if args.domain and row["domain_slug"] != args.domain: continue
        if args.risk and row["risk_level"] != args.risk: continue
        hay=" ".join(row.values()).lower()
        score=sum(4 if t in row["title_zh"].lower() or t in row["title_en"].lower() else 1 for t in q if t in hay)
        if q and score == 0: continue
        ranked.append((score,row))
    ranked.sort(key=lambda x:(-x[0],x[1]["id"]))
    for _,r in ranked[:args.limit]:
        print(f"{r['id']} | {r['title_zh']} | risk={r['risk_level']}\n  {r['description_zh']}\n  validate: {r['validation']}\n  source: {r['source_url']}")
if __name__ == "__main__": main()
'''
    validator = r'''#!/usr/bin/env python3
import csv, json, re, sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; errors=[]
with (ROOT/"skills/catalog.csv").open(encoding="utf-8") as f: rows=list(csv.DictReader(f))
if len(rows)!=1200: errors.append(f"expected 1200 rows, got {len(rows)}")
for key,expected in [("id",1200),("title_zh",1200),("title_en",1200)]:
    if len({r[key] for r in rows})!=expected: errors.append(f"{key} not unique")
if len({r['domain_slug'] for r in rows})!=48: errors.append("expected 48 domains")
if len({r['group_slug'] for r in rows})!=12: errors.append("expected 12 groups")
for r in rows:
    if not re.fullmatch(r"rof-[a-z0-9-]+-\d{2}", r['id']): errors.append(f"bad id {r['id']}")
    if r['record_type']!='workflow-blueprint' or r['maturity']!='blueprint': errors.append(f"truth boundary missing {r['id']}")
    if r['risk_level'] in {'high','critical'} and len(r['human_gate'])<10: errors.append(f"human gate missing {r['id']}")
    if r['risk_level']=='critical' and '禁止无人值守' not in r['human_gate']: errors.append(f"critical unattended ban missing {r['id']}")
    if not r['source_url'].startswith('https://'): errors.append(f"bad source {r['id']}")
for slug in {r['domain_slug'] for r in rows}:
    if not (ROOT/f"skills/categories/{slug}.md").exists(): errors.append(f"category page missing {slug}")
meta=json.loads((ROOT/"skills/catalog_metadata.json").read_text(encoding="utf-8"))
if meta.get('record_count')!=1200: errors.append('metadata count mismatch')
if errors:
    print("FAIL"); [print("-",e) for e in errors[:50]]; sys.exit(1)
print(f"PASS: {len(rows)} records, 48 domains, 12 groups; risk={dict(Counter(r['risk_level'] for r in rows))}")
'''
    renderer = r'''#!/usr/bin/env python3
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"skills/catalog.csv").open(encoding="utf-8") as f: rows=list(csv.DictReader(f))
by={}
for r in rows: by.setdefault(r['domain_slug'],[]).append(r)
for slug,rs in by.items():
    first=rs[0]
    lines=[f"# {first['domain_zh']} / {first['domain_en']}","",f"> 所属主题群：**{first['group_zh']}**。共 25 条可组合的任务工作流蓝图。","",f"权威入口：<{first['source_url']}>","","| ID | Skill 蓝图 | 风险 | 核心验证 |","|---|---|---|---|"]
    for r in rs: lines.append(f"| `{r['id']}` | **{r['title_zh']}**<br>{r['description_zh']} | `{r['risk_level']}` | {r['validation']} |")
    lines += ["","## 组合建议","","先从问题界定、来源核验和基线构建开始；高风险步骤必须通过 Human Gate。"]
    (ROOT/f"skills/categories/{slug}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"rendered {len(by)} category pages")
'''
    write("scripts/skill_finder.py", finder)
    write("scripts/validate_catalog.py", validator)
    write("scripts/render_catalog.py", renderer)


def generate_docs() -> None:
    docs = {
        "01-agent-basics.md": ("Agent 入门：先理解循环，再谈自治", "Agent 不是会聊天的万能机器人，而是在约束中反复执行观察—判断—行动—验证的系统。可靠 Agent 至少包含目标、状态、工具契约、停止条件、日志和人工升级路径。初学者先做低风险、可立即验证的单一任务，不要从全自动研究员起步。"),
        "02-tool-selection.md": ("工具选择：能力不等于适用性", "同时比较数据可达性、读写权限、确定性、延迟、成本、可观测性、失败模式和锁定风险。优先结构化 API；任何发送、删除、付款和公开发布工具都默认 Human Gate。"),
        "03-workflow-composition.md": ("工作流组合：把聪明拆成可检查步骤", "将检索、核验、计算、写作和审阅拆成职责单一节点，使用显式状态传递数据。每个节点声明前置条件、产物、验证和失败去向，并设计幂等、有限重试、检查点与人工升级。"),
        "04-agent-customization.md": ("Agent 定制：角色、权限、记忆与交接", "定制重点不是人格修辞，而是决策边界。定义职责与非职责、工具、预算、最大步骤、停止与拒绝条件。未经验证的输出不得写入长期记忆，多 Agent 交接必须携带证据、风险和未决问题。"),
        "05-skill-customization.md": ("Skill 定制：把经验写成可复用契约", "高质量 Skill 描述何时使用、需要什么、产生什么、如何验证和何时停止。包含触发条件、非适用情形、输入、步骤、输出、质量门、权限、风险、示例和维护者。"),
        "06-result-verification.md": ("结果验证：证据先于结论", "事实任务核对一手来源；代码运行测试；数据检查模式与分布；研究检查基线、功效、消融和复现；决策检查假设、反例与不可逆成本。机器硬检查与人工语义审查缺一不可。"),
        "07-risk-control.md": ("风险控制：最小权限、分级门控、可回滚", "按影响与可逆性分为 low、medium、high、critical。高风险需负责人复核，关键风险禁止无人值守。默认最小权限、读写分离、敏感数据最小化，并对提示注入、越权、供应链和数据外泄建模。"),
        "08-practice-path.md": ("实践路径：四周完成第一个可信 Agent", "第 1 周手工完成并记录决策点；第 2 周自动化一个步骤并加测试；第 3 周加入来源核验、日志和 Human Gate；第 4 周用至少 30 个样例评估成功率、成本、延迟和失败严重度。"),
        "09-template-library.md": ("模板库：从空白页转向受控复用", "仓库提供 Skill、Workflow、Evaluation Rubric、Run Log 和 Risk Review 模板。模板让隐含假设显式化；事故、评审分歧和复现失败都应反哺模板版本。"),
    }
    diagram = """```mermaid
flowchart LR
A[任务与边界] --> B[选择工具或 Skill]
B --> C[执行并记录]
C --> D[独立验证]
D --> E{风险等级}
E -- high/critical --> F[Human Gate]
E -- low/medium --> G[抽样复核]
F --> H[交付或回滚]
G --> H
```"""
    for filename, (title, body) in docs.items():
        write(f"docs/{filename}", f"# {title}\n\n{body}\n\n{diagram}\n\n## 实践检查\n\n- [ ] 输入、输出与停止条件明确\n- [ ] 存在可独立运行的验证\n- [ ] 高风险步骤配置 Human Gate\n- [ ] 失败后可以定位、恢复和回滚")


def generate_templates() -> None:
    templates = {
        "skill-template.md": "# Skill 模板\n\n## 触发条件\n\n## 不适用情形\n\n## 输入与前置条件\n\n## 步骤\n\n## 输出契约\n\n## 验证与质量门\n\n## 错误处理与回滚\n\n## 权限、隐私与风险\n\n## 示例与反例\n\n## 维护者、版本与变更记录",
        "workflow-template.md": "# Workflow 模板\n\n## 目标与停止条件\n\n## 状态模式\n\n## 节点与接口\n\n## 工具权限\n\n## 重试、超时与幂等\n\n## Human Gate\n\n## 可观测性\n\n## 回滚与恢复演练",
        "evaluation-rubric.md": "# Evaluation Rubric\n\n| 维度 | 权重 | 通过标准 | 失败示例 |\n|---|---:|---|---|\n| 正确性 | 30% | 与独立证据一致 | 事实或计算错误 |\n| 完整性 | 15% | 覆盖关键约束 | 遗漏反例 |\n| 可追溯性 | 20% | 可回到来源或运行记录 | 无证据断言 |\n| 安全性 | 20% | 权限与 Human Gate 生效 | 越权自动执行 |\n| 成本与延迟 | 10% | 满足预算和服务目标 | 无限制循环 |\n| 可维护性 | 5% | 文档、测试、所有权完整 | 无法接管 |",
        "run-log.md": "# Run Log\n\n- Run ID：\n- 时间与版本：\n- 任务与输入哈希：\n- 使用工具和权限：\n- 关键中间状态：\n- 输出与证据：\n- 验证结果：\n- 人工修改与批准：\n- 成本、延迟与重试：\n- 失败、根因与后续行动：",
        "risk-review.md": "# Risk Review\n\n## 系统边界与使用者\n\n## 资产、威胁与滥用场景\n\n## 数据与隐私\n\n## 权限和外部写操作\n\n## 严重度与可逆性\n\n## Human Gate 与责任人\n\n## 缓解措施、剩余风险与验收证据\n\n## 停止、回滚和退役条件",
    }
    for name, content in templates.items(): write(f"templates/{name}", content)


def generate_project_docs(rows: list[dict[str, str]]) -> None:
    write("ReadMe.md", """# 🌸 RoadOfFlower — Agent Skill 知识地图与实践教程

> 愿每个人都能沿着一条开满花的路，把模糊理想拆成可学习、可验证、可共同维护的能力。

RoadOfFlower 的主线是 **Agent Skill**：提供 1,200 条任务工作流蓝图、跨学科索引、Agent 入门与定制教程、模板、检索工具、验证与风险控制规范，帮助研究者、工程师和其他知识工作者打破 Agent 信息差。

[![Catalog](https://img.shields.io/badge/Skill_Blueprints-1200-blue)](skills/README.md)
[![Domains](https://img.shields.io/badge/Domains-48-success)](skills/README.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 先说清楚：1,200 条是什么

全部明确标记为 `workflow-blueprint / blueprint`，包含任务、输入、输出、验证、风险、Human Gate 和权威入口。**它们不是 1,200 个已经安装、可直接执行或完成安全审计的插件。**

## 从哪里开始

1. [浏览 Skill 地图](skills/README.md)。
2. 运行 `python scripts/skill_finder.py "空间组学 质控" --limit 8`。
3. 阅读 [Agent 入门](docs/01-agent-basics.md) 与 [结果验证](docs/06-result-verification.md)。
4. 复制 [Skill 模板](templates/skill-template.md)，从低风险真实任务开始。
5. 提交前运行 `python scripts/validate_catalog.py` 与 `python -m unittest discover -v`。

## 学习与执行闭环

```mermaid
flowchart LR
A[真实任务] --> B[检索 Skill 蓝图]
B --> C[选择工具与权限]
C --> D[组合工作流]
D --> E[运行与记录]
E --> F[机器验证]
F --> G{风险等级}
G -- low/medium --> H[抽样人工复核]
G -- high/critical --> I[强制 Human Gate]
H --> J[沉淀为可维护 Skill]
I --> J
J --> B
```

## 项目创新与实际意义

- **任务优先而非品牌优先**：先描述问题，再映射工具，降低营销和生态锁定造成的信息差。
- **跨学科统一接口**：AI、软件、科学、健康、工程、商业、人文与公共治理共享输入—输出—验证—风险结构。
- **真实性边界**：将蓝图、已验证 Skill 和已部署工具分开，禁止用数量冒充成熟度。
- **验证与风险内建**：每条蓝图自带质量门和 Human Gate，关键风险任务禁止无人值守执行。
- **人机共同维护**：机器检查格式、数量和一致性，人类负责语义、领域责任和价值判断。

## 对 LED 的祝愿

真诚祝愿 LED 在商业世界里成长为值得长期信任的计算机技术大牛：不只追逐新技术，也能判断什么值得做；不只写出漂亮代码，也能建立可靠产品、健康团队和可持续商业。愿技术深度、商业清醒、责任感与自由始终同行，做成真正帮助人的事业。🌸

## 许可证

MIT。外部资源仍遵循各自许可证与使用条款。""")
    write("LICENSE", """MIT License

Copyright (c) 2026 RoadOfFlower contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""")
    write("CONTRIBUTING.md", """# 贡献指南

1. 先说明用户任务、目标人群和信息差，而不是先指定产品。
2. 新 Skill 必须包含触发条件、输入、输出、验证、风险、Human Gate 和来源。
3. `blueprint` 不得描述为已部署或已审计；成熟度变化必须附测试证据。
4. 高风险与关键风险内容需要领域审阅；禁止绕过权限、隐私或安全门。
5. 更新 CSV 后运行渲染器、校验器和测试。

```bash
python scripts/render_catalog.py
python scripts/validate_catalog.py
python -m unittest discover -v
```""")
    write("GOVERNANCE.md", """# 治理与维护

- 目录维护者负责结构、自动检查和发布节奏。
- 领域维护者负责术语、来源、验证和风险等级。
- 安全与隐私审阅者可阻止高风险变更合并。
- 每季度抽查链接、陈旧条目、重复项和风险漂移。
- 提升成熟度必须提供可重复证据。""")
    write("ROADMAP.md", """# 路线图

## Milestone 1 — 可发现
1,200 条蓝图、48 个领域、CLI 检索、稳定 ID。

## Milestone 2 — 可验证
为高频蓝图补充公开测试集、基准和版本化运行记录。

## Milestone 3 — 可组合
提供跨工具工作流、状态模式、失败注入与恢复演练。

## Milestone 4 — 可持续
建立领域维护者网络、链接巡检、成熟度晋级和退役机制。""")
    write("PROJECT_CHARTER.md", """# 项目章程

**使命**：降低 Agent 知识与实践门槛，使跨学科工作者能够发现、组合、验证和维护可靠 Skill。

**非目标**：不宣称目录条目均可执行；不托管秘密凭据；不鼓励绕过专业资质；不以自动化替代责任人。

**成功标准**：新人能在 15 分钟内找到候选蓝图，在一天内搭建低风险最小闭环，并能说明证据、失败和风险。""")
    write("ECOSYSTEM.md", """# 官方生态入口

- OpenAI Agents SDK：<https://openai.github.io/openai-agents-python/>
- Model Context Protocol：<https://modelcontextprotocol.io/specification/>
- GitHub Actions：<https://docs.github.com/en/actions>
- Python：<https://docs.python.org/3/>
- OWASP Top 10：<https://owasp.org/www-project-top-ten/>
- NIST AI Risk Management Framework：<https://www.nist.gov/itl/ai-risk-management-framework>

外部链接用于学习与发现，不代表对第三方实现、许可证或安全性的背书。""")
    write("RELEASE_REPORT.md", f"""# 发布报告

- 目录记录：{len(rows)}
- 专业方向：48
- 主题群：12
- 教学章节：9
- 模板：5
- 类型：`workflow-blueprint`
- 成熟度：`blueprint`

## 发布门

- 数量、唯一性和字段契约通过。
- 48 个专业页存在。
- high/critical 条目均有 Human Gate。
- critical 条目明确禁止无人值守执行。
- 搜索、渲染、校验和 unittest 可运行。

本发布建立可信目录基础，不声称 1,200 个外部 Skill 已逐一执行或安全审计。""")
    write(".agents/skills/road-of-flower-curator/SKILL.md", """# RoadOfFlower Curator Skill

## Use when
维护、检索、审阅或扩展 RoadOfFlower Agent Skill 目录时使用。

## Workflow
1. 明确用户任务和领域。
2. 运行 `scripts/skill_finder.py` 找候选蓝图。
3. 检查来源、输入输出、验证和风险。
4. 修改 CSV 并运行渲染器。
5. 运行校验器和测试。
6. 在 PR 中报告证据、限制和 Human Gate。

## Never
- 不把 blueprint 冒充已安装插件。
- 不在 critical 任务中允许无人值守自动执行。
- 不删除来源、验证或风险字段来追求数量。""")


def generate_tests() -> None:
    write("tests/test_catalog.py", r'''import csv, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/"skills/catalog.csv").open(encoding="utf-8") as f: cls.rows=list(csv.DictReader(f))
    def test_counts(self):
        self.assertEqual(len(self.rows),1200); self.assertEqual(len({r['domain_slug'] for r in self.rows}),48); self.assertEqual(len({r['group_slug'] for r in self.rows}),12)
    def test_unique_ids_and_titles(self):
        self.assertEqual(len({r['id'] for r in self.rows}),1200); self.assertEqual(len({r['title_zh'] for r in self.rows}),1200); self.assertEqual(len({r['title_en'] for r in self.rows}),1200)
    def test_truth_boundary(self): self.assertTrue(all(r['record_type']=='workflow-blueprint' and r['maturity']=='blueprint' for r in self.rows))
    def test_human_gates(self):
        for r in self.rows:
            if r['risk_level'] in {'high','critical'}: self.assertGreater(len(r['human_gate']),10)
            if r['risk_level']=='critical': self.assertIn('禁止无人值守',r['human_gate'])
    def test_pages_and_docs(self):
        self.assertEqual(len(list((ROOT/'skills/categories').glob('*.md'))),48); self.assertEqual(len(list((ROOT/'docs').glob('*.md'))),9); self.assertEqual(len(list((ROOT/'templates').glob('*.md'))),5)
    def test_search(self):
        out=subprocess.check_output([sys.executable,str(ROOT/'scripts/skill_finder.py'),'空间组学','--limit','3'],text=True); self.assertIn('空间组学',out)
if __name__=='__main__': unittest.main()
''')
    write("tests/__init__.py", "")
    write(".github/workflows/validate.yml", """name: Validate Skill Map
on:
  pull_request:
  push:
    branches: [main, agent/skill-map-1200]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python scripts/validate_catalog.py
      - run: python -m unittest discover -v
      - run: python scripts/skill_finder.py '空间组学 质控' --limit 5
""")


def main() -> None:
    rows = build_rows()
    assert len(rows) == 1200
    generate_catalog(rows)
    generate_scripts()
    generate_docs()
    generate_templates()
    generate_project_docs(rows)
    generate_tests()
    print(f"generated {len(rows)} Skill blueprints in {ROOT}")

if __name__ == "__main__":
    main()
