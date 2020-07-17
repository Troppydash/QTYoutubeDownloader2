import sys

import PyQt5
import youtube_dl
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool, QMutex
from PyQt5.QtWidgets import QFileDialog

from MainWindow import Ui_MainWindow

import sys
from WorkerThread import Worker


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.threadpool = QThreadPool()

        self.CancelButton.clicked.connect(self.handleClose)
        self.DownloadButton.clicked.connect(self.handleDownload)

        self.settings = {
            "url": "",
            "type": "video",
            "dir": "C:\\Documents\\QTYoutubeDownloader"
        }

        # File Location
        self.DirSelectButton.clicked.connect(self.openDirSelect)

        # Type Of Url
        self.TypeSelectbox.addItems(["Video", "Audio"])
        self.TypeSelectbox.activated[str].connect(self.setType)
        self.show()

        # Url
        self.TextUrl.textChanged.connect(self.setUrl)

        self._mutex = QMutex()

    def openDirSelect(self, s):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.settings["dir"] = file
        self.DirText.setText(file)

    def setUrl(self, t):
        self.settings["url"] = t

    def setType(self, t):
        self.settings["type"] = t.lower()

    def setDebugText(self, text):
        self._mutex.lock()
        self.DebugText.setText(text)
        self.DebugText.verticalScrollBar().setValue(self.DebugText.verticalScrollBar().maximum())
        self._mutex.unlock()

    def addLog(self, log):
        self.setDebugText(self.DebugText.toPlainText() + "\n" + log)

    def handleDownload(self):
        opt = self.getOptions(self.settings)
        worker = Worker(self.download, self.settings["url"], opt)
        worker.signals.progress.connect(self.addLog)
        worker.signals.finished.connect(self.onComplete)

        self.DebugText.setText("")
        self.threadpool.start(worker)

    def onComplete(self, msg):
        self.setDebugText("Downloaded to {}.".format(self.settings["dir"]))

    @staticmethod
    def getOptions(setting):
        isAudio = setting["type"] == "audio"
        out = {
            'format': "bestaudio/best" if isAudio else "bestvideo+bestaudio",
            'outtmpl': "{}/%(title)s.%(ext)s".format(setting["dir"]),
            'ignoreerrors': True
        }
        if isAudio:
            out["postprocessors"] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192',
            }]

        return out

    @staticmethod
    def download(url: str, opt, progress_callback):
        opt['logger'] = Logger(progress_callback)
        with youtube_dl.YoutubeDL(opt) as ydl:
            ydl.download([url])

    @staticmethod
    def handleClose():
        app.exit(0)
        quit(0)


class Logger:
    def __init__(self, callback):
        self.callback = callback

    def debug(self, msg):
        self.callback.emit(msg)

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


app = QtWidgets.QApplication(sys.argv)
print(PyQt5.QtWidgets.QStyleFactory.keys())
app.setStyle('Fusion')
window = MainWindow()

app.exec()
