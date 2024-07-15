import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Загрузка предварительно обученного классификатора лиц из OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Функция для распознавания лиц
def detect_faces(frame):
    # Преобразование изображения в оттенки серого
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Распознавание лиц на изображении
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
    return faces

class FaceRecognitionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#2e3f4f")

        # Создание элемента для отображения видеопотока
        self.display_frame = tk.Frame(window, bg="#2e3f4f")
        self.display_frame.pack(side=tk.TOP, pady=10)  # Размещаем элемент сверху с отступом

        # Создание холста для отображения изображений и видео
        self.canvas = tk.Canvas(self.display_frame, width=640, height=480, bg="#cfcfcf")
        self.canvas.pack()  # Размещаем холст

        # Панель кнопок
        self.button_frame = tk.Frame(window, bg="#2e3f4f")
        self.button_frame.pack(side=tk.BOTTOM, pady=10)  # Размещаем панель кнопок снизу с отступом

        # Кнопки для выбора режима
        self.btn_load_image = tk.Button(self.button_frame, text="Загрузите фото", command=self.load_image, bg="#4a90e2",
                                        fg="white", font=("Helvetica", 12, "bold"))
        self.btn_load_image.grid(row=0, column=0, padx=5, pady=5)  # Размещаем кнопку загрузки фото

        self.btn_load_video = tk.Button(self.button_frame, text="Загрузите видео", command=self.load_video,
                                        bg="#4a90e2", fg="white", font=("Helvetica", 12, "bold"))
        self.btn_load_video.grid(row=0, column=1, padx=5, pady=5)  # Размещаем кнопку загрузки видео

        self.btn_camera = tk.Button(self.button_frame, text="Включить камеру", command=self.open_camera, bg="#4a90e2",
                                    fg="white", font=("Helvetica", 12, "bold"))
        self.btn_camera.grid(row=0, column=2, padx=5, pady=5)  # Размещаем кнопку включения камеры

        # Кнопка отмены
        self.btn_cancel = tk.Button(self.button_frame, text="Отмена", command=self.cancel_selection, bg="#e94e77",
                                    fg="white", font=("Helvetica", 12, "bold"))
        self.btn_cancel.grid(row=0, column=3, padx=5, pady=5)  # Размещаем кнопку отмены
        self.btn_cancel.grid_remove()  # Скрываем кнопку по умолчанию

        self.vid = None  # Инициализация переменной для видеозахвата
        self.window.mainloop()  # Запуск основного цикла окна

    def load_image(self):
        # Открытие диалогового окна для выбора изображения
        file_path = filedialog.askopenfilename()
        if not file_path:  # Если файл не выбран, выход из функции
            return

        # Загрузка изображения с использованием OpenCV
        image = cv2.imread(file_path)
        if image is None:  # Если изображение не удалось загрузить, показать сообщение об ошибке
            messagebox.showerror("Ошибка", "Невозможно открыть изображение")
            return

        # Распознавание лиц на изображении
        faces = detect_faces(image)
        for (x, y, w, h) in faces:
            # Рисование прямоугольников вокруг распознанных лиц
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Отображение изображения на холсте
        self.display_image(image)
        self.show_cancel_button()  # Показать кнопку отмены

    def load_video(self):
        # Открытие диалогового окна для выбора видео
        file_path = filedialog.askopenfilename()
        if not file_path:  # Если файл не выбран, выход из функции
            return

        # Захват видео с использованием OpenCV
        self.vid = cv2.VideoCapture(file_path)
        self.show_cancel_button()  # Показать кнопку отмены
        self.update_video()  # Начать обновление видео

    def open_camera(self):
        # Открытие камеры
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():  # Если не удалось открыть камеру, показать сообщение об ошибке
            messagebox.showerror("Ошибка", "Невозможно открыть камеру")
            return

        self.show_cancel_button()  # Показать кнопку отмены
        self.update_video()  # Начать обновление видео

    def update_video(self):
        if self.vid is None:  # Если видеозахват не инициализирован, выход из функции
            return

        # Захват следующего кадра из видео
        ret, frame = self.vid.read()
        if ret:  # Если кадр успешно захвачен
            faces = detect_faces(frame)  # Распознавание лиц на кадре
            for (x, y, w, h) in faces:
                # Рисование прямоугольников вокруг распознанных лиц
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Отображение кадра на холсте
            self.display_image(frame)
            self.window.after(15, self.update_video)  # Обновление кадра через 15 мс
        else:  # Если кадры больше не захватываются
            self.vid.release()  # Освобождение видеозахвата
            self.vid = None

    def display_image(self, frame):
        # Преобразование изображения из формата BGR в RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)  # Преобразование массива в изображение
        img = self.resize_image(img, 640, 480)  # Изменение размера изображения
        imgtk = ImageTk.PhotoImage(image=img)  # Преобразование изображения в формат Tkinter
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)  # Отображение изображения на холсте
        self.canvas.image = imgtk  # Сохранение ссылки на изображение

    def resize_image(self, image, max_width, max_height):
        # Вычисление пропорций для изменения размера
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        new_width = int(image.width * min(width_ratio, height_ratio))  # Новая ширина
        new_height = int(image.height * min(height_ratio, height_ratio))  # Новая высота
        return image.resize((new_width, new_height), Image.LANCZOS)  # Изменение размера изображения

    def show_cancel_button(self):
        self.btn_cancel.grid()  # Показ кнопки отмены

    def cancel_selection(self):
        if self.vid:  # Если видеозахват инициализирован
            self.vid.release()  # Освобождение видеозахвата
            self.vid = None
        self.canvas.delete("all")  # Очистка холста
        self.btn_cancel.grid_remove()  # Скрытие кнопки отмены


# Создание главного окна Tkinter
if __name__ == "__main__":
    FaceRecognitionApp(tk.Tk(), "Приложение для распознавания лиц")  # Запуск приложения
