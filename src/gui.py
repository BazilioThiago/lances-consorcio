from telas_2606 import tela_login, tela_botoes, tela_loading, tela_mensagem # Biblioteca própria de telas
import sys
import os
if "src" not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from globals import Constants as cs

#region GUI

class Screens:

    @classmethod
    def login(cls, last_login=None, error_message=None) -> dict:
        login_info = tela_login.run(form_type="email", last_login=last_login, error_message=error_message) # Tela de Login da biblioteca telas_2606

        if not login_info:
            raise Exception("Tela de login encerrada.")
        else:
            with open(f"{cs.PATH_LOGS}\\last_email.txt", "w") as f:
                f.write(login_info['login']) # Salva o último email usado no login
                
            return login_info
        

    @classmethod
    def principal(cls) -> str:
        escolha = tela_botoes.run(["Rodar lances"]) # Tela de escolha |Lances ou |Contemplações

        if not escolha:
            raise Exception("Tela principal encerrada.")
        else:
            return escolha
        

    @classmethod
    def loading(cls, done_event, mensagem: str = "Rodando Lances..."):
        tela_loading.run(mensagem, done_event)
    

    @classmethod
    def final(cls, mensagem: str = "Lances finalizados!\nLog disponível para verificação."):
        tela_mensagem.run(mensagem)


# Para fins de teste
if __name__ == '__main__':
    Screens.login()
    print(Screens.principal())
