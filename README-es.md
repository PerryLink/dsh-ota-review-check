# dsh-ota-review-check — Verificación del registro de respuestas a reseñas en línea

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-ota-review-check` lee un registro de reseñas en línea con sus respuestas —la cabecera del establecimiento más una fila por reseña— y comprueba la completitud y el cierre de ese mismo registro: que cada reseña registre su contenido o una puntuación, que una reseña respondida lleve fecha de respuesta y autor de la respuesta, que la respuesta no sea anterior a la reseña, que una reseña sin responder quede dentro del plazo que el propio registro declara, que el tipo de problema proceda del vocabulario de su institución y que los números de reseña sean únicos.

## Cómo se ve la salida

![Terminal demo of dsh-ota-review-check: real output over its OT-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-ota-review-check/main/docs/assets/dsh-ota-review-check-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `OT-001` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Una fila no tiene rellenos ni 点评内容 ni 评分. ¿Qué se informa? | `OT-001` informa de esa fila: cada reseña debe registrar al menos uno de los dos campos, `content` o `score`. Solo comprueba que uno de ellos esté relleno; no juzga si el contenido de la reseña es cierto ni si se trata de una reseña maliciosa. |
| Una fila está marcada 已回复, pero las celdas 回复日期 y 回复人 están vacías. ¿Qué se informa? | `OT-002` informa de la falta de `repliedAt` en toda fila cuyo `replyStatus` tome uno de los valores configurados (`是`, `Y`, `yes`, `true`, `已回复`, `√`), y `OT-005` exige que `replier` esté relleno en cualquier fila que traiga la columna 回复人, de modo que una celda vacía se informa incluso en una fila marcada 未回复. Ambas comprueban solo que la celda esté rellena: ninguna dice si la respuesta fue puntual ni si fue adecuada. |
| En nuestro registro la columna 回复期限 está vacía en todas las filas. ¿La comprobación supone un plazo de 24 o 48 horas? | No. El plugin no incorpora el plazo de ninguna plataforma: sin un valor en `replyDeadline` no hay nada que comparar y `OT-003` aparece en `skipped` en lugar de suponer un número de días. Solo se ejecuta contra el plazo que el propio registro escribe en la columna 回复期限, y una coincidencia significa que ese plazo y la fecha de la reseña no concuerdan, no que se haya infringido una regla de la plataforma. |
| La 回复日期 está escrita como 2026年3月15日 y es anterior a la 入住日期. ¿Qué se detecta? | `OT-004` compara `checkIn` con `repliedAt` e informa de una fecha de respuesta anterior a la fecha de la reseña, considerando el mismo día como no posterior; una fecha que no puede analizar —`2026年3月15日`, por ejemplo, ya que solo se analizan `2026-03-15`, `2026/3/15` y `2026.3.15` con hora opcional— se informa en esa fila en lugar de omitirse en silencio. Solo compara las dos fechas y no juzga si la respuesta fue puntual. |
| Hemos rellenado 问题类型 con nuestras propias palabras. ¿Por qué dice el informe que la comprobación no se ejecutó? | `OT-006` trae su lista `values` vacía, es decir, sin configurar, así que se declara en `skipped` con ese motivo en lugar de inventar un sistema de categorías: el vocabulario (卫生, 服务态度, 设施设备, 价格, 噪音, 预订与入住 o el suyo propio) lo fija su institución. Una vez lo configure, la regla informa de cualquier valor que no esté en la lista y no comprueba nada más: en qué categoría encaja una reseña sigue siendo juicio del operador. |
| El mismo 点评编号 aparece dos veces en el registro. ¿Qué se informa? | `OT-007` informa de la segunda fila como duplicada de la primera, comparando `reviewNo` e ignorando los espacios en blanco. La unicidad es la premisa de que cada reseña se registre una sola vez, por eso la regla está en `warn`; comprueba solo la unicidad y no dice cuál de las dos filas es la copia. Sin columna `reviewNo`, la regla se declara en `skipped` en lugar de pasar en silencio. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-ota-review-check
dsh --profile <name> --dump-config | grep 'dsh-ota-review-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/ota-review-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-ota-review-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-ota-review-check contributors.
