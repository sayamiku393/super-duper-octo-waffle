from PyQt6.QtGui import QPixmap
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel
import sys
from import_script import engine, text


class ProductWindow(QWidget):
    def __init__(self, row):
        super().__init__()
        uic.loadUi('UI\product.ui', self)
        if row[7] > 0:
            old_price = row[3]
            new_price = row[3]*(100 - row[7])/100
            self.price.setText(f"<s>{old_price}</s>")
            self.disc_price.setText(f"<font color='red'>{new_price}</font>")
        else:
            self.price.setText(str(row[3]))

        if row[7] <= 15:
            text_html = f"""<span style="background-color:green">{row[7]}%</span>"""
            self.discount.setText(text_html)
        else:
            self.discount.setText(str(row[7])+'%')

        if row[8] == 0:
            text_html = f"""<span style="background-color:blue">{row[8]}</span>"""
            self.amt.setText(text_html)
        else:
            self.amt.setText(str(row[8]))

        self.model.setText(row[1])
        self.measure.setText(row[2])
        # self.price.setText(str(row[3]))
        self.supplier.setText(row[4])
        self.manufactr.setText(row[5])
        self.category.setText(row[6])
        # self.discount.setText(str(row[7])+'%')
        # self.amt.setText(str(row[8]))
        self.descr.setText(row[9])
        self.image.setPixmap(QPixmap(row[10]).scaled(200, 300))

class MainWindow(QMainWindow):
    def __init__(self, user, role):
        super().__init__()
        uic.loadUi('UI\main.ui', self)
        self.username.setText(user)
        self.exit_btn.clicked.connect(self.back)
        if role == 'Авторизированный клиент':
            self.sort_by_manuf_btn.hide()
            # self.sort_btn.hide()
            self.add_btn.hide()
        self.sort_btn.clicked.connect(self.search_reload)

    def back(self):
        self.close()
        self.window = LoginWindow()
        self.window.show()

    def search_reload(self):
        content = self.search_area.toPlainText().strip()
        with engine.begin() as conn:
            if len(content) > 0:
                where_stmt = f"art ilike '{content}' or descr ilike '{content}' or supplier ilike '{content}' or manufactr ilike '{content}' or model ilike '{content}'"
                result = conn.execute(text(f"select * from itemz where {where_stmt}")).fetchall()
            else:
                result = conn.execute(text(f"select * from itemz")).fetchall()

        while self.scroll_layout.count():
            self.scroll_layout.takeAt(0).widget().deleteLater()

        for row in result:
            product = ProductWindow(row)
            self.scroll_layout.addWidget(product)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI\login.ui', self)
        self.err.hide()
        self.enter_btn.clicked.connect(self.login_)
        self.guest_btn.clicked.connect(self.login_guest)

    def login_(self):
        login = self.login_edit.text()
        password = self.password_edit.text()
        with engine.begin() as conn:
            result = conn.execute(text(f"select fio, role from userz where login = '{login}' and password = '{password}'")).fetchone()
        if result is not None:
            self.close()
            self.window = MainWindow(result[0], result[1])
            self.window.show()
        else:
            self.err.show()


    def login_guest(self):
        self.close()
        self.window = MainWindow('guest', 'Авторизированный клиент')
        self.window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())