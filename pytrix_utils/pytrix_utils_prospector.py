import psutil
import time
import random
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÃO ---
TEMP_LIMITE = 75  
MAX_THREADS = 10
ARQUIVO_FINAL = "pytrix_leads.json"

def ler_cpu_temp():
    temps = psutil.sensors_temperatures()
    if 'k10temp' in temps:
        return temps['k10temp'][0].current
    return 0

def formatar_whatsapp(telefone_raw):
    if not telefone_raw: return None
    clean = re.sub(r'\D', '', telefone_raw)
    return f"https://wa.me/55{clean}" if len(clean) >= 10 else None

def extrair_ativos(page):
    ativos = {"fotos": [], "reviews": [], "telefone": ""}
    try:
        # Telefone (Campo de acessibilidade do Maps)
        tel_el = page.locator('button[data-item-id^="phone:tel:"]')
        if tel_el.count() > 0:
            ativos["telefone"] = tel_el.first.get_attribute('data-item-id').replace('phone:tel:', '')

        # Fotos (Captura via style para evitar download do arquivo pesado)
        fotos_loc = page.locator('button[aria-label^="Foto de"]')
        for i in range(min(fotos_loc.count(), 3)):
            style = fotos_loc.nth(i).locator('div').first.get_attribute('style')
            if style and "url(" in style:
                url = style.split('url("')[1].split('")')[0]
                ativos["fotos"].append(url)

        # Reviews (Social Proof)
        reviews_loc = page.locator('div.MyEned')
        for i in range(min(reviews_loc.count(), 3)):
            t = reviews_loc.nth(i).inner_text()
            if len(t) > 15: ativos["reviews"].append(t.replace('\n', ' '))
    except: pass
    return ativos

def minerar(cidade, categoria):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64)")
        page = context.new_page()
        
        # O GHOST MODE (Bloqueia o que pesa e o que rastreia)
        page.route("**/*.{png,jpg,jpeg,css,woff2,svg}", lambda route: route.abort())
        
        try:
            # Proteção Térmica do Ryzen
            while ler_cpu_temp() > TEMP_LIMITE:
                time.sleep(5)

            query = f"{categoria} em {cidade} -anuncio"
            page.goto(f"https://www.google.com.br/maps/search/{query.replace(' ', '+')}")
            
            selector = 'div[role="article"]'
            page.wait_for_selector(selector, timeout=10000)
            
            cards = page.locator(selector)
            for i in range(min(cards.count(), 10)):
                card = cards.nth(i)
                
                # Só nos interessa quem NÃO tem site
                if card.locator('a[data-value="Website"]').count() > 0: continue

                nome = card.get_attribute('aria-label')
                card.click(force=True)
                page.wait_for_selector('h1.DUwDvf', timeout=5000)
                
                detalhes = extrair_ativos(page)
                
                lead = {
                    "empresa": nome,
                    "whatsapp": formatar_whatsapp(detalhes["telefone"]),
                    "cidade": cidade,
                    "categoria": categoria,
                    "mockup": {
                        "bio": "Referência em qualidade e atendimento na região.",
                        "foto_principal": detalhes["fotos"][0] if detalhes["fotos"] else None,
                        "review_destaque": detalhes["reviews"][0] if detalhes["reviews"] else "Ótimo atendimento!"
                    },
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # Dump incremental (Cada linha é um JSON para não corromper o arquivo)
                with open(ARQUIVO_FINAL, "a", encoding="utf-8") as f:
                    f.write(json.dumps(lead, ensure_ascii=False) + "\n")
                
                print(f"🎯 [HIT] {nome} - Salvo.")
                page.wait_for_timeout(random.randint(2000, 5000))
        finally:
            browser.close()

def main():
    # Cidades estratégicas da tua região (Vale do Paraíba)
    cidades = [
        "Jacareí", 
        "São José dos Campos", 
        "Caçapava", 
        "Taubaté", 
        "Santa Branca",
        "Igaratá"
    ]

    # Categorias ordenadas por potencial de fechamento (Dados históricos)
    categorias = [
        "Marmoraria",           # VIP: Ticket altíssimo, exige portfólio visual
        "Móveis Planejados",    # VIP: Decisão baseada em estética
        "Estética Automotiva",  # ALTA: Público exigente e digitalizado
        "Vidraçaria",           # ALTA: Precisa profissionalizar orçamentos
        "Serralheria",          # MÉDIA: Serviço de projeto/segurança
        "Oficina Mecânica",     # MÉDIA: Ganha na confiança e organização
        "Ar Condicionado",      # MÉDIA: Busca por urgência
        "Pet Shop",             # MÉDIA: Diferenciação no atendimento local
        "Gráfica",              # NICHO: B2B que precisa de site moderno
        "Energia Solar"         # BÔNUS: Mercado em explosão na região
    ]

    # Gera o cruzamento total (6 cidades * 10 categorias = 60 tarefas)
    tarefas = [(c, cat) for c in cidades for cat in categorias]

    # Randomizar é essencial para não ser bloqueado pelo Google
    random.shuffle(tarefas)

    print(f"🔥 Pytrix Refinery v2: {MAX_THREADS} threads a postos.")
    print(f"📦 Total de alvos na região: {len(tarefas)}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for cidade, categoria in tarefas:
            executor.submit(minerar, cidade, categoria)

if __name__ == "__main__":
    main()