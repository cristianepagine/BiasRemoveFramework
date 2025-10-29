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
    BiasCorrector
)
from src.reports import (
    GraphGenerator,
    ExcelReportGenerator,
    PowerPointGenerator,
    DashboardGenerator
)


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


def gerar_cenarios(scores, generos_dict):
    """Gera os 3 cenários de análise"""
    print("=" * 80)
    print("GERANDO 3 CENÁRIOS DE ANÁLISE".center(80))
    print("=" * 80 + "\n")

    analyzer = BiasAnalyzer(threshold_vies=0.05, alpha=0.05)
    corrector = BiasCorrector()

    # Agrupa scores por gênero
    scores_por_genero_antes = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in scores.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            scores_por_genero_antes[genero].append(score)

    # Converte para strings para compatibilidade
    scores_por_genero_antes_str = {
        'Feminino': scores_por_genero_antes[Genero.FEMININO],
        'Masculino': scores_por_genero_antes[Genero.MASCULINO]
    }

    # Analisa viés original
    analise_antes = analyzer.analisar_vies_genero(scores_por_genero_antes)

    print("Cenário 1: Sem Correção")
    print(f"  Média Feminino: {analise_antes.estatisticas_feminino.media:.2f}")
    print(f"  Média Masculino: {analise_antes.estatisticas_masculino.media:.2f}")
    print(f"  Diferença: {analise_antes.diferenca_medias:.3f}")
    print(f"  P-value: {analise_antes.p_value:.4f}\n")

    # Cenário 1: Sem correção
    cenario_1 = {
        'titulo': 'Cenário 1 - Sem Correção',
        'scores_por_genero': scores_por_genero_antes_str,
        'medias_antes': {
            'Feminino': analise_antes.estatisticas_feminino.media,
            'Masculino': analise_antes.estatisticas_masculino.media
        },
        'medias_depois': {
            'Feminino': analise_antes.estatisticas_feminino.media,
            'Masculino': analise_antes.estatisticas_masculino.media
        },
        'diferenca_antes': analise_antes.diferenca_medias,
        'diferenca_depois': analise_antes.diferenca_medias,
        'p_value_antes': analise_antes.p_value,
        'p_value_depois': analise_antes.p_value,
        'todos_scores': list(scores.values())
    }

    # Cenário 2: Correção parcial (50%)
    resultado_parcial = corrector.aplicar_reponderacao(
        scores, generos_dict, aplicar_correcao=True
    )

    scores_por_genero_parcial = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in resultado_parcial.scores_ajustados.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            # Aplica 50% da correção
            score_orig = scores[pessoa_id]
            score_meio = score_orig + (score - score_orig) * 0.5
            scores_por_genero_parcial[genero].append(score_meio)

    scores_por_genero_parcial_str = {
        'Feminino': scores_por_genero_parcial[Genero.FEMININO],
        'Masculino': scores_por_genero_parcial[Genero.MASCULINO]
    }

    analise_parcial = analyzer.analisar_vies_genero(scores_por_genero_parcial)

    print("Cenário 2: Correção Parcial (50%)")
    print(f"  Média Feminino: {analise_parcial.estatisticas_feminino.media:.2f}")
    print(f"  Média Masculino: {analise_parcial.estatisticas_masculino.media:.2f}")
    print(f"  Diferença: {analise_parcial.diferenca_medias:.3f}")
    print(f"  P-value: {analise_parcial.p_value:.4f}\n")

    cenario_2 = {
        'titulo': 'Cenário 2 - Correção Parcial',
        'scores_por_genero': scores_por_genero_parcial_str,
        'medias_antes': {
            'Feminino': analise_antes.estatisticas_feminino.media,
            'Masculino': analise_antes.estatisticas_masculino.media
        },
        'medias_depois': {
            'Feminino': analise_parcial.estatisticas_feminino.media,
            'Masculino': analise_parcial.estatisticas_masculino.media
        },
        'diferenca_antes': analise_antes.diferenca_medias,
        'diferenca_depois': analise_parcial.diferenca_medias,
        'p_value_antes': analise_antes.p_value,
        'p_value_depois': analise_parcial.p_value,
        'todos_scores': scores_por_genero_parcial_str['Feminino'] + scores_por_genero_parcial_str['Masculino']
    }

    # Cenário 3: Correção total
    scores_por_genero_depois = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in resultado_parcial.scores_ajustados.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            scores_por_genero_depois[genero].append(score)

    scores_por_genero_depois_str = {
        'Feminino': scores_por_genero_depois[Genero.FEMININO],
        'Masculino': scores_por_genero_depois[Genero.MASCULINO]
    }

    analise_depois = analyzer.analisar_vies_genero(scores_por_genero_depois)

    print("Cenário 3: Correção Total")
    print(f"  Média Feminino: {analise_depois.estatisticas_feminino.media:.2f}")
    print(f"  Média Masculino: {analise_depois.estatisticas_masculino.media:.2f}")
    print(f"  Diferença: {analise_depois.diferenca_medias:.3f}")
    print(f"  P-value: {analise_depois.p_value:.4f}\n")

    cenario_3 = {
        'titulo': 'Cenário 3 - Correção Total',
        'scores_por_genero': scores_por_genero_depois_str,
        'medias_antes': {
            'Feminino': analise_antes.estatisticas_feminino.media,
            'Masculino': analise_antes.estatisticas_masculino.media
        },
        'medias_depois': {
            'Feminino': analise_depois.estatisticas_feminino.media,
            'Masculino': analise_depois.estatisticas_masculino.media
        },
        'diferenca_antes': analise_antes.diferenca_medias,
        'diferenca_depois': analise_depois.diferenca_medias,
        'p_value_antes': analise_antes.p_value,
        'p_value_depois': analise_depois.p_value,
        'todos_scores': scores_por_genero_depois_str['Feminino'] + scores_por_genero_depois_str['Masculino']
    }

    return {
        'cenario_1': cenario_1,
        'cenario_2': cenario_2,
        'cenario_3': cenario_3
    }, analise_antes, analise_depois


