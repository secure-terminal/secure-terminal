## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

"""Application entry point for secure-terminal."""

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from secure_terminal.terminal import SecureTerminal


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('secure-terminal')

    window = QMainWindow()
    window.setWindowTitle('secure-terminal')
    terminal = SecureTerminal(window)
    window.setCentralWidget(terminal)
    window.resize(820, 520)
    window.show()
    terminal.setFocus()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
