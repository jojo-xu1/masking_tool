# Feature Specification: レポート表示改善と人名・電話番号マスク

**Feature Branch**: `002-report-spacy-phone`

**Created**: 2026-05-30

**Status**: Draft

**Input**: User description: "機密情報検出結果.xlsxの表示を適切に修正する、SpaCyを導入して人名をマスクすること、電話番号のマスクも対応する"

## Clarifications

### Session 2026-05-30

- Q: 人名検出で必須対応する言語範囲はどこまでにするか？ → A: 日本語・英語・中国語を対応対象にする。日本語・英語は必須モデルで対応し、中国語はモデル不可時に決定的フォールバック検出で対応する
- Q: 電話番号検出で必須対応する地域形式はどこまでにするか？ → A: 日本・米国・中国の代表的な電話番号形式を必須対応にする
- Q: `機密情報検出結果.xlsx` の列構成はどうするか？ → A: 必須 8 列だけに戻し、ファイルパス・処理ステータスは文脈や理由欄へまとめる
- Q: 人名・電話番号・既存ルールが同じ範囲に一致した場合の優先順位はどうするか？ → A: 個別指定ルールを最優先し、次にリスクレベル、同点なら既存ルール順で決める
- Q: 人名検出は既定で有効にするか？ → A: 人名検出は既定で有効、ユーザー設定で無効化できる
- Q: 人名検出が有効な状態で日本語・英語の必須検出機能が使えない場合はどうするか？ → A: 処理を失敗させて理由を表示する
- Q: テスト用ファイルの言語構成はどうするか？ → A: 既定の検証用ファイルは英語・日本語・中国語を混在させず、言語別フォルダに分ける
- Q: 漢字を含むテスト用ファイルの文字化けはどう扱うか？ → A: テキスト、Office、PDF の検証用ファイルで日本語・中国語文字が読める状態を必須にする
- Q: 同じ電話番号が同一実行内で複数回出現した場合の置換提案はどうするか？ → A: 同じ電話番号は同一実行内で同じ `PHONE_連番` にする
- Q: 中国語人名検出はどこまで対応するか？ → A: 中国語も既定対応し、spaCy 中国語モデルが利用できない場合は決定的な中国語人名フォールバック検出で置換する
- Q: マスキング処理中の外部通信・外部送信は許可するか？ → A: ユーザーが明示許可した場合だけ外部通信を許可する

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 検出結果 Excel を読みやすく確認する (Priority: P1)

利用者は処理後に `機密情報検出結果.xlsx` を開き、必須 8 列の範囲内で検出語句、置換提案、カテゴリ、リスク、処理状況、対象ファイルの手掛かりを迷わず確認できる。

**Why this priority**: レポートは成果物確認と監査の中心であり、表示が不適切だとマスキング結果のレビューが困難になる。

**Independent Test**: 複数カテゴリと複数ステータスを含む処理結果を生成し、Excel の列幅、フィルター、固定ヘッダー、色分け、ステータス表示が確認しやすい状態になることを検証する。

**Acceptance Scenarios**:

1. **Given** 複数ファイルの検出結果とスキップ結果がある, **When** 利用者が `機密情報検出結果.xlsx` を開く, **Then** ヘッダーが固定され、フィルターでカテゴリ・リスクを絞り込める
2. **Given** 長い文脈、対象ファイルの手掛かり、処理理由を含む行がある, **When** 利用者がレポートを確認する, **Then** 主要列が読みやすい幅と折り返し表示になり、内容が欠けて見えない
3. **Given** 高・中・低リスクとステータスのみの行がある, **When** 利用者がレポートを確認する, **Then** 行色とステータスで重要度と処理結果を判別できる

---

### User Story 2 - 人名を自動検出してマスクする (Priority: P2)

利用者は設定ルールに明示されていない人名も、文書中の人物名として検出し、分類ラベル付きの不可逆な値へ置換できる。

**Why this priority**: 人名は個人情報として頻出し、固定ルールや正規表現だけでは漏れが発生しやすい。

