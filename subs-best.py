import os
import whisper
import ffmpeg

def split_text_into_lines(text, max_words_per_line=7):
    """
    Разбивает текст на строки с ограничением по количеству слов.
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if len(current_line) >= max_words_per_line:
            lines.append(" ".join(current_line))
            current_line = []
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines

def generate_subtitles(video_path, output_srt_path, max_words_per_line=7):
    """
    Генерирует субтитры для видео и сохраняет их в формате .srt.
    Каждая строка субтитров содержит не более max_words_per_line слов.
    """
    model = whisper.load_model("base")  # Используем модель "base" для баланса скорости и точности
    print(f"Обрабатываю видео: {video_path}...")
    result = model.transcribe(video_path, language="ru")
    
    # Если текст не распознан, возвращаем False
    if not result["segments"]:
        print(f"Текст не распознан в видео: {video_path}")
        return False
    
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"]):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]
            
            # Разбиваем текст на строки
            lines = split_text_into_lines(text, max_words_per_line=max_words_per_line)
            
            # Если текст разбит на несколько строк, создаем отдельные субтитры для каждой строки
            for j, line in enumerate(lines):
                line_start = start_time + (end_time - start_time) * (j / len(lines))
                line_end = start_time + (end_time - start_time) * ((j + 1) / len(lines))
                
                srt_file.write(f"{i+1}.{j+1}\n")
                srt_file.write(f"{format_time(line_start)} --> {format_time(line_end)}\n")
                srt_file.write(f"{line}\n\n")
    
    print(f"Субтитры сохранены: {output_srt_path}")
    return True

def format_time(seconds):
    """
    Форматирует время в формат SRT (часы:минуты:секунды,миллисекунды).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:06.3f}".replace(".", ",")

def add_subtitles_to_video(video_path, srt_path, output_video_path):
    """
    Накладывает субтитры на видео и сохраняет результат.
    """
    print(f"Накладываю субтитры на видео: {video_path}...")
    (
        ffmpeg.input(video_path)
        .output(output_video_path, vf=f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF&'")
        .run(overwrite_output=True)
    )
    print(f"Видео с субтитрами сохранено: {output_video_path}")

def process_all_videos_in_folder(folder_path="clips", max_words_per_line=3):
    """
    Обрабатывает все видео в указанной папке:
    1. Генерирует субтитры.
    2. Накладывает субтитры на видео.
    """
    # Проверяем, существует ли папка
    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не существует.")
        
        return
    
    # Проходим по всем файлам в папке
    for filename in os.listdir(folder_path):
        # Обрабатываем только видеофайлы
        if filename.endswith(".mp4"):
            video_path = os.path.join(folder_path, filename)
            srt_path = video_path.replace(".mp4", ".srt")
            output_video_path = video_path.replace(".mp4", "_subtitled.mp4")
            
            # Генерация субтитров
            if not generate_subtitles(video_path, srt_path, max_words_per_line=max_words_per_line):
                print(f"Пропускаю видео: {video_path} (текст не распознан).")
                continue
            
            # Наложение субтитров на видео
            add_subtitles_to_video(video_path, srt_path, output_video_path)

# Запуск процесса
process_all_videos_in_folder(max_words_per_line=7)  # Укажите нужное количество слов в строке