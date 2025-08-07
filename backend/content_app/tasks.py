import subprocess
import os
import glob

resolutions = [480, 720, 1080]

def convert_resolutions_to_hls(source):
    """
        Convert videos into hls files
    """
    base, _ = os.path.splitext(source)

    for res in resolutions:
        output_dir = f'{base}_{res}p'
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, 'index.m3u8')

        cmd = [
            'ffmpeg',
            '-i', source,
            '-vf', f'scale=-2:{res}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', '6',                 
            '-hls_playlist_type', 'vod',        
            '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
            output_path
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")

    
def delete_hls_files(video_path):
    """
        Delete files
    """
    base, _ = os.path.splitext(video_path)

    for res in resolutions:
        dir = f'{base}_{res}p'
        m3u8_path = os.path.join(dir, 'index.m3u8')
        ts_pattern = os.path.join(dir, 'segment_*.ts')

        if os.path.exists(m3u8_path):
            os.remove(m3u8_path)

        ts_files = glob.glob(ts_pattern)
        for ts in ts_files:
            os.remove(ts)

        if os.path.exists(dir) and not os.listdir(dir):
            os.rmdir(dir)