**Independent Test**: 人名を含む日本語・英語・中国語のサンプル文書を処理し、人名が `PERSON_連番` 形式で置換され、レポートにカテゴリ `PERSON` と検出理由が記録されることを確認する。

**Acceptance Scenarios**:

1. **Given** 人名を含む対象ファイルがある, **When** 利用者が人名検出を有効にして処理する, **Then** 検出された人名は `PERSON_001` 形式の置換提案でマスクされる
2. **Given** 同じ人名が同一実行内で複数回出現する, **When** 処理が完了する, **Then** 同じ人名は同じ置換提案へ置換される
3. **Given** 人名検出が無効化されている, **When** 処理が完了する, **Then** 人名検出による追加マスクは行われず、他の有効ルールのみが適用される
4. **Given** 中国語人名を含む対象ファイルがあり spaCy 中国語モデルが利用できない, **When** 利用者が中国語ファイルを処理する, **Then** 決定的な中国語人名フォールバック検出により代表的人名が `PERSON_001` 形式でマスクされる

---

### User Story 3 - 電話番号をマスクする (Priority: P3)

利用者は文書中の電話番号を検出し、カテゴリ `PHONE` の不可逆な値へ置換できる。

**Why this priority**: 電話番号は機密・個人情報としてよく含まれ、既定ルールとして安定して検出できる必要がある。

**Independent Test**: 日本・米国・中国の代表的な電話番号形式、ハイフンあり、ハイフンなし、国番号付きの電話番号を含むサンプルを処理し、電話番号が `PHONE_連番` 形式で置換されることを確認する。

**Acceptance Scenarios**:

1. **Given** 対象ファイルに電話番号が含まれる, **When** 電話番号ルールを有効にして処理する, **Then** 電話番号は `PHONE_001` 形式の置換提案でマスクされる
2. **Given** 電話番号ルールが無効化されている, **When** 処理が完了する, **Then** 電話番号検出による追加マスクは行われない
3. **Given** 人名と電話番号が同じ文書に含まれる, **When** 処理が完了する, **Then** それぞれ `PERSON` と `PHONE` のカテゴリとして別々にレポートされる
4. **Given** 同じ電話番号が同一実行内で複数回出現する, **When** 処理が完了する, **Then** 同じ電話番号は同じ置換提案へ置換される

---

### Edge Cases

