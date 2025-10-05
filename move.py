import os
import shutil

def move_subtitled_videos(source_folder="clips", destination_folder="subtitled_clips"):
    """
    Перемещает все видео с именами вида clip_{index}_subtitled.mp4 в отдельную папку.
    """
    # Проверяем, существует ли исходная папка
    if not os.path.exists(source_folder):
        print(f"Исходная папка {source_folder} не существует.")
        return
    
    # Создаем целевую папку, если она не существует
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"Создана папка: {destination_folder}")
    
    # Проходим по всем файлам в исходной папке
    for filename in os.listdir(source_folder):
        # Проверяем, соответствует ли имя файла шаблону clip_{index}_subtitled.mp4
        if filename.startswith("clip_") and filename.endswith("_subtitled.mp4"):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)
            
            # Перемещаем файл
            shutil.move(source_path, destination_path)
            print(f"Перемещен файл: {filename} -> {destination_folder}")

# Запуск процесса
move_subtitled_videos()