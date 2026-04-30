import datetime
import decimal
import zoneinfo
import time
import re

import pydantic_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from commons import base_types
from domain.model import buscalibre

class _Settings(pydantic_settings.BaseSettings):
    headless: bool = True


_SETTINGS = _Settings()


class BuscaLibreScraper:

    def scrape_book(self, url: str) -> buscalibre.Book:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-dev-shm-usage")  # Fuerza a Chrome a usar /tmp en lugar de /dev/shm
        options.add_argument("--disable-gpu")  # Recomendado en servidores sin tarjeta gráfica
        options.add_argument("--window-size=1920,1080")  # Define un tamaño fijo para evitar errores de renderizado
        options.add_argument("--remote-debugging-pipe")  # A veces ayuda con errores de comunicación en Docker

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        wait = WebDriverWait(driver, 15)

        try:
            driver.get(url)

            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)

            nombre = self._get_title(driver=driver)
            autor = self._get_author(driver=driver)

            return buscalibre.Book.create(
                title=nombre, author=autor, link=url
            )

        except Exception as e:
            print("Error real:", repr(e))
            raise Exception("Error obteniedo data")# 👈 esto da mejor debug

        finally:
            driver.quit()

    def scrape_book_price_history(self, url: str, book_id: str) -> buscalibre.BookPriceHistory:
        options = Options()
        if _SETTINGS.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-dev-shm-usage")  # Fuerza a Chrome a usar /tmp en lugar de /dev/shm
        options.add_argument("--disable-gpu")  # Recomendado en servidores sin tarjeta gráfica
        options.add_argument("--window-size=1920,1080")  # Define un tamaño fijo para evitar errores de renderizado
        options.add_argument("--remote-debugging-pipe")  # A veces ayuda con errores de comunicación en Docker

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        wait = WebDriverWait(driver, 15)

        try:
            driver.get(url)

            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)

            nombre = self._get_title(driver=driver)
            autor = self._get_author(driver=driver)
            precio_actual = self._get_discounted_price(driver=driver)
            precio_original = self._get_current_price(driver=driver)
            descuento = self._get_discount(driver=driver)

            return buscalibre.BookPriceHistory(
                id=base_types.HumanFriendlyId(),
                book_id=book_id,
                title=nombre,
                author=autor,
                price=decimal.Decimal(precio_original),
                discounted_price=precio_actual,
                discount=int(descuento),
                requested_at=datetime.datetime.now(zoneinfo.ZoneInfo("America/Bogota")),
            )

        except Exception as e:
            print("Error real:", repr(e))
            raise Exception("Error obteniedo data")# 👈 esto da mejor debug

        finally:
            driver.quit()

    @staticmethod
    def _get_title(driver: webdriver.Chrome) -> str:
        return driver.find_element(By.CSS_SELECTOR, "p.tituloProducto").text

    @staticmethod
    def _get_author(driver: webdriver.Chrome) -> str:
        try:
            autor = driver.find_element(By.CSS_SELECTOR, "a[href*='autor']").text
        except Exception as e:
            print(e)
            autor = "No encontrado"

        return autor

    @staticmethod
    def _get_discounted_price(driver: webdriver.Chrome) -> decimal.Decimal:
        try:
            precio_actual_texto = driver.find_element(By.CSS_SELECTOR, ".colPrecio .ped").text
            precio_actual = re.sub(r'\D', '', precio_actual_texto)
            return decimal.Decimal(precio_actual)
        except:
            raise Exception("Precio no encontrado")

    @staticmethod
    def _get_current_price(driver: webdriver.Chrome) -> decimal.Decimal:
        try:
            precio_original_texto = driver.find_element(By.CSS_SELECTOR, ".colPrecio .pvp").text
            precio_original = re.sub(r'\D', '', precio_original_texto)
            return decimal.Decimal(precio_original)
        except:
            raise Exception("Precio original no encontrado")

    @staticmethod
    def _get_discount(driver: webdriver.Chrome) -> int:
        # Descuento
        try:
            descuento_texto = driver.find_element(By.CSS_SELECTOR, ".colDescuento span").text
            descuento = re.sub(r'\D', '', descuento_texto)
            return int(descuento)
        except:
            raise Exception("Descuento no encontrado")