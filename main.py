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
    # User-Agent real para evitar bloqueios do Cloudflare/DataDome
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    driver = None
    try:
        # Inicialização do Chrome
        driver = uc.Chrome(options=options, headless=True)
        driver.get(url)
        
        # Aguarda a página carregar
        time.sleep(7)

        # Rola um pouco a tela para acionar o carregamento (Lazy Load)
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)

        # Tenta pegar os cards de produtos completos
        cards = driver.find_elements(By.CSS_SELECTOR, ".poly-card, .ui-search-layout__item")
        
        produtos = []

        # Se encontrou cards estruturados
        if cards:
            for card in cards:
                try:
                    # Busca título
                    titulo_elem = card.find_elements(By.CSS_SELECTOR, ".poly-component__title, .ui-search-item__title")
                    # Busca preço
                    preco_elem = card.find_elements(By.CSS_SELECTOR, ".poly-price__current .andes-money-amount__fraction, .ui-search-price__part--medium .andes-money-amount__fraction")
                    
                    if titulo_elem and preco_elem:
                        nome = titulo_elem[0].text
                        preco = preco_elem[0].text
                        link = titulo_elem[0].get_attribute("href")
                        
                        if nome and preco:
                            produtos.append({
                                "nome": nome,
                                "preco": preco,
                                "url": link
                            })
                except Exception:
                    continue

        # Fallback: Se não encontrou por cards, busca elementos soltos na página
        if not produtos:
            titulos = driver.find_elements(By.CSS_SELECTOR, ".poly-component__title, .ui-search-item__title")
            precos = driver.find_elements(By.CSS_SELECTOR, ".poly-price__current .andes-money-amount__fraction, .andes-money-amount__fraction")
            
            for t, p in zip(titulos, precos):
                if t.text and p.text:
                    produtos.append({
                        "nome": t.text,
                        "preco": p.text,
                        "url": t.get_attribute("href")
                    })

        return {"status": "success", "total": len(produtos), "data": produtos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if driver:
            driver.quit()
