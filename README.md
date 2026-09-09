# SketchUp Architect

一个面向 Codex 智能体的建筑设计 skill：支持真实建筑案例研究、设计推理，以及可编辑的 SketchUp Desktop 建模。

本仓库以中文 README 为主；英文说明见 [README.en.md](README.en.md)，完整使用规范见 [USAGE.md](USAGE.md)。

演示：[塘间里 · 空间漫游](https://tangjianli-space.fxc060816.chatgpt.site)

## 它能做什么

- 将不完整的建筑 brief 转化为功能、面积账本、空间组织、结构概念、围护、流线和场地关系；
- 在方案生成前研究真实建筑案例，并记录原则如何被适配，而不是复制可辨认的形式；
- 在 SketchUp 主线程中使用 Ruby API，进行精确、语义化、可编辑的模型修改；
- 明确区分离线/静态检查，以及原生 SketchUp 几何检查、视觉 QA、保存重开和导出证据；
- 提供面积计划检查、官方资料检索、模型审计、受保护修订和离线测试工具。

## 快速安装

将仓库克隆到 Codex 的 skill 目录：

```sh
git clone https://github.com/Mentat-Uran/sketchup-architect-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
```

安装后可以显式调用 `$sketchup-architect`，也可以让智能体自动发现它。已有安装请先阅读 [通过智能体安装或更新](#通过智能体安装或更新)，不要直接覆盖目录。

## 通过智能体安装或更新

可以把下面这段话直接发给 Codex 或其他具备本机终端能力的编程智能体：

```text
请从 https://github.com/Mentat-Uran/sketchup-architect-skill 安装或更新
`sketchup-architect` Codex skill。

请使用标准目录 `${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect`。
如果目录已经存在，请先检查它是否是 Git checkout，以及是否有未提交修改；
有未提交修改或目录不是 Git checkout 时停止，不要删除或覆盖用户文件。
安装或更新完成后运行：

  python3 scripts/offline_checks.py
  ruby scripts/session_contract_test.rb

请报告实际安装路径、当前 Git revision 和检查结果。不要把官方 SketchUp
资料库复制进 skill；只有在确实需要本地 API 精确检索时，才配置
SKETCHUP_SOURCE_ROOT。
```

智能体也可以执行下面的安全流程：

```sh
SKILL_ROOT="${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
if [ -e "$SKILL_ROOT" ]; then
  if [ -d "$SKILL_ROOT/.git" ]; then
    git -C "$SKILL_ROOT" status --short
    if [ -n "$(git -C "$SKILL_ROOT" status --porcelain)" ]; then
      echo "拒绝更新存在未提交修改的 checkout：$SKILL_ROOT" >&2
      exit 1
    fi
    git -C "$SKILL_ROOT" pull --ff-only
  else
    echo "拒绝覆盖已有的非 Git 目录：$SKILL_ROOT" >&2
    exit 1
  fi
else
  git clone https://github.com/Mentat-Uran/sketchup-architect-skill.git "$SKILL_ROOT"
fi

cd "$SKILL_ROOT"
python3 scripts/offline_checks.py
ruby scripts/session_contract_test.rb
git rev-parse --short HEAD
```

安装完成后，建议开启新的智能体会话，或让智能体重新加载可用 skill。

## 使用规范摘要

完整规则在 [USAGE.md](USAGE.md)。最重要的约束是：

1. **先设计，再建模。** 从 brief 推导 program、面积、邻接、流线、结构、开口、材料和场地关系；不能把建筑做成只有外壳的装饰体块。
2. **新方案默认先研究真实案例。** 记录直接来源、访问日期、事实、图纸观察、解释和迁移到本项目的原则；明确适配和限制，不模仿可辨认形式。
3. **区分离线准备和原生 SketchUp 证据。** Python/Ruby 语法、离线检查通过，只能说明可进入 live test；不能据此声称几何、视觉、保存重开或导出已验证。
4. **Ruby 只在 SketchUp 主线程运行。** 系统 Ruby 和 API stubs 只能用于静态检查，不能当作 SketchUp 几何引擎；实际运行前要检查版本、活动模型、编辑上下文和模型身份。
5. **保护用户模型和文件。** 检查现有修改，使用版本化路径和明确的保存结果，不盲目覆盖、重复执行或清理无关内容。
6. **不把概念模型说成合规证明。** 结构、无障碍、消防、规划和当地法律要求必须标记为未验证或另行审查。

## 官方 SketchUp 资料库

仓库不会打包 SketchUp 官方手册、Git 仓库、PDF、issue 归档或 SQLite 索引。需要精确查询 API 时，请将官方资料库放在 skill 外部，并配置：

```sh
export SKETCHUP_SOURCE_ROOT=/path/to/sketchup-modeler-source
cd "${CODEX_HOME:-$HOME/.codex}/skills/sketchup-architect"
python3 scripts/source_library.py status
```

也可以在子命令前传入 `--root /path/to/sketchup-modeler-source`。资料库应来自官方 SketchUp/Trimble/GitHub 来源，并独立于本 skill 保存。

## 验证

下面的检查不会启动 SketchUp，也不代表原生几何或视觉 QA 已完成：

```sh
python3 scripts/offline_checks.py
ruby scripts/session_contract_test.rb
```

进行真实建模任务时，仍需使用当前 SketchUp Desktop 会话检查活动模型，并独立验证写出的 `.skp` 文件和所需导出物。

## 文件结构

```text
SKILL.md                  # 智能体实际加载的入口规则
agents/openai.yaml        # Codex 界面元数据
references/               # 建筑设计、案例研究、Ruby、QA 等按需参考
scripts/                  # 面积检查、模型审计、事务保护和离线测试
USAGE.md                  # 中文安装、使用、证据和交付规范
README.en.md              # 英文辅助说明
```

## 范围

本 skill 面向建筑概念设计和可编辑模型工作流；不替代结构工程、无障碍审查、规划审批、消防审查或当地法律合规判断。
