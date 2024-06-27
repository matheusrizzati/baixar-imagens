import requests
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.FirefoxOptions()
options.add_argument("--headless=new")

browser = webdriver.Firefox(options=options)
browser.set_window_size(1280, 800)

links = []
website = "estoquee.com.br"

def getPageData():
    sleep(0.5)
    try:
        cookies = browser.find_element(By.XPATH, '/html/body/div[1]/div/a')
        cookies.click()
        notifications = browser.find_element(By.XPATH, '//*[@id="onesignal-slidedown-allow-button"]')
        notifications.click()
    except:
        pass  

    produtos_wait = EC.presence_of_all_elements_located((By.XPATH, '/html/body/div/div[1]/div/div/main/div/ul/li/div[1]/a[1]'))
    produtos = WebDriverWait(browser, 10).until(produtos_wait)
        
    for i in produtos:
        links.append(i.get_attribute('href'))



def getLinkImages(href):
    browser.get(href)
    sleep(1)
    select = browser.find_element(By.XPATH, '//*[@id="pa_cor"]')
    # if select:
    #     print("TEM SELECT")
    #     print("select")
    #     options = browser.find_elements(By.CLASS_NAME, 'attached')
    #     print(options)
    # sleep(1)
    product_name = browser.find_element(By.CLASS_NAME, 'product_title').text
    product_sku = browser.find_element(By.CLASS_NAME, 'sku').text
    
    images_wait = EC.presence_of_element_located((By.XPATH, '//html/body/div[1]/div[1]/div/div/main/div/div[2]/div[1]/ol/li/img'))
    WebDriverWait(browser, 30).until(images_wait)
    images = browser.find_elements(By.XPATH, '/html/body/div[1]/div[1]/div/div/main/div/div[2]/div[1]/div/div/div/a/img')
    images_name = []
    images_src = []
    for i in images:
        src = i.get_attribute('data-large_image')
        name = i.get_attribute('alt')
        images_src.append(src)
        images_name.append(name)
    
    saveData(product_name, product_sku, images_src, images_name)

def saveData(name, sku, srcList, altList):
    folder = website + "/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    productFolder = os.path.join(folder, name)
    if not os.path.exists(productFolder):
        os.makedirs(productFolder)
        
    for i, val in enumerate(srcList):
        image_name = altList[i] + " - " + sku + ".jpg"
        image_path = os.path.join(productFolder, image_name)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        response = requests.get(val, headers=headers)
        response.raise_for_status()

        with open(image_path, 'wb') as file:
            file.write(response.content)

try:
    page_number = 1
    print("Acessando páginas")
    while True:
        browser.get(f"https://estoquee.com.br/todos-os-produtos/page/{page_number}/")
        getPageData()
        try:
            browser.find_element(By.CLASS_NAME, 'next')
            page_number += 1
        except NoSuchElementException:
            print("Todas as páginas foram processadas")
            print(f"Número total de links encontrados: {len(links)}")
            print("Processando produtos")
            for href in links:
                getLinkImages(href)
            break                    
finally:
    print("Imagens salvas com sucesso!")
    browser.close()