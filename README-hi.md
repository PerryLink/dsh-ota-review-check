# dsh-ota-review-check — ऑनलाइन समीक्षा उत्तर रजिस्टर की जाँच

`dsh-ota-review-check` ऑनलाइन समीक्षा और उत्तर का एक रजिस्टर पढ़ता है — प्रॉपर्टी हेडर और प्रत्येक समीक्षा की एक पंक्ति — और उसी रजिस्टर की पूर्णता तथा बंद-लूप (closed loop) की जाँच करता है: क्या प्रत्येक समीक्षा में उसका विवरण या स्कोर दर्ज है, क्या उत्तर दी गई समीक्षा में उत्तर की तिथि और उत्तर देने वाले का नाम दर्ज है, क्या उत्तर समीक्षा से पहले नहीं है, क्या बिना उत्तर वाली समीक्षा रजिस्टर में लिखी समय-सीमा के भीतर है, क्या समस्या-प्रकार आपकी संस्था की अपनी शब्दावली से लिया गया है, और क्या समीक्षा क्रमांक अद्वितीय हैं।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| किसी पंक्ति में 点评内容 और 评分 दोनों ही नहीं भरे हैं। क्या दर्ज होता है? | `OT-001` उस पंक्ति को दर्ज करता है: प्रत्येक समीक्षा में `content` या `score` में से कम से कम एक दर्ज होना चाहिए। यह केवल देखता है कि इनमें से एक भरा है; समीक्षा की सामग्री सच है या नहीं, या वह दुर्भावनापूर्ण समीक्षा है या नहीं, यह नहीं आँकता। |
| एक पंक्ति में 已回复 अंकित है, पर 回复日期 और 回复人 खाली हैं। क्या दर्ज होता है? | जिस पंक्ति का `replyStatus` कॉन्फ़िगर किए गए मानों (`是`, `Y`, `yes`, `true`, `已回复`, `√`) में से कोई एक लेता है, उसमें `OT-002` `repliedAt` के अभाव को दर्ज करता है, और `OT-005` उन सभी पंक्तियों में `replier` भरा होने की अपेक्षा करता है जिनमें 回复人 कॉलम है — इसलिए 未回复 अंकित पंक्ति में भी खाली 回复人 दर्ज होता है। दोनों केवल यह देखते हैं कि कॉलम भरा है: कोई यह नहीं बताता कि उत्तर समय पर था या उपयुक्त था। |
| हमारे रजिस्टर में 回复期限 कॉलम पूरा खाली है। क्या जाँच 24 या 48 घंटे की समय-सीमा मान लेती है? | नहीं। प्लगइन किसी भी प्लेटफ़ॉर्म की समय-सीमा अपने भीतर नहीं रखता: `replyDeadline` में मान न हो तो तुलना के लिए कुछ ही नहीं है, और `OT-003` किसी भी दिन-संख्या को मान लेने के बजाय `skipped` में दर्ज होता है। यह केवल उसी सीमा से तुलना करता है जो रजिस्टर स्वयं 回复期限 कॉलम में लिखता है, और मेल न खाने का अर्थ यह है कि रजिस्टर की सीमा और समीक्षा की तिथि में अंतर है — प्लेटफ़ॉर्म नियम का उल्लंघन नहीं। |
| 回复日期 2026年3月15日 लिखी है और वह 入住日期 से पहले है। क्या पकड़ में आता है? | `OT-004` `checkIn` की तुलना `repliedAt` से करता है और समीक्षा की तिथि से पहले की उत्तर-तिथि दर्ज करता है; एक ही दिन को बाद का नहीं माना जाता। जो तिथि पढ़ी न जा सके — जैसे `2026年3月15日`, क्योंकि केवल `2026-03-15`, `2026/3/15` और `2026.3.15` (वैकल्पिक समय के साथ) पढ़ी जाती हैं — वह उस पंक्ति में अलग से दर्ज होती है, चुपचाप छोड़ी नहीं जाती। यह केवल दोनों तिथियों की तुलना करता है, उत्तर समय पर था या नहीं यह नहीं आँकता। |
| हमने 问题类型 में अपने ही शब्द भरे हैं। रिपोर्ट क्यों कहती है कि यह जाँच चली ही नहीं? | `OT-006` की `values` सूची खाली यानी अनकॉन्फ़िगर आती है, इसलिए वह कोई वर्गीकरण तंत्र गढ़ने के बजाय उसी कारण के साथ `skipped` में दर्ज होता है: शब्दावली (卫生, 服务态度, 设施设备, 价格, 噪音, 预订与入住 या आपकी संस्था की अपनी) आपकी संस्था तय करती है। सूची कॉन्फ़िगर करने पर यह केवल सूची से बाहर के मान दर्ज करता है और इससे आगे कुछ नहीं देखता — कोई समीक्षा किस श्रेणी में है, यह संचालक का निर्णय है। |
| एक ही 点评编号 रजिस्टर में दो बार आया है। क्या दर्ज होता है? | `OT-007` दूसरी पंक्ति को पहली की दोहराव के रूप में दर्ज करता है और तुलना में रिक्त स्थान छोड़ देता है। क्रमांक की अद्वितीयता ही इस बात की शर्त है कि प्रत्येक समीक्षा एक ही बार दर्ज हो, इसलिए यह नियम `warn` पर है; यह केवल अद्वितीयता देखता है और यह नहीं बताता कि दोनों में से कौन-सी पंक्ति प्रतिलिपि है। `reviewNo` कॉलम न हो तो यह नियम चुपचाप पास होने के बजाय `skipped` में दर्ज होता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-ota-review-check
dsh --profile <name> --dump-config | grep 'dsh-ota-review-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/ota-review-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-ota-review-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-ota-review-check contributors.
