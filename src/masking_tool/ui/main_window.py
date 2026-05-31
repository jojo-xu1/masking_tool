from __future__ import annotations

import sys
from importlib.resources import files
from pathlib import Path

from masking_tool.config.loader import load_rule_files
from masking_tool.core.input_selection import make_file_selection, make_folder_selection
from masking_tool.core.processor import process


class MainWindow:
    def __init__(self) -> None:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QButtonGroup,
            QCheckBox,
            QComboBox,
            QFormLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QRadioButton,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        self.Qt = Qt
        self.QFileDialog = None
        self.QMessageBox = QMessageBox

        self.window = QMainWindow()
        self.window.setWindowTitle("Masking Tool")
        self.window.resize(820, 560)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Confidential String Masking")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        mode_row = QHBoxLayout()
        self.file_mode = QRadioButton("File")
        self.folder_mode = QRadioButton("Folder")
        self.file_mode.setChecked(True)
        self.mode_group = QButtonGroup(root)
        self.mode_group.addButton(self.file_mode)
        self.mode_group.addButton(self.folder_mode)
        mode_row.addWidget(QLabel("Input mode:"))
        mode_row.addWidget(self.file_mode)
        mode_row.addWidget(self.folder_mode)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        path_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Choose a file or folder to mask")
        self.browse_button = QPushButton("Browse")
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(self.browse_button)
        layout.addLayout(path_row)

        form = QFormLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["en", "ja", "zh"])
        self.language_note = QLabel("Single-file mode requires explicit language. Folder mode auto-detects each file.")
        self.language_note.setWordWrap(True)
        form.addRow("Language:", self.language_combo)
        form.addRow("", self.language_note)
        self.person_detection_check = QCheckBox("Person names")
        self.person_detection_check.setChecked(True)
        self.phone_detection_check = QCheckBox("Phone numbers")
        self.phone_detection_check.setChecked(True)
        form.addRow("Detection:", self.person_detection_check)
        form.addRow("", self.phone_detection_check)
        layout.addLayout(form)

        self.run_button = QPushButton("Run masking")
        self.run_button.setMinimumHeight(36)
        layout.addWidget(self.run_button)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Run results will appear here.")
        layout.addWidget(self.log, 1)

        self.window.setCentralWidget(root)
        self.window.setStyleSheet(
            """
            QMainWindow { background: #f7f8fa; }
            QLabel#titleLabel {
                font-size: 20px;
                font-weight: 700;
                color: #1f2937;
            }
            QLineEdit, QTextEdit, QComboBox {
                background: white;
                border: 1px solid #cfd6df;
                border-radius: 4px;
                padding: 7px;
                font-size: 13px;
            }
            QPushButton {
                background: #2563eb;
                color: white;
                border: 0;
                border-radius: 4px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #9ca3af; }
            QRadioButton, QLabel { font-size: 13px; color: #374151; }
            """
        )

        self.file_mode.toggled.connect(self._sync_mode)
        self.browse_button.clicked.connect(self._browse)
        self.run_button.clicked.connect(self._run)
        self._sync_mode()

    def show(self) -> None:
        self.window.show()

    def _sync_mode(self) -> None:
        is_file_mode = self.file_mode.isChecked()
        self.language_combo.setEnabled(is_file_mode)
        self.path_edit.setPlaceholderText("Choose a file to mask" if is_file_mode else "Choose a folder to mask")

    def _browse(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        if self.file_mode.isChecked():
            path, _ = QFileDialog.getOpenFileName(
                self.window,
                "Choose input file",
                "",
                "Supported files (*.txt *.csv *.log *.docx *.xlsx *.pptx *.pdf);;All files (*.*)",
            )
        else:
            path = QFileDialog.getExistingDirectory(self.window, "Choose input folder", "")
        if path:
            self.path_edit.setText(path)

    def _default_rule_paths(self) -> list[Path]:
        defaults = files("masking_tool_defaults")
        return [Path(str(defaults / name)) for name in ("en.yml", "ja.yml", "zh.yml")]

    def _run(self) -> None:
        raw_path = self.path_edit.text().strip()
        if not raw_path:
            self.QMessageBox.warning(self.window, "Missing input", "Choose an input file or folder first.")
            return

        try:
            input_path = Path(raw_path)
            if self.file_mode.isChecked():
                selection = make_file_selection(input_path, self.language_combo.currentText())
            else:
                selection = make_folder_selection(input_path)
            rules = load_rule_files(self._default_rule_paths())
            if not self.person_detection_check.isChecked():
                rules = [rule if rule.rule_type.value != "person" else _disabled_rule(rule) for rule in rules]
            if not self.phone_detection_check.isChecked():
                rules = [rule if rule.rule_type.value != "phone" else _disabled_rule(rule) for rule in rules]
            self.run_button.setEnabled(False)
            self.log.setPlainText("Processing...\n")
            output_dir, results = process(selection, rules)
            lines = [f"Output: {output_dir}", ""]
            for result in results:
                target = result.target
                lines.append(f"{target.status.value}: {target.relative_path}")
                if target.failure_reason:
                    lines.append(f"  reason: {target.failure_reason}")
            self.log.setPlainText("\n".join(lines))
            self.QMessageBox.information(self.window, "Masking complete", f"Output created:\n{output_dir}")
        except Exception as exc:
            self.log.setPlainText(f"Error: {exc}")
            self.QMessageBox.critical(self.window, "Masking failed", str(exc))
        finally:
            self.run_button.setEnabled(True)


def _disabled_rule(rule):
    from dataclasses import replace

    return replace(rule, enabled=False)


def run_app() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except Exception as exc:  # pragma: no cover
        print(f"PySide6 is required for the desktop UI: {exc}")
        return 1

    app = QApplication.instance() or QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    return app.exec()
