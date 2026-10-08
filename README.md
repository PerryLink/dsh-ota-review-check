# dsh-ota-review-check — Online review and reply register check

`dsh-ota-review-check` reads one online review-and-reply register — the property header plus one row per review — and checks that register's own completeness and closed loop: that each review records its content or a score, that a replied review carries a reply date and a reply author, that the reply does not precede the review, that an unreplied review falls inside the deadline the register itself states, that the problem category comes from your institution's own vocabulary, and that review numbers are unique.

## What it answers

| You ask | What it answers |
|---|---|
| A row has neither 点评内容 nor 评分 filled in. What is reported? | `OT-001` reports that row: a review must record at least one of the two fields, `content` or `score`. It checks only that one of them is filled; it does not judge whether the review's content is truthful or whether the review is a malicious one. |
| A row is marked 已回复, but the 回复日期 and 回复人 cells are blank. What is reported? | `OT-002` reports the missing `repliedAt` on any row whose `replyStatus` holds one of the configured conditions (`是`, `Y`, `yes`, `true`, `已回复`, `√`), and `OT-005` requires `replier` to be filled on every row that carries the 回复人 column, so a blank cell is reported even on a row marked 未回复. Both check only that the cell is filled: neither says whether the reply was timely or whether it was appropriate. |
| Our register has the 回复期限 column empty throughout. Does the check assume a 24- or 48-hour window? | No. The plugin builds in no platform's reply window: with no `replyDeadline` value there is nothing to compare, and `OT-003` appears in `skipped` instead of assuming any number of days. It runs only against the deadline the register itself writes in its 回复期限 column, and a hit means that deadline and the review date disagree — not that a platform rule was breached. |
| The 回复日期 is written as 2026年3月15日 and is earlier than the 入住日期. What is caught? | `OT-004` compares `checkIn` with `repliedAt` and reports a reply date earlier than the review date, counting the same day as not later; a date it cannot parse — `2026年3月15日`, for instance, since only `2026-03-15`, `2026/3/15` and `2026.3.15` with an optional time parse — is reported on that row rather than passed over in silence. It compares the two dates only and does not judge whether the reply was timely. |
| We filled 问题类型 with our own words. Why does the report say the check did not run? | `OT-006` ships with its `values` list empty, meaning not configured, so it states itself in `skipped` with that reason rather than inventing a category system: the vocabulary (卫生, 服务态度, 设施设备, 价格, 噪音, 预订与入住, or your own) is your institution's. Once you list it, the rule reports any value not on the list and checks nothing further — which category a review belongs in stays the operator's judgement. |
| The same 点评编号 appears twice in the register. What is reported? | `OT-007` reports the second row as a duplicate of the first, comparing `reviewNo` while ignoring whitespace. Uniqueness is the premise of each review being registered once, which is why the rule sits at `warn`; it checks uniqueness only and does not say which of the two rows is the copy. With no `reviewNo` column the rule states itself in `skipped` rather than passing in silence. |

## Standards it follows

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a month of reviews use `ptc` |

## What it does

Registers the `ota_review_check` tool. It reads one review-and-reply register — the property header plus one row
per review — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `OT-001` | the review records content or a score | warn | principle |
| `OT-002` | a replied review carries a reply date | warn | principle |
| `OT-003` | an unreplied review falls inside the recorded deadline | info | local |
| `OT-004` | the reply does not precede the review | warn | principle |
| `OT-005` | a replied review names the replier | warn | principle |
| `OT-006` | the problem category comes from your vocabulary (off by default) | info | local |
| `OT-007` | review numbers are unique | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-ota-review-check
dsh --profile <name> --dump-config | grep 'dsh-ota-review-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/ota-review-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `OT-002` `conditionValues` — the values in your 是否回复 column that mean "replied", by default
  `[是, Y, yes, true, 已回复, √]`.
- `OT-003` reads the register's 回复期限 / `replyDeadline` column. The plugin never derives a deadline from a
  day count, because windows vary by platform.
- `OT-006` `values` — your problem categories, e.g.
  `[卫生, 服务态度, 设施设备, 价格, 噪音, 预订与入住]`. Empty means no check.

## Material format

The tool accepts JSON or YAML:

```yaml
hotel: 某某门店
period: 2026 年 3 月
platform: 某某平台
rows:
  - { 序号: '1', 渠道: 某某平台, 房型: 标准大床房, 入住日期: 2026-03-01,
      总分: '4.5', 评分制: 5 分制, 点评内容: 位置方便，前台服务热情，房间隔音一般。,
      是否回复: 是, 回复日期: 2026-03-02, 回复期限: 2026-03-04, 回复人: 张店长,
      问题类型: 噪音, 是否整改: 是 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/ota-review-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`OT-003` reports itself as skipped.** The register records no reply deadline. Windows differ by platform,
  so the plugin will not supply one — record the platform's deadline in the ledger.
- **`OT-003` fires but the reply was in time.** The register's 回复期限 disagrees with the review date.
- **`OT-006` never runs.** Its vocabulary is empty; fill it with your operating categories.
- **`OT-006` fires on a category I think is fine.** The value is not in your list. Widen `values` or correct
  the cell — the plugin does not classify reviews itself.
- **`OT-007` fires twice on one review.** One review may legitimately be handled twice (a follow-up reply).
  Distinguish the rows rather than reusing the number.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-ota-review-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-ota-review-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-ota-review-check contributors.
