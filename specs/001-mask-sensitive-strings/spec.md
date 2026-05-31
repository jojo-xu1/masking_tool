# Feature Specification: 機密文字列マスキング

**Feature Branch**: `001-mask-sensitive-strings`

**Created**: 2026-05-30

**Status**: Draft

**Input**: User description: "Office ファイル、テキスト系ファイル、テキスト型 PDF に含まれる機密文字列を、分類ラベル付きの不可逆な値へ置換するツールを提供する。画面操作によりインプットファイル指定あるいはフォルダ指定。フォルダ指定の場合、フォルダ内すべての対象ファイルの置き換え処理が必要。第一版では、安全性と再現性を優先し、対応範囲を明示する。画像内文字、スキャン PDF、埋め込みオブジェクト、OCR は対象外とする。対応拡張子は .txt, .csv, .log, .docx, .xlsx, .pptx, .pdf。対象外の拡張子は処理せず、レポートへ skipped_unsupported として記録する。機密情報検出結果ファイルの検出語句を置換提案に置き換える。成果物は機密情報検出結果.xlsx と output フォルダ内の置換したファイル。Excel は指定列を持ち、リスクレベルにより行色を切り分ける。設定ファイルで正規表現置換と個別指定置換を管理し、一般的な機密情報正規表現をオンオフ管理する。英語、日本語、中国語のデフォルト設定を用意する。起動時にファイルの言語指定が必要。"

## Clarifications

### Session 2026-05-30

- Q: `機密情報検出結果.xlsx` は既存入力か、ツールが新規生成する成果物か？ → A: ツールが設定ファイルの正規表現・個別指定から `機密情報検出結果.xlsx` を新規生成し、それを使って置換する。
- Q: 置換提案の生成形式は何にするか？ → A: `カテゴリ_連番` 形式にする（例: `PERSON_001`, `EMAIL_002`）。
- Q: `output` に同名成果物が既にある場合どう扱うか？ → A: 実行ごとに `output/YYYYMMDD-HHMMSS/` を作成し、その中に成果物を出力する。
- Q: フォルダ処理時の言語指定はどう扱うか？ → A: ツールがファイルごとに言語を自動判定する。
- Q: 複数ルールが同じ文字列に一致した場合の優先順位は？ → A: 個別指定ルールを最優先し、次に高リスク、同リスクなら設定ファイル順で決める。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 単一ファイルをマスキングする (Priority: P1)

利用者は画面から対象ファイルを選択し、ファイル言語を指定して、設定ルールに基づく検出結果、置換済みファイル、レポートを得る。

**Why this priority**: 単一ファイル処理はツールの最小価値であり、置換契約、出力、レポートの中心動作を検証できる。

**Independent Test**: 対応拡張子の単一ファイルと有効な設定ルールを指定し、`output/YYYYMMDD-HHMMSS/` 配下に置換済みファイルが作成され、`機密情報検出結果.xlsx` に検出結果、置換提案、処理結果が記録されることを確認する。

**Acceptance Scenarios**:

1. **Given** 対応拡張子のファイル、言語指定、有効な正規表現または個別指定ルールがある, **When** 利用者が単一ファイル処理を実行する, **Then** ツールは `機密情報検出結果.xlsx` を生成し、検出語句は `カテゴリ_連番` 形式の置換提案へ置換され、置換済みファイルは実行ごとの `output/YYYYMMDD-HHMMSS/` に出力される
2. **Given** 検出語句が対象ファイル内に複数回存在する, **When** 利用者が処理を実行する, **Then** 該当箇所はすべて同じ置換提案へ置換される
3. **Given** 検出結果に含まれる語句が対象ファイルに存在しない, **When** 利用者が処理を実行する, **Then** ファイルは破壊されず、レポートに置換なしとして確認可能な状態が記録される

---

### User Story 2 - フォルダ内の対象ファイルを一括マスキングする (Priority: P2)

利用者は画面からフォルダを選択し、フォルダ内のすべての対象ファイルをまとめてマスキングし、対象ファイルごとの自動言語判定結果と対象外ファイルのスキップ結果を確認できる。

**Why this priority**: 実運用では複数ファイルをまとめて処理する必要があり、対象範囲とスキップ記録の信頼性が重要になる。

