"""Ricolora in palette lime il video hero della home (mp4 + webm + poster webp)
per il verticale inglese. Uso: python3 scripts/recolor_hero.py
Richiede imageio-ffmpeg (solo per questo script, non per il server)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import imageio_ffmpeg
from PIL import Image

sys.path.insert(0, '/app/backend')
import recolor  # noqa: E402

MEDIA = Path('/app/frontend/public/media')
SRC = MEDIA / 'hero-loop-parete-addominale'
DST = MEDIA / 'hero-loop-parete-addominale-en'
FF = imageio_ffmpeg.get_ffmpeg_exe()
GAIN = 1.45  # video piu' luminoso: dietro le scritte deve leggersi bene


def recolor_video(src, dst, w, h, enc_args):
    reader = subprocess.Popen([FF, '-v', 'error', '-i', str(src), '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                               '-s', f'{w}x{h}', '-'], stdout=subprocess.PIPE)
    writer = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}',
                               '-r', '24', '-i', '-', '-an', *enc_args, str(dst)], stdin=subprocess.PIPE)
    size = w * h * 3
    while True:
        buf = reader.stdout.read(size)
        if len(buf) < size:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        writer.stdin.write(recolor.recolor_array(frame, GAIN).tobytes())
    writer.stdin.close()
    writer.wait()
    reader.wait()


if __name__ == '__main__':
    poster = recolor.recolor_array(np.asarray(Image.open(f'{SRC}.webp').convert('RGB')), GAIN)
    Image.fromarray(poster, 'RGB').save(f'{DST}.webp', 'WEBP', quality=82, method=6)
    recolor_video(f'{SRC}.mp4', f'{DST}.mp4', 960, 540,
                  ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '26', '-preset', 'slow', '-movflags', '+faststart'])
    recolor_video(f'{SRC}.webm', f'{DST}.webm', 1280, 720,
                  ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuv420p', '-b:v', '0', '-crf', '40', '-row-mt', '1'])
    # versione leggera per telefono: ritaglio verticale centrato sul busto (360x600)
    mob = f'{DST}-mobile'
    subprocess.run([FF, '-v', 'error', '-y', '-i', f'{DST}.webm', '-vf', 'crop=432:720:424:0,scale=360:600', '-an',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '30', '-preset', 'slow',
                    '-movflags', '+faststart', '-r', '24', f'{mob}.mp4'], check=True)
    subprocess.run([FF, '-v', 'error', '-y', '-i', f'{mob}.mp4', '-an', '-c:v', 'libvpx-vp9', '-b:v', '0',
                    '-crf', '42', '-row-mt', '1', f'{mob}.webm'], check=True)
    print('ok')
