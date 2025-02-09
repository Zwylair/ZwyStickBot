import os
import logging
import tempfile
import subprocess
from io import BytesIO

import PIL
from PIL import Image
import imageio
import imageio_ffmpeg as ffmpeg

logger = logging.getLogger(__name__)


def is_image_supported(file: bytes) -> bool:
    try:
        image = Image.open(BytesIO(file))
        image.close()
        return True
    except PIL.UnidentifiedImageError:
        return False


def is_video_supported(file: bytes) -> bool:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temporary_file:
            temporary_file.write(file)
            temporary_file.seek(0)

        reader = imageio.get_reader(temporary_file.name)
        _ = reader.get_meta_data()
        reader.close()

        os.remove(temporary_file.name)
        return True
    except Exception as e:
        logger.error("Error on decoding video", exc_info=e)
        os.remove(temporary_file.name)
        return False


def resize_image(file: bytes) -> bytes:
    with PIL.Image.open(BytesIO(file)) as image:
        is_width_the_biggest = image.size[0] > image.size[1]

        if is_width_the_biggest:
            coefficient = image.size[0] / 512
            new_size = [512, round(image.size[1] / coefficient)]
        else:
            coefficient = image.size[1] / 512
            new_size = [round(image.size[0] / coefficient), 512]

        image = image.resize(new_size)
        new_file = BytesIO()
        image.save(new_file, format="png")
        new_file.seek(0)
    return new_file.read()


def resize_video(video_bytes: bytes) -> bytes | None:
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(video_bytes)
        temp_input.flush()
        temp_input_path = temp_input.name

        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            temp_input_path
        ]
        fps_output = subprocess.check_output(probe_cmd).decode("utf-8").strip()
        fps = eval(fps_output)

        if fps > 30:
            fps = 30

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_output:
            temp_output_path = temp_output.name

        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",  # Automatically overwrite a file if it already exists
            "-i", temp_input_path,
            "-vf", "scale='if(gt(iw,ih),512,trunc(iw/ih*512))':'if(gt(iw,ih),trunc(ih/iw*512),512)'",  # Scaling
            "-r", str(fps),  # Set FPS (30 or less)
            "-c:v", "libvpx-vp9",  # VP9 codec for WebM
            "-preset", "ultrafast",
            "-crf", "32",  # Lower value for size reduction (from 0 to 63, the higher - the worse quality)
            "-b:v", "500k",  # Set bitrate for video (500kbit/s)
            "-movflags", "+faststart",
            "-an",  # Mute
            "-t", "3",  # Limit the video to 3 seconds
            "-f", "webm",
            "-loglevel", "quiet",  # Disabling logging
            temp_output_path
        ]

    process = subprocess.Popen(ffmpeg_cmd)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        logger.error(f"FFmpeg error: {stderr.decode()}")
        return None

    with open(temp_output_path, "rb") as f:
        output_video = f.read()

    file_size = os.path.getsize(temp_output_path)
    logger.info(f"Output video size: {file_size / (1024 * 1024):.2f} MB")

    os.remove(temp_input_path)
    os.remove(temp_output_path)

    return output_video
