"""Send generated Horizon summaries to Telegram."""
import os
import glob
import requests

bot_token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id = os.environ['TELEGRAM_CHAT_ID']
base_url = f'https://api.telegram.org/bot{bot_token}'

files = sorted(glob.glob('data/summaries/horizon-*.md'))
if not files:
    print('No summary files found!')
    exit(1)

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    max_len = 4000
    chunks = []
    remaining = content

    while len(remaining) > max_len:
        split_at = remaining.rfind('\n\n', 0, max_len)
        if split_at == -1 or split_at < max_len // 2:
            split_at = remaining.rfind('\n', 0, max_len)
        if split_at == -1 or split_at < max_len // 2:
            split_at = max_len
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    chunks.append(remaining)

    for i, chunk in enumerate(chunks):
        prefix = f'({i+1}/{len(chunks)}) ' if len(chunks) > 1 else ''
        payload = {
            'chat_id': chat_id,
            'text': prefix + chunk,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        resp = requests.post(f'{base_url}/sendMessage', data=payload, timeout=30)
        lang = 'EN'
        if 'zh' in filepath.lower():
            lang = 'ZH'
        print(f'Telegram sent {lang} chunk {i+1}/{len(chunks)}: {resp.status_code} - {resp.text[:100]}')
