import os
import sys
import json
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtGui import *
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest


CONFIG_FILE = "config.json"
HISTORY_FILE = "history.json"
BOOKMARKS_FILE = "bookmarks.json"

# Define search engines and their base URLs
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Yandex": "https://yandex.com/search/?text=",
    "DuckDuckGo": "https://www.duckduckgo.com/?q=",
    "Bing": "https://www.bing.com",
    "Yep.com": "https://yep.com",
    "Gibiru": "https://gibiru.com"\
}

def load_config():
    default_config = {
        "home_url": "https://www.duckduckgo.com",
        "default_search_engine": "DuckDuckGo",
        "dark_mode": False,
        "show_toolbar": True
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

def load_json_file(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return default
    return default

def save_json_file(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

class DownloadManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Manager")
        self.setLayout(QVBoxLayout())

        self.download_list = QListWidget()
        self.layout().addWidget(self.download_list)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.layout().addWidget(self.close_button)

        self.downloads = {}

    def add_download(self, download_item):
        item = QListWidgetItem(f"Downloading: {download_item.url().fileName()}")
        self.download_list.addItem(item)
        self.downloads[download_item] = item

        # Update progress manually
        self.update_progress(item, download_item)

    def update_progress(self, item, download_item):
        total = download_item.totalBytes()
        received = download_item.receivedBytes()
        if total > 0:
            percent = int(received / total * 100)
            item.setText(f"Downloading: {download_item.url().fileName()} ({percent}%)")
        else:
            item.setText(f"Downloading: {download_item.url().fileName()} (Unknown size)")

        # Check if download is finished
        if download_item.isFinished():
            self.download_finished(item, download_item)
        else:
            QTimer.singleShot(500, lambda: self.update_progress(item, download_item))

    def download_finished(self, item, download_item):
        if download_item.state() == QWebEngineDownloadRequest.DownloadCompleted:
            item.setText(f"Completed: {download_item.url().fileName()}")
        else:
            item.setText(f"Failed: {download_item.url().fileName()}")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.config = load_config()
        self.history = load_json_file(HISTORY_FILE, [])
        self.bookmarks = load_json_file(BOOKMARKS_FILE, [])

        # Apply dark mode if enabled
        if self.config["dark_mode"]:
            self.enable_dark_mode()

        # Initialize Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.open_tab_context_menu)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)

        # Add navigation bar
        self.navbar = QToolBar()
        self.navbar.setVisible(self.config.get("show_toolbar", True))
        self.addToolBar(self.navbar)

        # Back button with icon
        back_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "", self)
        back_btn.triggered.connect(self.navigate_back)
        self.navbar.addAction(back_btn)

        # Forward button with icon
        forward_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "", self)
        forward_btn.triggered.connect(self.navigate_forward)
        self.navbar.addAction(forward_btn)

        # Refresh button with icon
        refresh_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "", self)
        refresh_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(refresh_btn)

        # Home button with icon
        home_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon), "", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # New Tab button with icon
        new_tab_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # History button
        history_btn = QAction("History", self)
        history_btn.triggered.connect(self.show_history)
        self.navbar.addAction(history_btn)

        # Bookmarks button
        bookmarks_btn = QAction("Bookmarks", self)
        bookmarks_btn.triggered.connect(self.show_bookmarks)
        self.navbar.addAction(bookmarks_btn)

        # Download Manager button
        download_manager_btn = QAction("Downloads", self)
        download_manager_btn.triggered.connect(self.open_download_manager)
        self.navbar.addAction(download_manager_btn)

        # Settings button with icon
        settings_btn = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "", self)
        settings_btn.triggered.connect(self.open_settings)
        self.navbar.addAction(settings_btn)

        # Download Manager Dialog
        self.download_manager = DownloadManagerDialog(self)

        # Initial Tab
        self.add_new_tab(QUrl(self.config["home_url"]), "Home")

    def enable_dark_mode(self):
        app.setStyle("Fusion")
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark_palette)

    def add_new_tab(self, url=None, label="New Tab"):
        if url is None or not isinstance(url, QUrl):
            url = QUrl(self.config["home_url"])
        elif isinstance(url, str):
            url = QUrl(url)

        browser = QWebEngineView()
        browser.setUrl(url)
        browser.urlChanged.connect(lambda q, browser=browser: self.update_tab(q, browser))
        browser.urlChanged.connect(self.record_history)
        browser.page().profile().downloadRequested.connect(self.handle_download)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

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

    def record_history(self, url):
        url_str = url.toString()
        if url_str not in self.history:
            self.history.append(url_str)
            save_json_file(HISTORY_FILE, self.history)

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QFormLayout()
        dialog.setLayout(layout)

        # Home URL setting
        home_url_edit = QLineEdit(self.config["home_url"])
        layout.addRow("Home URL:", home_url_edit)

        # Default search engine setting (Dropdown menu)
        search_engine_combo = QComboBox()
        search_engine_combo.addItems(SEARCH_ENGINES.keys())
        search_engine_combo.setCurrentText(self.config["default_search_engine"])
        layout.addRow("Default Search Engine:", search_engine_combo)

        # Dark mode toggle
        dark_mode_checkbox = QCheckBox()
        dark_mode_checkbox.setChecked(self.config["dark_mode"])
        layout.addRow("Enable Dark Mode:", dark_mode_checkbox)

        # Show/Hide toolbar toggle
        toolbar_checkbox = QCheckBox()
        toolbar_checkbox.setChecked(self.config.get("show_toolbar", True))
        layout.addRow("Show Toolbar:", toolbar_checkbox)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_settings(home_url_edit.text(), search_engine_combo.currentText(), dark_mode_checkbox.isChecked(), toolbar_checkbox.isChecked(), dialog))
        layout.addRow(save_button)

        dialog.exec()

    def save_settings(self, home_url, search_engine, dark_mode, show_toolbar, dialog):
        self.config["home_url"] = home_url
        self.config["default_search_engine"] = search_engine
        self.config["dark_mode"] = dark_mode
        self.config["show_toolbar"] = show_toolbar

        if dark_mode:
            self.enable_dark_mode()
        else:
            app.setPalette(QApplication.style().standardPalette())

        self.navbar.setVisible(show_toolbar)

        save_config(self.config)
        dialog.accept()

    def show_history(self):
        self.show_list_dialog("History", self.history)

    def show_bookmarks(self):
        self.show_list_dialog("Bookmarks", self.bookmarks)

    def show_list_dialog(self, title, items):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        list_widget = QListWidget()
        list_widget.addItems(items)
        layout.addWidget(list_widget)

        add_button = QPushButton("Add to Bookmarks")
        add_button.clicked.connect(lambda: self.add_to_bookmarks(list_widget.currentItem()))
        layout.addWidget(add_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    def add_to_bookmarks(self, item):
        if item and item.text() not in self.bookmarks:
            self.bookmarks.append(item.text())
            save_json_file(BOOKMARKS_FILE, self.bookmarks)

    def open_tab_context_menu(self, position):
        menu = QMenu()
        close_action = menu.addAction("Close Tab")
        duplicate_action = menu.addAction("Duplicate Tab")
        reload_action = menu.addAction("Reload Tab")

        action = menu.exec(self.tabs.mapToGlobal(position))
        index = self.tabs.tabBar().tabAt(position)

        if action == close_action:
            self.close_current_tab(index)
        elif action == duplicate_action:
            current_url = self.tabs.widget(index).url()
            self.add_new_tab(current_url, "Duplicate Tab")
        elif action == reload_action:
            self.tabs.widget(index).reload()

    def open_download_manager(self):
        self.download_manager.show()

    def handle_download(self, download_item):
        self.download_manager.add_download(download_item)
        download_item.accept()

app = QApplication(sys.argv)
QApplication.setApplicationName("Gamma Browser")
window = MainWindow()
window.show()
app.exec()

