"""
Pacote Principal do Projeto de Análise PS2.

Este pacote contém todos os módulos necessários para ler,
processar e visualizar dados dos ficheiros .ps2.

Módulos disponíveis:
- `leitura`: Responsável pela extração de dados brutos.
- `processamento`: Responsável pela introdução dos dados em listas de dicionarios.
- `validacao`: Responsável pela analíse dos dados e identificação de ficheiros com dados inválidos.
"""

from .leitura_ps2 import ler_ficheiro_ps2, ler_ficheiros_ps2

from .validacao_ps2 import validar_dados

from .processamento import converterParaPandas