# Módulo de Relatórios e Visualizações

Este módulo fornece ferramentas para gerar relatórios e visualizações automatizadas a partir dos dados do framework de redução de viés.

## Componentes

### 1. GraphGenerator - Gráficos PNG em Alta Resolução

Gera 8 gráficos essenciais automaticamente:

1. **Distribuição de scores por gênero (antes da correção)** - Violin plot
2. **Distribuição de scores por gênero (depois da correção)** - Violin plot
3. **Comparação de médias (antes vs depois)** - Gráfico de barras
4. **Boxplot de scores por tipo de avaliação**
5. **Eficácia da correção de viés** - Gráficos comparativos
6. **Histograma de distribuição de scores**
7. **Scatter plot desempenho vs potencial** - Nine Box
8. **Comparativo entre cenários** - Gráfico de barras agrupadas

**Características:**
- Alta resolução (300 DPI por padrão)
- Formato PNG
- Totalmente customizável
- Estatísticas integradas

**Exemplo de uso:**
```python
from src.reports import GraphGenerator

generator = GraphGenerator(output_dir="reports/graficos", dpi=300)

dados = {
    'scores_antes_por_genero': {'Feminino': [...], 'Masculino': [...]},
    'scores_depois_por_genero': {'Feminino': [...], 'Masculino': [...]},
    'medias_antes': {'Feminino': 7.2, 'Masculino': 7.8},
    'medias_depois': {'Feminino': 7.5, 'Masculino': 7.5},
    # ... outros dados
}

graficos = generator.gerar_todos_graficos(dados)
```

### 2. ExcelReportGenerator - Relatórios Excel Formatados

Gera relatórios Excel profissionais com 4 abas:

1. **Resumo Executivo** - Comparação dos 3 cenários
2. **Detecção de Viés** - Com conditional formatting
3. **Eficácia da Correção** - Percentuais em verde/vermelho
4. **Mudanças de Posição** - Com setas ↑↓

**Características:**
- Formatação profissional (cores, negrito, bordas)
- Conditional formatting automático
- Headers destacados
- Largura de colunas ajustada automaticamente
- Suporta openpyxl e xlsxwriter

**Exemplo de uso:**
```python
from src.reports import ExcelReportGenerator

generator = ExcelReportGenerator(output_dir="reports/excel")

dados = {
    'resumo_executivo': {...},
    'deteccao_vies': df_deteccao,
    'eficacia_correcao': df_eficacia,
    'mudancas_posicao': df_mudancas
}

caminho = generator.gerar_relatorio_completo(dados)
```

### 3. PowerPointGenerator - Apresentações Automatizadas

Gera apresentações PowerPoint completas com 15-20 slides:

- Slide de capa
- Agenda
- Metodologia
- Slides para cada cenário (com gráficos e tabelas)
- Análise comparativa
- Conclusões
- Recomendações
- Slide final

**Características:**
- Design profissional
- Gráficos PNG embedados
- Tabelas formatadas
- Cores corporativas customizáveis
- Bullet points automáticos

**Exemplo de uso:**
```python
from src.reports import PowerPointGenerator

generator = PowerPointGenerator(output_dir="reports/powerpoint")

caminho = generator.gerar_apresentacao_completa(
    graficos=lista_graficos,
    tabelas=dict_tabelas,
    dados_cenarios=dados
)
```

### 4. DashboardGenerator - Dashboards HTML Interativos

Gera dashboards HTML interativos com Plotly:

- 3 abas (uma para cada cenário)
- Gráficos interativos com hover
- Design responsivo
- Exportável como PDF
- Navegação por abas

**Características:**
- Gráficos interativos (Plotly)
- Hover com informações detalhadas
- Design moderno e responsivo
- Exportação para PDF (via impressão do navegador)
- Totalmente autocontido (CSS inline)

**Exemplo de uso:**
```python
from src.reports import DashboardGenerator

generator = DashboardGenerator(output_dir="reports/dashboards")

dados_cenarios = {
    'cenario_1': {...},
    'cenario_2': {...},
    'cenario_3': {...}
}

caminho = generator.gerar_dashboard_completo(dados_cenarios)
```

## Instalação de Dependências

```bash
pip install -r requirements.txt
```

Dependências necessárias:
- `matplotlib>=3.7.0` - Gráficos estáticos
- `seaborn>=0.12.0` - Visualizações estatísticas
- `openpyxl>=3.1.0` - Excel com formatação
- `xlsxwriter>=3.1.0` - Excel alternativo
- `python-pptx>=0.6.21` - PowerPoint
- `plotly>=5.14.0` - Gráficos interativos
- `kaleido>=0.2.1` - Exportação de gráficos Plotly

