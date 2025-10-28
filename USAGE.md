# Guia de Uso do Framework

Este documento explica como usar o BiasRemoveFramework para testar seu framework de mestrado.

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Execução Rápida

### Script Principal (Demo Completa)

Execute o script principal para ver todo o framework em ação:

```bash
python src/main.py
```

Este script demonstra:
1. Geração de 50 pessoas com hierarquia
2. Criação de avaliações por competências, 360 graus, OKR e Nine Box
3. Detecção e remoção de outliers usando Z-score
4. Análise de viés de gênero
5. Correção de viés por reponderação
6. Classificação automática e ranking final

### Exemplos Individuais

Para ver exemplos de uso de cada módulo separadamente:

```bash
python examples.py
```

## Uso dos Módulos

### 1. Criar Pessoas com Hierarquia

```python
from src.models import Pessoa, Genero, NivelHierarquico
from src.utils import MockDataGenerator
from datetime import datetime

# Opção 1: Criar pessoa manualmente
pessoa = Pessoa(
    id="P001",
    nome="Maria Silva",
    genero=Genero.FEMININO,
    idade=32,
    cargo="Analista Senior",
    nivel_hierarquico=NivelHierarquico.SENIOR,
    departamento="Tecnologia",
    tempo_empresa=48,
    tempo_cargo_atual=18,
    salario=10000.00,
    data_admissao=datetime(2020, 1, 15)
)

# Opção 2: Gerar pessoas mockadas
gerador = MockDataGenerator(seed=42)
pessoas = gerador.gerar_pessoas(quantidade=50)
```

### 2. Criar Avaliações

#### Avaliação por Competências

```python
from src.evaluations import MockCompetenciasGenerator

gerador = MockCompetenciasGenerator(seed=42)
avaliacoes = gerador.gerar_avaliacoes(
    pessoas,
    periodo="2024-Q1",
    introducao_vies=True,  # Introduz viés para teste
    intensidade_vies=0.15   # 15% de intensidade
)

# Acessar resultados
for av in avaliacoes:
    print(f"Pessoa {av.pessoa_id}: Média = {av.calcular_media_final():.2f}")
```

#### Avaliação 360 Graus

```python
from src.evaluations import Mock360Generator

gerador = Mock360Generator(seed=42)
avaliacoes_360 = gerador.gerar_avaliacoes(
    pessoas,
    todas_pessoas=pessoas,
    periodo="2024-Q1",
    introducao_vies=True,
    intensidade_vies=0.20
)

# Acessar resultados
for av in avaliacoes_360:
    print(f"Pessoa {av.pessoa_id}: Média = {av.calcular_media_geral():.2f}")
```

#### Avaliação por OKR

```python
from src.evaluations import MockOKRGenerator

gerador = MockOKRGenerator(seed=42)
avaliacoes_okr = gerador.gerar_avaliacoes(
    pessoas,
    periodo="2024-Q1",
    introducao_vies=True,
    intensidade_vies=0.15
)

# Acessar resultados
for av in avaliacoes_okr:
    score = av.calcular_score_geral()
    print(f"Pessoa {av.pessoa_id}: Score = {score:.2f}")
```

#### Avaliação Nine Box

```python
from src.evaluations import MockNineBoxGenerator

gerador = MockNineBoxGenerator(seed=42)
avaliacao_ninebox = gerador.gerar_avaliacao(
    pessoas,
    periodo="2024-Q1",
    avaliacoes_competencias=avaliacoes_comp,
    avaliacoes_360=avaliacoes_360,
    avaliacoes_okr=avaliacoes_okr,
    introducao_vies=True,
    intensidade_vies=0.10
)

# Ver estatísticas
stats = avaliacao_ninebox.estatisticas()
print(f"Talentos críticos: {stats['talentos_criticos']}")
```

### 3. Detectar e Remover Outliers

```python
from src.analytics import OutlierDetector

# Criar detector com threshold de 3 desvios padrão
detector = OutlierDetector(threshold=3.0)

# Extrair scores
scores = [av.calcular_media_final() for av in avaliacoes]

# Detectar outliers
resultado = detector.detectar_outliers(scores)

print(f"Outliers detectados: {len(resultado.indices_outliers)}")
print(f"Média: {resultado.media:.2f}")
print(f"Desvio padrão: {resultado.desvio_padrao:.2f}")

# Remover outliers
scores_limpos, indices_removidos = detector.remover_outliers(scores, resultado)
```

### 4. Analisar Viés de Gênero

```python
from src.analytics import BiasAnalyzer
from src.models import Genero

# Agrupar scores por gênero
scores_por_genero = {
    Genero.FEMININO: [],
    Genero.MASCULINO: []
}

for av in avaliacoes:
    pessoa = pessoas_dict[av.pessoa_id]
    if pessoa.genero in [Genero.FEMININO, Genero.MASCULINO]:
        score = av.calcular_media_final()
        scores_por_genero[pessoa.genero].append(score)

# Analisar viés
analyzer = BiasAnalyzer(threshold_vies=0.05, alpha=0.05)
analise = analyzer.analisar_vies_genero(scores_por_genero)

# Ver resultados
print(f"Média Feminino: {analise.estatisticas_feminino.media:.2f}")
print(f"Média Masculino: {analise.estatisticas_masculino.media:.2f}")
print(f"Diferença: {analise.diferenca_medias:.2f}")
print(f"P-value: {analise.p_value:.4f}")
print(f"Viés detectado? {analise.vies_detectado}")

# Gerar relatório detalhado
relatorio = analyzer.gerar_relatorio_analise(analise)
print(relatorio)
```

