# BiasRemoveFramework

Framework Heurístico para Redução de Vieses em Processos de Promoção de Recursos Humanos

## Descrição

Este projeto implementa um framework para auxiliar o processo de promoção de recursos humanos, visando mitigar vieses e subjetividades de gênero inerentes aos métodos tradicionais de avaliação.

## Estrutura do Projeto

```
BiasRemoveFramework/
├── src/
│   ├── models/          # Modelos de dados (Pessoa, Hierarquia)
│   ├── evaluations/     # Modelos de avaliação (360°, Competências, OKR, Nine Box)
│   ├── analytics/       # Algoritmos de análise e correção de viés
│   └── utils/           # Utilitários e helpers
├── data/                # Dados mockados para testes
└── tests/               # Testes unitários
```

## Métodos de Avaliação Implementados

1. **Avaliação 360 Graus** - Feedback estruturado de múltiplos avaliadores
2. **Avaliação por Competências** - Baseada em habilidades e comportamentos
3. **Avaliação por OKRs** - Objectives and Key Results
4. **Método Nine Box** - Matriz de desempenho vs. potencial

## Framework de Redução de Viés

O framework implementa três etapas principais:

1. **Detecção e Remoção de Outliers** - Usando método Z-score
2. **Detecção e Correção de Viés de Gênero** - Análise de distribuição e reponderação
3. **Classificação Automática** - Identificação objetiva da pessoa mais apta

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### Executar o Framework:

```bash
python src/main.py
```

### 📊 Relatórios Automatizados (PowerPoint, Excel, Dashboard HTML):

**Opção 1: Baixar arquivos de exemplo prontos** 📥

Os arquivos já estão disponíveis em `reports/`:
- 📑 `reports/powerpoint/apresentacao_completa_exemplo.pptx` (51 slides)
- 📋 `reports/excel/relatorio_vies_exemplo.xlsx` (4 abas)
- 🌐 `reports/dashboards/dashboard_v2_exemplo.html` (Premium - 23 gráficos interativos)
- 🎨 `reports/graficos/` (42 gráficos PNG)

**Opção 2: Gerar seus próprios relatórios** 🚀

```bash
python gerar_relatorios.py
```

Este script gera automaticamente:
- ✅ **42 gráficos PNG** em alta resolução (300 DPI)
- ✅ **Apresentação PowerPoint** completa (~50 slides)
- ✅ **Relatório Excel** formatado (4 abas)
- ✅ **Dashboard HTML Premium** (23 gráficos interativos Plotly, design profissional)

**Os relatórios são salvos em:** `reports/`

## Tecnologias

- Python 3.8+
- NumPy - Cálculos numéricos
- Pandas - Manipulação de dados
- Matplotlib/Seaborn - Visualização
- SciPy - Análises estatísticas

## Licença

Veja o arquivo LICENSE para mais detalhes.
