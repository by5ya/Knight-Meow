import io
import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, \
    QProgressBar, QDialog
from PyQt6.QtGui import QPainter, QBrush, QColor, QPixmap, QFont, QPen
from PyQt6.QtCore import QUrl, QRect, Qt, QTimer, pyqtSignal, QRectF, QPoint
import random
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from templates import templateMainWin, templateRegWin


class GameObject:
    def __init__(self, x, y, width, height, color, image, damage):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.image = image
        self.damage = damage

    def draw(self, painter):
        painter.setBrush(QBrush(QColor(*self.color)))
        painter.drawRect(QRect(self.x, self.y, self.width, self.height))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def drawImage(self, painter):
        painter.drawPixmap(self.x, self.y, self.image)


class Coin(GameObject):
    def __init__(self, x, y, width=20, height=20, color=(255, 255, 0), image=None, damage=0):
        super().__init__(x, y, width, height, color, image, damage)

    def draw(self, painter):
        if self.image:
            self.drawImage(painter)
        else:
            super().draw(painter)


class Obstacle(GameObject):
    def __init__(self, x, y, width, height, color, image, damage):
        super().__init__(x, y, width, height, color, image, damage)


class Player(GameObject):
    def __init__(self, x, y, width, height, color, image, damage):
        super().__init__(x, y, width, height, color, image, damage)
        self.is_crouching = False
        self.is_jumping = False
        self.jump_velocity = 15
        self.speed = 1
        self.groundY = 250
        self.jumpSnd = "jump.mp3"
        self.damageSnd = "damage.mp3"
        self.IFramed = False
        self.iFrameTimer = QTimer()
        self.iFrameTimer.timeout.connect(self.endIFrame)
        self.MaxHealth = 100
        self.Health = self.MaxHealth
        self.normalImage = QPixmap("static/images/plrNew.png")

        self.crouchImage = QPixmap("static/images/crouch.png")
        self.image = image

        self.AudioPlayer = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.AudioPlayer.setAudioOutput(self.audio_output)
        self.AudioPlayer.setProperty("analyzeduration", 100000)
        self.AudioPlayer.setProperty("probesize", 10000000)

        self.crouchOffset = 20

    def jump(self):
        if not self.is_jumping and not self.is_crouching:
            self.is_jumping = True
            self.AudioPlayer.setSource(QUrl.fromLocalFile(self.jumpSnd))
            self.AudioPlayer.play()

    def crouch(self):
        if not self.is_jumping and not self.is_crouching:
            self.is_crouching = True
            self.image = self.crouchImage
            self.height = 10

    def uncrouch(self):
        if self.is_crouching:
            self.is_crouching = False
            self.image = self.normalImage
            self.height = 30

    def update(self):
        if self.is_jumping and not self.is_crouching:
            self.y -= self.jump_velocity
            self.jump_velocity -= 1
            if self.y >= self.groundY:
                self.y = self.groundY
                self.is_jumping = False
                self.jump_velocity = 15

    def drawPlr(self, painter):
        if self.is_crouching:
            painter.drawPixmap(self.x, self.y + self.crouchOffset, self.image)
        else:
            painter.drawPixmap(self.x, self.y, self.image)

    def startIFrame(self):
        self.IFramed = True
        self.iFrameTimer.start(1000)

    def endIFrame(self):
        self.IFramed = False
        self.iFrameTimer.stop()


