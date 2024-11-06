import os
import sys
import json
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

CONFIG_FILE = "config.json"

# Define search engines and their base URLs
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Yandex": "https://yandex.com/search/?text=",
    "DuckDuckGo": "https://www.duckduckgo.com/?q="
}

def load_config():
    default_config = {
        "home_url": "https://www.duckduckgo.com",
        "default_search_engine": "DuckDuckGo"
    }

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}

    # Update config with any missing keys from default_config
    for key, value in default_config.items():
        config.setdefault(key, value)

    # Save updated config if any defaults were added
    save_config(config)
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.config = load_config()

        # Initialize Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)

        # Add navigation bar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Back button with icon
        back_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "", self)
        back_btn.triggered.connect(self.navigate_back)
        navbar.addAction(back_btn)

        # Forward button with icon
        forward_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "", self)
        forward_btn.triggered.connect(self.navigate_forward)
        navbar.addAction(forward_btn)

        # Refresh button with icon
        refresh_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "", self)
        refresh_btn.triggered.connect(self.reload_page)
        navbar.addAction(refresh_btn)

        # Home button with icon
        home_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon), "", self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # New Tab button with icon
        new_tab_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Settings button with icon
        settings_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "", self)
        settings_btn.triggered.connect(self.open_settings)
        navbar.addAction(settings_btn)

        # Initial Tab
        self.add_new_tab(QUrl(self.config["home_url"]), "Home")

    def add_new_tab(self, url=None, label="New Tab"):
        if url is None:
            url = QUrl(self.config["home_url"])
        browser = QWebEngineView()
        browser.setUrl(url)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda q, browser=browser: self.update_tab(q, browser))

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_back(self):
        self.tabs.currentWidget().back()

    def navigate_forward(self):
        self.tabs.currentWidget().forward()

    def reload_page(self):
        self.tabs.currentWidget().reload()

    def navigate_home(self):
        home_url = self.config["home_url"]
        self.tabs.currentWidget().setUrl(QUrl(home_url))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            search_engine_url = SEARCH_ENGINES[self.config["default_search_engine"]]
            url = f"{search_engine_url}{url}"
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_tab(self, q, browser):
        i = self.tabs.indexOf(browser)
        if i != -1:
            self.tabs.setTabText(i, browser.page().title())
        self.update_url_bar()

    def update_url_bar(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setLayout(QVBoxLayout())

        # Home URL setting
        home_url_label = QLabel("Home URL:")
        home_url_edit = QLineEdit(self.config["home_url"])
        dialog.layout().addWidget(home_url_label)
        dialog.layout().addWidget(home_url_edit)

        # Default search engine setting (Dropdown menu)
        search_engine_label = QLabel("Default Search Engine:")
        search_engine_combo = QComboBox()
        search_engine_combo.addItems(SEARCH_ENGINES.keys())
        search_engine_combo.setCurrentText(self.config["default_search_engine"])
        dialog.layout().addWidget(search_engine_label)
        dialog.layout().addWidget(search_engine_combo)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_settings(home_url_edit.text(), search_engine_combo.currentText(), dialog))
        dialog.layout().addWidget(save_button)

        # Credentials button
        credentials_button = QPushButton("Credentials")
        credentials_button.clicked.connect(self.show_credentials)
        dialog.layout().addWidget(credentials_button)

        dialog.exec()

    def save_settings(self, home_url, search_engine, dialog):
        self.config["home_url"] = home_url
        self.config["default_search_engine"] = search_engine
        save_config(self.config)
        dialog.accept()

    def show_credentials(self):
        # Display the credentials in a dialog
        credentials_dialog = QDialog(self)
        credentials_dialog.setWindowTitle("APOLLO Community")
        credentials_dialog.setLayout(QVBoxLayout())

        # Title
        title_label = QLabel("[APOLLO Community]")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        credentials_dialog.layout().addWidget(title_label)

        # Message
        message_label = QLabel("With love, from E.G., APOLLO Community's main developer, and ChatGPT 4.")
        credentials_dialog.layout().addWidget(message_label)

        # OK button to close dialog
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(credentials_dialog.accept)
        credentials_dialog.layout().addWidget(ok_button)

        credentials_dialog.exec()

app = QApplication(sys.argv)
QApplication.setApplicationName("Gamma Browser")
window = MainWindow()
window.show()
app.exec()
