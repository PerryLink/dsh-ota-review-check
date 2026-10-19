# dsh-ota-review-check — Verificação do registo de respostas a avaliações em linha

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-ota-review-check` lê um registo de avaliações em linha com as respetivas respostas —o cabeçalho do estabelecimento mais uma linha por avaliação— e verifica a completude e o fecho desse próprio registo: se cada avaliação regista o seu conteúdo ou uma pontuação, se uma avaliação respondida traz data de resposta e autor da resposta, se a resposta não é anterior à avaliação, se uma avaliação sem resposta cai dentro do prazo que o próprio registo declara, se o tipo de problema vem do vocabulário da sua instituição e se os números de avaliação são únicos.

## Install

```sh
dsh plugin --profile <name> add dsh-ota-review-check
dsh --profile <name> --dump-config | grep 'dsh-ota-review-check'
```

## Como é a saída

![Terminal demo of dsh-ota-review-check: real output over its OT-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-ota-review-check/main/docs/assets/dsh-ota-review-check-hero.png)

![Animated terminal demo of dsh-ota-review-check](https://raw.githubusercontent.com/PerryLink/dsh-ota-review-check/main/docs/assets/dsh-ota-review-check-demo.gif)

Saída real deste plugin sobre o seu próprio fixture de teste `OT-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Uma linha não tem preenchidos nem 点评内容 nem 评分. O que é reportado? | `OT-001` reporta essa linha: cada avaliação tem de registar pelo menos um dos dois campos, `content` ou `score`. Verifica apenas que um deles está preenchido; não julga se o conteúdo da avaliação é verdadeiro nem se se trata de uma avaliação maliciosa. |
| Uma linha está marcada 已回复, mas as células 回复日期 e 回复人 estão vazias. O que é reportado? | `OT-002` reporta a falta de `repliedAt` em qualquer linha cujo `replyStatus` tenha um dos valores configurados (`是`, `Y`, `yes`, `true`, `已回复`, `√`), e `OT-005` exige que `replier` esteja preenchido em qualquer linha que traga a coluna 回复人, pelo que uma célula vazia é reportada mesmo numa linha marcada 未回复. Ambas verificam apenas que a célula está preenchida: nenhuma diz se a resposta foi atempada ou adequada. |
| No nosso registo a coluna 回复期限 está vazia em todas as linhas. A verificação assume um prazo de 24 ou 48 horas? | Não. O plugin não incorpora o prazo de nenhuma plataforma: sem um valor em `replyDeadline` não há nada a comparar e `OT-003` aparece em `skipped` em vez de presumir um número de dias. Só corre contra o prazo que o próprio registo escreve na coluna 回复期限, e uma ocorrência significa que esse prazo e a data da avaliação não concordam, não que uma regra da plataforma tenha sido violada. |
| A 回复日期 está escrita como 2026年3月15日 e é anterior à 入住日期. O que é detetado? | `OT-004` compara `checkIn` com `repliedAt` e reporta uma data de resposta anterior à data da avaliação, considerando o mesmo dia como não posterior; uma data que não consegue analisar —`2026年3月15日`, por exemplo, pois só são analisadas `2026-03-15`, `2026/3/15` e `2026.3.15` com hora opcional— é reportada nessa linha em vez de ser omitida em silêncio. Compara apenas as duas datas e não julga se a resposta foi atempada. |
| Preenchemos 问题类型 com palavras nossas. Porque diz o relatório que a verificação não correu? | `OT-006` traz a lista `values` vazia, ou seja, por configurar, pelo que se declara em `skipped` com esse motivo em vez de inventar um sistema de categorias: o vocabulário (卫生, 服务态度, 设施设备, 价格, 噪音, 预订与入住 ou o da sua instituição) é definido pela instituição. Depois de o configurar, a regra reporta qualquer valor fora da lista e não verifica mais nada: em que categoria se enquadra uma avaliação continua a ser um juízo do operador. |
| O mesmo 点评编号 aparece duas vezes no registo. O que é reportado? | `OT-007` reporta a segunda linha como duplicada da primeira, comparando `reviewNo` e ignorando espaços em branco. A unicidade é a premissa de que cada avaliação seja registada uma só vez, por isso a regra está em `warn`; verifica apenas a unicidade e não diz qual das duas linhas é a cópia. Sem coluna `reviewNo`, a regra declara-se em `skipped` em vez de passar em silêncio. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《中华人民共和国电子商务法》与平台服务规则 | 现行版本与条号本次未核实 | OT-001 |
| 《中华人民共和国电子商务法》 | 现行版本与条号本次未核实 | OT-002, OT-004, OT-005, OT-007 |
| 各在线旅游平台服务规则（本机构配置） | 无统一标准（本条依据为本机构配置的回复时限） | OT-003 |
| 本机构点评管理办法（本机构配置） | 无统一标准（本条依据为本机构分类口径） | OT-006 |

