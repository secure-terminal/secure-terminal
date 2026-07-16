## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

"""The paste-warning dialog.

When a paste carries unicode or control characters, this dialog shows the text
four ways side by side -- the original as it would look, a Reveal rendering where
every non-ASCII character is a <U+XXXX> badge, and the two things you can actually
send: the stripped ASCII, and the same with printable unicode kept -- so you can
see exactly what each choice does before it reaches the shell. Three choices:
Reject (default), Paste stripped (safe, ASCII only), and Paste with unicode
(keeps the euro sign / accents / CJK but still drops control, bidi and zero-width;
red and countdown-gated so a stray Enter cannot send it).
"""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QDialog, QLabel, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QGridLayout,
)

# import the pure helpers from the core, not from terminal, to avoid an import
# cycle (terminal imports this dialog lazily for the paste warning).
from secure_terminal.sanitize import (
    render_output, classify_paste, sanitize_paste, sanitize_paste_unicode,
)


class PasteWarningDialog(QDialog):
    def __init__(self, text, delay_seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Paste warning')
        self.setModal(True)
        self._remaining = max(0, int(delay_seconds))

        findings = classify_paste(text)
        parts = ['%d %s%s' % (count, label, '' if count == 1 else 's')
                 for label, count in findings]
        if parts:
            headline = 'This paste hides ' + ', '.join(parts) + '.'
        else:
            headline = 'This paste contains hidden characters.'

        outer = QVBoxLayout(self)

        # warning row: a red dot + the headline
        row = QHBoxLayout()
        dot = QLabel()
        dot.setFixedSize(16, 16)
        dot.setStyleSheet('background-color:#d83933; border-radius:8px;')
        row.addWidget(dot)
        title = QLabel(headline)
        title.setStyleSheet('font-weight:bold;')
        row.addWidget(title)
        row.addStretch(1)
        outer.addLayout(row)

        outer.addWidget(QLabel(
            'Review it before it reaches the shell. The panes show, in order: how '
            'it looks, every hidden character revealed as a <U+XXXX> badge, and '
            'exactly what each button would send -- stripped to ASCII, or with '
            'printable unicode kept (control, bidi and zero-width dropped either '
            'way).'))

        # four previews: as-copied, revealed, and the two send options
        grid = QGridLayout()
        grid.addWidget(QLabel('Original (as copied)'), 0, 0)
        grid.addWidget(QLabel('Reveal (what is really there)'), 0, 1)
        grid.addWidget(QLabel('Paste stripped sends'), 0, 2)
        grid.addWidget(QLabel('Paste with unicode sends'), 0, 3)
        original = QPlainTextEdit(text)
        revealed = QPlainTextEdit(render_output(text, 'reveal'))
        # the sanitizers submit lines with '\r'; show them as newlines here
        stripped = QPlainTextEdit(sanitize_paste(text).replace('\r', '\n'))
        withuni = QPlainTextEdit(sanitize_paste_unicode(text).replace('\r', '\n'))
        for column, view in enumerate((original, revealed, stripped, withuni)):
            view.setReadOnly(True)
            view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            view.setMinimumSize(210, 150)
            grid.addWidget(view, 1, column)
        outer.addLayout(grid)

        # three choices: Reject (default), Paste stripped (green, safe), Paste
        # with unicode (red, countdown-gated because it sends non-ASCII bytes).
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self._reject = QPushButton('Reject')
        self._reject.clicked.connect(lambda: self._done('reject'))
        buttons.addWidget(self._reject)
        stripped_btn = QPushButton('Paste stripped')
        stripped_btn.setStyleSheet('color:#0a5c37; font-weight:600;')
        stripped_btn.clicked.connect(lambda: self._done('stripped'))
        buttons.addWidget(stripped_btn)
        self._unicode_btn = QPushButton('Paste with unicode')
        self._unicode_btn.setStyleSheet('color:#b1170f; font-weight:600;')
        self._unicode_btn.clicked.connect(lambda: self._done('unicode'))
        buttons.addWidget(self._unicode_btn)
        outer.addLayout(buttons)

        self._result = 'reject'
        self._reject.setDefault(True)
        self._reject.setFocus()

        # only the risky "with unicode" button is gated, so a stray Enter cannot
        # send non-ASCII bytes; the stripped paste is always available.
        if self._remaining > 0:
            self._unicode_btn.setEnabled(False)
            self._tick()
            self._countdown = QTimer(self)
            self._countdown.timeout.connect(self._tick)
            self._countdown.start(1000)

    def _done(self, result):
        self._result = result
        self.accept()

    def _tick(self):
        if self._remaining > 0:
            self._unicode_btn.setText('Paste with unicode (%d)' % self._remaining)
            self._remaining -= 1
        else:
            self._unicode_btn.setText('Paste with unicode')
            self._unicode_btn.setEnabled(True)
            if hasattr(self, '_countdown'):
                self._countdown.stop()

    @staticmethod
    def confirm(text, delay_seconds, parent=None):
        """Show the dialog; return the chosen action: 'reject', 'stripped' or
        'unicode'."""
        dialog = PasteWarningDialog(text, delay_seconds, parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return 'reject'
        return dialog._result
