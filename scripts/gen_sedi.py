#!/usr/bin/env python3
"""Figura 'sedi tipiche dei difetti' — soggetto scritto dall'hub, ricetta invariata."""
import asyncio, base64, io, os, json
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from emergentintegrations.llm.chat import LlmChat, UserMessage
from gen_figures import STYLE

load_dotenv('/app/backend/.env')
MEDIA = Path('/app/backend/static/media')
SUBJECT = ("abstract front view of an abdominal wall silhouette with schematic weak points "
           "marked as thin luminous rings at the midline, above the navel and at the lower "
           "sides. Square 1:1 format.")

async def main():
    out = MEDIA / 'sedi-dei-difetti.webp'
    if out.exists():
        print('gia presente'); return
    chat = LlmChat(api_key=os.environ['EMERGENT_LLM_KEY'], session_id='fig-sedi',
                   system_message='You generate one diagram per request.')
    chat.with_model('gemini', 'gemini-3.1-flash-image-preview').with_params(modalities=['image', 'text'])
    text, images = await chat.send_message_multimodal_response(UserMessage(text=f'{STYLE}\n\nSubject: {SUBJECT}'))
    if not images:
        print('NESSUNA IMMAGINE', str(text)[:120]); return
    im = Image.open(io.BytesIO(base64.b64decode(images[0]['data']))).convert('RGB')
    w, h = im.size
    if abs(w / h - 1.0) > 0.06:
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    if max(im.size) > 1200:
        r = 1200 / max(im.size)
        im = im.resize((int(im.size[0] * r), int(im.size[1] * r)), Image.LANCZOS)
    im.save(out, 'WEBP', quality=85)
    print('sedi-dei-difetti', im.size, out.stat().st_size, 'bytes')

asyncio.run(main())
