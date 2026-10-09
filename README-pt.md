# dsh-ota-review-check — Verificação do registo de respostas a avaliações em linha

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-ota-review-check` lê um registo de avaliações em linha com as respetivas respostas —o cabeçalho do estabelecimento mais uma linha por avaliação— e verifica a completude e o fecho desse próprio registo: se cada avaliação regista o seu conteúdo ou uma pontuação, se uma avaliação respondida traz data de resposta e autor da resposta, se a resposta não é anterior à avaliação, se uma avaliação sem resposta cai dentro do prazo que o próprio registo declara, se o tipo de problema vem do vocabulário da sua instituição e se os números de avaliação são únicos.

## Como é a saída

![Terminal demo of dsh-ota-review-check: real output over its OT-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-ota-review-check/main/docs/assets/dsh-ota-review-check-demo.png)

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
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-ota-review-check
dsh --profile <name> --dump-config | grep 'dsh-ota-review-check'
```

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

## License

[Apache License 2.0](LICENSE) © 2026 dsh-ota-review-check contributors.
