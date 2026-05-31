import os
from PySide6.QtCore import QThread, Signal, QObject, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QComboBox, QCheckBox, QProgressBar, QLabel, QHBoxLayout, QWidget
from core.scrapers import get_scraper_for_url

class FetchThread(QThread):
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.scraper = get_scraper_for_url(url)

    def run(self):
        try:
            # Passa o callback se o scraper suportar (args default)
            import inspect
            sig = inspect.signature(self.scraper.get_chapter_groups)
            if 'progress_callback' in sig.parameters:
                groups = self.scraper.get_chapter_groups(self.url, progress_callback=self.progress.emit)
            else:
                groups = self.scraper.get_chapter_groups(self.url)
            self.finished.emit(groups)
        except Exception as e:
            self.error.emit(str(e))

class DownloadThread(QThread):
    progress = Signal(int, int) # current, total
    log = Signal(str)
    success = Signal(str)
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
            if total == 1:
                base_path = self.output_dir
            else:
                base_path = os.path.join(self.output_dir, self.series_name)
            
            last_chap_name = ""
            for i, chap_url in enumerate(self.chapters):
                import re
                
                # Tentar extrair o número do capítulo usando a url completa
                match = re.search(r'(?:chapter|capitulo|cap|ch|episode|ep)(?:_no)?(?:[-_=/\s]*)(\d+(?:\.\d+)?)', str(chap_url), re.IGNORECASE)
                if match:
                    raw_chap_name = f"Capitulo {match.group(1)}"
                else:
                    clean_chap_url = str(chap_url).split('?')[0].strip('/')
                    chap_parts = [p for p in clean_chap_url.split('/') if p]
                    if chap_parts and chap_parts[-1] in ('list', 'viewer') and len(chap_parts) > 1:
                        raw_chap_name = chap_parts[-2]
                    else:
                        raw_chap_name = chap_parts[-1] if chap_parts else f"Capitulo_{i+1}"
                
                chap_name = re.sub(r'[\\/:*?"<>|]', '_', raw_chap_name)
                last_chap_name = chap_name
                self.log.emit(f"Baixando {chap_name}...")
                
                count = self.scraper.download_chapter(chap_url, base_path, chap_name)
                if count == 0:
                    raise Exception(f"Nenhuma imagem encontrada ou erro ao baixar {chap_name}.")
                
                self.log.emit(f"✓ {chap_name}: {count} imagens salvas.")
                self.progress.emit(i + 1, total)
                
            if total == 1:
                final_path = os.path.join(self.output_dir, last_chap_name)
            else:
                final_path = base_path
                
            self.success.emit(final_path)
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
        self.fetch_thread.progress.connect(lambda msg: self.dlStatusLabel.setText(msg))
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
            
            # Tentar extrair o número do capítulo a partir de formatações na URL inteira
            match = re.search(r'(?:chapter|capitulo|cap|ch|episode|ep)(?:_no)?(?:[-_=/\s]*)(\d+(?:\.\d+)?)', url_str, re.IGNORECASE)
            if match:
                return f"Capítulo {match.group(1)}"
                
            basename = url_str.split('?')[0].split('/')[-1]
                
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
        clean_url = url.split('?')[0].strip('/')
        parts = [p for p in clean_url.split('/') if p]
        
        if "chapter" in parts:
            idx = parts.index("chapter")
            series_name = parts[idx - 1] if idx > 0 else parts[-1]
        elif parts and parts[-1] in ('list', 'viewer') and len(parts) > 1:
            series_name = parts[-2]
        else:
            series_name = parts[-1] if parts else "Download"
            
        import re
        # Remove sufixos hexadecimais como -7b57f74d
        series_name = re.sub(r'-[a-f0-9]{8,12}$', '', series_name)
        # Troca hífens e underscores por espaços
        series_name = series_name.replace('-', ' ').replace('_', ' ')
        # Coloca as primeiras letras maiúsculas
        series_name = series_name.title()
        series_name = re.sub(r'[\\/:*?"<>|]', '_', series_name)

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
        self.download_thread.success.connect(self.on_dl_success)
        self.download_thread.error.connect(self.on_dl_error)
        self.download_thread.start()

    def on_dl_progress(self, current, total):
        self.dlProgressBar.setValue(current)

    def on_dl_log(self, msg):
        self.dlStatusLabel.setText(msg)

    def on_dl_success(self, final_path):
        self.w.dlDownloadButton.setEnabled(True)
        self.w.dlDownloadButton.setText("Baixar Capítulos Selecionados")
        self.dlStatusLabel.setText("Download concluído!")
        
        if self.dlAutoProcessCheckbox.isChecked():
            self.w.inputField.setText(final_path)
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
    
    # Tab changed logic moved to controller.py
