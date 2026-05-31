# Feature Specification: 行単位文脈・住所郵便番号マスク・UI進捗改善

**Feature Branch**: `004-address-postal-ui-progress`

**Created**: 2026-05-31

**Status**: Draft

**Input**: User description: "原文または前後の文脈は行単位で検出し、住所と郵便番号も置換する、各国のルールに従って検出する、UIの改善もする、実行中でプログレスバーを表示する、一行で複数検出した場合はそれぞれも置換する、原文または前後の文脈は置換前で表示する"

## Clarifications

### Session 2026-05-31

- Q: 住所と郵便番号が同じ行に連続している場合の置換単位はどうするか？ → A: 郵便番号部分は `POSTAL_CODE_連番`、住所部分は `ADDRESS_連番` として別々に置換する
- Q: 住所検出の範囲はどうするか？ → A: `住所:`, `Address:`, `地址:` などのラベル、または国別の明確な住所構造がある場合だけ検出する
- Q: 英語ファイルの住所・郵便番号ルール範囲はどうするか？ → A: 日本語は日本、英語は米国、中国語は中国の代表形式に限定する
- Q: 言語指定または言語判定ができない場合はどう扱うか？ → A: 単一ファイルで言語未指定または未対応なら実行前エラー、フォルダで言語判定不能なら対象ファイルを `failed` として置換せず理由をレポートする

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 行単位の原文文脈で検出結果を確認する (Priority: P1)

利用者は `機密情報検出結果.xlsx` を確認するとき、各検出行の `原文または前後の文脈` に、置換前の元テキストから該当語句を含む行全体が表示されるため、どの文脈で検出されたかを正確に判断できる。

**Why this priority**: レポート文脈が置換後だったり一部だけだったりすると、レビュー時に誤検出や漏れの判断が難しくなるため。

**Independent Test**: 一行に複数の検出語句を含むテキスト、CSV、ログ、Office、テキスト型PDFを処理し、各レポート行の文脈が置換前の同一行全体であることを確認する。

**Acceptance Scenarios**:

1. **Given** 一行に氏名、電話番号、郵便番号、住所が含まれる, **When** 利用者が処理を実行する, **Then** 各検出結果の `原文または前後の文脈` は置換前の同じ行全体を表示する
2. **Given** 一行に複数の機密語句が含まれる, **When** レポートが生成される, **Then** 検出語句ごとに個別の行が作成され、各行の文脈は同じ置換前原文行を保持する
3. **Given** 置換後ファイルで検出語句がラベルへ置換されている, **When** 利用者がレポートを確認する, **Then** レポート文脈には置換ラベルではなく置換前の原文が表示される

---

### User Story 2 - 各国ルールに従って住所と郵便番号をマスクする (Priority: P2)

利用者は英語、日本語、中国語のファイルに含まれる住所と郵便番号を、適用言語・対象国に応じた既定ルールで検出し、分類ラベル付きの不可逆な値へ置換できる。

**Why this priority**: 住所と郵便番号は個人情報・機密情報として頻出し、電話番号や人名と同じく既定で安定して置換対象にする必要があるため。

**Independent Test**: 日本語=日本、英語=米国、中国語=中国の言語別サンプルに住所と郵便番号を含めて処理し、期待する住所・郵便番号がそれぞれ `ADDRESS_連番` と `POSTAL_CODE_連番` で置換されることを確認する。

**Acceptance Scenarios**:

1. **Given** 日本語ファイルに日本の郵便番号と住所が含まれる, **When** 日本語ルールで処理する, **Then** 郵便番号は `POSTAL_CODE_001`、住所は `ADDRESS_001` 形式で置換される
2. **Given** 英語ファイルに米国形式のZIPコードと住所が含まれる, **When** 英語ルールで処理する, **Then** ZIPコードと住所が各カテゴリの置換提案で置換される
3. **Given** 中国語ファイルに中国形式の郵政编码と住所が含まれる, **When** 中国語ルールで処理する, **Then** 郵便番号と住所が各カテゴリの置換提案で置換される
4. **Given** 住所、郵便番号、人名、電話番号が同じ行に含まれる, **When** 処理が完了する, **Then** すべての検出語句がそれぞれのカテゴリで置換される

---

### User Story 3 - 実行中の進捗をUIで確認する (Priority: P3)

利用者は画面からファイルまたはフォルダ処理を開始した後、処理中であること、全体の進捗、完了・失敗の状態を視覚的に確認できる。

**Why this priority**: フォルダ処理や大きめのOffice/PDF処理では、無反応に見えると利用者が処理停止や重複実行をしてしまうため。

**Independent Test**: 複数ファイルのフォルダを画面から処理し、進捗バー、処理中状態、完了結果、失敗理由表示が一連の操作で確認できることを検証する。

**Acceptance Scenarios**:

1. **Given** 複数の対象ファイルを含むフォルダが選択されている, **When** 利用者が処理を開始する, **Then** 実行中は進捗バーが表示され、処理済み件数または進捗割合が更新される
2. **Given** 処理中である, **When** 利用者が画面を見る, **Then** 実行ボタンの重複実行が防止され、現在処理中であることが分かる
3. **Given** 処理が完了または一部失敗する, **When** 結果が表示される, **Then** 出力先、処理件数、失敗件数、失敗理由を確認できる

---

### Edge Cases

- 置換対象が同じ行に複数存在する場合でも、先頭の1件だけでなく全件を検出し、各検出語句を個別に置換する。
- 同じ住所または郵便番号が同一実行内で複数回出現する場合、同じ置換提案を再利用する。
- 郵便番号らしい数値が日付、電話番号、社員番号、金額など明らかに別カテゴリの値である場合、郵便番号として誤検出しない。
- 郵便番号は `Postal code:`, `ZIP:`, `postal=`, `郵便番号=`, `邮编=` などのラベル付き表記、CSV の `postal`/`zip`/`郵便番号`/`邮政编码` 列、XLSX の左隣またはヘッダーセルで郵便番号ラベルが示される値も検出対象とする。
- 住所検出と郵便番号検出が隣接する場合、郵便番号部分は `POSTAL_CODE_連番`、住所部分は `ADDRESS_連番` として別々にレポート・置換し、出力ファイルでは文字列が破損しないようにする。
- 住所は `住所:`, `Address:`, `地址:` などのラベル、または国別の明確な住所構造がある場合に検出し、住所らしい曖昧な文字列を広く推測して置換しない。
- フォルダ処理でファイルごとに適用言語が異なる場合、各ファイルの言語に応じた住所・郵便番号ルールを適用する。
- 単一ファイル処理で言語が未指定または未対応の場合、処理開始前にエラーとして扱い、入力ファイルも出力ファイルも変更しない。
- フォルダ処理でファイルの言語判定ができない場合、その対象ファイルは置換せず `failed` として扱い、理由を `機密情報検出結果.xlsx` に記録する。
- 住所・郵便番号の国別ルールは、日本語ファイルでは日本、英語ファイルでは米国、中国語ファイルでは中国の代表形式に限定し、それ以外の国・地域形式は第一版の標準検出対象外とする。
- テキスト型PDFの文脈行は抽出可能なテキスト行を対象とし、画像内文字、スキャンPDF、OCR、埋め込みオブジェクトは対象外のままとする。
- 画面処理中に一部ファイルが失敗しても、進捗表示と最終結果で成功・失敗を区別して確認できる。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST populate `原文または前後の文脈` with the full original line containing the detected term before any replacement is applied.
- **FR-002**: System MUST create a separate report row for each detected term when multiple sensitive values appear on the same original line.
- **FR-003**: System MUST replace every accepted detection on a line, not only the first detection in that line.
- **FR-004**: System MUST support configurable address detection as a default detection category for English, Japanese, and Chinese files.
- **FR-005**: System MUST support configurable postal-code detection as a default detection category for English, Japanese, and Chinese files.
- **FR-006**: System MUST apply country-appropriate address and postal-code rules based on the file's applied language: Japanese files use representative Japan formats, English files use representative US formats, and Chinese files use representative China formats.
- **FR-007**: System MUST mask detected addresses using deterministic `ADDRESS_連番` replacement suggestions.
- **FR-008**: System MUST mask detected postal codes using deterministic `POSTAL_CODE_連番` replacement suggestions.
- **FR-009**: System MUST apply the same replacement suggestion to the same address or postal-code value within a processing run.
- **FR-010**: System MUST report address detections with information category `ADDRESS`, risk level, judgment reason, and recommended action.
- **FR-011**: System MUST report postal-code detections with information category `POSTAL_CODE`, risk level, judgment reason, and recommended action.
- **FR-012**: System MUST avoid classifying dates, phone numbers, account numbers, money amounts, and other clearly non-postal numeric values as postal codes.
- **FR-012a**: System MUST detect supported postal-code values when postal-code context is provided by inline labels, key/value labels, CSV headers, or XLSX adjacent/header cells.
- **FR-013**: System MUST preserve existing conflict-resolution behavior for overlapping explicit, regex, person, phone, address, and postal-code detections.
- **FR-014**: Users MUST be able to enable or disable address and postal-code detection in the same general manner as other configurable detection sources.
- **FR-015**: The UI MUST show visible progress while processing is running.
- **FR-016**: The UI MUST prevent accidental duplicate processing starts while a run is already in progress.
- **FR-017**: The UI MUST show a completion summary including output location, processed count, skipped count, failed count, and failure reasons when available.
- **FR-018**: The UI MUST keep file/folder selection, language selection, and detection-source controls understandable and easy to scan.
- **FR-019**: System MUST keep original input files unchanged and write masked files only under the configured output location.
- **FR-020**: System MUST preserve the existing eight-column report layout and risk-level coloring while adding address, postal-code, and line-context behavior.
- **FR-021**: System MUST treat adjacent postal-code and address text as separate detections and separate replacements, using `POSTAL_CODE_連番` for the postal-code segment and `ADDRESS_連番` for the address segment.
- **FR-022**: System MUST limit address detection to values with address labels or country-appropriate address structures, and MUST avoid broad free-form guessing of ambiguous address-like text.
- **FR-023**: System MUST treat non-Japan formats in Japanese files, non-US formats in English files, and non-China formats in Chinese files as outside the default address and postal-code detection scope unless explicitly configured by the user.
- **FR-024**: System MUST fail validation before processing when single-file input has no language selection or an unsupported language selection.
- **FR-025**: System MUST mark a folder-mode target file as `failed`, avoid writing a masked output for that file, and report the reason when its language cannot be determined.

