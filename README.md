# Gerenciador de Empréstimos - AgPay

Um sistema para gerenciamento de empréstimos pessoais com cálculo automático de juros e controle de pagamentos.

## Funcionalidades Principais

- 🤑 **Cadastro de Empréstimos**
  - Nome do cliente
  - Valor do empréstimo
  - Taxa de juros (%)
  - Período de pagamento (dias)
  
- 📅 **Gestão de Pagamentos**
  - Data do empréstimo
  - Data do próximo pagamento
  - Destaque vermelho para pagamentos atrasados
  
- 📊 **Cálculos Automáticos**
  - Valor total a pagar (valor + juros)
  - Atualização automática de status
  
- 📁 **Operações Básicas**
  - Adicionar/Editar/Excluir registros
  - Exportar dados para CSV
  - Pesquisa rápida

## Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas:
  ```bash
  tkinter
  sqlite3
  csv
  datetime
