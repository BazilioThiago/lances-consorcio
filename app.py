import openpyxl as opxl
import threading
import time
import os
from globals import Constants as cs
from src.gui import Screens
from src.navigations import Logs
from src.bases import Consorcio
from src.functions import PortalConsorcio

LOGGER = Logs.load_log(__name__, f"{cs.PATH_LOGS}\\main")
RESULTADOS = {}

# 0211082_Lances_de_Consórcio
#responsável: Thiago Bazilio


#region lance
def lance(base: Consorcio, web: PortalConsorcio, login_info: dict, loading_done) -> None:
    df_lances = base.base_lances()
    excel_log_path = f"{cs.PATH_LOGS}\\log_lances.xlsx"
    dict_resultados = {}
    
    qtd_erros = 0

    # Abre ou cria o arquivo Excel uma vez
    if os.path.exists(excel_log_path):
        wb = opxl.load_workbook(excel_log_path)
        ws = wb.active
    else:
        wb = opxl.Workbook()
        ws = wb.active

    try:
        i = 0
        while i < len(df_lances):
            row = df_lances.iloc[i]

            ## Faz o lance livre
            lance_livre = web.rodar_lance(
                row['cod_agencia'], 
                row['cod_grupo'], 
                row['cod_cota'], 
                row['conta_corrente_real'], 
                row['segmento']
                ) # Livre
            
            # Monta os registros do lance
            dict_resultados = Consorcio.retorno_para_log(dict_resultados, lance_livre)
            data = Consorcio.lances_para_log(row, web.resultado_lance)
            ws.append(list(data.values()))  # Adiciona a linha ao Excel
            wb.save(excel_log_path)  # Salva a cada linha

            # Verifica se o aplicativo foi fechado
            if loading_done.is_set():
                LOGGER.info("Loading fechado, parando os lances...")
                break

            ## Faz o lance fixo 
            lance_fixo = web.rodar_lance(
                row['cod_agencia'], 
                row['cod_grupo'], 
                row['cod_cota'], 
                row['conta_corrente_real'], 
                row['segmento'],
                "Fixo"
                )
            
            # Monta os registros do lance
            dict_resultados = Consorcio.retorno_para_log(dict_resultados, lance_fixo)
            data = Consorcio.lances_para_log(row, web.resultado_lance)
            ws.append(list(data.values()))  # Adiciona a linha ao Excel
            wb.save(excel_log_path)  # Salva a cada linha

            # Verifica se o aplicativo foi fechado
            if loading_done.is_set():
                LOGGER.info("Loading fechado, parando os lances...")
                break

            # Se der erro em um lances, em duas linhas, reseta o driver
            if lance_livre == 404 or lance_fixo == 404: 
                qtd_erros += 1
                base.base_erros(row)

                # if qtd_erros >= 5:
                #     LOGGER.critical("Muitos erros consecutivos, encerrando o aplicativo.")
                #     break
                if qtd_erros % 2 == 0:
                    LOGGER.warning("Erro em 2 linhas, resetando o driver.")
                    # i -= 2 # Volta 2 linhas
                    web.encerrar() # reseta o driver
                    time.sleep(5)
                    
                    web = PortalConsorcio()
                    logou = web.login_portal(login_info)
                    if not logou: # se deu erro no login, fecha o app
                        break 
            else: # Se voltou a funcionar, zera o contador
                qtd_erros = 0
                base.registrar_sucesso(i)

            # Verifica se caiu a internet
            if lance_livre == 9 or lance_fixo == 9:
                qtd_erros += 1
                if qtd_erros % 2 == 0:
                    LOGGER.critical("Sem conexão com a internet, aplicativo encerrado.")
                    break # Caiu a internet, fecha o app

            base.salvar_linha(str(dict_resultados))
            i += 1

    finally:
        LOGGER.info(dict_resultados) # Registra o dicionário
        wb.close()  # Fecha o arquivo Excel ao final
        if hasattr(base, 'log_linha_path') and os.path.exists(base.log_linha_path): # Apaga o temp
            os.remove(base.log_linha_path)

        base.reescrever_base_lances() # Exclui linhas de sucesso da base de lances

        global RESULTADOS
        RESULTADOS.update(dict_resultados)


#region Main
def main():
    LOGGER.info("Aplicativo iniciado.")
    web = PortalConsorcio()
    last_email = None
    resultado = None
    # Verifica se registrou no main a ultima vez que rodou
    base = Consorcio()
    if base.ultima_linha: 
        LOGGER.info(f"Registro da última run: {base.ultima_linha}")

    while True: # Loop até logar corretamente
        try: last_email = open(f"{cs.PATH_LOGS}\\last_email.txt").read().strip()
        except: pass

        login_info = Screens.login(last_login=last_email, error_message=resultado)  # Tela de Login

        if web.login_portal(login_info): # Logou no portal
            break

        resultado = web.resultado_login
        if web.resultado_login != "Login ou senha incorretos.": # Login incorreto -> tenta de novo, outros erros -> reseta o driver
            web.encerrar()
            web = PortalConsorcio()
        
    LOGGER.info(f"|{login_info['login']}")
    escolha = Screens.principal()

    if escolha == "Rodar lances":
        loading_done = threading.Event()

        # Thread da automação
        automacao_thread = threading.Thread(target=lance, args=(base, web, login_info, loading_done))
        automacao_thread.start()

        # Thread da tela de loading
        loading_thread = threading.Thread(target=Screens.loading, args=(loading_done,))
        loading_thread.start()

        # Aguarda qualquer uma das threads terminar
        while automacao_thread.is_alive() and loading_thread.is_alive():
            threading.Event().wait(0.1)
            
        # Sinaliza para ambas pararem
        loading_done.set()
        # Aguarda ambas terminarem
        automacao_thread.join()
        loading_thread.join()

        # Mostra a tela de mensagem
        web.encerrar()
        time.sleep(2)
        resultados_str = '\n'.join([f"{k}: {v}" for k, v in RESULTADOS.items()])
        Screens.final(f"Lances finalizados!\n{resultados_str}")
    
        
# main
if __name__ == '__main__':
    # Automático (fr)
    try: main()
    finally: LOGGER.info("Aplicativo finalizado.\n")
