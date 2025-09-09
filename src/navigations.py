from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from win32com.client import Dispatch
from dotenv import load_dotenv
import pythoncom
import logging
import getpass
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 
from globals import Constants as cs

USER = getpass.getuser()
HEADLESS = cs.FLAG_HEADLESS

#region NAVIGATIONS


class Logs:
    @staticmethod
    def load_log(name: str, log: str = f"{cs.PATH_LOGS}\\specific", minimal_level: str = "info") -> logging.Logger:
        '''
        name - nome do logger: não usado na formatação pq (filename) é mais bonito
        log - arquivo do log: opcional, especificar quando houver mais de um log
        minimal_level - nivel mínimo de log registrado: "info" não registrará .debug, apenas .info pra cima
        '''
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, minimal_level.upper(), logging.INFO))

        if not logger.handlers:
            # if not os.path.exists("logs"):
            #     os.makedirs("logs")
            log_path = f"{log}.log"
            file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger

"""
Em todos os arquivos que usarão log, deve ser chamada a função no início:
LOGGER = Logs.load_log(__name__)

Caso tenha mais de um arquivo de log, necessário especificar:
LOGGER = Logs.load_log(__name__, "main")

Para registrar, pode ser usado assim:
LOGGER.info("informação geral")
LOGGER.warning("aviso simples")
LOGGER.error("erro pesado")
"""
# Carrega o log


class ExpectedException(Exception):
    pass # Classe para tratativas de exceções esperadas


class Browser:
    @staticmethod
    def set_browser():
        LOGGER = Logs.load_log(__name__)
        LOGGER.debug("| set_browser")

        try:
            # Configurações do Edge
            edge_options = Options()
            edge_options.add_argument('--start-maximized')
            edge_options.add_argument('--enable-cloud-management')
            
            if HEADLESS:
                edge_options.add_argument('--headless=new')  # Modo headless
            
            # Configurações para melhorar estabilidade
            edge_options.add_argument("window-size=1920,1080")  # Define a resolução
            edge_options.add_argument("--disable-gpu")  # Desativa GPU
            edge_options.add_argument("--disable-software-rasterizer")  # Desativa rasterização de software
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging']) # n faço ideia
            
            # Opções que contornam o bloqueio do uso de Headless
            edge_options.add_argument("--disable-blink-features=AutomationControlled") 
            edge_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

            # Encontra o driver certo do Edge
            def get_version(filename):
                pythoncom.CoInitialize() # Inicializa o COM para a thread atual
                parser = Dispatch("Scripting.FileSystemObject")
                try:
                    versao_browser = parser.GetFileVersion(filename)
                except:
                    versao_browser = '134.0.3124.51'
                return versao_browser

            paths = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                     r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
            edge_options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            versao_browser = list(filter(None, [get_version(p) for p in paths]))[0]
            versao_browser = versao_browser[0:3]
            caminho_browser = f"{cs.PATH_DRIVER}_{versao_browser}.exe"
            edge_service = Service(caminho_browser)
            LOGGER.debug(caminho_browser)

            edge_options.add_argument("https://www.sicredi.com.br/")
            driver = webdriver.Edge(options=edge_options, service=edge_service)

            LOGGER.debug(f"_ Setou o driver")
            return driver
        
        except Exception as e:
            LOGGER.error(f"Erro no set_browser: {e}")
        
    
    @staticmethod
    def wait_until_located(driver, tempo: int, tipo: str, variavel: str, multiple: bool = False):
        by_type = getattr(By, tipo.upper())  # Obtém o atributo da classe By dinamicamente
        if not multiple:
            aux = WebDriverWait(driver, tempo).until(EC.presence_of_element_located((by_type, variavel)))
        else:
            aux = WebDriverWait(driver, tempo).until(EC.presence_of_all_elements_located((by_type, variavel)))
        return aux
    


    @staticmethod
    def wait_until_clickable(driver, tempo: int, tipo: str, variavel: str):
        by_type = getattr(By, tipo.upper())
        aux = WebDriverWait(driver, tempo).until(EC.element_to_be_clickable((by_type, variavel)))
        return aux 


    @staticmethod
    def click_element_by_text(driver, x_path: str, texto: str):
        elementos = Browser.wait_until_located(driver, 10, 'xpath', x_path, multiple=True)  # Busca múltiplos elementos

        for elemento in elementos:
            if texto in elemento.text:
                driver.execute_script("arguments[0].click();", elemento)
                return # Sai da função após clicar no elemento
        #print(f'Nenhum elemento compatível: \nTexto: {texto} \nXPath: {x_path}')
    

    @staticmethod
    def wait_alert(driver, tempo: int):
        WebDriverWait(driver, tempo).until(EC.alert_is_present())
        return
