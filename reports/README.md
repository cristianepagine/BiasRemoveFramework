# Relatórios Gerados - Análise de Viés

Este diretório contém exemplos de relatórios gerados automaticamente pelo framework de redução de viés.

## 📊 Conteúdo

### 1. Gráficos PNG (📁 graficos/)
6 gráficos em alta resolução (300 DPI):
- `03_comparacao_medias` - Comparação de médias antes vs depois
- `04_boxplot_avaliacoes` - Distribuição por tipo de avaliação
- `05_eficacia_correcao` - Eficácia da correção de viés
- `06_histograma_distribuicao` - Distribuição geral de scores
- `07_scatter_desempenho_potencial` - Nine Box (Desempenho vs Potencial)
- `08_comparativo_cenarios` - Comparação entre os 7 cenários

### 2. Relatório Excel (📁 excel/)
**Arquivo:** `relatorio_vies_20251029_194500.xlsx`

Excel formatado profissionalmente com 4 abas:
- **Resumo Executivo**: Comparação dos 7 cenários
- **Detecção de Viés**: Análise estatística com conditional formatting
- **Eficácia da Correção**: Métricas de redução de viés
- **Mudanças de Posição**: Impacto no ranking com setas ↑↓

### 3. Apresentação PowerPoint (📁 powerpoint/)
**Arquivo:** `apresentacao_vies_20251029_194500.pptx`

Apresentação completa com **37 slides**:
- Capa e agenda
- Metodologia
- 7 cenários com gráficos e tabelas individuais
- Análise comparativa
- Conclusões e recomendações

### 4. Dashboard HTML Interativo (📁 dashboards/)
**Arquivo:** `dashboard_vies_20251029_194500.html`

Dashboard interativo com:
- **7 abas** (uma para cada cenário)
- Gráficos interativos (Plotly)
- Hover com informações detalhadas
- Exportável como PDF (Ctrl+P)

**Para visualizar:** Abra o arquivo HTML em qualquer navegador moderno.

## 🎯 Os 7 Cenários

| Cenário | Correção | Diferença Médias | P-value | Status |
|---------|----------|------------------|---------|--------|
| Cenário 1 | 0% | 0.560 | < 0.0001 | ⚠️ Viés detectado |
| Cenário 2 | 17% | 0.467 | < 0.0001 | ⚠️ Viés detectado |
| Cenário 3 | 33% | 0.373 | < 0.0001 | ⚠️ Viés detectado |
| Cenário 4 | 50% | 0.280 | 0.0002 | ⚠️ Viés detectado |
| Cenário 5 | 67% | 0.187 | 0.0108 | ⚠️ Viés detectado |
| Cenário 6 | 83% | 0.094 | 0.1921 | ✅ Sem viés |
| Cenário 7 | 100% | 0.000 | 0.9970 | ✅ Sem viés |

## 🔄 Como Regenerar

Para gerar novos relatórios com dados atualizados:

```bash
python demo_relatorios.py
```

Isso criará novos arquivos com timestamp atual.

## 📦 Tamanho Total

- **Total:** 2.4 MB
- Gráficos PNG: ~1.1 MB
- PowerPoint: 936 KB
- Dashboard HTML: 328 KB
- Excel: 8.5 KB

## 🛠️ Tecnologias Utilizadas

- **Matplotlib + Seaborn**: Gráficos estáticos
- **Plotly**: Gráficos interativos
- **OpenPyXL**: Relatórios Excel
- **python-pptx**: Apresentações PowerPoint
- **Pandas**: Análise de dados
- **NumPy + SciPy**: Estatísticas

---

**Gerado em:** 29/10/2025 às 19:45
**Framework:** BiasRemoveFramework v2.0
