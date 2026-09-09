from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    cookies_string: str  # String de cookies copiada do navegador/planilha

@app.post("/scrape")
def scrape_mercadolivre(data: ScrapeRequest):
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = None
    try:
        driver = uc.Chrome(options=options, headless=True)
        
        # 1. É preciso primeiro carregar o domínio para poder definir os cookies
        driver.get("https://lista.mercadolivre.com.br")
        time.sleep(2)

        # 2. Converte a string de cookies em dicionários que o Selenium entende
        if data.cookies_string:
            cookie_pairs = data.cookies_string.split(";")
            for pair in cookie_pairs:
                if "=" in pair:
                    name, value = pair.strip().split("=", 1)
                    driver.add_cookie({
                        "name": name,
                        "value": value,
                        "domain": ".mercadolivre.com.br",
                        "path": "/"
                    })

        # 3. Acessa a URL desejada já autenticado/com cookies
        driver.get(data.url)
        time.sleep(6)

        titulos = driver.find_elements(By.CSS_SELECTOR, ".poly-component__title")
        precos = driver.find_elements(By.CSS_SELECTOR, ".poly-price__current .andes-money-amount__fraction")
        links = driver.find_elements(By.CSS_SELECTOR, ".poly-component__title")

        produtos = []
        for t, p, l in zip(titulos, precos, links):
            produtos.append({
                "nome": t.text,
                "preco": p.text,
                "url": l.get_attribute("href")
            })

        return {"status": "success", "total": len(produtos), "data": produtos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if driver:
            driver.quit()