class RunnerGame(QWidget):
    gameOverSignal = pyqtSignal()

    def __init__(self, username):
        super().__init__()
        self.db_cursor = None
        self.db_conn = None
        self.update()
        self.show()
        self.setWindowTitle("Рыцарь Мяу")
        self.setGeometry(500, 200, 600, 400)
        self.setFixedSize(600, 400)
        self.sky_x = 0
        self.paused = False
        self.current_username = username
        self.coins_num = 0

        self.player = Player(50, 250, 20, 30, (0, 255, 0), QPixmap("static/images/plrNew.png"), 0)
        self.obstacles = []
        self.coins = []
        self.obstacleSpeed = 5
        self.game_over = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(1000 // 60)

        self.spawnObstacleTimer = QTimer()
        self.spawnObstacleTimer.timeout.connect(self.spawnObstacle)
        self.spawnObstacleTimer.start(1500)

        self.spawnCoinTimer = QTimer()
        self.spawnCoinTimer.timeout.connect(self.spawnCoin)
        self.spawnCoinTimer.start(2000)

        self.groundWidth = 600
        self.groundHeight = 300
        self.groundX = 0

        self.score = 0
        self.previous_score = 0

        self.music_player = QMediaPlayer()
        self.music_url = QUrl.fromLocalFile("back_music.mp3")  # Replace with your music file path
        self.music_player.setSource(self.music_url)
        # Set source directly using QUrl
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)
        self.music_player.setAudioOutput(self.audio_output)

        self.music_player.play()

        self.health_bar = QProgressBar(self)
        self.health_bar.setGeometry(10, 50, 100, 20)
        self.health_bar.setMaximum(self.player.Health)
        self.health_bar.setValue(self.player.Health)

        self.game_over_screen = QWidget(self)
        self.game_over_screen.setGeometry(self.rect())
        self.game_over_screen.hide()

        self.background_label = QLabel(self.game_over_screen)
        self.background_label.setGeometry(0, 0, self.game_over_screen.width(), self.game_over_screen.height())
        pixmap = QPixmap("static/images/castle.png")
        self.background_label.setPixmap(pixmap)
        self.game_over_text = QLabel("Конец игры", self.game_over_screen)
        self.game_over_text.setFont(QFont('Fixedsys', 24))
        self.game_over_text.setStyleSheet("color: white;")
        self.game_over_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_over_text.setGeometry(self.game_over_screen.width() // 2 - 100,
                                        self.game_over_screen.height() // 3 - 50,
                                        200, 50)

        # Best Score Text
        self.best_score_text = QLabel(self.game_over_screen)
        self.best_score_text.setFont(QFont('Fixedsys', 22))
        self.best_score_text.setStyleSheet("color: white;")
        self.best_score_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_score_text.setGeometry(self.game_over_screen.width() // 2 - 100,
                                         self.game_over_screen.height() // 2 - 50,
                                         200, 30)

        self.coins_text = QLabel(self.game_over_screen)
        self.coins_text.setFont(QFont('Fixedsys', 22))
        self.coins_text.setStyleSheet("color: white;")
        self.coins_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coins_text.setGeometry(self.game_over_screen.width() // 2 - 150,
                                           self.game_over_screen.height() // 2 + 20,
                                         300, 30)

        # Play Again Button
        self.play_again_button = QPushButton("Играть еще", self.game_over_screen)
        self.play_again_button.setFont(QFont('Fixedsys', 20))
        self.play_again_button.setStyleSheet("background-color: #ffa500; color: white;")
        self.play_again_button.setGeometry(self.game_over_screen.width() // 2 - 100,
                                           self.game_over_screen.height() // 2 + 70,
                                           200, 50)
        self.play_again_button.clicked.connect(self.restart_game)

        self.db_conn = sqlite3.connect('game_data.db')
        self.db_cursor = self.db_conn.cursor()

        self.gameOverSignal.connect(self.show_game_over_screen)

        self.player_rect = QRect(self.player.x, self.player.y, self.player.image.width(), self.player.image.height())

        self.obstacleImage1 = QPixmap("static/images/spikeObstacle.png")
        self.obstacleImage2 = QPixmap("static/images/chainsaw.png")

        self.skyIMG = QPixmap("static/images/sky.png")
        self.groundIMG = QPixmap("static/images/grassNew.png")
        self.coinImage = QPixmap("static/images/coin.png")

    def pauseGame(self):
        if self.game_over:
            return

        if self.timer.isActive():
            self.timer.stop()
            self.spawnObstacleTimer.stop()
            self.spawnCoinTimer.stop()
            self.paused = True
            self.update()  # Перерисовать экран с затемнением
            self.showPauseMenu()  # Отобразить кнопку "Продолжить"
        else:
            self.timer.start(1000 // 60)  # Возобновить таймер
            self.spawnObstacleTimer.start(1500)
            self.paused = False
            self.hidePauseMenu()  # Скрыть кнопку "Продолжить"
            self.update()

    def showPauseMenu(self):
        # Создаем кнопку "Продолжить"
        self.continueButton = QPushButton("Продолжить", self)
        self.continueButton.setGeometry(self.width() // 2 - 50, self.height() // 2 - 20, 100, 40)
        self.continueButton.clicked.connect(self.pauseGame)
        self.continueButton.show()

    def hidePauseMenu(self):
        if hasattr(self, 'continueButton'):  # Проверяем, существует ли кнопка
            self.continueButton.clicked.disconnect(self.pauseGame)  # Отключаем обработчик
            self.continueButton.hide()
            del self.continueButton
            self.update()

    def drawHealthBar(self, painter):
        bar_width = 100
        bar_height = 20
        border_radius = 5

        # Позиция полоски здоровья
        x = 10
        y = 50

        # Отрисовка фона полоски здоровья
        painter.setBrush(QBrush(QColor(150, 150, 150)))  # Серый фон
        painter.drawRoundedRect(x, y, bar_width, bar_height, border_radius, border_radius)

        # Расчет ширины заполненной части полоски здоровья
        health_ratio = self.player.Health / self.player.MaxHealth  # Предполагается, что в игроке есть MaxHealth
        fill_width = bar_width * health_ratio

        # Отрисовка заполненной части полоски здоровья
        painter.setBrush(QBrush(QColor(255, 0, 0)))  # Красный цвет для заполненной части
        painter.drawRoundedRect(x, y, int(fill_width), int(bar_height), int(border_radius), int(border_radius))

        # Отрисовка надписи "Здоровье"
        font = QFont("Fixedsys", 20)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255)))  # Черный цвет для текста

        # Используйте boundingRect() для получения ширины текста
        text_rect = painter.boundingRect(QRectF(x, y, bar_width, bar_height), "Здоровье")
        text_width = text_rect.width()

        painter.drawText(int(x + (bar_width - text_width) // 2), int(y - 10), "Здоровье")

        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255)))  # Белый цвет для текста

        # Вычисление позиции для текста
        text_rect = painter.boundingRect(QRectF(x, y, bar_width, bar_height), f"Счет: {self.score}")
        text_width = text_rect.width()
        text_x = self.width() - text_width - 10  # Выравниваем по правому краю
        text_y = y - 5
        painter.drawText(int(text_x), int(text_y), f"Счет: {self.score}")

    def collision_occurred(self):
        self.player.Health -= 10
        if self.player.Health <= 0:
            self.game_over = True
            self.gameOverSignal.emit()

    def paintEvent(self, event):
        if not self.game_over:
            painter = QPainter(self)
            self.update()

            # Draw the sky image
            painter.drawPixmap(self.sky_x, 0, self.skyIMG)
            painter.drawPixmap(self.sky_x + self.skyIMG.width(), 0,
                               self.skyIMG)
            painter.drawPixmap(self.sky_x + 2 * self.skyIMG.width(), 0, self.skyIMG)

            # Draw the ground image
            painter.drawPixmap(0, -40, self.groundIMG)

            self.player.drawPlr(painter)

            for obstacle in self.obstacles:
                obstacle.drawImage(painter)

            for coin in self.coins:
                coin.draw(painter)
            self.drawHealthBar(painter)

            if self.paused:
                painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

    def updater(self):
        if self.game_over != True:
            self.player.update()
            self.sky_x -= self.obstacleSpeed
            if self.sky_x <= -self.skyIMG.width():
                self.sky_x = 0

            # Обновляем прямоугольник игрока
            if self.player.is_crouching:
                player_height = self.player.crouchImage.height()
            else:
                player_height = self.player.image.height()

            self.player_rect.setRect(self.player.x, self.player.y, self.player.image.width(), player_height)

            for obstacle in self.obstacles:
                obstacle.move(-self.obstacleSpeed, 0)

            self.obstacles = [obstacle for obstacle in self.obstacles if obstacle.x + obstacle.width > 0]

            for coin in self.coins:
                coin.move(-self.obstacleSpeed, 0)
                if coin.x + coin.width < 0:
                    self.coins.remove(coin)

            self.check_collisions()

            if self.player.x < 0:
                self.player.x = 0
            if self.player.x > 600:
                self.player.x = 600

            self.score += 1

            if self.score != self.previous_score:
                self.previous_score = self.score

            self.update()

    def check_collisions(self):
        if self.player.is_crouching:
            player_y = self.player.y + self.player.crouchOffset  # Добавляем смещение для приседания
        else:
            player_y = self.player.y  # Обычная Y-координата

        self.player_rect.setRect(self.player.x, player_y, self.player.image.width(), self.player.image.height())

        for obstacle in self.obstacles:
            obstacle_rect = QRect(obstacle.x, obstacle.y, obstacle.image.width(), obstacle.image.height())

            # Проверка столкновения с учетом высоты игрока
            if self.player_rect.intersects(obstacle_rect) and self.game_over != True and self.player.IFramed == False:
                self.player.AudioPlayer.setSource(QUrl.fromLocalFile(self.player.damageSnd))
                self.player.AudioPlayer.play()
                self.collision_occurred()  # Обработка столкновения и изменения здоровья

                self.player.startIFrame()  # Начать индикатор неуязвимости

                # Вызов обновления здесь не требуется, это будет сделано в updater()
                break
        for coin in self.coins:
            coin_rect = QRect(coin.x, coin.y, coin.image.width(), coin.image.height())
            if self.player_rect.intersects(coin_rect):
                self.coins.remove(coin)
                self.score += 200
                self.coins_num += 1

    def keyPressEvent(self, event):
        if not self.game_over:
            if event.key() == Qt.Key.Key_W:
                self.player.jump()
            elif event.key() == Qt.Key.Key_S:
                self.player.crouch()
            elif event.key() == Qt.Key.Key_Escape:
                self.pauseGame()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_S:
            self.player.uncrouch()

    def spawnCoin(self):
        if random.random() < 0.5:
            y = random.randint(200, 300)
            self.coins.append(Coin(self.width() + 50, y, image=self.coinImage))

    def spawnObstacle(self):

        if self.score >= 1000:
            obstacleImage = random.choice([self.obstacleImage1, self.obstacleImage2])
        else:
            obstacleImage = self.obstacleImage1

        if obstacleImage == self.obstacleImage1:
            damage = 5
        else:
            damage = 10

        obstaclex = self.width()
        obstacley = 335 - self.obstacleImage1.height()
        if obstacleImage == self.obstacleImage2:
            obstacley = 260 - self.obstacleImage1.height()
        obstaclewidth = self.obstacleImage1.width()
        obstacleheight = self.obstacleImage1.height()

        spawnRate = 6000 - (self.score * 50)
        if spawnRate < 1000:
            spawnRate = 1000

        newObstacle = Obstacle(obstaclex, obstacley, obstaclewidth, obstacleheight,
                               (255, 255, 255), obstacleImage, damage)
        self.obstacles.append(newObstacle)

        self.spawnObstacleTimer.stop()
        self.spawnObstacleTimer.start(spawnRate)
        self.obstacleSpeed = random.randint(3, 10)

    def show_game_over_screen(self):
        self.music_player.stop()

        self.game_over_screen.show()

        self.db_cursor.execute("UPDATE users_data SET coins = coins + ? WHERE username = ?", (self.coins_num, self.current_username))
        self.db_cursor.execute("SELECT coins FROM users_data WHERE username = ?", (self.current_username,))
        coins = self.db_cursor.fetchone()
        if coins:
            coins = int(coins[0])
        else:
            coins = 0

        self.db_cursor.execute("SELECT score FROM users_data WHERE username = ?", (self.current_username,))
        best_score_row = self.db_cursor.fetchone()

        if best_score_row:
            best_score = int(best_score_row[0])
        else:
            best_score = 0

        if self.score > best_score:
            self.db_cursor.execute("UPDATE users_data SET score = ? WHERE username = ?",
                                   (self.score, self.current_username))
            self.db_conn.commit()

        self.best_score_text.setText(f'Лучший счет: {max(self.score, best_score)}')
        self.coins_text.setText(f'Общее количество монет: {coins}')

    def restart_game(self):
        if self.game_over == True:
            self.player.x = 50
            self.player.y = 250
            self.player.is_jumping = False
            self.player.jump_velocity = 15
            self.obstacles = []
            self.game_over = False
            self.groundX = 0
            self.score = 0
            self.player.Health = 100

            self.music_player.setSource(self.music_url)
            self.music_player.play()

            self.game_over_screen.hide()

            self.setFocus()