- 人名検出結果、電話番号検出結果、個別指定ルール、正規表現ルールが同じ文字列範囲に一致する場合、個別指定ルールを最優先し、次にリスクレベル、同点なら既存ルール順で採用されたルールだけを置換に使う。
- 人名検出が有効で、日本語または英語の必須人名検出機能が利用できない場合、処理を失敗させ、理由を画面または処理ログで確認できるようにする。
- 中国語の spaCy 人名検出機能が利用できない場合、処理全体を止めず、決定的な中国語人名フォールバック検出で代表的人名を置換する。
- 中国語人名フォールバック検出は、代表的な中国語姓と人名文脈に合う値を対象にし、電話番号・日付・プロジェクト名などの非人名語を人名として扱わない。
- 電話番号らしい数字列が短すぎる、長すぎる、または日付・郵便番号と判断できる場合、電話番号として誤検出しない。
- UTF-8 BOM 付きのテキスト系ファイルを処理する場合、BOM が検出語句や置換結果に混入せず、日本語・中国語文字が文字化けしない。
- 検証用ファイルを使う場合、英語・日本語・中国語の通常検証は言語別ファイルで行い、多言語混在ファイルはストレステスト用途として扱う。
- Office ファイルとテキスト型 PDF に日本語・中国語文字が含まれる場合、検証時に文字が読める状態で抽出・レポート確認できる。
- マスキング処理中に外部通信や外部送信が必要になる場合、ユーザーの明示許可がない限り、入力内容、検出語句、置換提案、レポート内容を外部へ送信しない。
- レポート行数が多い場合でも、ヘッダー固定、フィルター、列幅、折り返し、色分けが保持される。
- 既存の `検出語句`、`置換提案`、リスク色分け、`output` 出力、入力ファイル非破壊の契約は維持する。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST improve `機密情報検出結果.xlsx` display so users can review headers, filters, risk colors, detected terms, replacement suggestions, context, processing status, and target-file clues within the required 8 columns without manual formatting.
- **FR-002**: System MUST freeze the report header row and enable filtering for report columns.
- **FR-003**: System MUST apply readable column widths and text wrapping for long context, target-file clues, judgment reason, and recommended action values.
- **FR-004**: System MUST preserve risk-level row coloring and status-only row coloring in the improved report.
- **FR-005**: System MUST keep the report limited to the required 8 columns and include enough context, judgment reason, or recommended action text to distinguish detection rows, no-replacement rows, unsupported rows, out-of-scope rows, and failed rows.
- **FR-006**: System MUST support configurable person-name detection as an additional detection source for Japanese, English, and Chinese.
- **FR-007**: System MUST enable person-name detection by default and allow users to turn it off.
- **FR-008**: System MUST report person-name detections with information category `PERSON`, risk level, judgment reason, and recommended action.
- **FR-009**: System MUST mask detected person names with deterministic `PERSON_連番` replacement suggestions.
- **FR-010**: System MUST apply the same replacement suggestion to the same detected person name within a processing run.
- **FR-011**: System MUST support phone-number detection as a configurable default rule.
- **FR-012**: System MUST allow phone-number detection to be turned on or off.
- **FR-013**: System MUST mask detected phone numbers with deterministic `PHONE_連番` replacement suggestions.
- **FR-014**: System MUST support representative Japanese, US, and Chinese phone-number forms, including hyphenated, non-hyphenated, and country-code-prefixed forms.
- **FR-015**: System MUST avoid treating clearly non-phone numeric values such as dates and postal codes as phone numbers.
- **FR-016**: System MUST integrate person-name and phone-number detections into the existing `検出語句` -> `置換提案` replacement contract.
- **FR-017**: System MUST resolve overlapping person-name, phone-number, regex, and explicit detections by prioritizing explicit detections first, then higher risk level, then existing rule order.
- **FR-018**: System MUST keep existing supported file scope, out-of-scope exclusions, per-run output layout, and original input non-destruction behavior unchanged.
- **FR-019**: System MUST attempt Chinese person-name detection with a supported spaCy detection model when available, and MUST use deterministic Chinese person-name fallback detection when that model is unavailable.
- **FR-020**: System MUST fail processing with a visible reason when person-name detection is enabled and required Japanese or English person-name detection is unavailable.
- **FR-021**: System MUST process UTF-8 text-family files with or without BOM without including the BOM in detected terms, replacements, or report context.
- **FR-022**: System MUST provide language-separated validation samples for English, Japanese, and Chinese so standard verification does not depend on mixed-language files.
- **FR-023**: System MUST provide Office and text-based PDF validation samples whose Japanese and Chinese text remains readable and extractable for masking verification.
- **FR-024**: System MUST NOT transmit input content, detected terms, replacement suggestions, or report content to external services during masking unless the user explicitly permits that communication.

### Masking Tool Contract *(mandatory for this project)*

- **MC-001**: Specification MUST state whether users select a file, a folder, or both.
- **MC-002**: Specification MUST cover supported extensions: `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`.
- **MC-003**: Specification MUST state that unsupported extensions are not modified and are reported as `skipped_unsupported`.
- **MC-004**: Specification MUST exclude image text, scanned PDFs, embedded objects, and OCR unless the constitution is amended.
- **MC-005**: Specification MUST use generated `検出語句` -> `置換提案` as the replacement contract for detected terms.
- **MC-006**: Specification MUST require masked files under per-run `output/YYYYMMDD-HHMMSS/` without overwriting input files.
- **MC-007**: Specification MUST require `機密情報検出結果.xlsx` with the columns `No`, `検出語句`, `置換提案`, `原文または前後の文脈`, `情報カテゴリ`, `リスクレベル`, `判定理由`, `推奨対応`.
- **MC-008**: Specification MUST require risk-level row coloring in the Excel report.
- **MC-009**: Specification MUST require single-file language selection, folder-mode language auto-detection, and default rule sets for English, Japanese, and Chinese.
- **MC-010**: Specification MUST cover regex-based replacement rules and explicitly specified replacement rules, including on/off control.
- **MC-011**: Specification MUST cover added ML/NER detection sources, including detection source, target languages, on/off control, unavailable-source behavior, conflict resolution, and report reason.