**Independent Test**: 複数言語の対応ファイルと対象外ファイルを含むフォルダを指定し、対応ファイルのみが実行ごとの出力フォルダに出力され、各対象ファイルの自動言語判定結果と対象外ファイルの `skipped_unsupported` がレポートに記録されることを確認する。

**Acceptance Scenarios**:

1. **Given** 対応拡張子と対象外拡張子が混在するフォルダがある, **When** 利用者がフォルダ処理を実行する, **Then** 対応拡張子のみが処理され、対象ファイルごとに言語が自動判定され、対象外拡張子は変更されず `skipped_unsupported` として記録される
2. **Given** フォルダ内にサブフォルダがある, **When** 利用者がフォルダ処理を実行する, **Then** 配下の対象ファイルはすべて処理対象になり、出力先で元の相対構造を追跡できる
3. **Given** 一部の対象ファイルで処理に失敗する, **When** 利用者がフォルダ処理を実行する, **Then** 他の処理可能なファイルは継続され、失敗したファイルは理由とともにレポートへ記録される

---

### User Story 3 - 設定ファイルでマスク対象を管理する (Priority: P3)

管理者または利用者は、正規表現ルールと個別指定ルールを設定し、英語・日本語・中国語の既定ルールをオン・オフして、処理対象に合わせたマスキングを行える。

**Why this priority**: 機密情報の種類は文書や組織で異なるため、設定可能性がないと継続利用に耐えない。

**Independent Test**: 言語別設定とルールのオン・オフ状態を変えて同じファイルを処理し、有効なルールだけがレポートと置換結果に反映されることを確認する。

**Acceptance Scenarios**:

1. **Given** 英語、日本語、中国語のいずれかの言語指定と既定ルールがある, **When** 利用者が処理を実行する, **Then** 指定言語の有効ルールだけが適用候補として扱われる
2. **Given** 正規表現ルールがオンになっている, **When** 対象ファイル内に該当パターンがある, **Then** 検出結果と置換提案に基づき該当文字列がマスキングされる
3. **Given** 個別指定ルールが設定されている, **When** 対象ファイル内に一致する文字列がある, **Then** 指定された内容が置換対象として扱われる

---

### Edge Cases

