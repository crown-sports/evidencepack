# EvidencePack

从很长的工具输出里挑出有用原文，再检查回答有没有引用对。

[English](README.md) · [接入说明](docs/integration.md) · [v0.2.0 预发布](https://github.com/crown-sports/evidencepack/releases/tag/v0.2.0)

![实际 quickstart 结果：配置与运行状态原文被选入证据包，正确引文通过，改写端口后被拒绝](docs/assets/pack-verify.png)

*生成的日志，真实的 `pack()` 和 `verify()` 输出；没有调用模型。[本次输出](docs/assets/readme-demo.json)。*

工具返回几千行日志，真正的错误藏在中间，模型回答时又把端口抄错了。
EvidencePack 保存完整输出，按预算选择完整片段，再核对引文是否来自这次交给模型的
证据包。它是接到现有 Agent 里的 Python 库。

## 不接模型，先跑一下

需要 Python 3.11 以上：

```sh
git clone --branch v0.2.0 https://github.com/crown-sports/evidencepack.git
cd evidencepack
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m examples.quickstart
python -m examples.answer_gate
```

第一个例子把 **55,945 字节**的生成日志选成 **2,000 字节预算以内**的证据包。
`upstream_port=8080` 通过，改成 `9999` 就返回 `quote_mismatch`。
第二个例子先接受回答，再拒绝新增了无引用结论的回答。
`python -m examples.diagnose` 还会用规则修复器，把一个真实本地 HTTP 故障从 **502 修到 200**。

## 接到一个工具外面

```python
from evidencepack import EvidenceService, Scope, SQLiteRepository

service = EvidenceService(SQLiteRepository("vault.sqlite"), Scope("local", "case-1"))
artifact = service.capture("probe", "ERROR connection refused\n")
pack = service.pack("Why did the probe fail?", [artifact.id], budget=2048)
print(pack.to_json())  # 把这份内容交给模型。
excerpt = pack.excerpts[0]
verdict = service.verify(pack.receipt, excerpt.citation, "connection refused")
assert verdict.valid
service.release(pack.receipt)
```

把字符串换成工具的真实输出。回执留在宿主中，让模型返回引用编号和逐字引文。
用 `service.verify_answer(receipt, claims)` 可以检查整个结构化回答：缺少引用或任一引文
不匹配，就拒绝回答。[结论格式和中间件示例](docs/integration.md)。

CLI 和可选 MCP 适配器使用同一套检查。预算包含序列化后的证据和元数据，默认按 UTF-8
字节计量，也可接模型实际使用的 tokenizer。[计量、重读和回收](docs/product.md)。

## 通过检查说明什么

只说明引文确实出现在本次证据包的未改动原文中，**不证明推理正确**。
宿主要把完整回答交给门禁，并执行拒绝决定。作用域标签不是身份认证，证据库应放在
Agent 无法直接改写的位置。

公开的本地故障实验中，平均 **99,689 字节**输入选成 **1,847 字节**证据包。
BM25 与 EvidencePack 的模型总成绩相同。[输入、对照、失败情况与复现命令](docs/results.md)。

[调试第一个证据包](docs/troubleshooting.md) · [设计](docs/design.md) · [相关工作](docs/related-work.md) · [参与开发](CONTRIBUTING.md) · MIT 许可证
