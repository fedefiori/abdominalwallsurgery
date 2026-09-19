#!/usr/bin/env python3
"""Genera le 2 nuove figure (chirurgo in sala operatoria, parete per pre-abilitazione)
con la ricetta dell'hub: gemini-3.1-flash-image-preview via EMERGENT_LLM_KEY."""
import asyncio, base64, io, os, sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv('/app/backend/.env')
MEDIA = Path('/app/backend/static/media')

STYLE = ("Ultra-minimal premium editorial diagram for a surgeon's website. Thin "
         "electric-blue (#0B81E1) and light-blue (#4FB0F5) line work with cool silver "
         "accents on a deep steel-grey background (#161B21), faint 1px silver hairline "
         "grid. Schematic and abstract, anatomically suggestive but never realistic, "
         "never graphic or bloody: no gore, no wounds, no blood, no faces, no "
         "photographic skin, no logos. Absolutely no text, no letters, no numbers, no "
         "labels and no arrows with captions anywhere in the image. Centred "
         "composition, generous negative space, fine film grain, soft vignette, sober "
         "and high-tech.")

SUBJECTS = {
    'chirurgo-sala-operatoria': "abstract schematic of a surgeon at work in an operating room: a standing figure in surgical gown and cap, seen from the side, leaning over an operating table, gloved hands above a softly highlighted abdominal field traced in luminous lines, a slim overhead surgical light. Wide 4:3 format.",
    'preabilitazione-parete': "front schematic view of the human abdominal wall: two rectus muscles drawn as luminous parallel bands, the vertical linea alba as a bright central line, subtle ascending stepped motif along one side suggesting gradual preparation, faint concentric support lines. Wide 4:3 format.",
}

async def gen(name, subject):
    out = MEDIA / f'{name}.webp'
    chat = LlmChat(api_key=os.environ['EMERGENT_LLM_KEY'],
                   session_id=f'fig-{name}', system_message='You generate one diagram per request.')
    chat.with_model('gemini', 'gemini-3.1-flash-image-preview').with_params(modalities=['image', 'text'])
    text, images = await chat.send_message_multimodal_response(UserMessage(text=f'{STYLE}\n\nSubject: {subject}'))
    if not images:
        print(name, 'NESSUNA IMMAGINE', str(text)[:120])
        return
    raw = base64.b64decode(images[0]['data'])
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    w, h = im.size
    target = 4 / 3
    cur = w / h
    if abs(cur - target) > 0.06:
        if cur > target:
            nw = int(h * target)
            im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = int(w / target)
            im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    if max(im.size) > 1200:
        r = 1200 / max(im.size)
        im = im.resize((int(im.size[0] * r), int(im.size[1] * r)), Image.LANCZOS)
    q = 85
    while True:
        im.save(out, 'WEBP', quality=q)
        if out.stat().st_size <= 150_000 or q <= 40:
            break
        q -= 10
    print(name, im.size, out.stat().st_size, 'bytes')

async def main():
    for name, subject in SUBJECTS.items():
        try:
            await gen(name, subject)
        except Exception as e:
            print(name, 'ERRORE', str(e)[:200])

asyncio.run(main())
