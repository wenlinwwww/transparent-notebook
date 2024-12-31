import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QCheckBox, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QPoint
import fitz  # PyMuPDF
from docx import Document  # 导入 python-docx


class DraggableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.offset = QPoint()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)  # 允许鼠标事件

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
            self.parent().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.parent().move(self.parent().pos() + event.position().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False


class FloatingTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Floating Text Viewer')
        self.setGeometry(300, 300, 600, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # 设置窗口背景透明，但仍能接收事件
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(1.0)

        layout = QVBoxLayout()

        self.text_edit = DraggableTextEdit(self)
        self.text_edit.setReadOnly(False)
        # 默认文本框背景透明
        self.text_edit.setStyleSheet("background: rgba(255, 255, 255, 0); color: black; font-size: 16px; border: none;")
        layout.addWidget(self.text_edit)

        self.open_button = QPushButton('导入文件')
        self.open_button.clicked.connect(self.open_file)
        layout.addWidget(self.open_button)

        self.transparent_checkbox = QCheckBox("背景透明")
        self.transparent_checkbox.stateChanged.connect(self.toggle_transparency)
        self.transparent_checkbox.setChecked(True)
        layout.addWidget(self.transparent_checkbox)

        self.close_button = QPushButton('关闭窗口')
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.container = QWidget()
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)
        self.toggle_widget_visibility(False)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "Text Files (*.txt);;PDF Files (*.pdf);;Word Files (*.docx *.doc);;All Files (*.*)",
            "All Files (*.*)"  # 设置默认过滤器为“所有文件”
        )
        if file_name:
            if file_name.endswith('.txt'):
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.text_edit.setText(f.read())
            elif file_name.endswith('.pdf'):
                text = self.extract_pdf_text(file_name)
                self.text_edit.setText(text)
            elif file_name.endswith('.docx') or file_name.endswith('.doc'):
                text = self.extract_doc_text(file_name)
                self.text_edit.setText(text)

    # 提取PDF文本
    def extract_pdf_text(self, file_path):
        pdf = fitz.open(file_path)
        text = ''
        for page in pdf:
            text += page.get_text()
        return text

    # 提取Word文本
    def extract_doc_text(self, file_path):
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

    # 滚轮事件，防止透明背景下滚轮失效
    def wheelEvent(self, event):
        QApplication.sendEvent(self.text_edit, event)

    def toggle_transparency(self, state):
        if state == Qt.CheckState.Checked.value:
            # 仅文本框背景透明，窗口保持接收事件
            self.text_edit.setStyleSheet("background: rgba(255, 255, 255, 0); color: black;")
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)  # 禁止穿透鼠标事件
        else:
            # 文本框恢复不透明背景
            self.text_edit.setStyleSheet("background: rgba(128, 128, 128, 200); color: black;")
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)  # 确保鼠标事件仍能生效

    def enterEvent(self, event):
        self.toggle_widget_visibility(True)

    def leaveEvent(self, event):
        self.toggle_widget_visibility(False)

    def toggle_widget_visibility(self, visible):
        self.open_button.setVisible(visible)
        self.transparent_checkbox.setVisible(visible)
        self.close_button.setVisible(visible)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FloatingTextApp()
    window.show()
    sys.exit(app.exec())