- 対応拡張子のファイルがフォルダ内に存在しない場合、処理対象なしとしてレポートを作成し、入力ファイルは変更しない。
- 単一ファイル処理で言語が未指定または未対応の場合、ファイル処理前にエラーを表示し、置換済みファイルを作成しない。
- フォルダ処理でファイルの言語を判定できない場合、そのファイルは置換せず、言語判定失敗としてレポートに理由を記録する。
- テキスト型ではない PDF、スキャン PDF、画像内文字、埋め込みオブジェクトは処理対象外として扱い、レポートで確認できるようにする。
- 読み取り不能、パスワード保護、破損ファイルなど処理不能な対象ファイルは失敗としてレポートに理由を記録し、他ファイルの処理を妨げない。
- ルールから置換提案を生成できない検出結果は置換せず、レポートで不完全な検出結果として識別できるようにする。
- 同じ文字列に複数ルールが一致する場合、個別指定ルールを最優先し、次に高リスク、同リスクなら設定ファイル順で採用ルールを決定する。
- 実行時刻が同一秒に重なり出力フォルダ名が衝突する場合、既存成果物を上書きせず、決定的に識別できる実行フォルダを作成する。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to select either a single input file or an input folder through the user interface.
- **FR-002**: System MUST require a file language selection before single-file processing starts.
- **FR-003**: System MUST support only `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, and text-based `.pdf` files as processing targets.
- **FR-004**: System MUST process every supported target file inside a selected folder, including files in subfolders.
- **FR-004a**: System MUST automatically determine the language for each supported target file during folder processing.
- **FR-005**: System MUST leave unsupported extensions unmodified and record them as `skipped_unsupported` in the report.
- **FR-006**: System MUST exclude image text, scanned PDFs, embedded objects, and OCR from v1 processing.
- **FR-007**: System MUST generate `機密情報検出結果.xlsx` from enabled regex-based and explicitly specified masking rules.
- **FR-008**: System MUST produce irreversible replacement suggestions in `カテゴリ_連番` format, such as `PERSON_001` or `EMAIL_002`.
- **FR-009**: System MUST write replaced files under a per-run `output/YYYYMMDD-HHMMSS/` folder and MUST NOT overwrite original input files.
- **FR-010**: System MUST use the generated `検出語句` and corresponding `置換提案` as the replacement mapping for each processing run.
- **FR-011**: System MUST include the report columns `No`, `検出語句`, `置換提案`, `原文または前後の文脈`, `情報カテゴリ`, `リスクレベル`, `判定理由`, and `推奨対応`.
- **FR-012**: System MUST visually distinguish report rows by `リスクレベル`.
- **FR-013**: System MUST record per-file processing status, including processed, no replacement, skipped unsupported, skipped out of scope, and failed.
- **FR-014**: System MUST support detection and masking rules configured as `正規表現で置換`.
- **FR-015**: System MUST support detection and masking rules configured as `個別指定した内容を置換`.
- **FR-016**: System MUST provide default configurable rule sets for English, Japanese, and Chinese files.
- **FR-017**: System MUST allow common confidential-information regular expression rules to be turned on or off.
- **FR-018**: System MUST produce the same replaced content and report for the same input files, applied languages, settings, and generated detection results.
- **FR-019**: System MUST report clear reasons when a file cannot be processed.
- **FR-020**: System MUST keep the original input files unchanged even when processing fails.
- **FR-021**: System MUST assign replacement sequence numbers deterministically for the same inputs, settings, and applied languages.
- **FR-022**: System MUST avoid overwriting existing output artifacts when a per-run output folder name collides.
- **FR-023**: System MUST record the applied or detected language for each processed target file in the report.
- **FR-024**: System MUST resolve rule conflicts by prioritizing explicit rules first, then higher risk level, then configuration file order.

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

### Key Entities *(include if feature involves data)*

- **Input Selection**: The file or folder chosen by the user, including path, selection type, explicit single-file language when provided, and folder-mode auto-detection mode.
- **Target File**: A file discovered from the input selection, including extension, relative location, processing eligibility, applied or detected language, status, and output location.
- **Detection Result Row**: A generated report row containing detected term, `カテゴリ_連番` replacement suggestion, context, information category, risk level, judgment reason, recommended action, and processing status.
- **Masking Rule**: A configurable rule that defines a regex-based or explicit replacement target, language, category, risk level, enabled state, configuration order, and replacement behavior.
- **Processing Report**: The generated Excel artifact that summarizes detections, replacements, skipped files, failures, risk levels, and recommended handling.
- **Masked Output File**: The replaced file written under a per-run `output/YYYYMMDD-HHMMSS/` folder, traceable to its original target file without modifying that original.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a single-file masking run and locate both the replaced file and report in the per-run output folder within 3 minutes after selecting valid inputs.
- **SC-002**: In a folder containing at least 20 mixed files across English, Japanese, and Chinese, 100% of supported files are processed or given a clear failure reason, and 100% of unsupported files are recorded as `skipped_unsupported`.
- **SC-003**: For the same inputs, settings, and applied languages, repeated runs produce identical detections, `カテゴリ_連番` replacement suggestions, replacement content, and report values.
- **SC-004**: 100% of report files contain all required columns and visually distinguish every row with a risk level.
- **SC-005**: 100% of original input files remain unchanged after successful runs, partial failures, and validation errors.
- **SC-006**: At least one default rule set is available for each supported language: English, Japanese, and Chinese.

## Assumptions

- Users operate the tool locally and have permission to read the selected input files and write to the selected output location.
- Single-file processing uses explicit language selection; folder processing uses per-file language auto-detection.
- Folder processing includes subfolders by default because the requirement says all target files inside the folder must be replaced.
- PDF support in v1 means text-based PDFs only; scanned PDFs and image-only PDFs are outside scope.
- If a file cannot be processed, the run continues for other files and records the failure in the report.
- Each run writes to a timestamped output folder. If that folder already exists, the tool uses a deterministic collision-avoidance suffix so results remain traceable.
- The confidential information result used for replacement is generated during the run from enabled settings and contains at least detected terms and replacement suggestions.
- Rule conflict resolution is deterministic and does not prompt users during processing.
