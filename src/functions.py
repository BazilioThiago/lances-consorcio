from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 
    # pra poder rodar tanto pelo main (app.py) quanto direto (functions.py)
from globals import Constants as cs
from src.navigations import Browser, Logs, ExpectedException

#region FUNCTIONS

# Carrega o log
LOGGER = Logs.load_log(__name__)


class PortalConsorcio:

    def __init__(self): 
        self.driver = Browser.set_browser()
        self.link_portal = cs.LINK_PORTAL


    def encerrar(self):
        self.driver.quit()
        

    #region login_portal
    def login_portal(self, login_info: dict) -> bool:
        LOGGER.debug("| login_portal")

        try: # Preenche email, senha e confirma
            self.resultado_login = None
            self.driver.get(self.link_portal)

            campo_autenticacao = Browser.wait_until_clickable(self.driver, 10, 'id', 'diana-button-1-label')
            campo_autenticacao.click()

            # Verifica se entrou no portal
            try:
                Browser.wait_until_located(self.driver, 5, 'id', 'ctl00_Conteudo_lblInfoUsuario')
                LOGGER.debug("_ Entrou no portal")
                return True
            except: pass

            # Se não logou direto, tenta pelo email e senha
            campo_email = Browser.wait_until_located(self.driver, 10, 'id', 'i0116')
            campo_email.click()
            campo_email.send_keys(login_info['login'])
            time.sleep(1)

            try: # Verifica se o email está incorreto
                Browser.wait_until_located(self.driver, 3, 'id', 'i0116')
                self.resultado_login = "Email incorreto."
                LOGGER.warning(self.resultado_login)
                return False
            except: pass

            campo_senha = Browser.wait_until_located(self.driver, 10, 'id', 'i0118')
            campo_senha.click()
            campo_senha.send_keys(login_info['password'])
            time.sleep(1)

            try: # Verifica se a senha está incorreta
                Browser.wait_until_located(self.driver, 3, 'id', 'i0118')
                self.resultado_login = "Senha incorreta."
                LOGGER.warning(self.resultado_login)
                return False
            except: pass

            botao_confirma = Browser.wait_until_located(self.driver, 10, 'id', 'idSIButton9')
            botao_confirma.click()
            time.sleep(1)
            botao_confirma.click() # clica em 'Sim'

            # Verifica se entrou no portal
            try:
                Browser.wait_until_located(self.driver, 3, 'id', 'ctl00_Conteudo_lblInfoUsuario')
                LOGGER.debug("_ Entrou no portal")
                return True
            except: pass
            
            try: # Verifica erros
                erro_elem = Browser.wait_until_located(self.driver, 3, 'id', 'lblMensagemErro') # Mensagem de erro do portal
            except:
                raise Exception 
            else:
                if "Não foi encontrada nenhuma função de usuário" in erro_elem.text: # Erro de usuário sem acesso
                    self.resultado_login = "Colaborador sem permissão pra acessar o portal."
                else:
                    self.resultado_login = erro_elem.text # Outros erros

                LOGGER.warning(self.resultado_login)
                return False
            
        except Exception as e:
            self.driver.save_screenshot(f"{cs.PATH_LOGS}\\error_screenshot(login_portal).png")
            self.resultado_login = "Ocorreu um erro ao entrar no portal, tente novamente."
            LOGGER.error(f"Erro no login_portal: {e}")
            return False
        

    # region rodar_lance
    def rodar_lance(self, cod_ua: int, cod_grupo: int, cod_cota: int, conta: str, segmento: str, tipo_lance: str = "Livre") -> int:
        """
        Retornos: 
        | 0 - Sucesso
        | 1 - Consorciado inválido
        | 2 - Lance fora do prazo
        | 3 - Valor de lance excedido
        | 4 - Parcela atual paga com multa/juros
        | 9 - Sem conexão com a internet
        | 10 - Lance livre pulado, já existe lance feito
        | 11 - Lance fixo pulado, segmento PESADO
        | 12 - Lance fixo pulado, lance máximo menor que 20%
        | 99 - Exceção não parametrizada
        | 404 - Erro desconhecido
        """
        LOGGER.debug("| rodar_lance")

        try: # try geral
            time.sleep(2)
            self.driver.get(self.link_portal+"CONAT/frmConAtSrcConsorciado.aspx") # Link de atendimento
            # Browser.wait_until_clickable(self.driver, 10, 'id', 'ctl00_img_Atendimento').click() # Botão que leva à página de atendimento (redundância)

            grupo_e_cota = Browser.wait_until_located(self.driver, 10, 'id', 'ctl00_Conteudo_edtGrupo') # Grupo
            
            grupo_e_cota.send_keys(f"{cod_grupo}\t{cod_cota}") # Preenche Grupo e Cota
            Browser.wait_until_clickable(self.driver, 10, 'id', 'ctl00_Conteudo_btnLocalizar').click() # Botão "Localizar"
            time.sleep(1)

            # region Exc 1
            # Verifica consorciado inválido e se não saiu da tela
            try:
                a = Browser.wait_until_located(self.driver, 3, 'id', 'ctl00_Conteudo_lblErrMsg') # Mensagem "Consorciado inválido."
                Browser.wait_until_located(self.driver, 3, 'id', 'ctl00_Conteudo_edtGrupo') # Grupo (mesma tela)
                if "Consorciado inválido." in a.text:
                    self.retorno = 1 
                    raise ExpectedException("Consorciado inválido.")
            except ExpectedException: raise
            except: pass # Entrou, grupo e cota válidos    
            else:
                self.retorno = 99
                raise ExpectedException(a.text)
            
            # Oferta de Lance
            Browser.wait_until_clickable(self.driver, 10, 'id', 'ctl00_Conteudo_Menu_CONAT_grd' \
            'Menu_CONAT_ctl19_hlkFormulario').click()
            time.sleep(1)

            # region Exc 2
            # Verifica lance fora do prazo
            try: 
                alert = self.driver.switch_to.alert
                if "Oferta de Lance só" in alert.text:
                    self.retorno = 2
                    raise ExpectedException("Lance fora do prazo.")
            except ExpectedException: raise
            except: pass # Sem alerta
            else: 
                self.retorno = 99
                raise ExpectedException(alert.text)
            
            # Pega o lance máximo e formata como 0,0000
            a = Browser.wait_until_located(self.driver, 10, 'id', 'ctl00_Conteudo_lblVA_Lance_Maximo')
            lance_maximo = float(a.text.replace('%', '').replace(',', '.').strip())

            # Lance Livre (25%)
            if tipo_lance == "Livre":
                # region Exc 10
                # Verifica se já tem lance feito
                try:
                    a = Browser.wait_until_located(self.driver, 3, 'id', 'ctl00_Conteudo_lblNM_Ocorrencia') # Mensagem na oferta do lance
                    if "Último lance ofertado em" in a.text: # Se tiver lance feito, pula o livre pra não sobrepor
                        self.retorno = 10
                        raise ExpectedException("Lance livre pulado, já existe lance feito.")
                except ExpectedException: raise
                except: pass
                    
                # Compara valor padrão com lance máximo
                lance_livre: str = "250000" # 25%
                if lance_maximo < 25:
                    lance_livre = "{:.4f}".format(lance_maximo).replace('.', '').zfill(6) # Garante 6 dígitos (ex: 22.0 -> 220000)
                
                # Preenche o valor do lance
                livre_percentual = Browser.wait_until_located(self.driver, 10, 'id', 'ctl00_Conteudo_edtOferta')
                livre_percentual.click()
                livre_percentual.send_keys(Keys.END)
                livre_percentual.send_keys(lance_livre)
            
            # Lance Fixo (20%)
            else: 
                # region Exc 11
                # Verifica o segmento
                if segmento == "CAMINHÃO, TRATOR E EQUIP":
                    self.retorno = 11
                    raise ExpectedException("Lance fixo pulado, segmento PESADO.")
                
                # region Exc 12
                # Verifica o lance máximo e formata como 0,0000
                # lance_fixo: str = "200000" #20%
                if lance_maximo < 20:
                    # lance_fixo = "{:.4f}".format(lance_maximo).replace('.', '').zfill(6) # Garante 6 dígitos (ex: 22.0 -> 220000)
                    self.retorno = 12
                    raise ExpectedException("Lance fixo pulado, lance máximo menor que 20%.")
                    # Lance fixo bloqueado se o lance máximo for menor que 20%
                
                fixo = Browser.wait_until_located(self.driver, 5, 'xpath', '//*[@id="ctl00_Conteudo_rgLance_1" and @name="ctl00$Conteudo$rgLance"]')
                fixo.click()

            # Confirma lance
            try: Browser.wait_until_located(self.driver, 10, 'id', 'ctl00_Conteudo_Label5').click() #clica fora
            except: pass
            time.sleep(1)
            confirma = Browser.wait_until_clickable(self.driver, 10, 'id', 'ctl00_Conteudo_btnConfirma') # Botão "Confirmar"
            confirma.click()

            # region Exc 3
            # Verifica valor excedido
            try: 
                alert = self.driver.switch_to.alert
                texto_alerta = alert.text
                if "Percentual convertido é maior que o máximo permitido" in texto_alerta:
                    self.retorno = 3
                    raise ExpectedException("Lance com valor excedido.")
            except ExpectedException: raise
            except: pass # Sem alerta
            
            # Se já tiver lance feito, prossegue (no fixo)
            try:
                alert = self.driver.switch_to.alert
                if "Consorciado já credenciado" in alert.text:
                    alert.accept()
            except: pass

            #region Exc 4
            # Verifica parcela atual paga com multa/juros
            try: 
                alert = self.driver.switch_to.alert
                texto_alerta = alert.text
                if "parcela atual paga com multa" in texto_alerta:
                    self.retorno = 4
                    raise ExpectedException("Parcela atual paga com multa/juros.")
            except ExpectedException: raise
            except: pass # Sem alerta
                
            # Verficiar telefone
            campo_telefone = Browser.wait_until_located(self.driver, 10, 'id', 'ctl00_Conteudo_lblTelefone_Completo')

            try:
                ddd, numero = campo_telefone.text.split("-")
                if len(ddd) == 2 and len(numero) == 9:
                    telefone_correto = True
            except:
                telefone_correto = False

            # se o telefone não estiver no formato certo ("47-123456789")
            if not telefone_correto: 
                ler_tabela = lambda xp: Browser.wait_until_located(self.driver, 10, 'xpath', xp).text # Função para ler a célula de uma tabela
                telefone = cs.TELEFONE_PADRAO # Telefone padrão (SDN)

                Browser.wait_until_clickable(self.driver, 10, 'id', 'ctl00_Conteudo_btnAlterarTelefone').click()
                tabela_telefones = Browser.wait_until_located(self.driver, 10, 'id', 'ctl00_Conteudo_ucBuscaTelefone4_grdTelefone')
                linhas = tabela_telefones.find_elements(By.XPATH, ".//tbody/tr[not(contains(@class, 'header'))]")
                
                adicionar_telefone = True
                preencher_telefone = True
                i_lista: int = 3 # telefone adicionado fica em tr[3]

                # Lê todos os telefones da tabela
                for i in range(3, 2 + len(linhas)):  # a tabela começa em tr[2], itera a quantidade de linhas
                    telefone_linha = ler_tabela(f'//*[@id="ctl00_Conteudo_ucBuscaTelefone4_grdTelefone"]/tbody/tr[{i}]/td[2]')
                    
                    if str(telefone_linha)[0] != "3": # Se o telefone começar com 3 pula (pode ser fixo)
                        ddd_linha = ler_tabela(f'//*[@id="ctl00_Conteudo_ucBuscaTelefone4_grdTelefone"]/tbody/tr[{i}]/td[1]')

                        match len(telefone_linha):
                            case 9: # Telefone válido
                                # Seleciona o telefone e clica em Definir, se tiver DDD
                                if len(ddd_linha) == 2 and ddd_linha.isdigit():
                                    Browser.wait_until_located(self.driver, 5, 'xpath', f'//*[@id="ctl00_Conteudo_ucBuscaTelefone4_grdTelefone"]/tbody/tr[{i}]/td[2]').click()
                                    time.sleep(1)
                                    Browser.wait_until_clickable(self.driver, 5, 'id', 'ctl00_Conteudo_ucBuscaTelefone4_btnDefinir').click() # Definir
                                    preencher_telefone = False
                                else: # Sem ddd, edita o telefone
                                    Browser.wait_until_located(self.driver, 5, 'id', f"ctl00_Conteudo_ucBuscaTelefone4_grdTelefone_ctl0{i}_LinkEditar").click() # Editar
                                    i_lista = i # Atualiza o índice para o telefone editado

                                telefone = telefone_linha
                                adicionar_telefone = False
                                break

                            case 8:
                                Browser.wait_until_located(self.driver, 5, 'id', f"ctl00_Conteudo_ucBuscaTelefone4_grdTelefone_ctl0{i}_LinkEditar").click() # Editar
                                telefone = f"9{telefone_linha}" # Adiciona um digito ao telefone
                                adicionar_telefone = False
                                i_lista = i # Atualiza o índice para o telefone editado
                                break

                            # case 10:
                            #     if len(ddd_linha) == 2 and ddd_linha.isdigit():

                            case _: 
                                pass

                # Adiciona novo telefone
                if adicionar_telefone: 
                    Browser.wait_until_located(self.driver, 5, 'id', 'ctl00_Conteudo_ucBuscaTelefone4_grdTelefone_ctl01_lkbNovoTelefone').click() # +

                if preencher_telefone: # Tela de editar/preencher telefone
                    ddd = Browser.wait_until_located(self.driver, 5, 'id', 'ctl00_Conteudo_ucBuscaTelefone4_edtDDD_Cidade')
                    ddd.click()
                    ddd.clear()
                    ddd.send_keys(f"47\t{telefone}") 
                    Browser.wait_until_clickable(self.driver, 5, 'id', 'ctl00_Conteudo_ucBuscaTelefone4_btnGravaTelefone').click() # Gravar
                    Browser.wait_until_located(self.driver, 5, 'xpath', f'//*[@id="ctl00_Conteudo_ucBuscaTelefone4_grdTelefone"]/tbody/tr[{i_lista}]/td[2]').click()
                    time.sleep(1)
                    Browser.wait_until_clickable(self.driver, 5, 'id', 'ctl00_Conteudo_ucBuscaTelefone4_btnDefinir').click() # Definir

            try: # Confirmação de cota
                Browser.wait_until_located(self.driver, 5, 'id', 'ctl00_Conteudo_Label42') # Texto 'Cotas do Consorciado'
                Browser.wait_until_clickable(self.driver, 5, 'id', 'ctl00_Conteudo_ucBuscaCotas_btnConfirmar').click() # Confirmar
                Browser.click_element_by_text(self.driver, '//*[@class="ui-button ui-corner-all ui-widget"]', 'Sim')
            except: 
                pass

            Browser.wait_until_clickable(self.driver, 10, 'id', 'ctl00_Conteudo_btnConfirmaTelEmail').click() # Confirmar
            
            janela_original = self.driver.current_window_handle # guarda o handle da página
            time.sleep(1)
            
            Browser.wait_alert(self.driver, 10)
            alert = self.driver.switch_to.alert # Se o alerta de sucesso não fechar sozinho, aceita
            if "Anote os" not in alert.text:
                self.retorno = 99
                raise ExpectedException(alert.text)
            alert.accept()
            
            time.sleep(1.5) # Volta pra mesma página, o que faz carregar o comprovante
            self.driver.switch_to.window(janela_original)
            time.sleep(1.5)
            try:
                # Agora fecha as janelas extras
                current_handles = self.driver.window_handles
                if len(current_handles) > 1:
                    for handle in current_handles:
                        if handle != janela_original:
                            self.driver.switch_to.window(handle)
                            self.driver.close()
                else:
                    # LOGGER.warning("Nenhuma janela extra encontrada para fechar")
                    pass
                    
            except Exception as e:
                # LOGGER.warning(f"Erro ao fechar janelas extras: {e}")
                pass

            finally:
                try: self.driver.switch_to.window(janela_original)
                except Exception as e: LOGGER.warning(f"Erro ao voltar para janela original: {e}")

        except ExpectedException as e: # Exceções esperadas
            if self.retorno in (10, 11, 12):
                LOGGER.info(f"{e} | UA {cod_ua} | Grupo {cod_grupo} | Cota {cod_cota} | Conta {conta} | {segmento}")
            else:
                LOGGER.warning(f"{e} | UA {cod_ua} | Grupo {cod_grupo} | Cota {cod_cota} | Conta {conta} | {segmento}")
            self.resultado_lance = e
            return self.retorno
        
        except Exception as e: # Erro não esperado
            try: # Caso tenha um alerta não esperado, aceita e salva o texto
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                LOGGER.warning(f"Auto-accepted unexpected alert: {alert_text}")
            except:
                pass
            
            self.resultado_lance = f"Erro inesperado ao rodar lance {tipo_lance}."
            LOGGER.critical(f"{self.resultado_lance} | UA {cod_ua} | Grupo {cod_grupo} | Cota {cod_cota} | Conta {conta} | {segmento}")
            self.driver.save_screenshot(f"{cs.PATH_LOGS}\\error_screenshot(rodar_lance)-{cod_grupo},{cod_cota}.png")

            # region Exc 9
            if "ERR_INTERNET_DISCONNECTED" in str(e): # Caiu a internet
                self.resultado_lance = "A conexão com a internet caiu."
                LOGGER.error(f"Erro no WebDriver: A conexão com a internet caiu.")
                return 9

            #region Exc 404
            # Outros erros
            self.driver.save_screenshot(f"{cs.PATH_LOGS}\\error_screenshot(rodar_lance)-{cod_grupo},{cod_cota}.png")
            LOGGER.error(f"404 - Erro no rodar_lance: {e}")
            return 404
        
        else: # Se deu tudo certo
            self.resultado_lance = f"Lance {tipo_lance} realizado com sucesso."
            LOGGER.info(f"{self.resultado_lance} | UA {cod_ua} | Grupo {cod_grupo} | Cota {cod_cota} | Conta {conta} | {segmento}")
            LOGGER.debug(f"_ Fez o lance {tipo_lance}")
            return 0


# Para fins de teste
if __name__ == '__main__':
    teste = PortalConsorcio()
    teste.login_portal({'login': ''+cs.LOGIN_RPA, 'password': ''+cs.SENHA_RPA})
    # teste.rodar_lance("260610", "010706", "799", "222646", "AUTOMOVEIS")
    # teste.rodar_lance("260610", "010706", "799", "222646", "AUTOMOVEIS", "Fixo")
    print(teste.rodar_lance("260633", "10721", "598", "363517", "AUTOMOVEIS")) # consorciado invalido
    input()
    teste.encerrar()