**Boundary:** this plugin checks an **在线点评回复台账** for the closed loop a register can be held to — that
each review records its content or score, that a reply carries a date and a reply author, that the reply does
not precede the review, that an unreplied review falls inside the deadline the register states, that the
problem category comes from your vocabulary, and that review numbers are unique. It does **not** decide whether
a reply was appropriate, whether a review should be appealed or removed, whether a bad review is malicious, or
whether service quality is acceptable.

> ### ⚠️ What the law does — and does not — require here
>
> **《中华人民共和国电子商务法》was obtained and read verbatim** (see
> `rules/evidence/clause-verification.md`), and the check **overturned this pack's earlier framing**. Article 39
> puts the duty on the **platform operator**, not the merchant:
>
> > 电子商务平台经营者应当建立健全信用评价制度，公示信用评价规则，为消费者提供对平台内销售的商品或者提供的服务进行评价的途径。
> > 电子商务平台经营者**不得删除**消费者对其平台内销售的商品或者提供的服务的评价。
>
> **There is no provision requiring a merchant to reply to a review.** So this plugin checks a duty that comes
> from **each platform's own service rules and your institution's management policy** — never from the statute —
> and neither the rule pack nor this README now describes replying as a legal obligation. Articles 17 (no
> fabricated reviews) and 20 (deliver as promised) concern other things and are deliberately **not** cited.
>
> **Every `excerpt` still says "本次未取得", and every rule remains `warn` or `info`** — the platform service
> rules themselves were not obtained, and the statute governs the platform rather than the merchant, so raising
> a rule to `direct` would dress a register gap up as a breach of law.
>
> **The plugin builds in no platform's reply window.** `OT-003` compares the review date against the deadline
> **written in the register's own 回复期限 column**, and with that column empty it reports itself in `skipped`.
> A finding says "the deadline and the review date disagree", never "you breached the platform's rules".
> The category vocabulary ships **empty** for the same reason. And the plugin **does not read sentiment**: it
> checks that a low score has a rectification recorded, and what counts as low is your configuration, not its
> judgement.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-rc.2`. **`engines.dsh` é declarado como `>=0.2.1-0 <0.3.0`** e o host o aplica desde 0.2.1 |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native` e `ptc`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/ota-review-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-ota-review-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## Família de plugins DSH da PerryLink

