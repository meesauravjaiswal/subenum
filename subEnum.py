import sys
import os
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


# Subdomain scanner thread
class SubdomainScanner(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, domain, wordlist_path):
        super().__init__()
        self.domain = domain
        self.wordlist_path = wordlist_path

    def run(self):
        try:
            with open(self.wordlist_path, 'r') as wordlist:
                for line in wordlist:
                    sub = line.strip()
                    test_url = f"{sub}.{self.domain}"
                    for scheme in ["https://", "http://"]:
                        try:
                            response = requests.get(scheme + test_url, timeout=5)
                            if response.status_code < 400:
                                self.result_signal.emit(f"[+] Found: {scheme}{test_url}")
                                break
                        except requests.RequestException:
                            continue
        except FileNotFoundError:
            self.result_signal.emit(f"[!] Wordlist file not found: {self.wordlist_path}")
        except Exception as e:
            self.result_signal.emit(f"[!] Error: {str(e)}")


# Main GUI Window
class SubdomainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subdomain Scanner")
        self.setGeometry(300, 200, 700, 500)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter target domain (e.g., example.com)")

        self.wordlist_path = QLineEdit()
        self.wordlist_path.setPlaceholderText("Select a wordlist...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_wordlist)

        wordlist_layout = QHBoxLayout()
        wordlist_layout.addWidget(self.wordlist_path)
        wordlist_layout.addWidget(browse_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        scan_btn = QPushButton("Start Scan")
        scan_btn.clicked.connect(self.start_scan)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Target Domain:"))
        layout.addWidget(self.domain_input)
        layout.addWidget(QLabel("Wordlist:"))
        layout.addLayout(wordlist_layout)
        layout.addWidget(scan_btn)
        layout.addWidget(QLabel("Scan Output:"))
        layout.addWidget(self.output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def browse_wordlist(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Wordlist File")
        if file_path:
            self.wordlist_path.setText(file_path)

    def start_scan(self):
        domain = self.domain_input.text().strip()
        wordlist = self.wordlist_path.text().strip()

        if not domain or "." not in domain:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid domain.")
            return
        if not os.path.isfile(wordlist):
            QMessageBox.warning(self, "File Error", "Please select a valid wordlist file.")
            return

        self.output.clear()
        self.output.append(f"[*] Starting scan for {domain}...\n")

        self.scanner_thread = SubdomainScanner(domain, wordlist)
        self.scanner_thread.result_signal.connect(self.output.append)
        self.scanner_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SubdomainGUI()
    gui.show()
    sys.exit(app.exec())
