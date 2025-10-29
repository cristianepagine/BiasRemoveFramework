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
    """Gera os 7 cenários de análise com diferentes níveis de correção"""
    print("=" * 80)
    print("GERANDO 7 CENÁRIOS DE ANÁLISE".center(80))
    print("=" * 80 + "\n")

    analyzer = BiasAnalyzer(threshold_vies=0.05, alpha=0.05)
    corrector = BiasCorrector()

    # Agrupa scores por gênero original
    scores_por_genero_antes = {
        Genero.FEMININO: [],
        Genero.MASCULINO: []
    }

    for pessoa_id, score in scores.items():
        genero = generos_dict.get(pessoa_id)
        if genero in [Genero.FEMININO, Genero.MASCULINO]:
            scores_por_genero_antes[genero].append(score)

    # Analisa viés original
    analise_antes = analyzer.analisar_vies_genero(scores_por_genero_antes)

    # Aplica correção total
    resultado_correcao = corrector.aplicar_reponderacao(
        scores, generos_dict, aplicar_correcao=True
    )

    # Define 7 cenários com diferentes níveis de correção
    cenarios = {}
    niveis_correcao = [0, 16.67, 33.33, 50, 66.67, 83.33, 100]  # 0% a 100% em 7 passos

    for idx, nivel in enumerate(niveis_correcao, 1):
        # Aplica percentual de correção
        scores_por_genero_cenario = {
            Genero.FEMININO: [],
            Genero.MASCULINO: []
        }

        for pessoa_id, score_orig in scores.items():
            genero = generos_dict.get(pessoa_id)
            if genero in [Genero.FEMININO, Genero.MASCULINO]:
                score_corrigido = resultado_correcao.scores_ajustados[pessoa_id]
                # Interpola entre original e corrigido
                score_final = score_orig + (score_corrigido - score_orig) * (nivel / 100.0)
                scores_por_genero_cenario[genero].append(score_final)

        # Converte para strings
        scores_por_genero_str = {
            'Feminino': scores_por_genero_cenario[Genero.FEMININO],
            'Masculino': scores_por_genero_cenario[Genero.MASCULINO]
        }

        # Analisa
        analise_cenario = analyzer.analisar_vies_genero(scores_por_genero_cenario)

        # Define título baseado no nível
        if nivel == 0:
            titulo = f'Cenário {idx} - Sem Correção (0%)'
            descricao = 'Dados brutos sem aplicação de correções'
        elif nivel < 50:
            titulo = f'Cenário {idx} - Correção Mínima ({nivel:.0f}%)'
            descricao = f'Aplicação de {nivel:.0f}% de correção de viés'
        elif nivel == 50:
            titulo = f'Cenário {idx} - Correção Moderada ({nivel:.0f}%)'
            descricao = 'Aplicação de 50% de correção de viés'
        elif nivel < 100:
            titulo = f'Cenário {idx} - Correção Forte ({nivel:.0f}%)'
            descricao = f'Aplicação de {nivel:.0f}% de correção de viés'
        else:
            titulo = f'Cenário {idx} - Correção Total (100%)'
            descricao = 'Correção completa de viés aplicada'

        print(f"{titulo}")
        print(f"  Média Feminino: {analise_cenario.estatisticas_feminino.media:.2f}")
        print(f"  Média Masculino: {analise_cenario.estatisticas_masculino.media:.2f}")
        print(f"  Diferença: {analise_cenario.diferenca_medias:.3f}")
        print(f"  P-value: {analise_cenario.p_value:.4f}\n")

        cenarios[f'cenario_{idx}'] = {
            'titulo': titulo,
            'descricao': descricao,
            'scores_por_genero': scores_por_genero_str,
            'medias_antes': {
                'Feminino': analise_antes.estatisticas_feminino.media,
                'Masculino': analise_antes.estatisticas_masculino.media
            },
            'medias_depois': {
                'Feminino': analise_cenario.estatisticas_feminino.media,
                'Masculino': analise_cenario.estatisticas_masculino.media
            },
            'diferenca_antes': analise_antes.diferenca_medias,
            'diferenca_depois': analise_cenario.diferenca_medias,
            'p_value_antes': analise_antes.p_value,
            'p_value_depois': analise_cenario.p_value,
            'todos_scores': scores_por_genero_str['Feminino'] + scores_por_genero_str['Masculino']
        }

    return cenarios, analise_antes, resultado_correcao.analise_pos_ajuste


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


def demo_powerpoint(cenarios, graficos):
    """Demonstra geração de PowerPoint"""
    print("\n" + "=" * 80)
    print("DEMO 3: APRESENTAÇÕES POWERPOINT".center(80))
    print("=" * 80 + "\n")

    generator = PowerPointGenerator(output_dir="reports/powerpoint")

    # Prepara tabelas dinamicamente para todos os cenários
    tabelas = {}
    for key, dados in cenarios.items():
        tabelas[key] = pd.DataFrame([
            {'Métrica': 'Média Feminino', 'Valor': f"{dados['medias_depois']['Feminino']:.2f}"},
            {'Métrica': 'Média Masculino', 'Valor': f"{dados['medias_depois']['Masculino']:.2f}"},
            {'Métrica': 'P-value', 'Valor': f"{dados['p_value_depois']:.4f}"}
        ])

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

    # Adiciona dados de desempenho vs potencial para todos os cenários
    for key in cenarios.keys():
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
    print("  2. Relatórios Excel formatados (4 abas, 7 cenários)")
    print("  3. Apresentações PowerPoint (7 cenários com gráficos e tabelas)")
    print("  4. Dashboard HTML interativo (7 abas, um cenário por aba)")
    print("\n  Os 7 cenários variam de 0% a 100% de correção de viés")
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
    print(f"  - Dashboard interativo com {len(cenarios)} abas (7 cenários)")
    print(f"  - Exportável como PDF")
    print(f"  - Localização: {dashboard_path}\n")

    print("=" * 80)
    print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
