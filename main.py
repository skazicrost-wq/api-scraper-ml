from fastapi import FastAPI, HTTPException
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

app = FastAPI()

@app.get("/scrape")
def scrape_mercadolivre(url: str):
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = None
    try:
        # Inicializa o Chrome mascarado
        driver = uc.Chrome(options=options, headless=True)
        driver.get(url)
        
        # Aguarda carregamento
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
