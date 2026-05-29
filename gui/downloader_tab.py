import os
from PySide6.QtCore import QThread, Signal, QObject, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QComboBox, QCheckBox, QProgressBar, QLabel, QHBoxLayout, QWidget
from core.scrapers import get_scraper_for_url

class FetchThread(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.scraper = get_scraper_for_url(url)

    def run(self):
        try:
            groups = self.scraper.get_chapter_groups(self.url)
            self.finished.emit(groups)
        except Exception as e:
            self.error.emit(str(e))

class DownloadThread(QThread):
    progress = Signal(int, int) # current, total
    log = Signal(str)
    success = Signal()
    error = Signal(str)

    def __init__(self, chapters, output_dir, series_name, url):
        super().__init__()
        self.chapters = chapters
        self.output_dir = output_dir
        self.series_name = series_name
        self.scraper = get_scraper_for_url(url)

    def run(self):
        try:
            total = len(self.chapters)
            series_path = os.path.join(self.output_dir, self.series_name)
            
            for i, chap_url in enumerate(self.chapters):
                # Extract chapter slug/name from url
                chap_name = [p for p in chap_url.split('/') if p][-1]
                self.log.emit(f"Baixando {chap_name}...")
                
                count = self.scraper.download_chapter(chap_url, series_path, chap_name)
                if count == 0:
                    raise Exception(f"Nenhuma imagem encontrada ou erro ao baixar {chap_name}.")
                
                self.log.emit(f"✓ {chap_name}: {count} imagens salvas.")
                self.progress.emit(i + 1, total)
                
            self.success.emit()
        except Exception as e:
            self.error.emit(str(e))

class DownloaderController(QObject):
    def __init__(self, main_window, settings):
        super().__init__()
        self.w = main_window
        self.s = settings
        
        self.w.dlDirField.setText(self.s.load("download_dir"))
        
        # Add checkbox for auto-processing
        self.dlAutoProcessCheckbox = QCheckBox("Processar automaticamente após baixar (Stitch)")
        self.dlAutoProcessCheckbox.setChecked(True)
        self.w.downloaderGroupBox.layout().insertWidget(3, self.dlAutoProcessCheckbox)
        
        # Add Group ComboBox with Label
        self.groupWidget = QWidget()
        self.groupLayout = QHBoxLayout(self.groupWidget)
        self.groupLayout.setContentsMargins(0, 0, 0, 0)
        self.groupLabel = QLabel("Selecione o Grupo de Tradução:")
        self.dlGroupCombo = QComboBox()
        self.groupLayout.addWidget(self.groupLabel)
        self.groupLayout.addWidget(self.dlGroupCombo)
        self.groupWidget.setVisible(False)
        self.w.downloaderGroupBox.layout().insertWidget(4, self.groupWidget)
        self.dlGroupCombo.currentTextChanged.connect(self.on_group_changed)
        
        # Add specific progress bar and label for downloader
        self.dlStatusLabel = QLabel("")
        self.dlProgressBar = QProgressBar()
        self.dlProgressBar.setValue(0)
        self.dlProgressBar.setVisible(False)
        self.dlStatusLabel.setVisible(False)
        self.w.downloaderGroupBox.layout().addWidget(self.dlStatusLabel)
        self.w.downloaderGroupBox.layout().addWidget(self.dlProgressBar)
        
        self.w.dlDirBrowseButton.clicked.connect(self.browse_dir)
        self.w.dlFetchButton.clicked.connect(self.fetch_chapters)
        self.w.dlDownloadButton.clicked.connect(self.start_download)
        
        self.fetch_thread = None
        self.download_thread = None
        self.current_groups = {}

    def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self.w, "Selecionar Pasta de Downloads", self.w.dlDirField.text())
        if d:
            self.w.dlDirField.setText(d)
            self.s.save("download_dir", d)

    def fetch_chapters(self):
        url = self.w.dlUrlField.text().strip()
        if not url:
            QMessageBox.warning(self.w, "Aviso", "Por favor, insira a URL da série.")
            return

        self.w.dlFetchButton.setEnabled(False)
        self.w.dlFetchButton.setText("Buscando...")
        self.w.dlChapterList.clear()
        self.dlGroupCombo.clear()
        self.groupWidget.setVisible(False)
        self.w.dlDownloadButton.setEnabled(False)
        
        self.dlStatusLabel.setVisible(True)
        self.dlStatusLabel.setText("Buscando capítulos...")
        self.dlProgressBar.setVisible(False)

        self.fetch_thread = FetchThread(url)
        self.fetch_thread.finished.connect(self.on_fetch_success)
        self.fetch_thread.error.connect(self.on_fetch_error)
        self.fetch_thread.start()

    def on_fetch_success(self, groups_dict):
        self.w.dlFetchButton.setEnabled(True)
        self.w.dlFetchButton.setText("Buscar Capítulos")
        
        if not groups_dict:
            self.dlStatusLabel.setText("Nenhum capítulo encontrado.")
            return
            
        self.current_groups = groups_dict
        
        if len(groups_dict) > 1:
            self.groupWidget.setVisible(True)
            self.dlGroupCombo.addItems(list(groups_dict.keys()))
        else:
            self.groupWidget.setVisible(False)
            group_name = list(groups_dict.keys())[0]
            self.dlGroupCombo.addItem(group_name)
            
        self.w.dlDownloadButton.setEnabled(True)

    def on_group_changed(self, group_name):
        self.w.dlChapterList.clear()
        if not group_name or group_name not in self.current_groups:
            return
            
        chapters = self.current_groups[group_name]
        self.dlStatusLabel.setText(f"{len(chapters)} capítulos encontrados no grupo '{group_name}'.")
        
        import re
        def format_chapter_name(url):
            url_str = str(url).rstrip('/')
            basename = url_str.split('/')[-1]
            
            # Tentar extrair o número de formatações comuns (ex: chapter-11, capitulo-2.5, ch-3)
            match = re.search(r'(?:chapter|capitulo|cap|ch)[-_\s]*(\d+(?:\.\d+)?)', basename, re.IGNORECASE)
            if match:
                return f"Capítulo {match.group(1)}"
                
            # Se a string inteira for só um número
            match = re.search(r'^(\d+(?:\.\d+)?)$', basename)
            if match:
                return f"Capítulo {match.group(1)}"
                
            # Fallback
            return basename.capitalize()
            
        for chap in chapters:
            chap_name = format_chapter_name(chap)
            item = QListWidgetItem(chap_name)
            item.setData(Qt.UserRole, str(chap))
            self.w.dlChapterList.addItem(item)
            # Removido: item.setSelected(True) para não marcar todos por padrão

    def on_fetch_error(self, err):
        self.w.dlFetchButton.setEnabled(True)
        self.w.dlFetchButton.setText("Buscar Capítulos")
        self.dlStatusLabel.setText("Erro ao buscar.")
        QMessageBox.critical(self.w, "Erro", f"Erro ao buscar capítulos:\n{err}")

    def start_download(self):
        selected = [item.data(Qt.UserRole) for item in self.w.dlChapterList.selectedItems()]
        if not selected:
            QMessageBox.warning(self.w, "Aviso", "Selecione pelo menos um capítulo para baixar.")
            return
            
        out_dir = self.w.dlDirField.text().strip()
        if not out_dir:
            QMessageBox.warning(self.w, "Aviso", "Por favor, selecione uma pasta de destino.")
            return

        url = self.w.dlUrlField.text().strip()
        parts = [p for p in url.split('/') if p]
        if "chapter" in parts:
            idx = parts.index("chapter")
            series_name = parts[idx - 1] if idx > 0 else parts[-1]
        else:
            series_name = parts[-1]

        self.w.dlDownloadButton.setEnabled(False)
        self.w.dlDownloadButton.setText("Baixando...")
        
        self.dlProgressBar.setVisible(True)
        self.dlStatusLabel.setVisible(True)
        self.dlProgressBar.setMaximum(len(selected))
        self.dlProgressBar.setValue(0)
        self.dlStatusLabel.setText("Iniciando download...")

        self.download_thread = DownloadThread(selected, out_dir, series_name, url)
        self.download_thread.progress.connect(self.on_dl_progress)
        self.download_thread.log.connect(self.on_dl_log)
        self.download_thread.success.connect(lambda: self.on_dl_success(out_dir, series_name))
        self.download_thread.error.connect(self.on_dl_error)
        self.download_thread.start()

    def on_dl_progress(self, current, total):
        self.dlProgressBar.setValue(current)

    def on_dl_log(self, msg):
        self.dlStatusLabel.setText(msg)

    def on_dl_success(self, out_dir, series_name):
        self.w.dlDownloadButton.setEnabled(True)
        self.w.dlDownloadButton.setText("Baixar Capítulos Selecionados")
        self.dlStatusLabel.setText("Download concluído!")
        
        if self.dlAutoProcessCheckbox.isChecked():
            series_path = os.path.join(out_dir, series_name)
            self.w.inputField.setText(series_path)
            # Make sure parallel processing is enabled to process all downloaded chapters
            self.w.parallelProcessingCheckbox.setChecked(True)
            self.s.save("parallel_processing", True)
            
            self.w.mainTabWidget.setCurrentIndex(0) # Go to basic tab
            self.w.startProcessButton.click()
        else:
            QMessageBox.information(self.w, "Sucesso", "Todos os capítulos selecionados foram baixados com sucesso!")

    def on_dl_error(self, err):
        self.w.dlDownloadButton.setEnabled(True)
        self.w.dlDownloadButton.setText("Baixar Capítulos Selecionados")
        self.dlStatusLabel.setText("Erro no download.")
        QMessageBox.critical(self.w, "Erro", f"Erro durante o download:\n{err}")

def setup_downloader_tab(main_window, settings):
    # Store reference so it's not garbage collected
    main_window._downloader_controller = DownloaderController(main_window, settings)
    
    # Hide ActionGroupBox when in Downloader tab
    def on_tab_changed(index):
        current_widget = main_window.mainTabWidget.widget(index)
        if current_widget and current_widget.objectName() == "downloaderTab":
            main_window.ActionGroupBox.setVisible(False)
        else:
            main_window.ActionGroupBox.setVisible(True)

    main_window.mainTabWidget.currentChanged.connect(on_tab_changed)
    on_tab_changed(main_window.mainTabWidget.currentIndex())