### Masking Tool Contract *(mandatory for this project)*

- **MC-001**: Specification covers both single-file selection and folder selection.
- **MC-002**: Specification covers supported extensions: `.txt`, `.csv`, `.log`, `.docx`, `.xlsx`, `.pptx`, `.pdf`.
- **MC-003**: Unsupported extensions are not modified and are reported as `skipped_unsupported`.
- **MC-004**: Image text, scanned PDFs, embedded objects, and OCR remain excluded.
- **MC-005**: Replacement uses `検出語句` -> `置換提案` for all accepted detected terms, including address and postal-code detections.
- **MC-006**: Masked files are written under `output` without overwriting input files.
- **MC-007**: `機密情報検出結果.xlsx` keeps the columns `No`, `検出語句`, `置換提案`, `原文または前後の文脈`, `情報カテゴリ`, `リスクレベル`, `判定理由`, `推奨対応`.
- **MC-008**: The Excel report keeps risk-level row coloring.
- **MC-009**: Single-file processing requires language selection; folder processing applies language handling per file; default rule sets exist for English, Japanese, and Chinese.
- **MC-010**: Regex-based replacement rules and explicitly specified replacement rules remain configurable with on/off control.
- **MC-011**: Address and postal-code detection sources must define target languages, on/off control, conflict behavior, and report reasons.

### Key Entities

- **Line Context**: The full original line that contains a detected term and is shown in the report before replacement.
- **Address Detection Rule**: A configurable detection source that identifies country-appropriate address values and produces `ADDRESS_連番` replacement suggestions.
- **Postal-Code Detection Rule**: A configurable detection source that identifies country-appropriate postal-code values and produces `POSTAL_CODE_連番` replacement suggestions.
- **Multi-Detection Line**: A single original line containing multiple accepted detections, each represented as an individual report row and replacement.
- **Processing Progress State**: The visible run state shown to users during UI execution, including current progress and final counts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In validation files containing multiple sensitive values on one line, 100% of expected values on that line are individually reported and replaced.
- **SC-002**: 100% of report rows for detected terms show a `原文または前後の文脈` value from the pre-replacement original line.
- **SC-003**: Japanese/Japan, English/US, and Chinese/China validation samples each mask at least one expected address and one expected postal code when the relevant detection sources are enabled.
- **SC-004**: Validation samples marked as non-postal numeric values produce zero postal-code detections.
- **SC-005**: Repeated runs with the same inputs and settings produce identical `ADDRESS_連番` and `POSTAL_CODE_連番` values.
- **SC-006**: During UI folder processing, users can see progress within 1 second of starting the run and can identify when processing is complete.
- **SC-007**: UI completion summary shows processed, skipped, and failed counts for every run involving more than one target file.
- **SC-008**: Existing supported-file processing, unsupported-file skips, input non-destruction, and the required report columns remain passing after the enhancement.
- **SC-009**: In validation rows where postal code and address are adjacent, the masked output contains separate postal-code and address replacement labels in the expected order.
- **SC-010**: Validation samples with labeled or structurally clear addresses are masked, while ambiguous unlabeled location-like text marked as non-address is not masked as an address.
- **SC-011**: Validation samples containing out-of-scope country formats for the applied language are not masked by default address or postal-code detection.
- **SC-012**: Single-file runs without a supported language selection fail before processing and leave the input unchanged.
- **SC-013**: Folder runs with a language-undetectable file continue processing other files and report the undetectable file as `failed` without creating a masked output for it.

## Assumptions

- Address and postal-code detection is limited to representative formats for the applied language/country and does not attempt global free-form address parsing beyond the default rule scope.
- Postal-code and address detection use the applied language to choose the expected country format: Japanese defaults to representative Japan patterns, English defaults to representative US patterns, and Chinese defaults to representative China patterns.
- Address detection uses surrounding labels or country-specific address markers to reduce false positives.
- Folder processing continues to determine the applied language per file before selecting country-appropriate rules.
- UI progress can be based on file-level completion rather than byte-level or page-level completion.
- Existing exclusions for image-only PDFs, scanned PDFs, OCR, and embedded objects remain unchanged.
