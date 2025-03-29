#!/usr/bin/env python
import sys, os
import mimetypes
#from fire import Fire
from pathlib import Path
from PyQt5 import QtGui, QtCore,QtWidgets
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt

def is_valid(path):
    from PIL import Image
    try:
        Image.open(path)
        return True
    except:
        return False

def is_image(path):
    file_type = mimetypes.guess_file_type(path)[0]
    return file_type and file_type.split('/')[0] == 'image'


class QExampleLabel(QLabel):
    def __init__(self, parentQWidget = None):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.initUI()
        if sys.argv[1:]:
            self.files = [str(p.absolute()) for p in map(Path, sys.argv[1:]) if p.is_file() and p.suffix.lower() in exts]
            self.first()
        else:
            self.load_dir(os.getcwd())
        if not self.files:
            sys.exit(1)

    def load_dir(self, path):
        path = Path(path)
        print(path)
        self.files = [str(p.absolute()) for p in path.glob('*') if p.is_file() and p.suffix.lower() in exts]
        if not self.files:
            sys.exit(1)
        self.first()

    def setPixmap(self, pixmap: QPixmap): #overiding setPixmap
        if not pixmap or pixmap.isNull():
            path = self.path
            if self.files.index(path) == len(self.files)-1:
                self.prev()
            else:
                self.next()
            self.files.remove(path)
            print(f'Removed {path}')
            return 
        self.setWindowTitle(os.path.basename(self.path))
        self._pixmap = pixmap.copy()
        if '-s' in sys.argv:
            if pixmap.size().width() > self.size().width():
                pixmap = pixmap.scaledToWidth(self.size().width())
            if pixmap.size().height() > self.size().height():
                pixmap = pixmap.scaledToHeight(self.size().height())
        else:
            self.resize(pixmap.size())
        return super().setPixmap(pixmap)
        # res = QtWidgets.QLabel.setPixmap(self,self._pixmap.scaled(
        #         self.frameSize(),
        #         QtCore.Qt.KeepAspectRatio))
        # return res
    def ratio(self):
        return (self._pixmap.size().width() / self.size().width(), self._pixmap.size().height() / self.size().height())

    def saveas(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        ext = self.path.split('.')[-1]
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save File",os.path.basename(self.path) ,f"All Files(*);;{ext} Files(*.{ext})",options = options)
        if file_name:
            data = open(self.path, 'rb').read()
            with open(file_name, 'wb') as f:
                f.write(data)

            return True
        else:
            return False

    def movefile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        ext = self.path.split('.')[-1]
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save File",os.path.basename(self.path) ,f"All Files(*);;{ext} Files(*.{ext})",options = options)
        if file_name:
            path = self.path
            os.rename(path, file_name)
            if self.files.index(path) == len(self.files)-1:
                self.prev()
            else:
                self.next()
            self.files.remove(path)
            if not self.files:
                sys.exit(0)

            return True
        else:
            return False
    
    def first(self):
        self.path = self.files[0]
        self.setPixmap(QPixmap(self.path))

    def last(self):
        self.path = self.files[0]
        self.setPixmap(QPixmap(self.path))

    def next(self):
       try:
           self.path = self.files[self.files.index(self.path)+1]
       except IndexError:
           pass
       self.setPixmap(QPixmap(self.path))

    def prev(self):
       self.path = self.files[max(self.files.index(self.path)-1, 0)]
       self.setPixmap(QPixmap(self.path))

    def up_dir(self):
        if any(p for p in Path(self.path).parent.parent.glob('*') if p.is_file() and p.suffix.lower() in exts):
            self.load_dir(Path(self.path).parent.parent)

    def first_sub_dir(self):
        dirs = list(sorted(set(p.parent.absolute() for p in Path(self.path).parent.glob('*/*') if p.is_file() and p.suffix.lower() in exts)))
        if dirs:
            self.load_dir(dirs[0])

    def next_dir(self):
        dirs = list(sorted(set(p.parent.absolute() for p in Path(self.path).parent.parent.glob('*/*') if p.is_file() and p.suffix.lower() in exts)))
        try:
            self.load_dir(dirs[dirs.index(Path(self.path).parent)+1])
        except IndexError:
            pass

    def prev_dir(self):
        dirs = list(sorted(set(p.parent.absolute() for p in Path(self.path).parent.parent.glob('*/*') if p.is_file() and p.suffix.lower() in exts)))
        self.load_dir(dirs[max(dirs.index(Path(self.path).parent)-1, 0)])

    def initUI (self):
        self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)

    def keyPressEvent(self, k):
        if k.key() in (Qt.Key_Return, Qt.Key_Enter):
            currentQRect = self.currentQRubberBand.geometry()
            currentQRect.setLeft(int(currentQRect.left() * self.ratio()[0]))
            currentQRect.setWidth(int(currentQRect.width() * self.ratio()[0]))
            currentQRect.setTop(int(currentQRect.top() * self.ratio()[1]))
            currentQRect.setHeight(int(currentQRect.height() * self.ratio()[1]))
            cropQPixmap = self._pixmap.copy(currentQRect)
            cropQPixmap.save(self.path)
            self.next()
        if k.key() == Qt.Key_Escape:
            sys.exit(0)
        if k.key() == Qt.Key_Left:
            self.prev()
        if k.key() == Qt.Key_Right:
            self.next()
        if k.key() == Qt.Key_A:
            self.prev_dir()
        if k.key() == Qt.Key_S:
            self.next_dir()
        if k.key() == Qt.Key_E:
            self.saveas()
        if k.key() == Qt.Key_M:
            self.movefile()
        if k.key() == Qt.Key_D:
            path = self.path
            os.unlink(path)
            if self.files.index(path) == len(self.files)-1:
                self.prev()
            else:
                self.next()
            self.files.remove(path)
            if not self.files:
                sys.exit(0)

        if k.key() == Qt.Key_C:
            currentQRect = self.currentQRubberBand.geometry()
            cropQPixmap = self.pixmap().copy(currentQRect)
            cropQPixmap.save(self.path)
            self.setPixmap(QPixmap(self.path))

            

    def mousePressEvent (self, eventQMouseEvent):
        self.originQPoint = eventQMouseEvent.pos()
        self.currentQRubberBand.setGeometry(QRect(self.originQPoint, QtCore.QSize()))
        self.currentQRubberBand.show()

    def mouseMoveEvent (self, eventQMouseEvent):
        self.currentQRubberBand.setGeometry(QRect(self.originQPoint, eventQMouseEvent.pos()).normalized())

    def mouseReleaseEvent (self, eventQMouseEvent):
        return
        self.currentQRubberBand.hide()
        currentQRect = self.currentQRubberBand.geometry()
        self.currentQRubberBand.deleteLater()
        cropQPixmap = self.pixmap().copy(currentQRect)
        cropQPixmap.save('output.png')

if __name__ == '__main__':
    myQApplication = QApplication([])#sys.argv)
    myQExampleLabel = QExampleLabel()
    myQExampleLabel.show()
    sys.exit(myQApplication.exec_())