### Key Entities *(include if feature involves data)*

- **Report Display Settings**: Workbook presentation rules such as frozen header, filters, widths, wrapping, colors, and status row styling.
- **Person Name Detection Rule**: Configurable detection source that finds person names and produces `PERSON_連番` replacement suggestions.
- **Chinese Person Name Fallback Detection**: Deterministic fallback behavior used for Chinese person-name masking when the configured spaCy Chinese model is unavailable.
- **Phone Number Rule**: Configurable default rule that finds phone numbers and produces `PHONE_連番` replacement suggestions.
- **Enhanced Detection Result Row**: A report row that may originate from explicit, regex, person-name, or phone-number detection while preserving the existing replacement contract.
- **Detection Source**: The origin of a detection, used to explain whether the row came from explicit rule, regex rule, person-name detection, or phone-number detection.
- **Language-Separated Validation Sample**: A test input set grouped by one primary language to validate language-specific detection and replacement without cross-language ambiguity.
- **CJK Text Encoding Handling**: The expected ability to read and report Japanese and Chinese characters from text-family, Office, and text-based PDF files without garbling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated report workbooks have frozen headers, filters, readable column widths, and wrapped long-text columns.
- **SC-002**: In representative Japanese, English, and Chinese samples containing person names, at least one person-name detection is reported and masked for each language when the feature is enabled.
- **SC-003**: In samples containing representative Japanese, US, and Chinese phone-number formats, 100% of expected phone numbers in the fixture set are masked when phone detection is enabled.
- **SC-004**: In samples containing dates and postal codes, 0 fixture values marked as non-phone examples are masked as phone numbers.
- **SC-005**: Repeated runs with the same inputs, settings, and applied languages produce identical `PERSON_連番` and `PHONE_連番` replacement suggestions.
- **SC-006**: Existing masking behavior for explicit rules, regex rules, unsupported files, out-of-scope files, and input non-destruction remains passing after the enhancement.
- **SC-007**: English, Japanese, and Chinese language-separated sample folders each include supported text, Office, and text-based PDF files plus an unsupported file for skip verification.
- **SC-008**: In Japanese and Chinese validation samples, representative CJK strings are readable before processing and appear correctly in extracted text or report context after processing.
- **SC-009**: A default masking run completes without requiring external communication, and any external communication path requires an explicit user permission state before it can transmit masking-related content.

## Assumptions

- Users continue to select either a single file or a folder using the existing workflow.
- The requested spaCy adoption is a planning constraint for person-name detection; this specification describes the user-visible detection behavior rather than model internals.
- Person-name detection is enabled by default and can be disabled when users want only explicit and regex-based masking.
- Chinese person-name detection uses the configured spaCy model, defaulting to `zh_core_web_sm`, when available and falls back to deterministic Chinese name-pattern detection when the model is unavailable.
- Phone-number detection is delivered as an enabled default rule unless the user disables it.
- Existing `カテゴリ_連番` replacement behavior applies to `PERSON` and `PHONE`.
- The same detected phone-number value receives the same `PHONE_連番` replacement suggestion within a processing run.
- Existing supported extensions, OCR exclusions, and per-run output layout are unchanged.
- Mixed-language files may remain available for stress testing, but standard acceptance verification uses language-separated files.
- Text-family inputs may include UTF-8 BOM because they are often opened or edited on Windows.
- Dependency and model installation may use normal package sources outside the masking run, but masking execution itself treats external communication as opt-in only.
