"""
Gerador Automático de Gráficos - 8 Gráficos Essenciais
Gera visualizações em alta resolução (PNG) a partir dos DataFrames do framework
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configuração de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class GraphGenerator:
    """
    Gerador de gráficos automático para o framework de redução de viés.

    Gera 8 gráficos essenciais:
    1. Distribuição de scores por gênero (antes da correção)
    2. Distribuição de scores por gênero (depois da correção)
    3. Comparação de médias (masculino vs feminino)
    4. Boxplot de scores por tipo de avaliação
    5. Gráfico de barras da eficácia da correção
    6. Histograma de distribuição de scores
    7. Scatter plot desempenho vs potencial
    8. Radar chart com múltiplos critérios
    """

    def __init__(self, output_dir: str = "reports/graficos", dpi: int = 300):
        """
        Inicializa o gerador de gráficos.

        Args:
            output_dir: Diretório para salvar os gráficos
            dpi: Resolução dos gráficos (300 = alta qualidade)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _save_figure(self, fig: plt.Figure, nome: str):
        """Salva figura com configurações de alta qualidade"""
        caminho = self.output_dir / f"{nome}_{self.timestamp}.png"
        fig.savefig(
            caminho,
            dpi=self.dpi,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none'
        )
        plt.close(fig)
        print(f"✓ Gráfico salvo: {caminho}")
        return caminho

    def grafico_1_distribuicao_scores_antes(
        self,
        scores_por_genero: Dict[str, List[float]],
        titulo: str = "Distribuição de Scores por Gênero (Antes da Correção)"
    ) -> Path:
        """
        Gráfico 1: Distribuição de scores por gênero antes da correção
        Violin plot mostrando distribuição completa
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        # Prepara dados
        data = []
        for genero, scores in scores_por_genero.items():
            for score in scores:
                data.append({'Gênero': genero, 'Score': score})
        df = pd.DataFrame(data)

        # Violin plot
        sns.violinplot(data=df, x='Gênero', y='Score', ax=ax, inner='box')

        # Adiciona pontos individuais
        sns.stripplot(data=df, x='Gênero', y='Score', ax=ax,
                     color='black', alpha=0.3, size=3)

        # Adiciona médias
        for i, (genero, scores) in enumerate(scores_por_genero.items()):
            media = np.mean(scores)
            ax.hlines(media, i-0.3, i+0.3, colors='red',
                     linestyles='--', linewidth=2, label=f'Média {genero}' if i == 0 else '')

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Gênero', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.grid(True, alpha=0.3)

        return self._save_figure(fig, "01_distribuicao_antes")

    def grafico_2_distribuicao_scores_depois(
        self,
        scores_por_genero: Dict[str, List[float]],
        titulo: str = "Distribuição de Scores por Gênero (Depois da Correção)"
    ) -> Path:
        """
        Gráfico 2: Distribuição de scores por gênero depois da correção
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        # Prepara dados
        data = []
        for genero, scores in scores_por_genero.items():
            for score in scores:
                data.append({'Gênero': genero, 'Score': score})
        df = pd.DataFrame(data)

        # Violin plot
        sns.violinplot(data=df, x='Gênero', y='Score', ax=ax, inner='box',
                      palette='Set2')

        # Adiciona pontos individuais
        sns.stripplot(data=df, x='Gênero', y='Score', ax=ax,
                     color='black', alpha=0.3, size=3)

        # Adiciona médias
        for i, (genero, scores) in enumerate(scores_por_genero.items()):
            media = np.mean(scores)
            ax.hlines(media, i-0.3, i+0.3, colors='green',
                     linestyles='--', linewidth=2)

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Gênero', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.grid(True, alpha=0.3)

        return self._save_figure(fig, "02_distribuicao_depois")

    def grafico_3_comparacao_medias(
        self,
        medias_antes: Dict[str, float],
        medias_depois: Dict[str, float],
        titulo: str = "Comparação de Médias: Antes vs Depois da Correção"
    ) -> Path:
        """
        Gráfico 3: Comparação de médias antes e depois da correção
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        generos = list(medias_antes.keys())
        x = np.arange(len(generos))
        width = 0.35

        # Barras
        bars1 = ax.bar(x - width/2, [medias_antes[g] for g in generos],
                      width, label='Antes da Correção', color='#E74C3C', alpha=0.8)
        bars2 = ax.bar(x + width/2, [medias_depois[g] for g in generos],
                      width, label='Depois da Correção', color='#27AE60', alpha=0.8)

        # Adiciona valores nas barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Gênero', fontsize=12)
        ax.set_ylabel('Média de Score', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(generos)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        return self._save_figure(fig, "03_comparacao_medias")

    def grafico_4_boxplot_avaliacoes(
        self,
        scores_por_tipo: Dict[str, List[float]],
        titulo: str = "Distribuição de Scores por Tipo de Avaliação"
    ) -> Path:
        """
        Gráfico 4: Boxplot de scores por tipo de avaliação
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        # Prepara dados
        data = []
        for tipo, scores in scores_por_tipo.items():
            for score in scores:
                data.append({'Tipo': tipo, 'Score': score})
        df = pd.DataFrame(data)

        # Boxplot
        sns.boxplot(data=df, x='Tipo', y='Score', ax=ax, palette='Set3')

        # Adiciona média como ponto vermelho
        medias = df.groupby('Tipo')['Score'].mean()
        ax.scatter(range(len(medias)), medias, color='red', s=100,
                  zorder=3, label='Média', marker='D')

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Tipo de Avaliação', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        return self._save_figure(fig, "04_boxplot_avaliacoes")

    def grafico_5_eficacia_correcao(
        self,
        diferenca_antes: float,
        diferenca_depois: float,
        p_value_antes: float,
        p_value_depois: float,
        titulo: str = "Eficácia da Correção de Viés"
    ) -> Path:
        """
        Gráfico 5: Gráfico de barras mostrando eficácia da correção
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Subgráfico 1: Diferença de médias
        categorias = ['Antes\nda Correção', 'Depois\nda Correção']
        valores = [abs(diferenca_antes), abs(diferenca_depois)]
        cores = ['#E74C3C', '#27AE60']

        bars = ax1.bar(categorias, valores, color=cores, alpha=0.8, width=0.5)

        # Adiciona valores
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Calcula redução percentual
        reducao = ((abs(diferenca_antes) - abs(diferenca_depois)) / abs(diferenca_antes) * 100)
        ax1.text(0.5, max(valores) * 0.5, f'Redução:\n{reducao:.1f}%',
                ha='center', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

        ax1.set_title('Diferença de Médias entre Gêneros', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Diferença Absoluta', fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')

        # Subgráfico 2: P-values
        valores_p = [p_value_antes, p_value_depois]
        cores_p = ['#E74C3C' if v < 0.05 else '#27AE60' for v in valores_p]

        bars2 = ax2.bar(categorias, valores_p, color=cores_p, alpha=0.8, width=0.5)

        # Linha de significância
        ax2.axhline(y=0.05, color='black', linestyle='--', linewidth=2,
                   label='Nível de Significância (0.05)')

        # Adiciona valores
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax2.set_title('Significância Estatística (p-value)', fontsize=13, fontweight='bold')
        ax2.set_ylabel('P-value', fontsize=11)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        fig.suptitle(titulo, fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        return self._save_figure(fig, "05_eficacia_correcao")

    def grafico_6_histograma_distribuicao(
        self,
        scores: List[float],
        titulo: str = "Histograma de Distribuição de Scores",
        bins: int = 30
    ) -> Path:
        """
        Gráfico 6: Histograma da distribuição de scores
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        # Histograma
        n, bins_edges, patches = ax.hist(scores, bins=bins, alpha=0.7,
                                         color='skyblue', edgecolor='black')

        # Adiciona curva de densidade
        mu = np.mean(scores)
        sigma = np.std(scores)
        x = np.linspace(min(scores), max(scores), 100)

        # Normaliza para escala do histograma
        from scipy import stats
        densidade = stats.norm.pdf(x, mu, sigma)
        densidade_normalizada = densidade * len(scores) * (bins_edges[1] - bins_edges[0])

        ax.plot(x, densidade_normalizada, 'r-', linewidth=2,
               label=f'Distribuição Normal\n(μ={mu:.2f}, σ={sigma:.2f})')

        # Linha vertical na média
        ax.axvline(mu, color='red', linestyle='--', linewidth=2,
                  label=f'Média: {mu:.2f}')

        # Linhas verticais nos percentis
        p25, p50, p75 = np.percentile(scores, [25, 50, 75])
        ax.axvline(p25, color='orange', linestyle=':', linewidth=1.5,
                  label=f'P25: {p25:.2f}')
        ax.axvline(p50, color='green', linestyle=':', linewidth=1.5,
                  label=f'Mediana: {p50:.2f}')
        ax.axvline(p75, color='purple', linestyle=':', linewidth=1.5,
                  label=f'P75: {p75:.2f}')

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Score', fontsize=12)
        ax.set_ylabel('Frequência', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        return self._save_figure(fig, "06_histograma_distribuicao")

    def grafico_7_scatter_desempenho_potencial(
        self,
        desempenho: List[float],
        potencial: List[float],
        generos: Optional[List[str]] = None,
        titulo: str = "Desempenho vs Potencial"
    ) -> Path:
        """
        Gráfico 7: Scatter plot de desempenho vs potencial
        """
        fig, ax = plt.subplots(figsize=(12, 10))

        # Se temos informação de gênero, colorir por gênero
        if generos:
            df = pd.DataFrame({
                'Desempenho': desempenho,
                'Potencial': potencial,
                'Gênero': generos
            })

            for genero in df['Gênero'].unique():
                mask = df['Gênero'] == genero
                ax.scatter(df[mask]['Desempenho'], df[mask]['Potencial'],
                          label=genero, alpha=0.6, s=100, edgecolors='black')
        else:
            ax.scatter(desempenho, potencial, alpha=0.6, s=100,
                      edgecolors='black', c='blue')

        # Linhas de referência (Nine Box)
        ax.axhline(y=6.67, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=3.33, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.axvline(x=6.67, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.axvline(x=3.33, color='gray', linestyle='--', linewidth=1, alpha=0.5)

        # Adiciona labels dos quadrantes (Nine Box simplificado)
        quadrantes = [
            (8.5, 8.5, 'Alto Potencial\nAlto Desempenho', 'green'),
            (8.5, 5, 'Médio Potencial\nAlto Desempenho', 'lightgreen'),
            (8.5, 1.5, 'Baixo Potencial\nAlto Desempenho', 'yellow'),
            (5, 8.5, 'Alto Potencial\nMédio Desempenho', 'lightgreen'),
            (5, 5, 'Médio Potencial\nMédio Desempenho', 'yellow'),
            (5, 1.5, 'Baixo Potencial\nMédio Desempenho', 'orange'),
            (1.5, 8.5, 'Alto Potencial\nBaixo Desempenho', 'yellow'),
            (1.5, 5, 'Médio Potencial\nBaixo Desempenho', 'orange'),
            (1.5, 1.5, 'Baixo Potencial\nBaixo Desempenho', 'red'),
        ]

        for x, y, label, color in quadrantes:
            ax.text(x, y, label, ha='center', va='center', fontsize=8,
                   bbox=dict(boxstyle='round', facecolor=color, alpha=0.2))

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Desempenho', fontsize=12)
        ax.set_ylabel('Potencial', fontsize=12)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

        if generos:
            ax.legend(title='Gênero', fontsize=11)

        ax.grid(True, alpha=0.3)

        return self._save_figure(fig, "07_scatter_desempenho_potencial")

    def grafico_8_comparativo_cenarios(
        self,
        cenarios_data: Dict[str, Dict[str, float]],
        titulo: str = "Comparativo de Cenários"
    ) -> Path:
        """
        Gráfico 8: Comparativo entre diferentes cenários

        Args:
            cenarios_data: Dict com estrutura:
                {
                    'Cenário 1': {'Métrica 1': valor, 'Métrica 2': valor, ...},
                    'Cenário 2': {'Métrica 1': valor, 'Métrica 2': valor, ...},
                }
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        # Prepara dados
        cenarios = list(cenarios_data.keys())
        metricas = list(next(iter(cenarios_data.values())).keys())

        x = np.arange(len(metricas))
        width = 0.8 / len(cenarios)

        # Cores para cada cenário
        cores = plt.cm.Set3(np.linspace(0, 1, len(cenarios)))

        # Desenha barras para cada cenário
        for i, (cenario, cor) in enumerate(zip(cenarios, cores)):
            valores = [cenarios_data[cenario][metrica] for metrica in metricas]
            offset = width * i - (width * len(cenarios) / 2) + width / 2
            bars = ax.bar(x + offset, valores, width, label=cenario,
                         color=cor, alpha=0.8, edgecolor='black')

            # Adiciona valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=8, rotation=0)

        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Métricas', fontsize=12)
        ax.set_ylabel('Valor', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(metricas, rotation=45, ha='right')
        ax.legend(title='Cenários', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        return self._save_figure(fig, "08_comparativo_cenarios")

    def gerar_todos_graficos(
        self,
        dados_completos: Dict
    ) -> List[Path]:
        """
        Gera todos os 8 gráficos automaticamente a partir de dados completos.

        Args:
            dados_completos: Dicionário com todos os dados necessários
                Estrutura esperada:
                {
                    'scores_antes_por_genero': Dict[str, List[float]],
                    'scores_depois_por_genero': Dict[str, List[float]],
                    'medias_antes': Dict[str, float],
                    'medias_depois': Dict[str, float],
                    'scores_por_tipo': Dict[str, List[float]],
                    'diferenca_antes': float,
                    'diferenca_depois': float,
                    'p_value_antes': float,
                    'p_value_depois': float,
                    'todos_scores': List[float],
                    'desempenho': List[float],
                    'potencial': List[float],
                    'generos': List[str],
                    'cenarios': Dict[str, Dict[str, float]]
                }

        Returns:
            Lista com caminhos de todos os gráficos gerados
        """
        graficos = []

        print("\n=== Gerando 8 Gráficos Essenciais ===\n")

        try:
            # Gráfico 1
            if 'scores_antes_por_genero' in dados_completos:
                graficos.append(self.grafico_1_distribuicao_scores_antes(
                    dados_completos['scores_antes_por_genero']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 1: {e}")

        try:
            # Gráfico 2
            if 'scores_depois_por_genero' in dados_completos:
                graficos.append(self.grafico_2_distribuicao_scores_depois(
                    dados_completos['scores_depois_por_genero']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 2: {e}")

        try:
            # Gráfico 3
            if 'medias_antes' in dados_completos and 'medias_depois' in dados_completos:
                graficos.append(self.grafico_3_comparacao_medias(
                    dados_completos['medias_antes'],
                    dados_completos['medias_depois']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 3: {e}")

        try:
            # Gráfico 4
            if 'scores_por_tipo' in dados_completos:
                graficos.append(self.grafico_4_boxplot_avaliacoes(
                    dados_completos['scores_por_tipo']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 4: {e}")

        try:
            # Gráfico 5
            if all(k in dados_completos for k in ['diferenca_antes', 'diferenca_depois',
                                                   'p_value_antes', 'p_value_depois']):
                graficos.append(self.grafico_5_eficacia_correcao(
                    dados_completos['diferenca_antes'],
                    dados_completos['diferenca_depois'],
                    dados_completos['p_value_antes'],
                    dados_completos['p_value_depois']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 5: {e}")

        try:
            # Gráfico 6
            if 'todos_scores' in dados_completos:
                graficos.append(self.grafico_6_histograma_distribuicao(
                    dados_completos['todos_scores']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 6: {e}")

        try:
            # Gráfico 7
            if 'desempenho' in dados_completos and 'potencial' in dados_completos:
                graficos.append(self.grafico_7_scatter_desempenho_potencial(
                    dados_completos['desempenho'],
                    dados_completos['potencial'],
                    dados_completos.get('generos')
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 7: {e}")

        try:
            # Gráfico 8
            if 'cenarios' in dados_completos:
                graficos.append(self.grafico_8_comparativo_cenarios(
                    dados_completos['cenarios']
                ))
        except Exception as e:
            print(f"⚠ Erro no Gráfico 8: {e}")

        print(f"\n✓ Total de gráficos gerados: {len(graficos)}/8")

        return graficos
