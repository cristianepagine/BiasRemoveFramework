"""
Script Principal - Demonstração do Framework de Redução de Viés

Este script demonstra todo o fluxo do framework:
1. Geração de dados mockados (pessoas e avaliações)
2. Detecção e remoção de outliers
3. Análise e correção de viés de gênero
4. Classificação automática da pessoa mais apta
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Pessoa, Genero
from src.utils import MockDataGenerator
from src.evaluations import (
    MockCompetenciasGenerator,
    Mock360Generator,
    MockOKRGenerator,
    MockNineBoxGenerator
)
from src.analytics import (
    OutlierDetector,
    BiasAnalyzer,
    BiasCorrector,
    RankingCalculator,
    combinar_avaliacoes_em_scores
)


def print_header(titulo: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(titulo.center(80))
    print("=" * 80 + "\n")


def print_section(titulo: str):
    """Imprime seção"""
    print("\n" + "-" * 80)
    print(titulo)
    print("-" * 80)


def main():
    """Função principal"""

    print_header("FRAMEWORK DE REDUÇÃO DE VIÉS EM PROMOÇÕES")
    print("Este framework implementa técnicas para mitigar vieses de gênero")
    print("em processos de avaliação e promoção de recursos humanos.\n")

    # ==========================================================================
    # ETAPA 1: GERAÇÃO DE DADOS MOCKADOS
    # ==========================================================================
    print_section("ETAPA 1: Geração de Dados Mockados")

    print("Gerando pessoas com hierarquia...")
    gerador_pessoas = MockDataGenerator(seed=42)
    pessoas = gerador_pessoas.gerar_pessoas(quantidade=50)

    print(f"✓ {len(pessoas)} pessoas geradas")
    print(f"  - Mulheres: {len([p for p in pessoas if p.genero == Genero.FEMININO])}")
    print(f"  - Homens: {len([p for p in pessoas if p.genero == Genero.MASCULINO])}")

    # Dicionários de lookup
    pessoas_dict = {p.id: p for p in pessoas}
    generos_dict = {p.id: p.genero for p in pessoas}

    print("\nGerando avaliações...")

    # Avaliação por Competências (COM viés introduzido)
    gerador_comp = MockCompetenciasGenerator(seed=42)
    avaliacoes_comp = gerador_comp.gerar_avaliacoes(
        pessoas,
        periodo="2024-Q1",
        introducao_vies=True,
        intensidade_vies=0.15
    )
    print(f"✓ {len(avaliacoes_comp)} avaliações por competências geradas (com viés)")

    # Avaliação 360 Graus (COM viés introduzido)
    gerador_360 = Mock360Generator(seed=42)
    avaliacoes_360 = gerador_360.gerar_avaliacoes(
        pessoas,
        todas_pessoas=pessoas,
        periodo="2024-Q1",
        introducao_vies=True,
        intensidade_vies=0.20
    )
    print(f"✓ {len(avaliacoes_360)} avaliações 360 graus geradas (com viés)")

    # Avaliação OKR (COM viés introduzido)
    gerador_okr = MockOKRGenerator(seed=42)
    avaliacoes_okr = gerador_okr.gerar_avaliacoes(
        pessoas,
        periodo="2024-Q1",
        introducao_vies=True,
        intensidade_vies=0.15
    )
    print(f"✓ {len(avaliacoes_okr)} avaliações OKR geradas (com viés)")

    # Avaliação Nine Box (usa resultados anteriores)
    gerador_ninebox = MockNineBoxGenerator(seed=42)
    avaliacao_ninebox = gerador_ninebox.gerar_avaliacao(
        pessoas,
        periodo="2024-Q1",
        avaliacoes_competencias=avaliacoes_comp,
        avaliacoes_360=avaliacoes_360,
        avaliacoes_okr=avaliacoes_okr,
        introducao_vies=True,
        intensidade_vies=0.10
    )
    print(f"✓ Avaliação Nine Box gerada com {len(avaliacao_ninebox.posicoes)} pessoas")

    # ==========================================================================
    # ETAPA 2: EXTRAÇÃO DE SCORES
    # ==========================================================================
    print_section("ETAPA 2: Extração de Scores das Avaliações")

    # Extrai scores de cada tipo de avaliação
    scores_comp = {av.pessoa_id: av.calcular_media_final() for av in avaliacoes_comp}
    scores_360 = {av.pessoa_id: av.calcular_media_geral() for av in avaliacoes_360}
    scores_okr = {av.pessoa_id: av.calcular_score_geral() * 10 for av in avaliacoes_okr}
    scores_ninebox_desemp = {pos.pessoa_id: pos.score_desempenho for pos in avaliacao_ninebox.posicoes}
    scores_ninebox_potenc = {pos.pessoa_id: pos.score_potencial for pos in avaliacao_ninebox.posicoes}

    print(f"✓ Scores extraídos de todas as avaliações")
    print(f"  - Competências: Média = {sum(scores_comp.values())/len(scores_comp):.2f}")
    print(f"  - 360 Graus: Média = {sum(scores_360.values())/len(scores_360):.2f}")
    print(f"  - OKR: Média = {sum(scores_okr.values())/len(scores_okr):.2f}")
    print(f"  - Nine Box (Desempenho): Média = {sum(scores_ninebox_desemp.values())/len(scores_ninebox_desemp):.2f}")
    print(f"  - Nine Box (Potencial): Média = {sum(scores_ninebox_potenc.values())/len(scores_ninebox_potenc):.2f}")

    # ==========================================================================
    # ETAPA 3: DETECÇÃO E REMOÇÃO DE OUTLIERS
    # ==========================================================================
    print_section("ETAPA 3: Detecção e Remoção de Outliers (Z-score)")

    detector = OutlierDetector(threshold=3.0)

    # Aplica detecção em scores de competências
    resultado_outliers = detector.detectar_outliers(list(scores_comp.values()))

    print(f"Análise de Outliers em Avaliações de Competências:")
    print(f"  - Média: {resultado_outliers.media:.2f}")
    print(f"  - Desvio Padrão: {resultado_outliers.desvio_padrao:.2f}")
    print(f"  - Outliers detectados: {len(resultado_outliers.indices_outliers)}")

    if resultado_outliers.indices_outliers:
        print(f"  - IDs removidos:", end=" ")
        ids_lista = list(scores_comp.keys())
        for idx in resultado_outliers.indices_outliers[:5]:
            print(f"{ids_lista[idx]}", end=" ")
        if len(resultado_outliers.indices_outliers) > 5:
            print(f"... (+{len(resultado_outliers.indices_outliers)-5} mais)")
        else:
            print()

        # Remove outliers
        scores_comp_limpo, _ = detector.remover_outliers(
            list(scores_comp.values()),
            resultado_outliers
        )
        print(f"  - Scores após remoção: {len(scores_comp_limpo)}")

    # ==========================================================================
    # ETAPA 4: ANÁLISE DE VIÉS DE GÊNERO
    # ==========================================================================
    print_section("ETAPA 4: Análise de Viés de Gênero")

    analyzer = BiasAnalyzer(threshold_vies=0.05, alpha=0.05)

    # Agrupa scores por gênero para análise de competências
    scores_por_genero_comp = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in scores_comp.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            scores_por_genero_comp[genero].append(score)

    # Analisa viés
    analise_vies_comp = analyzer.analisar_vies_genero(scores_por_genero_comp)

    print("\nAnálise de Competências:")
    print(f"  Média Feminino: {analise_vies_comp.estatisticas_feminino.media:.2f}")
    print(f"  Média Masculino: {analise_vies_comp.estatisticas_masculino.media:.2f}")
    print(f"  Diferença: {analise_vies_comp.diferenca_medias:.2f} ({analise_vies_comp.diferenca_percentual*100:.2f}%)")
    print(f"  P-value: {analise_vies_comp.p_value:.4f}")

    if analise_vies_comp.vies_detectado:
        print(f"  ⚠️ VIÉS DETECTADO!")
    else:
        print(f"  ✓ Sem viés significativo")

    # Análise similar para Nine Box
    scores_por_genero_nb = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in scores_ninebox_desemp.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            scores_por_genero_nb[genero].append(score)

    analise_vies_nb = analyzer.analisar_vies_genero(scores_por_genero_nb)

    print("\nAnálise de Nine Box (Desempenho):")
    print(f"  Média Feminino: {analise_vies_nb.estatisticas_feminino.media:.2f}")
    print(f"  Média Masculino: {analise_vies_nb.estatisticas_masculino.media:.2f}")
    print(f"  Diferença: {analise_vies_nb.diferenca_medias:.2f} ({analise_vies_nb.diferenca_percentual*100:.2f}%)")
    print(f"  P-value: {analise_vies_nb.p_value:.4f}")

    if analise_vies_nb.vies_detectado:
        print(f"  ⚠️ VIÉS DETECTADO!")
    else:
        print(f"  ✓ Sem viés significativo")

    # ==========================================================================
    # ETAPA 5: CORREÇÃO DE VIÉS (REPONDERAÇÃO)
    # ==========================================================================
    print_section("ETAPA 5: Correção de Viés por Reponderação")

    corrector = BiasCorrector()

    # Aplica reponderação em Nine Box (desempenho)
    resultado_repond = corrector.aplicar_reponderacao(
        scores_ninebox_desemp,
        generos_dict,
        aplicar_correcao=True
    )

    print("Reponderação aplicada:")
    print(f"  Peso ajuste Feminino: {resultado_repond.peso_ajuste_feminino:.4f}")
    print(f"  Peso ajuste Masculino: {resultado_repond.peso_ajuste_masculino:.4f}")

    if resultado_repond.analise_pos_ajuste:
        print("\nAnálise pós-correção:")
        print(f"  Média Feminino: {resultado_repond.analise_pos_ajuste.estatisticas_feminino.media:.2f}")
        print(f"  Média Masculino: {resultado_repond.analise_pos_ajuste.estatisticas_masculino.media:.2f}")
        print(f"  Diferença: {resultado_repond.analise_pos_ajuste.diferenca_medias:.2f}")
        print(f"  P-value: {resultado_repond.analise_pos_ajuste.p_value:.4f}")

        # Calcula melhoria
        diff_pre = abs(resultado_repond.analise_pre_ajuste.diferenca_percentual)
        diff_pos = abs(resultado_repond.analise_pos_ajuste.diferenca_percentual)
        melhoria = (diff_pre - diff_pos) / diff_pre * 100 if diff_pre > 0 else 0

        print(f"  ✓ Redução do viés: {melhoria:.2f}%")

    # Usa scores ajustados para próximas etapas
    scores_ninebox_desemp_ajustado = resultado_repond.scores_ajustados

    # ==========================================================================
    # ETAPA 6: CLASSIFICAÇÃO AUTOMÁTICA
    # ==========================================================================
    print_section("ETAPA 6: Classificação Automática da Pessoa Mais Apta")

    calculator = RankingCalculator()

    # Combina avaliações
    avaliacoes_combinadas, criterios = combinar_avaliacoes_em_scores(
        avaliacoes_ninebox_desempenho=scores_ninebox_desemp_ajustado,
        avaliacoes_ninebox_potencial=scores_ninebox_potenc,
        usar_ninebox=True
    )

    print(f"Critérios utilizados:")
    for criterio in criterios:
        print(f"  - {criterio.nome} (peso: {criterio.peso})")

    # Calcula ranking
    ranking = calculator.calcular_ranking(
        avaliacoes_combinadas,
        criterios,
        pessoas_dict
    )

    print(f"\nTop 10 Pessoas para Promoção:")
    print(f"{'Pos':<5} {'Nome':<25} {'Gênero':<12} {'Cargo':<20} {'Score':<10}")
    print("-" * 80)

    for score in ranking.obter_top_n(10):
        pessoa = pessoas_dict[score.pessoa_id]
        print(
            f"{score.posicao:<5} "
            f"{pessoa.nome:<25} "
            f"{pessoa.genero.value:<12} "
            f"{pessoa.cargo:<20} "
            f"{score.score_final:<10.2f}"
        )

    # ==========================================================================
    # RELATÓRIO FINAL
    # ==========================================================================
    print_section("RELATÓRIO FINAL")

    # Conta gêneros no top 10
    top_10 = ranking.obter_top_n(10)
    generos_top10 = {
        Genero.FEMININO: 0,
        Genero.MASCULINO: 0,
        Genero.OUTRO: 0
    }

    for score in top_10:
        genero = generos_dict.get(score.pessoa_id)
        if genero in generos_top10:
            generos_top10[genero] += 1

    print("Distribuição de Gênero no Top 10:")
    print(f"  - Mulheres: {generos_top10[Genero.FEMININO]} ({generos_top10[Genero.FEMININO]/10*100:.1f}%)")
    print(f"  - Homens: {generos_top10[Genero.MASCULINO]} ({generos_top10[Genero.MASCULINO]/10*100:.1f}%)")

    print("\nResumo do Framework:")
    print(f"  ✓ {len(pessoas)} pessoas avaliadas")
    print(f"  ✓ 4 tipos de avaliação aplicados")
    print(f"  ✓ Outliers detectados e removidos")
    print(f"  ✓ Viés de gênero detectado e corrigido")
    print(f"  ✓ Ranking final gerado com {len(ranking.scores)} pessoas")

    print_header("FRAMEWORK EXECUTADO COM SUCESSO!")

    print("\nPróximos passos sugeridos:")
    print("  1. Revisar o top 10 com comitê de promoção")
    print("  2. Analisar casos individuais para contexto adicional")
    print("  3. Documentar decisões e critérios utilizados")
    print("  4. Fornecer feedback detalhado para todos os avaliados")


if __name__ == "__main__":
    main()
