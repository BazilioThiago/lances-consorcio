## Ajustes a Fazer

### Validação de Telefones Inexplicáveis [1 a 3] ✅Feito

- Verifica se o telefone está exatamente no formato `12-123456789`.
- Qualquer diferença é considerada incorreta e entrará na tabela de números para ajustar/adicionar.

### Sessão Encerrada [4] ✅Feito

- O WebDriver é resetado a cada 2 linhas com erro.
- Ao acumular 5 erros, a aplicação é encerrada.
- Se voltar a funcionar após o reset, o contador de erros é zerado.
