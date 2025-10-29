"""
Exemplos de uso dos módulos do framework

Este arquivo demonstra como usar cada módulo individualmente
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import Pessoa, Genero, NivelHierarquico
from src.utils import MockDataGenerator
from src.evaluations import MockCompetenciasGenerator
from src.analytics import OutlierDetector, BiasAnalyzer, BiasCorrector
from datetime import datetime


def exemplo_criar_pessoa():
    """Exemplo: Criar uma pessoa manualmente"""
    print("\n=== Exemplo: Criar Pessoa ===")

    pessoa = Pessoa(
        id="P001",
        nome="Maria Silva",
        genero=Genero.FEMININO,
        idade=32,
        cargo="Analista Senior",
        nivel_hierarquico=NivelHierarquico.SENIOR,
        departamento="Tecnologia",
        tempo_empresa=48,  # 4 anos
        tempo_cargo_atual=18,  # 1.5 anos
        salario=10000.00,
        data_admissao=datetime(2020, 1, 15),
        email="maria.silva@empresa.com"
    )

    print(f"Pessoa criada: {pessoa.nome}")
    print(f"  - Cargo: {pessoa.cargo}")
    print(f"  - Nível: {pessoa.nivel_hierarquico.name}")
    print(f"  - Pode ser promovido? {pessoa.pode_ser_promovido()}")
    print(f"  - Próximo nível: {pessoa.proximo_nivel()}")


def exemplo_gerar_pessoas_mockadas():
    """Exemplo: Gerar pessoas mockadas"""
    print("\n=== Exemplo: Gerar Pessoas Mockadas ===")

    gerador = MockDataGenerator(seed=42)

    # Gera 20 pessoas
    pessoas = gerador.gerar_pessoas(quantidade=20)

    print(f"Geradas {len(pessoas)} pessoas:")
    print(f"  - Mulheres: {len([p for p in pessoas if p.genero == Genero.FEMININO])}")
    print(f"  - Homens: {len([p for p in pessoas if p.genero == Genero.MASCULINO])}")

    # Mostra algumas
    print("\nPrimeiras 3 pessoas:")
    for pessoa in pessoas[:3]:
        print(f"  - {pessoa.nome} ({pessoa.genero.value}) - {pessoa.cargo}")


def exemplo_avaliacao_competencias():
    """Exemplo: Criar avaliações por competências"""
    print("\n=== Exemplo: Avaliação por Competências ===")

    # Gera pessoas
    gerador_pessoas = MockDataGenerator(seed=42)
    pessoas = gerador_pessoas.gerar_pessoas(quantidade=10)

    # Gera avaliações
    gerador_comp = MockCompetenciasGenerator(seed=42)
    avaliacoes = gerador_comp.gerar_avaliacoes(
        pessoas,
        periodo="2024-Q1",
        introducao_vies=False  # Sem viés para este exemplo
    )

    print(f"Geradas {len(avaliacoes)} avaliações")

    # Mostra primeira avaliação
    av = avaliacoes[0]
    print(f"\nAvaliação de {av.pessoa_id}:")
    print(f"  - Média final: {av.calcular_media_final():.2f}")
    print(f"  - Total competências: {len(av.itens_avaliacao)}")
    print(f"  - Status: {av.status}")


def exemplo_deteccao_outliers():
    """Exemplo: Detectar outliers"""
    print("\n=== Exemplo: Detecção de Outliers ===")

    # Dados de exemplo (scores de avaliação)
    scores = [7.5, 8.0, 7.8, 8.2, 7.9, 8.1, 9.5, 7.7, 8.0, 2.0, 7.6, 8.3]

    # Cria detector
    detector = OutlierDetector(threshold=3.0)

    # Detecta outliers
    resultado = detector.detectar_outliers(scores)

    print(f"Análise de {len(scores)} scores:")
    print(f"  - Média: {resultado.media:.2f}")
    print(f"  - Desvio padrão: {resultado.desvio_padrao:.2f}")
    print(f"  - Outliers detectados: {len(resultado.indices_outliers)}")

    if resultado.indices_outliers:
        print(f"  - Valores outliers:", end=" ")
        for idx in resultado.indices_outliers:
            print(f"{scores[idx]:.2f}", end=" ")
        print()

    # Remove outliers
    scores_limpos, indices_removidos = detector.remover_outliers(scores, resultado)
    print(f"  - Scores após remoção: {len(scores_limpos)}")
    print(f"  - Nova média: {sum(scores_limpos)/len(scores_limpos):.2f}")


def exemplo_analise_vies():
    """Exemplo: Analisar viés de gênero"""
    print("\n=== Exemplo: Análise de Viés de Gênero ===")

    # Scores simulados (com viés)
    scores_por_genero = {
        Genero.FEMININO: [7.2, 7.5, 7.3, 7.8, 7.4, 7.6, 7.1],
        Genero.MASCULINO: [8.1, 8.3, 8.0, 8.5, 8.2, 8.4, 8.1]
    }

    # Analisa
    analyzer = BiasAnalyzer()
    resultado = analyzer.analisar_vies_genero(scores_por_genero)

    print("Análise de viés:")
    print(f"  - Média Feminino: {resultado.estatisticas_feminino.media:.2f}")
    print(f"  - Média Masculino: {resultado.estatisticas_masculino.media:.2f}")
    print(f"  - Diferença: {resultado.diferenca_medias:.2f}")
    print(f"  - Diferença %: {resultado.diferenca_percentual*100:.2f}%")
    print(f"  - P-value: {resultado.p_value:.4f}")
    print(f"  - Viés detectado? {resultado.vies_detectado}")


def exemplo_correcao_vies():
    """Exemplo: Corrigir viés por reponderação"""
    print("\n=== Exemplo: Correção de Viés ===")

    # Scores e gêneros
    scores = {
        "P001": 7.2,
        "P002": 8.1,
        "P003": 7.5,
        "P004": 8.3,
        "P005": 7.3,
        "P006": 8.0
    }

    generos = {
        "P001": Genero.FEMININO,
        "P002": Genero.MASCULINO,
        "P003": Genero.FEMININO,
        "P004": Genero.MASCULINO,
        "P005": Genero.FEMININO,
        "P006": Genero.MASCULINO
    }

    # Aplica correção
    corrector = BiasCorrector()
    resultado = corrector.aplicar_reponderacao(scores, generos, aplicar_correcao=True)

    print("Resultado da reponderação:")
    print(f"  - Peso Feminino: {resultado.peso_ajuste_feminino:.4f}")
    print(f"  - Peso Masculino: {resultado.peso_ajuste_masculino:.4f}")

    print("\nComparação (primeiros 3):")
    for pessoa_id in list(scores.keys())[:3]:
        score_orig = resultado.scores_originais[pessoa_id]
        score_ajust = resultado.scores_ajustados[pessoa_id]
        genero = generos[pessoa_id].value

        print(f"  {pessoa_id} ({genero}): {score_orig:.2f} → {score_ajust:.2f}")


def main():
    """Executa todos os exemplos"""
    print("=" * 80)
    print("EXEMPLOS DE USO DO FRAMEWORK".center(80))
    print("=" * 80)

    exemplo_criar_pessoa()
    exemplo_gerar_pessoas_mockadas()
    exemplo_avaliacao_competencias()
    exemplo_deteccao_outliers()
    exemplo_analise_vies()
    exemplo_correcao_vies()

    print("\n" + "=" * 80)
    print("Todos os exemplos executados com sucesso!".center(80))
    print("=" * 80)


if __name__ == "__main__":
    main()
