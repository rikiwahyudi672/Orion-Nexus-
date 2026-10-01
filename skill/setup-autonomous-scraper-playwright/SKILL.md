---
name: setup-autonomous-scraper-playwright
description: Dipakai saat user meminta atau menyetujui pembuatan template bot scraping web / browser automation autonomous menggunakan Python.
version: 1.0.0
author: Orion
---


## Kapan dipakai
Dipakai saat user meminta atau menyetujui pembuatan template bot scraping web / browser automation autonomous menggunakan Python.

## Langkah
1. Identifikasi kebutuhan otomasi browser / web scraping user.
2. Berikan instruksi instalasi library `playwright` dan binary browser Chromium.
3. Sediakan boilerplate code berbasis `asyncio` dan `playwright.async_api`.
4. Berikan struktur dasar navigasi target URL dan ekstraksi data untuk diintegrasikan ke agent AI.

## Contoh
**Query:**
"boleh sih" (konfirmasi lanjut buat scraper) / "bikinin autonomous scraper pake python dong"

**Hasil:**
```bash
pip install playwright
playwright install chromium
```
```python
import asyncio
from playwright.async_api import async_playwright

async def autonomous_scraper(target_url: str):
    print(f"[*] Agent meluncur ke: {target_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(target_url)
        content = await page.content()
        await browser.close()
        return content
```