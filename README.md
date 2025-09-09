## Automação de Lances de Consórcio

Este projeto realiza a automação do processo de oferta de lances em consórcios, utilizando Python, Selenium e integração com planilhas Excel para registro de logs e resultados.

### Funcionalidades

- Automatiza o acesso ao portal de consórcio e a oferta de lances (livre e fixo) para múltiplos consorciados.
- Registra logs detalhados de cada operação, incluindo erros e exceções.
- Salva os resultados em planilhas Excel para auditoria e acompanhamento.
- Permite reinicialização automática do driver em caso de falhas.
- Detecta e trata quedas de conexão com a internet.

### Estrutura do Projeto

- `app.py`: Script principal de execução da automação.
- `src/`: Módulos de funções, navegação, GUI e bases de dados.
- `logs/`: Diretório onde são salvos os logs e planilhas de resultados.
- `assets/`: Estrutura de recursos visuais e de apoio:
  - `assets/exceptions/`: Contém capturas de tela (`.png`) utilizadas para validação e tratamento de erros específicos (ex: "Consorciado inválido", "Lance fora do prazo", "Valor de lance excedido"). Esses arquivos ajudam na identificação visual dos erros exibidos no portal.
  - `assets/ajustes/`: Imagens (`.png`) e o arquivo `a_fazer.md` que documenta observações, tarefas de ajuste de interface e possíveis melhorias na automação conforme mudanças de layout do portal.
- `.env`: Variáveis de ambiente (paths, credenciais, flags).

### Módulos Principais

- `app.py`: Orquestrador principal que carrega configuração, inicia a GUI, percorre a base de consorciados e chama as rotinas de lance.
- `src/functions.py`: Funções utilitárias responsáveis por:
  - Verificar conectividade com a internet.
  - Registrar logs no Excel de forma incremental e persistente.
  - Transformar dados e tratar exceções genéricas antes do envio de lances.
- `src/navigations.py`: Implementa a classe `Browser` para inicialização e comandos do Selenium, `Logs` para configuração de logging, e `ExpectedException` para sinalizar erros parametrizados do portal.
- `src/gui.py`: Interface gráfica simples (Tkinter) para input de usuário e senha, além de feedback de status antes de iniciar a automação.
- `src/bases.py`: Leitura e validação da planilha base de consorciados (.xlsx), garantindo o formato correto e identificando entradas inválidas.

### Pré-requisitos

- Python 3.11+
- [openpyxl](https://openpyxl.readthedocs.io/)
- [Selenium](https://selenium-python.readthedocs.io/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- Edge WebDriver compatível com a versão do navegador

### Instalação

1. Clone este repositório ou copie os arquivos para o servidor desejado.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env` com os caminhos corretos para drivers, bases e logs.

### Uso

1. Execute o script principal:
   ```bash
   python app.py
   ```
2. Siga as instruções na tela para login e acompanhamento do processo.
3. Os resultados e logs serão salvos na pasta definida em `PATH_LOGS`.

### Observações

- O script salva os resultados no Excel a cada lance processado, garantindo integridade mesmo em caso de falhas de conexão.
- Em caso de muitos erros consecutivos ou queda de internet, o processo é interrompido de forma segura.
- As credenciais de acesso devem ser mantidas seguras no arquivo `.env`.

### Manutenção

- Para atualizar as bases de consorciados, substitua o arquivo Excel indicado em `PATH_BASE`.
- Para atualizar o driver, altere o caminho em `PATH_DRIVER`.

---

**
