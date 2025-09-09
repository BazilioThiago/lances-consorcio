from datetime import datetime
import xlwings as xw
import pandas as pd
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from globals import Constants as cs
from src.navigations import Logs, USER

#region BASES

# Carrega o log
LOGGER = Logs.load_log(__name__)
PATH_INICIAL = f"C:\\Users\\{USER}\\"


class Consorcio:

    def __init__(self):
        self.df_lances = pd.DataFrame()
        self.success_indices: list[int] = []
        self.planilha_lances = f"{cs.PATH_BASE}"
        self.ultima_linha = None
        # Verifica se registrou no main a ultima vez que rodou
        self.log_linha_path = f"{PATH_INICIAL}Documents\\temp_lances.txt"
        if os.path.exists(self.log_linha_path):
            with open(self.log_linha_path, "r", encoding="utf-8") as f:
                linhas = f.readlines()
                if linhas:
                    ultima_linha = linhas[-1].strip()
                    self.ultima_linha = ultima_linha


    def base_lances(self) -> pd.DataFrame:
        """ cod_agencia, segmento, cod_grupo, cod_cota, conta_corrente_real, """
        LOGGER.debug("| base_lances")
        LOGGER.info("Aplicativo iniciado.")
        self.df_lances = pd.read_excel(self.planilha_lances, sheet_name='dados', engine='calamine')
        self.df_lances['conta_corrente_real'] = self.df_lances['conta_corrente_real'].astype(str).str.replace(r'\.0$', '', regex=True)
        LOGGER.debug("_ Preparou a base de lances")
        return self.df_lances


    def salvar_linha(self, linha: str) -> None:
        """ Cria um temp pra salvar o dicionário de resultado dos lances """
        with open(self.log_linha_path, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
    

    def registrar_sucesso(self, row_index: int) -> None:
        """ Armazena o índice da linha que teve lance(s) bem-sucedido(s) """
        self.success_indices.append(row_index)


    def reescrever_base_lances(self) -> None:
        """ Exclui linhas de sucesso, preservando conexões e formatações da planilha Excel """
        if self.success_indices: 
            # Abre Excel e remove linhas bem-sucedidas da tabela
            app = xw.App(visible=False)
            wb = app.books.open(self.planilha_lances)
            sht = wb.sheets['dados']
            try:
                tbl = sht.api.ListObjects(1)
                # Remove em ordem inversa para não desalinhar índices
                for idx in sorted(self.success_indices, reverse=True):
                    tbl.ListRows(idx).Delete()
            except Exception:
                pass
            wb.save()
            wb.close()
            app.quit()
            LOGGER.info("Linhas bem-sucedidas removidas da base de dados.")
            return

        # Se não houver linhas de sucesso, não altera a planilha
        LOGGER.info("Nenhuma linha de sucesso para remover; planilha mantida intacta.")


    @staticmethod
    def retorno_para_log(resultados: dict, retorno_lance: int) -> dict:
        """ Monta o dicionário de retornos dos lances, para o main.log """
        match retorno_lance:
            case 0:
                r = "Sucesso"
                resultados[r] = resultados.get(r, 0) + 1
            case 1:
                r = "Consorciado inválido"
                resultados[r] = resultados.get(r, 0) + 1
            case 2:
                r = "Lance fora do prazo"
                resultados[r] = resultados.get(r, 0) + 1
            case 3:
                r = "Valor de lance excedido"
                resultados[r] = resultados.get(r, 0) + 1
            case 9:
                r = "Sem conexão com a internet"
                resultados[r] = resultados.get(r, 0) + 1
            case 10:
                r = "Lance livre pulado, já existe lance feito"
                resultados[r] = resultados.get(r, 0) + 1
            case 11:
                r = "Lance fixo pulado, segmento PESADO"
                resultados[r] = resultados.get(r, 0) + 1
            case 12:
                r = "Lance fixo pulado, lance máximo menor que 20%"
                resultados[r] = resultados.get(r, 0) + 1
            case 99:
                r = "Exceção não parametrizada"
                resultados[r] = resultados.get(r, 0) + 1
            case _: 
                r = "404 - Erro"
                resultados[r] = resultados.get(r, 0) + 1
        return resultados
    

    @staticmethod
    def lances_para_log(row, resultado_lance: str) -> dict:
        """ Monta o dicionário de lances, para o log_lances.xlsx """
        data = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "resultado_lance": str(resultado_lance),
            "cod_agencia": row['cod_agencia'],
            "cod_grupo": row['cod_grupo'],
            "cod_cota": row['cod_cota'],
            "conta_corrente_real": row['conta_corrente_real'],
            "cpf_cnpj": row['cpf_cnpj'],
            "consorciado": row['consorciado'],
            "segmento": row['segmento']
            }
        return data
    

# Para fins de teste
if __name__ == '__main__':
    a = Consorcio()
    df = a.base_lances()
    print(df)