Este projeto faz parte da família de plugins do DeepSeek Harness da [PerryLink](https://github.com/PerryLink). O registro fica recolhido abaixo para que cada README mantenha uma primeira tela curta; expanda para ver cada linha e seu status.

<details>
<summary>Expandir todos os plugins</summary>

| Plugin | Status |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** |  |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** |  |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** |  |
| **[dsh-demurrage-ledger](https://github.com/PerryLink/dsh-demurrage-ledger)** |  |
| **[dsh-doublecheck](https://github.com/PerryLink/dsh-doublecheck)** |  |
| **[dsh-drill-script-check](https://github.com/PerryLink/dsh-drill-script-check)** |  |
| **[dsh-eia-guide-check](https://github.com/PerryLink/dsh-eia-guide-check)** |  |
| **[dsh-emergency-plan](https://github.com/PerryLink/dsh-emergency-plan)** |  |
| **[dsh-essay-rubric-check](https://github.com/PerryLink/dsh-essay-rubric-check)** |  |
| **[dsh-evidence-check](https://github.com/PerryLink/dsh-evidence-check)** |  |
| **[dsh-export-ctl-check](https://github.com/PerryLink/dsh-export-ctl-check)** |  |
| **[dsh-fast](https://github.com/PerryLink/dsh-fast)** |  |
| **[dsh-fmea-table-check](https://github.com/PerryLink/dsh-fmea-table-check)** |  |
| **[dsh-forecast-penalty](https://github.com/PerryLink/dsh-forecast-penalty)** |  |
| **[dsh-fund-research](https://github.com/PerryLink/dsh-fund-research)** |  |
| **[dsh-github](https://github.com/PerryLink/dsh-github)** |  |
| **[dsh-gongwen-flow-check](https://github.com/PerryLink/dsh-gongwen-flow-check)** |  |
| **[dsh-gongwen-word-check](https://github.com/PerryLink/dsh-gongwen-word-check)** |  |
| **[dsh-guard-plan-qc](https://github.com/PerryLink/dsh-guard-plan-qc)** |  |
| **[dsh-hazchem-check](https://github.com/PerryLink/dsh-hazchem-check)** |  |
| **[dsh-hazplan-check](https://github.com/PerryLink/dsh-hazplan-check)** |  |
| **[dsh-hidden-risk-map](https://github.com/PerryLink/dsh-hidden-risk-map)** |  |
| **[dsh-hs-classify](https://github.com/PerryLink/dsh-hs-classify)** |  |
| **[dsh-icd-rule-check](https://github.com/PerryLink/dsh-icd-rule-check)** |  |
| **[dsh-industry-research](https://github.com/PerryLink/dsh-industry-research)** |  |
| **[dsh-lawcite-adapter](https://github.com/PerryLink/dsh-lawcite-adapter)** |  |
| **[dsh-laya](https://github.com/PerryLink/dsh-laya)** |  |
| **[dsh-lc-doc-check](https://github.com/PerryLink/dsh-lc-doc-check)** |  |
| **[dsh-learning-gap-check](https://github.com/PerryLink/dsh-learning-gap-check)** |  |
| **[dsh-library](https://github.com/PerryLink/dsh-library)** |  |
| **[dsh-local-ai](https://github.com/PerryLink/dsh-local-ai)** |  |
| **[dsh-lsp-actions](https://github.com/PerryLink/dsh-lsp-actions)** |  |
| **[dsh-mask](https://github.com/PerryLink/dsh-mask)** |  |
| **[dsh-mcp-panel](https://github.com/PerryLink/dsh-mcp-panel)** |  |
| **[dsh-medrec-qc](https://github.com/PerryLink/dsh-medrec-qc)** |  |
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** |  |
| **[dsh-nsfc-form-check](https://github.com/PerryLink/dsh-nsfc-form-check)** |  |
| **[dsh-nurse-record-check](https://github.com/PerryLink/dsh-nurse-record-check)** |  |
| **[dsh-observe](https://github.com/PerryLink/dsh-observe)** |  |
| **[dsh-origin-rvc-check](https://github.com/PerryLink/dsh-origin-rvc-check)** |  |
| **[dsh-ota-review-check](https://github.com/PerryLink/dsh-ota-review-check)** |  |
| **[dsh-output-styles](https://github.com/PerryLink/dsh-output-styles)** |  |
| **[dsh-paper-doc-adapter](https://github.com/PerryLink/dsh-paper-doc-adapter)** |  |
| **[dsh-permission-rules](https://github.com/PerryLink/dsh-permission-rules)** |  |
| **[dsh-permit-report-check](https://github.com/PerryLink/dsh-permit-report-check)** |  |
| **[dsh-pipeline-check](https://github.com/PerryLink/dsh-pipeline-check)** |  |
| **[dsh-pleading-draft](https://github.com/PerryLink/dsh-pleading-draft)** |  |
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** |  |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** |  |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** |  |
| **[dsh-policy-brief-draft](https://github.com/PerryLink/dsh-policy-brief-draft)** |  |
| **[dsh-power-loss-split](https://github.com/PerryLink/dsh-power-loss-split)** |  |
| **[dsh-power-ticket-check](https://github.com/PerryLink/dsh-power-ticket-check)** |  |
| **[dsh-ppap-check](https://github.com/PerryLink/dsh-ppap-check)** |  |
| **[dsh-protest-deadline](https://github.com/PerryLink/dsh-protest-deadline)** |  |
| **[dsh-railway-window](https://github.com/PerryLink/dsh-railway-window)** |  |
| **[dsh-repair-order-qc](https://github.com/PerryLink/dsh-repair-order-qc)** |  |
| **[dsh-research-report](https://github.com/PerryLink/dsh-research-report)** |  |
| **[dsh-review-reply-check](https://github.com/PerryLink/dsh-review-reply-check)** |  |
| **[dsh-rulefile-check](https://github.com/PerryLink/dsh-rulefile-check)** |  |
| **[dsh-safety-brief-check](https://github.com/PerryLink/dsh-safety-brief-check)** |  |
| **[dsh-score](https://github.com/PerryLink/dsh-score)** |  |
| **[dsh-session-sync](https://github.com/PerryLink/dsh-session-sync)** |  |
| **[dsh-site-log-check](https://github.com/PerryLink/dsh-site-log-check)** |  |
| **[dsh-skill-pack-security](https://github.com/PerryLink/dsh-skill-pack-security)** |  |
| **[dsh-soe-decision-check](https://github.com/PerryLink/dsh-soe-decision-check)** |  |
| **[dsh-soilwater-check](https://github.com/PerryLink/dsh-soilwater-check)** |  |
| **[dsh-sop-sync-check](https://github.com/PerryLink/dsh-sop-sync-check)** |  |
| **[dsh-spc-gbt-adapter](https://github.com/PerryLink/dsh-spc-gbt-adapter)** |  |
| **[dsh-talk](https://github.com/PerryLink/dsh-talk)** |  |
| **[dsh-tender-extract](https://github.com/PerryLink/dsh-tender-extract)** |  |
| **[dsh-tender-matrix](https://github.com/PerryLink/dsh-tender-matrix)** |  |
| **[dsh-test-drive](https://github.com/PerryLink/dsh-test-drive)** |  |
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** |  |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 CONGELADO — ver o README do repositório |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 CONGELADO — ver o README do repositório |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 CONGELADO — ver o README do repositório |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 CONGELADO — ver o README do repositório |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 CONGELADO — ver o README do repositório |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 RETIRADO — ver o README do repositório |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 RETIRADO — ver o README do repositório |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 RETIRADO — ver o README do repositório |

</details>## License

[Apache License 2.0](LICENSE) © 2026 dsh-ota-review-check contributors.