## Demonstração Completa

Execute o script de demonstração para ver todos os módulos em ação:

```bash
python demo_relatorios.py
```

Isso irá:
1. Gerar dados de exemplo
2. Criar 3 cenários de análise
3. Gerar todos os 8 gráficos PNG
4. Criar relatório Excel completo
5. Gerar apresentação PowerPoint
6. Criar dashboard HTML interativo

Todos os arquivos serão salvos em `reports/`.

## Estrutura de Diretórios

```
reports/
├── graficos/          # Gráficos PNG
├── excel/             # Relatórios Excel
├── powerpoint/        # Apresentações PPTX
└── dashboards/        # Dashboards HTML
```

## Formato de Dados

### Para Gráficos

```python
dados_completos = {
    'scores_antes_por_genero': {
        'Feminino': [7.2, 7.5, 7.3, ...],
        'Masculino': [7.8, 8.1, 8.0, ...]
    },
    'scores_depois_por_genero': {...},
    'medias_antes': {'Feminino': 7.2, 'Masculino': 7.8},
    'medias_depois': {'Feminino': 7.5, 'Masculino': 7.5},
    'scores_por_tipo': {
        'Competências': [...],
        '360 Graus': [...],
        'OKR': [...],
        'Nine Box': [...]
    },
    'diferenca_antes': 0.6,
    'diferenca_depois': 0.0,
    'p_value_antes': 0.001,
    'p_value_depois': 0.456,
    'todos_scores': [...],
    'desempenho': [...],
    'potencial': [...],
    'generos': ['Feminino', 'Masculino', ...],
    'cenarios': {
        'Cenário 1': {'Métrica 1': valor, ...},
        'Cenário 2': {...},
        'Cenário 3': {...}
    }
}
```

### Para Excel

```python
dados_excel = {
    'resumo_executivo': {
        'Cenário 1': {
            'Média Feminino': 7.2,
            'Média Masculino': 7.8,
            'Diferença': 0.6,
            'P-value': 0.001,
            'Viés Detectado': 'Sim'
        },
        ...
    },
    'deteccao_vies': DataFrame(...),
    'eficacia_correcao': DataFrame(...),
    'mudancas_posicao': DataFrame(...)
}
```

## Customização

### Cores

Você pode customizar as cores nos geradores:

```python
# Dashboard
generator = DashboardGenerator()
generator.cores = {
    'feminino': '#FF1493',
    'masculino': '#1E90FF',
    'positivo': '#32CD32',
    'negativo': '#DC143C'
}

# PowerPoint
generator = PowerPointGenerator()
generator.cor_primaria = RGBColor(54, 96, 146)
generator.cor_secundaria = RGBColor(79, 129, 189)
```

### Resolução dos Gráficos

```python
# Baixa resolução (tela)
generator = GraphGenerator(dpi=100)

# Alta resolução (impressão)
generator = GraphGenerator(dpi=300)

# Altíssima resolução (publicação)
generator = GraphGenerator(dpi=600)
```

## Dicas de Uso

1. **Gere os gráficos primeiro** - Use os PNGs nas outras ferramentas
2. **Organize por timestamp** - Todos os geradores usam timestamp nos nomes
3. **Use dados reais** - Os exemplos são apenas demonstração
4. **Customize as cores** - Adapte às cores da sua organização
5. **Teste a exportação PDF** - Dashboard HTML pode ser exportado via impressão

## Troubleshooting

### Erro ao salvar PNG
- Certifique-se de que o diretório existe
- Verifique permissões de escrita

### Excel não abre
- Instale `openpyxl`: `pip install openpyxl`
- Verifique se o arquivo não está aberto em outro programa

### PowerPoint sem gráficos
- Verifique se os caminhos dos PNGs estão corretos
- Certifique-se de que os arquivos existem

### Dashboard não carrega
- Abra com um navegador moderno (Chrome, Firefox, Edge)
- Verifique a conexão com CDN do Plotly
- Para uso offline, baixe o plotly.js localmente

## Suporte

Para problemas ou dúvidas:
1. Verifique os exemplos em `demo_relatorios.py`
2. Consulte a documentação inline dos métodos
3. Execute os testes unitários (quando disponíveis)

## Licença

Este módulo faz parte do Framework de Redução de Viés em Avaliações de RH.