def demo_graficos(cenarios):
    """Demonstra geração de gráficos"""
    print("\n" + "=" * 80)
    print("DEMO 1: GRÁFICOS PNG EM ALTA RESOLUÇÃO".center(80))
    print("=" * 80 + "\n")

    generator = GraphGenerator(output_dir="reports/graficos", dpi=300)

    # Usa dados do cenário 3 para exemplo completo
    dados = cenarios['cenario_3']

    # Prepara dados adicionais
    dados['desempenho'] = dados['todos_scores'][:25]
    dados['potencial'] = list(np.random.uniform(5, 9, 25))
    dados['generos'] = ['Feminino' if i % 2 == 0 else 'Masculino' for i in range(25)]

    dados['scores_por_tipo'] = {
        'Competências': list(np.random.uniform(6, 9, 30)),
        '360 Graus': list(np.random.uniform(5, 8, 30)),
        'OKR': list(np.random.uniform(7, 9, 30)),
        'Nine Box': dados['todos_scores'][:30]
    }

    dados['cenarios'] = {
        'Sem Correção': {
            'Diferença Médias': abs(cenarios['cenario_1']['diferenca_antes']),
            'P-value': cenarios['cenario_1']['p_value_antes']
        },
        'Correção Parcial': {
            'Diferença Médias': abs(cenarios['cenario_2']['diferenca_depois']),
            'P-value': cenarios['cenario_2']['p_value_depois']
        },
        'Correção Total': {
            'Diferença Médias': abs(cenarios['cenario_3']['diferenca_depois']),
            'P-value': cenarios['cenario_3']['p_value_depois']
        }
    }

    # Gera todos os gráficos
    graficos = generator.gerar_todos_graficos(dados)

    print(f"\n✓ {len(graficos)} gráficos gerados com sucesso!")
    print(f"  Localização: {generator.output_dir}")

    return graficos


