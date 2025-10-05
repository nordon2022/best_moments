from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
import ffmpeg
import os

def find_scenes(video_path, threshold=40.0):
    """
    Находит моменты смены сцен в видео.
    """
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    
    scenes = scene_manager.get_scene_list()
    return [(start.get_seconds(), end.get_seconds()) for start, end in scenes]

def split_long_scenes(scenes, min_duration=15, max_duration=30):
    """
    Делит слишком длинные сцены на части, объединяет короткие.
    """
    new_scenes = []
    buffer_start, buffer_end = None, None
    
    for start, end in scenes:
        duration = end - start
        
        if duration < min_duration:
            if buffer_start is None:
                buffer_start, buffer_end = start, end
            else:
                buffer_end = end
                if buffer_end - buffer_start >= min_duration:
                    new_scenes.append((buffer_start, buffer_end))
                    buffer_start, buffer_end = None, None
        else:
            if buffer_start is not None:
                new_scenes.append((buffer_start, buffer_end))
                buffer_start, buffer_end = None, None
            
            if duration > max_duration:
                num_splits = int(duration // max_duration)
                for i in range(num_splits):
                    new_scenes.append((start + i * max_duration, start + (i + 1) * max_duration))
                if duration % max_duration >= min_duration:
                    new_scenes.append((start + num_splits * max_duration, end))
            else:
                new_scenes.append((start, end))
    
    if buffer_start is not None:
        new_scenes.append((buffer_start, buffer_end))
    
    return new_scenes

def cut_scenes(video_path, scene_timestamps, output_dir="clips"):
    """
    Вырезает сцены и сохраняет их в директорию output_dir.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    clips = []
    for i, (start, end) in enumerate(scene_timestamps):
        output_file = os.path.join(output_dir, f"clip_{i+1}.mp4")
        (
            ffmpeg.input(video_path, ss=start, to=end)
            .output(output_file, format="mp4", vcodec="libx264", acodec="aac")
            .run(overwrite_output=True)
        )
        clips.append(output_file)
    return clips

# Основной процесс
video_file = "xiaomi.mp4"
scene_timestamps = find_scenes(video_file)
scene_timestamps = split_long_scenes(scene_timestamps)
print("Финальные сцены:", scene_timestamps)
clips = cut_scenes(video_file, scene_timestamps)
print("Вырезанные клипы сохранены в папке clips:", clips)