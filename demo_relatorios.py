"""
Script de Demonstração - Geração de Relatórios Automatizados

Este script demonstra o uso dos módulos de relatórios:
1. Gráficos PNG em alta resolução
2. Relatórios Excel formatados
3. Apresentações PowerPoint
4. Dashboards HTML interativos
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import Pessoa, Genero
from src.utils import MockDataGenerator
from src.evaluations import (
    MockCompetenciasGenerator,
    Mock360Generator,
    MockOKRGenerator,
    MockNineBoxGenerator
)
from src.analytics import (
    BiasAnalyzer,
    BiasCorrector,
    OutlierDetector
)
from src.reports import (
    GraphGenerator,
    ExcelReportGenerator
)
from src.reports.dashboard_generator_v2 import DashboardGeneratorV2
from src.reports.ppt_generator_v3 import PowerPointGeneratorV3


def preparar_dados_exemplo():
    """Prepara dados de exemplo para os relatórios"""
    print("\n" + "=" * 80)
    print("PREPARANDO DADOS DE EXEMPLO".center(80))
    print("=" * 80 + "\n")

    # Gera pessoas
    gerador_pessoas = MockDataGenerator(seed=42)
    pessoas = gerador_pessoas.gerar_pessoas(quantidade=50)
    print(f"✓ {len(pessoas)} pessoas geradas")

    # Dicionários de lookup
    generos_dict = {p.id: p.genero for p in pessoas}

    # Gera avaliações com viés
    gerador_comp = MockCompetenciasGenerator(seed=42)
    avaliacoes_comp = gerador_comp.gerar_avaliacoes(
        pessoas, periodo="2024-Q1",
        introducao_vies=True, intensidade_vies=0.15
    )

    gerador_360 = Mock360Generator(seed=42)
    avaliacoes_360 = gerador_360.gerar_avaliacoes(
        pessoas, todas_pessoas=pessoas, periodo="2024-Q1",
        introducao_vies=True, intensidade_vies=0.20
    )

    gerador_okr = MockOKRGenerator(seed=42)
    avaliacoes_okr = gerador_okr.gerar_avaliacoes(
        pessoas, periodo="2024-Q1",
        introducao_vies=True, intensidade_vies=0.15
    )

    gerador_ninebox = MockNineBoxGenerator(seed=42)
    avaliacao_ninebox = gerador_ninebox.gerar_avaliacao(
        pessoas, periodo="2024-Q1",
        avaliacoes_competencias=avaliacoes_comp,
        avaliacoes_360=avaliacoes_360,
        avaliacoes_okr=avaliacoes_okr,
        introducao_vies=True, intensidade_vies=0.10
    )

    print(f"✓ Avaliações geradas\n")

    # Extrai scores
    scores_ninebox = {pos.pessoa_id: pos.score_desempenho for pos in avaliacao_ninebox.posicoes}
    scores_potencial = {pos.pessoa_id: pos.score_potencial for pos in avaliacao_ninebox.posicoes}

    return pessoas, generos_dict, scores_ninebox, scores_potencial, avaliacao_ninebox


def detectar_e_remover_outliers(scores, generos_dict, threshold=2.0):
    """
    ETAPA 1: Detecção e Remoção de Outliers usando Z-score

    Esta etapa é crucial para garantir a qualidade dos dados antes da análise de viés.
    Outliers podem distorcer as estatísticas e levar a conclusões incorretas.

    Args:
        scores: Dicionário {pessoa_id: score}
        generos_dict: Dicionário {pessoa_id: genero}
        threshold: Limite de Z-score (padrão: 2.0)

    Returns:
        Tupla (scores_limpos, resultado_detecao, info_outliers)
    """
    print("=" * 80)
    print("ETAPA 1: DETECÇÃO DE OUTLIERS (Z-SCORE)".center(80))
    print("=" * 80 + "\n")
    print(f"Threshold: |Z| > {threshold} (valores que se afastam mais de {threshold} desvios padrão)\n")

    detector = OutlierDetector(threshold=threshold)

    # Extrai valores dos scores
    ids = list(scores.keys())
    valores = list(scores.values())

    # Detecta outliers
    resultado = detector.detectar_outliers(valores)

    print(f"📊 Estatísticas dos dados originais:")
    print(f"  Total de observações: {len(valores)}")
    print(f"  Média: {resultado.media:.2f}")
    print(f"  Desvio Padrão: {resultado.desvio_padrao:.2f}")
    print(f"  Outliers detectados: {len(resultado.indices_outliers)}")

    if resultado.indices_outliers:
        print(f"\n⚠️  Outliers identificados (índices): {resultado.indices_outliers[:10]}")
        if len(resultado.indices_outliers) > 10:
            print(f"     ... e mais {len(resultado.indices_outliers) - 10}")

        # Mostra alguns exemplos
        print(f"\n  Exemplos de Z-scores extremos:")
        z_sorted_idx = np.argsort(np.abs(resultado.z_scores))[::-1]
        for i in range(min(5, len(resultado.indices_outliers))):
            idx = z_sorted_idx[i]
            if idx in resultado.indices_outliers:
                pessoa_id = ids[idx]
                genero = generos_dict.get(pessoa_id, "?")
                print(f"    Pessoa {pessoa_id} ({genero.value if hasattr(genero, 'value') else genero}): "
                      f"Score={valores[idx]:.2f}, Z-score={resultado.z_scores[idx]:.2f}")
    else:
        print(f"\n✅ Nenhum outlier detectado!")

    # Remove outliers
    scores_limpos = {}
    ids_removidos = []

    for i, pessoa_id in enumerate(ids):
        if i in resultado.indices_outliers:
            ids_removidos.append(pessoa_id)
        else:
            scores_limpos[pessoa_id] = scores[pessoa_id]

    # Informações sobre outliers por gênero
    outliers_por_genero = {
        Genero.FEMININO: 0,
        Genero.MASCULINO: 0,
        Genero.OUTRO: 0
    }

    for pessoa_id in ids_removidos:
        genero = generos_dict.get(pessoa_id)
        if genero in outliers_por_genero:
            outliers_por_genero[genero] += 1

    print(f"\n📋 Resultado da limpeza:")
    print(f"  Observações mantidas: {len(scores_limpos)}")
    print(f"  Observações removidas: {len(ids_removidos)}")
    print(f"  Taxa de remoção: {len(ids_removidos)/len(scores)*100:.1f}%")

    if ids_removidos:
        print(f"\n  Outliers por gênero:")
        print(f"    Feminino: {outliers_por_genero[Genero.FEMININO]}")
        print(f"    Masculino: {outliers_por_genero[Genero.MASCULINO]}")
        if outliers_por_genero[Genero.OUTRO] > 0:
            print(f"    Outro: {outliers_por_genero[Genero.OUTRO]}")

    print(f"\n✓ Detecção de outliers concluída!\n")

    info_outliers = {
        'total_original': len(scores),
        'total_limpo': len(scores_limpos),
        'outliers_removidos': len(ids_removidos),
        'ids_removidos': ids_removidos,
        'outliers_por_genero': outliers_por_genero,
        'media_original': resultado.media,
        'desvio_original': resultado.desvio_padrao,
        'threshold': threshold,
        'z_scores': resultado.z_scores,
        'indices_outliers': resultado.indices_outliers
    }

    return scores_limpos, resultado, info_outliers


def gerar_cenarios(scores, generos_dict):
    """
    ETAPA 2: Gera os 7 cenários de análise - BIDIRECIONAL

    Cenários demonstram detecção de viés em AMBAS as direções:
    - Cenário 1: SEM viés (baseline)
    - Cenários 2-4: Viés CONTRA mulheres (homens favorecidos)
    - Cenários 5-7: Viés CONTRA homens (mulheres favorecidas)

    IMPORTANTE: Esta função recebe scores já limpos de outliers!
    """
    print("=" * 80)
    print("ETAPA 2: GERANDO 7 CENÁRIOS DE ANÁLISE BIDIRECIONAL".center(80))
    print("=" * 80 + "\n")
    print("NOTA: Cenário 1 = SEM viés (baseline equitativo)")
    print("      Cenários 2-4 = Viés CONTRA mulheres (homens favorecidos)")
    print("      Cenários 5-7 = Viés CONTRA homens (mulheres favorecidas)")
    print("      Dados já passaram por limpeza de outliers (Etapa 1)\n")

    analyzer = BiasAnalyzer(threshold_vies=0.05, alpha=0.05)
    corrector = BiasCorrector()

    # Primeiro, REMOVE qualquer viés existente para criar baseline limpo
    resultado_limpeza = corrector.aplicar_reponderacao(
        scores, generos_dict, aplicar_correcao=True
    )
    scores_limpos = resultado_limpeza.scores_ajustados

    # Agrupa scores limpos por gênero
    scores_por_genero_limpos = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in scores_limpos.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            scores_por_genero_limpos[genero].append(score)

    # Analisa scores limpos
    analise_limpos = analyzer.analisar_vies_genero(scores_por_genero_limpos)

    # Define 7 cenários BIDIRECIONAIS
    cenarios = {}

    # Configuração dos cenários:
    # (direção_viés, intensidade_percentual, título, descrição)
    configuracoes_cenarios = [
        (None, 0, 'Sem Viés (Baseline)', 'Dados equitativos sem viés de gênero - estado ideal'),
        ('contra_mulheres', 8, 'Viés Leve contra Mulheres', 'Homens recebem avaliações 8% superiores'),
        ('contra_mulheres', 15, 'Viés Moderado contra Mulheres', 'Homens recebem avaliações 15% superiores'),
        ('contra_mulheres', 25, 'Viés Severo contra Mulheres', 'Homens recebem avaliações 25% superiores'),
        ('contra_homens', 8, 'Viés Leve contra Homens', 'Mulheres recebem avaliações 8% superiores'),
        ('contra_homens', 15, 'Viés Moderado contra Homens', 'Mulheres recebem avaliações 15% superiores'),
        ('contra_homens', 25, 'Viés Severo contra Homens', 'Mulheres recebem avaliações 25% superiores'),
    ]

    for idx, (direcao, intensidade, titulo_base, descricao) in enumerate(configuracoes_cenarios, 1):
        scores_por_genero_cenario = {
            Genero.FEMININO: [],
            Genero.MASCULINO: []
        }

        for pessoa_id, score_limpo in scores_limpos.items():
            genero = generos_dict.get(pessoa_id)
            if genero in [Genero.FEMININO, Genero.MASCULINO]:

                if direcao is None:
                    # Cenário 1: sem viés (usa score limpo)
                    score_final = score_limpo
                elif direcao == 'contra_mulheres':
                    # Reduz scores femininos, mantém masculinos
                    if genero == Genero.FEMININO:
                        score_final = score_limpo * (1 - intensidade / 100.0)
                    else:
                        score_final = score_limpo
                else:  # contra_homens
                    # Reduz scores masculinos, mantém femininos
                    if genero == Genero.MASCULINO:
                        score_final = score_limpo * (1 - intensidade / 100.0)
                    else:
                        score_final = score_limpo

                scores_por_genero_cenario[genero].append(score_final)

        # Converte para strings
        scores_por_genero_str = {
            'Feminino': scores_por_genero_cenario[Genero.FEMININO],
            'Masculino': scores_por_genero_cenario[Genero.MASCULINO]
        }

        # Analisa
        analise_cenario = analyzer.analisar_vies_genero(scores_por_genero_cenario)

        # Define título e detalhes
        titulo = f'Cenário {idx} - {titulo_base}'

        # Imprime resultados
        print(f"{titulo}")
        print(f"  Descrição: {descricao}")
        print(f"  Média Feminino: {analise_cenario.estatisticas_feminino.media:.2f}")
        print(f"  Média Masculino: {analise_cenario.estatisticas_masculino.media:.2f}")
        print(f"  Diferença: {analise_cenario.diferenca_medias:.3f}")
        print(f"  P-value: {analise_cenario.p_value:.4f}")
        if analise_cenario.vies_detectado:
            print(f"  Status: ⚠️ VIÉS DETECTADO\n")
        else:
            print(f"  Status: ✅ SEM VIÉS\n")

        cenarios[f'cenario_{idx}'] = {
            'numero': idx,
            'titulo': titulo,
            'descricao': descricao,
            'nivel_vies': intensidade,  # Intensidade do viés aplicado
            'direcao_vies': direcao,  # Direção do viés (contra_mulheres/contra_homens/None)
            'scores_por_genero': scores_por_genero_str,
            'media_feminino': analise_cenario.estatisticas_feminino.media,  # Para dashboard
            'media_masculino': analise_cenario.estatisticas_masculino.media,  # Para dashboard
            'diferenca': analise_cenario.diferenca_medias,  # Para dashboard
            'p_value': analise_cenario.p_value,  # Para dashboard
            'medias_antes': {
                'Feminino': analise_limpos.estatisticas_feminino.media,
                'Masculino': analise_limpos.estatisticas_masculino.media
            },
            'medias_depois': {
                'Feminino': analise_cenario.estatisticas_feminino.media,
                'Masculino': analise_cenario.estatisticas_masculino.media
            },
            'diferenca_antes': analise_limpos.diferenca_medias,
            'diferenca_depois': analise_cenario.diferenca_medias,
            'p_value_antes': analise_limpos.p_value,
            'p_value_depois': analise_cenario.p_value,
            'todos_scores': scores_por_genero_str['Feminino'] + scores_por_genero_str['Masculino'],
            'vies_detectado': analise_cenario.vies_detectado
        }

    return cenarios, analise_limpos, analise_cenario


def demo_graficos(cenarios):
    """Demonstra geração de gráficos - TODOS os 8 gráficos para CADA cenário"""
    print("\n" + "=" * 80)
    print("DEMO 1: GRÁFICOS PNG EM ALTA RESOLUÇÃO (56 GRÁFICOS TOTAIS)".center(80))
    print("=" * 80 + "\n")
    print("Gerando 8 gráficos para cada um dos 7 cenários...\n")

    todos_graficos = {}

    for key, dados_cenario in cenarios.items():
        num_cenario = int(key.split('_')[1])
        print(f"\n--- Gerando gráficos para {dados_cenario['titulo']} ---")

        # Cria subpasta para este cenário
        generator = GraphGenerator(output_dir=f"reports/graficos/cenario_{num_cenario}", dpi=300)

        # Prepara dados completos para este cenário
        dados = dados_cenario.copy()

        # Adiciona dados adicionais necessários
        dados['desempenho'] = dados['todos_scores'][:25]
        dados['potencial'] = list(np.random.uniform(5, 9, 25))
        dados['generos'] = ['Feminino' if i % 2 == 0 else 'Masculino' for i in range(25)]

        dados['scores_por_tipo'] = {
            'Competências': list(np.random.uniform(6, 9, 30)),
            '360 Graus': list(np.random.uniform(5, 8, 30)),
            'OKR': list(np.random.uniform(7, 9, 30)),
            'Nine Box': dados['todos_scores'][:30]
        }

        # Comparativo deste cenário específico
        dados['cenarios'] = {
            dados_cenario['titulo']: {
                'Diferença Médias': abs(dados_cenario['diferenca_depois']),
                'P-value': dados_cenario['p_value_depois']
            }
        }

        # Gera todos os 8 gráficos para este cenário
        graficos_cenario = generator.gerar_todos_graficos(dados)

        todos_graficos[key] = graficos_cenario

        print(f"✓ {len(graficos_cenario)} gráficos gerados para Cenário {num_cenario}")

    total_graficos = sum(len(g) for g in todos_graficos.values())
    print(f"\n✓ TOTAL: {total_graficos} gráficos gerados em alta resolução!")
    print(f"  Localização: reports/graficos/cenario_*/")

    return todos_graficos


def demo_excel(cenarios):
    """Demonstra geração de Excel"""
    print("\n" + "=" * 80)
    print("DEMO 2: RELATÓRIOS EXCEL FORMATADOS".center(80))
    print("=" * 80 + "\n")

    generator = ExcelReportGenerator(output_dir="reports/excel")

    # Prepara dados para as abas

    # Aba 1: Resumo Executivo - Gera dinamicamente para todos os cenários
    resumo_executivo = {}
    for key, dados in cenarios.items():
        resumo_executivo[dados['titulo']] = {
            'Média Feminino': dados['medias_depois']['Feminino'],
            'Média Masculino': dados['medias_depois']['Masculino'],
            'Diferença': dados['diferenca_depois'],
            'P-value': dados['p_value_depois'],
            'Viés Detectado': 'Sim' if dados['p_value_depois'] < 0.05 else 'Não'
        }

    # Aba 2: Detecção de Viés
    deteccao_vies = pd.DataFrame([
        {
            'Tipo_Avaliacao': 'Competências',
            'Genero': 'Feminino',
            'N_Amostras': 25,
            'Media': 7.2,
            'Desvio_Padrao': 0.8,
            'Diferenca_Percentual': '-7.8%',
            'P_value': 0.012,
            'Vies_Detectado': 'Sim'
        },
        {
            'Tipo_Avaliacao': 'Nine Box',
            'Genero': 'Feminino',
            'N_Amostras': 25,
            'Media': 7.5,
            'Desvio_Padrao': 0.9,
            'Diferenca_Percentual': '-4.2%',
            'P_value': 0.045,
            'Vies_Detectado': 'Sim'
        }
    ])

    # Aba 3: Eficácia da Correção
    eficacia_correcao = pd.DataFrame([
        {
            'Tipo_Avaliacao': 'Competências',
            'Diferenca_Antes': 0.6,
            'Diferenca_Depois': 0.15,
            'Reducao_Absoluta': 0.45,
            'Reducao_Percentual': '75.0%',
            'Eficacia': 'Alta'
        },
        {
            'Tipo_Avaliacao': 'Nine Box',
            'Diferenca_Antes': 0.4,
            'Diferenca_Depois': 0.12,
            'Reducao_Absoluta': 0.28,
            'Reducao_Percentual': '70.0%',
            'Eficacia': 'Alta'
        }
    ])

    # Aba 4: Mudanças de Posição
    mudancas_posicao = pd.DataFrame([
        {'Pessoa_ID': 'P001', 'Nome': 'Maria Silva', 'Genero': 'Feminino',
         'Posicao_Antes': 15, 'Posicao_Depois': 8, 'Mudanca': 7, 'Direcao': 'Subiu'},
        {'Pessoa_ID': 'P002', 'Nome': 'João Santos', 'Genero': 'Masculino',
         'Posicao_Antes': 5, 'Posicao_Depois': 12, 'Mudanca': -7, 'Direcao': 'Desceu'},
        {'Pessoa_ID': 'P003', 'Nome': 'Ana Costa', 'Genero': 'Feminino',
         'Posicao_Antes': 20, 'Posicao_Depois': 15, 'Mudanca': 5, 'Direcao': 'Subiu'},
        {'Pessoa_ID': 'P004', 'Nome': 'Pedro Lima', 'Genero': 'Masculino',
         'Posicao_Antes': 10, 'Posicao_Depois': 10, 'Mudanca': 0, 'Direcao': 'Manteve'}
    ])

    dados_completos = {
        'resumo_executivo': resumo_executivo,
        'deteccao_vies': deteccao_vies,
        'eficacia_correcao': eficacia_correcao,
        'mudancas_posicao': mudancas_posicao
    }

    caminho = generator.gerar_relatorio_completo(dados_completos)

    print(f"\n✓ Relatório Excel gerado!")
    print(f"  Localização: {caminho}")

    return caminho


def demo_powerpoint(cenarios, todos_graficos):
    """Demonstra geração de PowerPoint ULTRA DETALHADO"""
    print("\n" + "=" * 80)
    print("DEMO 3: APRESENTAÇÃO POWERPOINT ULTRA DETALHADA".center(80))
    print("=" * 80 + "\n")

    generator = PowerPointGeneratorV3(output_dir="reports/powerpoint")

    caminho = generator.gerar_apresentacao_completa(
        dados_cenarios=cenarios,
        todos_graficos=todos_graficos
    )

    print(f"\n✓ Apresentação PowerPoint ULTRA DETALHADA gerada!")
    print(f"  Localização: {caminho}")

    return caminho


def demo_dashboard(cenarios, pessoas, generos_dict, scores_desempenho, scores_potencial, info_outliers=None):
    """Demonstra geração de Dashboard HTML Premium para Apresentações"""
    print("\n" + "=" * 80)
    print("DEMO 4: DASHBOARD HTML PREMIUM PARA APRESENTAÇÕES".center(80))
    print("=" * 80 + "\n")

    generator = DashboardGeneratorV2(output_dir="reports/dashboards")

    # Prepara dados completos para o dashboard
    dados_completos = {
        'cenarios': cenarios,
        'pessoas': {p.id: p for p in pessoas},
        'info_outliers': info_outliers
    }

    caminho = generator.gerar_dashboard_completo(dados_completos)

    print(f"\n✓ Dashboard HTML gerado!")
    print(f"  Localização: {caminho}")
    print(f"  Abra o arquivo no navegador para visualizar")

    return caminho


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print("DEMONSTRAÇÃO DE RELATÓRIOS AUTOMATIZADOS - COM DETECÇÃO DE OUTLIERS".center(80))
    print("=" * 80)
    print("\nEste script demonstra o framework completo com:")
    print("  ETAPA 1: Detecção e Remoção de Outliers (Z-score, threshold=3.0)")
    print("  ETAPA 2: Análise de Viés de Gênero (7 cenários)")
    print("  ETAPA 3: Geração de Relatórios Automatizados")
    print("\nRelatórios gerados:")
    print("  • Gráficos PNG em alta resolução (56 gráficos = 8 por cenário)")
    print("  • Relatórios Excel formatados (4 abas, 7 cenários)")
    print("  • Apresentações PowerPoint ULTRA DETALHADAS (~70 slides)")
    print("  • Dashboard HTML interativo (7 abas, um cenário por aba)")
    print("\n  IMPORTANTE: Cenário 1 = SEM viés (dados limpos)")
    print("              Cenários 2-7 = COM viés progressivo (0% → 100%)")
    print("\n" + "=" * 80 + "\n")

    # Prepara dados
    pessoas, generos_dict, scores_desempenho, scores_potencial, avaliacao_ninebox = preparar_dados_exemplo()

    # ETAPA 1: Detecta e remove outliers
    scores_limpos, resultado_outliers, info_outliers = detectar_e_remover_outliers(
        scores_desempenho,
        generos_dict,
        threshold=2.0
    )

    # ETAPA 2: Gera cenários (usando dados limpos)
    cenarios, analise_antes, analise_depois = gerar_cenarios(scores_limpos, generos_dict)

    # Demo 1: Gráficos
    graficos = demo_graficos(cenarios)

    # Demo 2: Excel
    excel_path = demo_excel(cenarios)

    # Demo 3: PowerPoint
    ppt_path = demo_powerpoint(cenarios, graficos)

    # Demo 4: Dashboard Premium
    dashboard_path = demo_dashboard(cenarios, pessoas, generos_dict, scores_limpos, scores_potencial, info_outliers)

    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DOS RELATÓRIOS GERADOS".center(80))
    print("=" * 80 + "\n")

    print("✓ Gráficos PNG:")
    total_graficos = sum(len(g) for g in graficos.values())
    print(f"  - {total_graficos} gráficos em alta resolução (300 DPI)")
    print(f"  - {len(graficos)} cenários × 8 gráficos cada")
    print(f"  - Localização: reports/graficos/cenario_*/\n")

    print("✓ Relatório Excel:")
    print(f"  - 4 abas com formatação profissional")
    print(f"  - Conditional formatting aplicado")
    print(f"  - Localização: {excel_path}\n")

    print("✓ Apresentação PowerPoint:")
    print(f"  - Apresentação completa com gráficos e tabelas")
    print(f"  - Localização: {ppt_path}\n")

    print("✓ Dashboard HTML:")
    print(f"  - Dashboard interativo com {len(cenarios)} abas (7 cenários)")
    print(f"  - Exportável como PDF")
    print(f"  - Localização: {dashboard_path}\n")

    print("=" * 80)
    print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