def demo_excel(cenarios):
    """Demonstra geração de Excel"""
    print("\n" + "=" * 80)
    print("DEMO 2: RELATÓRIOS EXCEL FORMATADOS".center(80))
    print("=" * 80 + "\n")

    generator = ExcelReportGenerator(output_dir="reports/excel")

    # Prepara dados para as abas

    # Aba 1: Resumo Executivo
    resumo_executivo = {
        'Cenário 1 - Sem Correção': {
            'Média Feminino': cenarios['cenario_1']['medias_depois']['Feminino'],
            'Média Masculino': cenarios['cenario_1']['medias_depois']['Masculino'],
            'Diferença': cenarios['cenario_1']['diferenca_depois'],
            'P-value': cenarios['cenario_1']['p_value_depois'],
            'Viés Detectado': 'Sim' if cenarios['cenario_1']['p_value_depois'] < 0.05 else 'Não'
        },
        'Cenário 2 - Correção Parcial': {
            'Média Feminino': cenarios['cenario_2']['medias_depois']['Feminino'],
            'Média Masculino': cenarios['cenario_2']['medias_depois']['Masculino'],
            'Diferença': cenarios['cenario_2']['diferenca_depois'],
            'P-value': cenarios['cenario_2']['p_value_depois'],
            'Viés Detectado': 'Sim' if cenarios['cenario_2']['p_value_depois'] < 0.05 else 'Não'
        },
        'Cenário 3 - Correção Total': {
            'Média Feminino': cenarios['cenario_3']['medias_depois']['Feminino'],
            'Média Masculino': cenarios['cenario_3']['medias_depois']['Masculino'],
            'Diferença': cenarios['cenario_3']['diferenca_depois'],
            'P-value': cenarios['cenario_3']['p_value_depois'],
            'Viés Detectado': 'Sim' if cenarios['cenario_3']['p_value_depois'] < 0.05 else 'Não'
        }
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


def demo_powerpoint(cenarios, graficos):
    """Demonstra geração de PowerPoint"""
    print("\n" + "=" * 80)
    print("DEMO 3: APRESENTAÇÕES POWERPOINT".center(80))
    print("=" * 80 + "\n")

    generator = PowerPointGenerator(output_dir="reports/powerpoint")

    # Prepara tabelas
    tabelas = {
        'cenario_1': pd.DataFrame([
            {'Métrica': 'Média Feminino', 'Valor': f"{cenarios['cenario_1']['medias_depois']['Feminino']:.2f}"},
            {'Métrica': 'Média Masculino', 'Valor': f"{cenarios['cenario_1']['medias_depois']['Masculino']:.2f}"},
            {'Métrica': 'P-value', 'Valor': f"{cenarios['cenario_1']['p_value_depois']:.4f}"}
        ]),
        'cenario_2': pd.DataFrame([
            {'Métrica': 'Média Feminino', 'Valor': f"{cenarios['cenario_2']['medias_depois']['Feminino']:.2f}"},
            {'Métrica': 'Média Masculino', 'Valor': f"{cenarios['cenario_2']['medias_depois']['Masculino']:.2f}"},
            {'Métrica': 'P-value', 'Valor': f"{cenarios['cenario_2']['p_value_depois']:.4f}"}
        ]),
        'cenario_3': pd.DataFrame([
            {'Métrica': 'Média Feminino', 'Valor': f"{cenarios['cenario_3']['medias_depois']['Feminino']:.2f}"},
            {'Métrica': 'Média Masculino', 'Valor': f"{cenarios['cenario_3']['medias_depois']['Masculino']:.2f}"},
            {'Métrica': 'P-value', 'Valor': f"{cenarios['cenario_3']['p_value_depois']:.4f}"}
        ])
    }

    caminho = generator.gerar_apresentacao_completa(
        graficos=graficos if graficos else [],
        tabelas=tabelas,
        dados_cenarios=cenarios
    )

    print(f"\n✓ Apresentação PowerPoint gerada!")
    print(f"  Localização: {caminho}")

    return caminho


def demo_dashboard(cenarios, pessoas, generos_dict, scores_desempenho, scores_potencial):
    """Demonstra geração de Dashboard"""
    print("\n" + "=" * 80)
    print("DEMO 4: DASHBOARD HTML INTERATIVO".center(80))
    print("=" * 80 + "\n")

    generator = DashboardGenerator(output_dir="reports/dashboards")

    # Adiciona dados de desempenho vs potencial para cada cenário
    for key in ['cenario_1', 'cenario_2', 'cenario_3']:
        # Pega primeiras 30 pessoas
        pessoas_subset = list(pessoas)[:30]

        cenarios[key]['desempenho'] = [scores_desempenho.get(p.id, 7.0) for p in pessoas_subset]
        cenarios[key]['potencial'] = [scores_potencial.get(p.id, 7.0) for p in pessoas_subset]
        cenarios[key]['generos'] = [p.genero.value for p in pessoas_subset]
        cenarios[key]['nomes'] = [p.nome for p in pessoas_subset]

    caminho = generator.gerar_dashboard_completo(cenarios)

    print(f"\n✓ Dashboard HTML gerado!")
    print(f"  Localização: {caminho}")
    print(f"  Abra o arquivo no navegador para visualizar")

    return caminho


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print("DEMONSTRAÇÃO DE RELATÓRIOS AUTOMATIZADOS".center(80))
    print("=" * 80)
    print("\nEste script demonstra a geração automática de:")
    print("  1. Gráficos PNG em alta resolução (8 gráficos)")
    print("  2. Relatórios Excel formatados (4 abas)")
    print("  3. Apresentações PowerPoint (15-20 slides)")
    print("  4. Dashboard HTML interativo (3 abas)")
    print("\n" + "=" * 80 + "\n")

    # Prepara dados
    pessoas, generos_dict, scores_desempenho, scores_potencial, avaliacao_ninebox = preparar_dados_exemplo()

    # Gera cenários
    cenarios, analise_antes, analise_depois = gerar_cenarios(scores_desempenho, generos_dict)

    # Demo 1: Gráficos
    graficos = demo_graficos(cenarios)

    # Demo 2: Excel
    excel_path = demo_excel(cenarios)

    # Demo 3: PowerPoint
    ppt_path = demo_powerpoint(cenarios, graficos)

    # Demo 4: Dashboard
    dashboard_path = demo_dashboard(cenarios, pessoas, generos_dict, scores_desempenho, scores_potencial)

    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DOS RELATÓRIOS GERADOS".center(80))
    print("=" * 80 + "\n")

    print("✓ Gráficos PNG:")
    print(f"  - {len(graficos)} gráficos em alta resolução (300 DPI)")
    print(f"  - Localização: reports/graficos/\n")

    print("✓ Relatório Excel:")
    print(f"  - 4 abas com formatação profissional")
    print(f"  - Conditional formatting aplicado")
    print(f"  - Localização: {excel_path}\n")

    print("✓ Apresentação PowerPoint:")
    print(f"  - Apresentação completa com gráficos e tabelas")
    print(f"  - Localização: {ppt_path}\n")

    print("✓ Dashboard HTML:")
    print(f"  - Dashboard interativo com 3 abas")
    print(f"  - Exportável como PDF")
    print(f"  - Localização: {dashboard_path}\n")

    print("=" * 80)
    print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
