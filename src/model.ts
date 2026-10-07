/**
 * dsh-ota-review-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'ota_review_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  reviewNo: ['序号', '点评编号', '编号', 'reviewNo'],
  channel: ['渠道', '来源渠道', '平台', 'channel'],
  roomType: ['房型', '产品', '产品类型', 'roomType'],
  checkIn: ['入住日期', '消费日期', '订单日期', 'checkIn'],
  score: ['总分', '评分', '打分', 'score'],
  scoreScale: ['评分制', '满分', '评分标准', 'scoreScale'],
  content: ['点评内容', '评价内容', '内容', 'content'],
  replyStatus: ['是否回复', '回复状态', 'replyStatus'],
  repliedAt: ['回复日期', '回复时间', 'repliedAt'],
  replyDeadline: ['回复期限', '应回复日期', 'replyDeadline'],
  replier: ['回复人', '处理人', 'replier'],
  issueType: ['问题类型', '问题分类', '分类', 'issueType'],
  rectified: ['是否整改', '整改情况', 'rectified'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'reviews', '点评'],
  columns: COLUMNS,
  header: {
  hotel: ['hotel', '门店名称', '酒店名称'],
  period: ['period', '统计期间', '周期'],
  platform: ['platform', '平台名称', '渠道平台'],
  checkedAt: ['checkedAt', '核对日期'],
  replyWindowDays: ['replyWindowDays', '回复时限天数'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '点评内容',
  'content',
  '总分',
  'score',
  '是否回复',
  'replyStatus',
  '问题类型',
  'issueType',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