class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        f = io.StringIO(templateMainWin)
        uic.loadUi(f, self)

        pixmap1 = QPixmap("static/images/castle.png")
        self.back.setPixmap(pixmap1)
        global main_win
        main_win = self

        pixmap = QPixmap('static/images/New Piskel.png')
        self.setWindowTitle("Рыцарь Мяу - Авторизация")

        self.label_image.setPixmap(pixmap)
        self.entryBtn.clicked.connect(self.check)
        self.registrationBtn.clicked.connect(self.registrate)
        self.registrationWin = RegistrationWin(main_win)

        self.db_conn = sqlite3.connect('game_data.db')  # Create/open DB
        self.db_cursor = self.db_conn.cursor()

    def check(self):
        log = self.loginline.text()
        passw = self.passwordline.text()

        if not log or not passw:
            QMessageBox.warning(self, "Ошибка входа", "Пожалуйста, введите имя пользователя и пароль.")
            return

        try:
            # Check if user exists in the database
            self.db_cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (log, passw))
            user = self.db_cursor.fetchone()

            if user:

                self.show_game_info_dialog(user[1])
                self.hide()
            else:
                # Invalid login
                QMessageBox.warning(self, "Ошибка входа", "Неверные имя пользователя или пароль.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def show_game_info_dialog(self, username):
        """
        Displays a dialog box with game controls and lore.
        """
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Добро пожаловать!")
        self.dialog.setFixedSize(450, 450)
        btn = QPushButton("Играть", self.dialog)
        self.background_image = QPixmap("static/images/bg_dialog.png")  # Замените на путь к вашему изображению

        # Создаем QLabel для отображения фона
        self.background_label = QLabel(self.dialog)
        self.background_label.setPixmap(self.background_image)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        btn.clicked.connect(lambda: self.open_new_window(username))

        # Add a label for game controls
        controls_label = QLabel("Управление:")
        controls_label.setFont(QFont("Arial", 12))

        # Add a label for game lore
        lore_label = QLabel("Предыстория:")
        lore_label.setFont(QFont("Arial", 12))

        controls_text = QLabel("W - Прыжок\nS - Клубочек\nEsc - пауза")
        lore_text = QLabel("В сказочном королевстве Котония, где пушистые коти"
                           "ки правят бал, жил отважный рыцарь по имени Мяу. Его меч "
                           "был острее иглы, а сердце — храбрее льва. "
                           "Но однажды коварный злодей, повелитель крыс, украл королевский запас любимых к"
                           "ошачьих лакомств! Теперь Мяу должен "
                           "отправиться в опасное путешествие по волшебным землям, "
                           "чтобы вернуть пропажу и спасти Котонию от голода."
                           "Готов ли ты стать рыцарем Мяу и отправиться в захватывающее приключение?")
        lore_text.setWordWrap(True)

        # Create a layout to arrange elements in the dialog box
        layout = QVBoxLayout(self.dialog)
        layout.addWidget(controls_label)
        layout.addWidget(controls_text)
        layout.addWidget(lore_label)
        layout.addWidget(lore_text)
        layout.addWidget(btn)

        # Show the dialog box
        self.dialog.exec()

    def registrate(self):
        self.registrationWin.show()
        self.hide()

    def open_new_window(self, username):
        self.hide()
        self.dialog.hide()
        self.new_window = RunnerGame(username)
        self.new_window.show()


class RegistrationWin(QWidget):
    def __init__(self, main_win):
        super().__init__()
        f = io.StringIO(templateRegWin)
        uic.loadUi(f, self)
        pixmap1 = QPixmap('static/images/castle.png')
        self.backg.setPixmap(pixmap1)
        pixmap = QPixmap('static/images/New Piskel.png')
        self.setWindowTitle("Рыцарь Мяу - Регистрация")
        self.label_image.setPixmap(pixmap)
        self.backBtn.clicked.connect(self.back)
        self.reg_btn.clicked.connect(self.registrate)
        self.mainWin = main_win

        self.db_conn = sqlite3.connect('game_data.db')  # Create/open DB
        self.db_cursor = self.db_conn.cursor()
        self.db_conn.commit()

    def registrate(self):
        login = self.login_line.text()
        password = self.password_line.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка регистрации", "Пожалуйста, введите имя пользователя и пароль.")
            return

        try:
            # Insert new user into the database
            self.db_cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (login, password))
            self.db_cursor.execute("INSERT INTO users_data (username) VALUES (?)", (login,))
            self.db_conn.commit()

            # Display success message and close registration window
            QMessageBox.information(self, "Успешная регистрация", "Регистрация прошла успешно!")
            self.hide()
            self.mainWin.show()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка регистрации", "Имя пользователя уже существует.")

    def back(self):
        self.hide()
        self.mainWin.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MainWin()
    game.show()
    sys.exit(app.exec())
