# Relatórios Gerados Automaticamente

Este diretório contém todos os relatórios gerados automaticamente pelo framework BiasRemoveFramework.

## ⚠️ IMPORTANTE: Como Gerar os Relatórios

**Os arquivos PowerPoint, Excel e Dashboard HTML NÃO estão no Git** (para evitar corrupção).
Você precisa **gerá-los localmente** na sua máquina.

### 🚀 Geração Rápida (Recomendado):

```bash
# Na raiz do projeto, execute:
python gerar_relatorios.py
```

Este script irá gerar **TODOS** os relatórios automaticamente!

### 📋 Pré-requisitos:

```bash
# Certifique-se de ter as dependências instaladas:
pip install -r requirements.txt
```

## 📊 Estrutura dos Relatórios

### 🎨 Gráficos PNG (`graficos/`)
- **42 gráficos** em alta resolução (300 DPI)
- Organizados por cenário: `cenario_1/` até `cenario_7/`
- **6 tipos de gráficos por cenário:**
  1. Comparação de médias
  2. Boxplot de avaliações
  3. Eficácia da correção
  4. Histograma de distribuição
  5. Scatter plot desempenho vs potencial
  6. Comparativo de cenários

### 📑 Apresentação PowerPoint (`powerpoint/`)
- **Apresentação completa** com ~51 slides
- **Estrutura:**
  - Slide de capa profissional
  - Slide de índice
  - Para cada cenário: 1 slide de introdução + 6 slides com gráficos
- **Formato:** Microsoft PowerPoint 2007+ (.pptx)
- **Tamanho:** ~6.1 MB

### 📋 Relatório Excel (`excel/`)
- **4 abas formatadas:**
  1. **Resumo Executivo** - Visão geral dos 7 cenários
  2. **Detecção de Viés** - Análise estatística detalhada
  3. **Eficácia da Correção** - Antes e depois da correção
  4. **Mudanças de Posição** - Ranking comparativo
- **Formato:** Microsoft Excel 2007+ (.xlsx)
- **Tamanho:** ~8 KB

### 🌐 Dashboard HTML (`dashboards/`)
- **Dashboard interativo** com 7 abas (uma por cenário)
- **Gráficos interativos** usando Plotly
- **Exportável como PDF:** Abra no navegador e use Ctrl+P > Salvar como PDF
- **Formato:** HTML5 com JavaScript embutido
- **Tamanho:** ~328 KB

## 📖 Cenários Analisados

### Lógica INVERTIDA (Correta):
- **Cenário 1:** SEM VIÉS (baseline limpo - Diferença=0.000, p-value>0.05)
- **Cenários 2-7:** COM VIÉS PROGRESSIVO
  - Cenário 2: 17% de viés
  - Cenário 3: 33% de viés
  - Cenário 4: 50% de viés
  - Cenário 5: 67% de viés ⚠️
  - Cenário 6: 83% de viés ⚠️
  - Cenário 7: 100% de viés (máximo) ⚠️

## 🔧 Como Usar

### PowerPoint
```bash
# Baixe o arquivo .pptx e abra com:
# - Microsoft PowerPoint 2007+
# - LibreOffice Impress
# - Google Slides (fazer upload)
```

### Excel
```bash
# Baixe o arquivo .xlsx e abra com:
# - Microsoft Excel 2007+
# - LibreOffice Calc
# - Google Sheets (fazer upload)
```

### Dashboard HTML
```bash
# Baixe o arquivo .html e:
# 1. Abra diretamente no navegador (Chrome, Firefox, Edge, Safari)
# 2. Para exportar como PDF: Ctrl+P > Salvar como PDF
```

### Gráficos PNG
```bash
# Os gráficos PNG podem ser:
# - Visualizados em qualquer visualizador de imagens
# - Inseridos em documentos (Word, Google Docs, etc.)
# - Usados em apresentações
# - Impressos em alta qualidade (300 DPI)
```

## 🔍 Verificação de Integridade

Se os arquivos não abrirem corretamente:

1. **Verifique o tamanho do arquivo:**
   - PowerPoint: ~6 MB
   - Excel: ~8 KB
   - Dashboard HTML: ~300 KB

2. **Verifique a extensão:**
   - `.pptx` para PowerPoint
   - `.xlsx` para Excel
   - `.html` para Dashboard
   - `.png` para gráficos

3. **Baixe novamente:**
   - Às vezes o download pode ser interrompido
   - Certifique-se de que o arquivo foi baixado completamente

4. **Use um software compatível:**
   - PowerPoint/Excel: Microsoft Office 2007+ ou LibreOffice
   - Dashboard: Navegador moderno (Chrome, Firefox, Edge, Safari)

## 🚀 Regenerar Relatórios

Para regenerar todos os relatórios:

```bash
# Execute o script de demonstração
python demo_relatorios.py

# Os relatórios serão gerados em:
# - reports/graficos/
# - reports/powerpoint/
# - reports/excel/
# - reports/dashboards/
```

## 📝 Notas Técnicas

- **Gráficos:** Gerados com Matplotlib/Seaborn em 300 DPI
- **PowerPoint:** Gerado com python-pptx
- **Excel:** Gerado com openpyxl
- **Dashboard:** Gerado com Plotly
- **Git:** Arquivos binários (.pptx, .xlsx, .png) são tratados corretamente pelo Git através do `.gitattributes`

## ⚠️ Importante

**TODOS os arquivos foram gerados com o framework REAL**, usando:
- MockDataGenerator (50 pessoas)
- MockCompetenciasGenerator (avaliações de competências)
- Mock360Generator (avaliações 360 graus)
- MockOKRGenerator (avaliações OKR)
- MockNineBoxGenerator (matriz nine box)
- BiasAnalyzer (detecção de viés)
- BiasCorrector (correção por reponderação)

Os dados são **mock** (simulados), mas o processo é **real** e representa exatamente como o framework funciona em produção.

---

**Gerado automaticamente pelo BiasRemoveFramework**