### 5. Corrigir Viés por Reponderação

```python
from src.analytics import BiasCorrector

# Preparar dados
scores = {av.pessoa_id: av.calcular_media_final() for av in avaliacoes}
generos = {p.id: p.genero for p in pessoas}

# Aplicar correção
corrector = BiasCorrector()
resultado = corrector.aplicar_reponderacao(
    scores,
    generos,
    aplicar_correcao=True
)

print(f"Peso ajuste Feminino: {resultado.peso_ajuste_feminino:.4f}")
print(f"Peso ajuste Masculino: {resultado.peso_ajuste_masculino:.4f}")

# Scores ajustados
scores_ajustados = resultado.scores_ajustados

# Ver relatório
relatorio = corrector.gerar_relatorio_reponderacao(resultado)
print(relatorio)
```

### 6. Classificação e Ranking

```python
from src.analytics import RankingCalculator, combinar_avaliacoes_em_scores

# Preparar scores
scores_ninebox_desemp = {
    pos.pessoa_id: pos.score_desempenho
    for pos in avaliacao_ninebox.posicoes
}
scores_ninebox_potenc = {
    pos.pessoa_id: pos.score_potencial
    for pos in avaliacao_ninebox.posicoes
}

# Combinar avaliações
avaliacoes_combinadas, criterios = combinar_avaliacoes_em_scores(
    avaliacoes_ninebox_desempenho=scores_ninebox_desemp,
    avaliacoes_ninebox_potencial=scores_ninebox_potenc,
    usar_ninebox=True
)

# Calcular ranking
calculator = RankingCalculator()
pessoas_dict = {p.id: p for p in pessoas}

ranking = calculator.calcular_ranking(
    avaliacoes_combinadas,
    criterios,
    pessoas_dict
)

# Ver top 10
print("Top 10:")
for score in ranking.obter_top_n(10):
    pessoa = pessoas_dict[score.pessoa_id]
    print(f"{score.posicao}. {pessoa.nome} - Score: {score.score_final:.2f}")

# Gerar relatório
relatorio = calculator.gerar_relatorio_ranking(ranking, top_n=10)
print(relatorio)
```

## Personalização

### Ajustar Intensidade do Viés

Você pode controlar a intensidade do viés introduzido nos dados mockados:

```python
# Viés leve (5%)
avaliacoes = gerador.gerar_avaliacoes(
    pessoas,
    introducao_vies=True,
    intensidade_vies=0.05
)

# Viés moderado (15%)
avaliacoes = gerador.gerar_avaliacoes(
    pessoas,
    introducao_vies=True,
    intensidade_vies=0.15
)

# Viés forte (30%)
avaliacoes = gerador.gerar_avaliacoes(
    pessoas,
    introducao_vies=True,
    intensidade_vies=0.30
)
```

### Ajustar Threshold de Outliers

```python
# Mais conservador (detecta menos outliers)
detector = OutlierDetector(threshold=3.5)

# Padrão
detector = OutlierDetector(threshold=3.0)

# Mais agressivo (detecta mais outliers)
detector = OutlierDetector(threshold=2.5)
```

### Ajustar Sensibilidade de Viés

```python
# Mais sensível (detecta diferenças menores)
analyzer = BiasAnalyzer(threshold_vies=0.03, alpha=0.05)

# Padrão
analyzer = BiasAnalyzer(threshold_vies=0.05, alpha=0.05)

# Menos sensível
analyzer = BiasAnalyzer(threshold_vies=0.10, alpha=0.05)
```

## Exportando Dados

Para exportar dados para análise externa:

```python
import pandas as pd

# Exportar pessoas
df_pessoas = pd.DataFrame([p.to_dict() for p in pessoas])
df_pessoas.to_csv('data/pessoas.csv', index=False)

# Exportar avaliações
df_avaliacoes = pd.DataFrame([av.to_dict() for av in avaliacoes])
df_avaliacoes.to_csv('data/avaliacoes.csv', index=False)

# Exportar ranking
df_ranking = pd.DataFrame([s.to_dict() for s in ranking.scores])
df_ranking.to_csv('data/ranking.csv', index=False)
```

## Dicas para Uso no Mestrado

1. **Teste diferentes intensidades de viés** para ver como o framework se comporta
2. **Compare resultados com e sem correção** para demonstrar eficácia
3. **Varie o tamanho da amostra** (10, 50, 100, 500 pessoas) para análise estatística
4. **Documente os parâmetros** usados em cada experimento
5. **Gere visualizações** (histogramas, boxplots) usando matplotlib/seaborn
6. **Execute múltiplas vezes** com diferentes seeds para análise de robustez

## Suporte

Para questões ou problemas:
- Consulte o código fonte em `src/`
- Veja exemplos em `examples.py`
- Execute o demo completo em `src/main.py`
