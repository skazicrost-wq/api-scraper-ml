from fastapi import FastAPI, HTTPException
import undetected_chromedriver as uc
import time

app = FastAPI()

@app.get("/scrape")
def scrape_mercadolivre(url: str):
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    driver = None
    try:
        driver = uc.Chrome(options=options, headless=True)
        driver.get(url)
        time.sleep(7)

        # Captura o título real da página renderizada
        page_title = driver.title
        # Captura os primeiros 1000 caracteres do código fonte
        html_snippet = driver.page_source[:1000]

        return {
            "titulo_da_pagina": page_title,
            "is_captcha": "Seguridad" in page_title or "captcha" in html_snippet.lower(),
            "html_preview": html_snippet
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if driver:
            driver.quit()
