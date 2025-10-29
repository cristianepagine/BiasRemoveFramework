"""
Gerador de Dashboard HTML Interativo
Cria dashboards interativos com Plotly para análise de viés
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class DashboardGenerator:
    """
    Gerador de dashboards HTML interativos com Plotly.

    Características:
    - 3 abas (1 por cenário)
    - Gráficos interativos
    - Hover mostrando dados detalhados
    - Exportável como PDF
    """

    def __init__(self, output_dir: str = "reports/dashboards"):
        """
        Inicializa o gerador de dashboards.

        Args:
            output_dir: Diretório para salvar os dashboards
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Configurações de cores
        self.cores = {
            'feminino': '#E91E63',  # Rosa
            'masculino': '#2196F3',  # Azul
            'outro': '#9C27B0',  # Roxo
            'positivo': '#4CAF50',  # Verde
            'negativo': '#F44336',  # Vermelho
            'neutro': '#FFC107'  # Amarelo
        }

    def grafico_violino_interativo(
        self,
        scores_por_genero: Dict[str, List[float]],
        titulo: str = "Distribuição de Scores por Gênero"
    ) -> go.Figure:
        """Cria violin plot interativo"""
        fig = go.Figure()

        for genero, scores in scores_por_genero.items():
            cor = self.cores.get(genero.lower(), '#999999')

            fig.add_trace(go.Violin(
                y=scores,
                name=genero,
                box_visible=True,
                meanline_visible=True,
                fillcolor=cor,
                opacity=0.6,
                x0=genero,
                hovertemplate='<b>%{x}</b><br>' +
                             'Score: %{y:.2f}<br>' +
                             '<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=titulo, font=dict(size=20, color='#333')),
            yaxis_title="Score",
            xaxis_title="Gênero",
            template="plotly_white",
            hovermode='closest',
            height=500
        )

        return fig

    def grafico_barras_comparativo(
        self,
        medias_antes: Dict[str, float],
        medias_depois: Dict[str, float],
        titulo: str = "Comparação de Médias: Antes vs Depois"
    ) -> go.Figure:
        """Cria gráfico de barras comparativo"""
        generos = list(medias_antes.keys())

        fig = go.Figure(data=[
            go.Bar(
                name='Antes da Correção',
                x=generos,
                y=[medias_antes[g] for g in generos],
                marker_color='#E74C3C',
                text=[f'{medias_antes[g]:.2f}' for g in generos],
                textposition='auto',
                hovertemplate='<b>Antes</b><br>' +
                             'Gênero: %{x}<br>' +
                             'Média: %{y:.2f}<br>' +
                             '<extra></extra>'
            ),
            go.Bar(
                name='Depois da Correção',
                x=generos,
                y=[medias_depois[g] for g in generos],
                marker_color='#27AE60',
                text=[f'{medias_depois[g]:.2f}' for g in generos],
                textposition='auto',
                hovertemplate='<b>Depois</b><br>' +
                             'Gênero: %{x}<br>' +
                             'Média: %{y:.2f}<br>' +
                             '<extra></extra>'
            )
        ])

        fig.update_layout(
            title=dict(text=titulo, font=dict(size=20, color='#333')),
            xaxis_title="Gênero",
            yaxis_title="Média de Score",
            barmode='group',
            template="plotly_white",
            height=500
        )

        return fig

    def grafico_boxplot_avaliacoes(
        self,
        scores_por_tipo: Dict[str, List[float]],
        titulo: str = "Distribuição por Tipo de Avaliação"
    ) -> go.Figure:
        """Cria boxplot por tipo de avaliação"""
        fig = go.Figure()

        for tipo, scores in scores_por_tipo.items():
            fig.add_trace(go.Box(
                y=scores,
                name=tipo,
                boxmean='sd',
                hovertemplate='<b>%{x}</b><br>' +
                             'Score: %{y:.2f}<br>' +
                             '<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=titulo, font=dict(size=20, color='#333')),
            yaxis_title="Score",
            xaxis_title="Tipo de Avaliação",
            template="plotly_white",
            showlegend=True,
            height=500
        )

        return fig

    def grafico_scatter_desempenho_potencial(
        self,
        desempenho: List[float],
        potencial: List[float],
        generos: List[str],
        nomes: Optional[List[str]] = None,
        titulo: str = "Desempenho vs Potencial"
    ) -> go.Figure:
        """Cria scatter plot interativo"""
        df = pd.DataFrame({
            'Desempenho': desempenho,
            'Potencial': potencial,
            'Gênero': generos,
            'Nome': nomes if nomes else [f'P{i+1}' for i in range(len(desempenho))]
        })

        fig = px.scatter(
            df,
            x='Desempenho',
            y='Potencial',
            color='Gênero',
            hover_data=['Nome'],
            color_discrete_map={
                'Feminino': self.cores['feminino'],
                'Masculino': self.cores['masculino'],
                'Outro': self.cores['outro']
            }
        )

        # Adiciona linhas de referência (Nine Box)
        for v in [3.33, 6.67]:
            fig.add_hline(y=v, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=v, line_dash="dash", line_color="gray", opacity=0.5)

        fig.update_traces(
            marker=dict(size=10, line=dict(width=1, color='white')),
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Desempenho: %{x:.2f}<br>' +
                         'Potencial: %{y:.2f}<br>' +
                         'Gênero: %{fullData.name}<br>' +
                         '<extra></extra>'
        )

        fig.update_layout(
            title=dict(text=titulo, font=dict(size=20, color='#333')),
            xaxis_title="Desempenho",
            yaxis_title="Potencial",
            template="plotly_white",
            height=600,
            xaxis=dict(range=[0, 10]),
            yaxis=dict(range=[0, 10])
        )

        return fig

    def grafico_eficacia_correcao(
        self,
        diferenca_antes: float,
        diferenca_depois: float,
        p_value_antes: float,
        p_value_depois: float,
        titulo: str = "Eficácia da Correção"
    ) -> go.Figure:
        """Cria gráfico de eficácia da correção"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Diferença de Médias", "P-value (Significância)")
        )

        # Subgráfico 1: Diferença de médias
        fig.add_trace(
            go.Bar(
                x=['Antes', 'Depois'],
                y=[abs(diferenca_antes), abs(diferenca_depois)],
                marker_color=['#E74C3C', '#27AE60'],
                text=[f'{abs(diferenca_antes):.3f}', f'{abs(diferenca_depois):.3f}'],
                textposition='auto',
                name='Diferença',
                hovertemplate='<b>%{x}</b><br>Diferença: %{y:.3f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Subgráfico 2: P-value
        cores_p = ['#E74C3C' if p_value_antes < 0.05 else '#27AE60',
                   '#27AE60' if p_value_depois >= 0.05 else '#E74C3C']

        fig.add_trace(
            go.Bar(
                x=['Antes', 'Depois'],
                y=[p_value_antes, p_value_depois],
                marker_color=cores_p,
                text=[f'{p_value_antes:.4f}', f'{p_value_depois:.4f}'],
                textposition='auto',
                name='P-value',
                hovertemplate='<b>%{x}</b><br>P-value: %{y:.4f}<extra></extra>'
            ),
            row=1, col=2
        )

        # Linha de significância
        fig.add_hline(
            y=0.05, line_dash="dash", line_color="black",
            annotation_text="α = 0.05",
            row=1, col=2
        )

        fig.update_layout(
            title_text=titulo,
            template="plotly_white",
            showlegend=False,
            height=450
        )

        fig.update_yaxes(title_text="Diferença Absoluta", row=1, col=1)
        fig.update_yaxes(title_text="P-value", row=1, col=2)

        return fig

    def grafico_histograma_interativo(
        self,
        scores: List[float],
        titulo: str = "Distribuição de Scores",
        bins: int = 30
    ) -> go.Figure:
        """Cria histograma interativo com curva de densidade"""
        fig = go.Figure()

        # Histograma
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=bins,
            name='Frequência',
            marker_color='#2196F3',
            opacity=0.7,
            hovertemplate='Score: %{x:.2f}<br>Frequência: %{y}<extra></extra>'
        ))

        # Estatísticas
        media = np.mean(scores)
        mediana = np.median(scores)

        fig.add_vline(
            x=media,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Média: {media:.2f}"
        )

        fig.add_vline(
            x=mediana,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Mediana: {mediana:.2f}"
        )

        fig.update_layout(
            title=dict(text=titulo, font=dict(size=20, color='#333')),
            xaxis_title="Score",
            yaxis_title="Frequência",
            template="plotly_white",
            height=500
        )

        return fig

    def grafico_mudancas_ranking(
        self,
        dados_mudancas: pd.DataFrame,
        titulo: str = "Mudanças no Ranking"
    ) -> go.Figure:
        """Cria gráfico de mudanças no ranking"""
        # Ordena por mudança (maiores mudanças primeiro)
        dados_mudancas = dados_mudancas.sort_values('Mudanca', ascending=True).tail(20)

        cores = []
        for mudanca in dados_mudancas['Mudanca']:
            if mudanca > 0:
                cores.append(self.cores['positivo'])
            elif mudanca < 0:
                cores.append(self.cores['negativo'])
            else:
                cores.append(self.cores['neutro'])

        fig = go.Figure(go.Bar(
            x=dados_mudancas['Mudanca'],
            y=dados_mudancas['Nome'],
            orientation='h',
            marker_color=cores,
            text=[f"{m:+d}" for m in dados_mudancas['Mudanca']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         'Mudança: %{x:+d} posições<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text=titulo, font=dict(size=20, color='#333')),
            xaxis_title="Mudança de Posições",
            yaxis_title="",
            template="plotly_white",
            height=600
        )

        return fig

    def criar_dashboard_cenario(
        self,
        dados_cenario: Dict,
        numero_cenario: int
    ) -> str:
        """
        Cria dashboard para um cenário específico.

        Args:
            dados_cenario: Dados do cenário
            numero_cenario: Número do cenário (1, 2 ou 3)

        Returns:
            HTML do dashboard
        """
        titulo_cenario = dados_cenario.get('titulo', f'Cenário {numero_cenario}')

        # Cria figuras
        figuras = []

        # Gráfico 1: Distribuição por gênero
        if 'scores_por_genero' in dados_cenario:
            fig1 = self.grafico_violino_interativo(
                dados_cenario['scores_por_genero'],
                f"{titulo_cenario} - Distribuição por Gênero"
            )
            figuras.append(fig1)

        # Gráfico 2: Comparação antes/depois
        if 'medias_antes' in dados_cenario and 'medias_depois' in dados_cenario:
            fig2 = self.grafico_barras_comparativo(
                dados_cenario['medias_antes'],
                dados_cenario['medias_depois'],
                f"{titulo_cenario} - Comparação de Médias"
            )
            figuras.append(fig2)

        # Gráfico 3: Eficácia
        if all(k in dados_cenario for k in ['diferenca_antes', 'diferenca_depois',
                                             'p_value_antes', 'p_value_depois']):
            fig3 = self.grafico_eficacia_correcao(
                dados_cenario['diferenca_antes'],
                dados_cenario['diferenca_depois'],
                dados_cenario['p_value_antes'],
                dados_cenario['p_value_depois'],
                f"{titulo_cenario} - Eficácia da Correção"
            )
            figuras.append(fig3)

        # Gráfico 4: Scatter desempenho vs potencial
        if all(k in dados_cenario for k in ['desempenho', 'potencial', 'generos']):
            fig4 = self.grafico_scatter_desempenho_potencial(
                dados_cenario['desempenho'],
                dados_cenario['potencial'],
                dados_cenario['generos'],
                dados_cenario.get('nomes'),
                f"{titulo_cenario} - Desempenho vs Potencial"
            )
            figuras.append(fig4)

        # Gráfico 5: Histograma
        if 'todos_scores' in dados_cenario:
            fig5 = self.grafico_histograma_interativo(
                dados_cenario['todos_scores'],
                f"{titulo_cenario} - Distribuição de Scores"
            )
            figuras.append(fig5)

        # Gera HTML para as figuras
        html_figuras = ""
        for fig in figuras:
            html_figuras += fig.to_html(full_html=False, include_plotlyjs='cdn')

        return html_figuras

    def gerar_dashboard_completo(
        self,
        dados_cenarios: Dict[str, Dict],
        nome_arquivo: Optional[str] = None
    ) -> Path:
        """
        Gera dashboard HTML completo com 3 abas (cenários).

        Args:
            dados_cenarios: Dicionário com dados dos 3 cenários:
                {
                    'cenario_1': {...},
                    'cenario_2': {...},
                    'cenario_3': {...}
                }
            nome_arquivo: Nome do arquivo (opcional)

        Returns:
            Path do arquivo gerado
        """
        if nome_arquivo is None:
            nome_arquivo = f"dashboard_vies_{self.timestamp}.html"

        caminho = self.output_dir / nome_arquivo

        print("\n=== Gerando Dashboard HTML Interativo ===\n")

        # Gera HTML para cada cenário
        html_cenario_1 = self.criar_dashboard_cenario(
            dados_cenarios.get('cenario_1', {}), 1
        )
        print("✓ Cenário 1 processado")

        html_cenario_2 = self.criar_dashboard_cenario(
            dados_cenarios.get('cenario_2', {}), 2
        )
        print("✓ Cenário 2 processado")

        html_cenario_3 = self.criar_dashboard_cenario(
            dados_cenarios.get('cenario_3', {}), 3
        )
        print("✓ Cenário 3 processado")

        # Template HTML com abas
        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Análise de Viés</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .tabs {{
            display: flex;
            justify-content: center;
            background-color: white;
            padding: 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .tab {{
            padding: 20px 40px;
            cursor: pointer;
            border: none;
            background: white;
            font-size: 1.1em;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}

        .tab:hover {{
            background-color: #f8f9fa;
            color: #667eea;
        }}

        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            background-color: #f8f9fa;
        }}

        .tab-content {{
            display: none;
            padding: 30px;
            animation: fadeIn 0.5s;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .chart-container {{
            margin-bottom: 40px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            background-color: white;
            margin-top: 40px;
            border-top: 1px solid #e0e0e0;
        }}

        .export-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
        }}

        .export-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Dashboard de Análise de Viés</h1>
        <p>Framework de Redução de Viés em Avaliações de RH</p>
        <p style="font-size: 0.9em; margin-top: 10px;">Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="openTab(event, 'cenario1')">Cenário 1 - Sem Correção</button>
        <button class="tab" onclick="openTab(event, 'cenario2')">Cenário 2 - Correção Parcial</button>
        <button class="tab" onclick="openTab(event, 'cenario3')">Cenário 3 - Correção Total</button>
    </div>

    <div id="cenario1" class="tab-content active">
        <div class="container">
            <h2 style="color: #667eea; margin-bottom: 20px;">Cenário 1: Sem Correção de Viés</h2>
            <p style="color: #666; margin-bottom: 30px; font-size: 1.1em;">
                Análise dos dados brutos sem aplicação de correções. Este cenário mostra o estado original das avaliações.
            </p>
            {html_cenario_1}
        </div>
    </div>

    <div id="cenario2" class="tab-content">
        <div class="container">
            <h2 style="color: #667eea; margin-bottom: 20px;">Cenário 2: Com Correção Parcial</h2>
            <p style="color: #666; margin-bottom: 30px; font-size: 1.1em;">
                Aplicação de correção moderada de viés. Este cenário demonstra o impacto de uma correção parcial.
            </p>
            {html_cenario_2}
        </div>
    </div>

    <div id="cenario3" class="tab-content">
        <div class="container">
            <h2 style="color: #667eea; margin-bottom: 20px;">Cenário 3: Com Correção Total</h2>
            <p style="color: #666; margin-bottom: 30px; font-size: 1.1em;">
                Aplicação completa de correção de viés. Este cenário mostra o resultado da correção máxima possível.
            </p>
            {html_cenario_3}
        </div>
    </div>

    <div class="footer">
        <p><strong>Framework de Redução de Viés</strong></p>
        <p>Dashboard Interativo - Todos os gráficos são interativos (hover para detalhes)</p>
        <p style="margin-top: 10px; font-size: 0.9em; color: #999;">
            Para exportar como PDF: Use a função de impressão do navegador (Ctrl+P) e selecione "Salvar como PDF"
        </p>
    </div>

    <button class="export-btn" onclick="window.print()">
        📄 Exportar como PDF
    </button>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tabs;

            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].classList.remove("active");
            }}

            tabs = document.getElementsByClassName("tab");
            for (i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove("active");
            }}

            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }}

        // Ajusta altura dos gráficos em telas menores
        window.addEventListener('resize', function() {{
            if (window.innerWidth < 768) {{
                var plots = document.querySelectorAll('.js-plotly-plot');
                plots.forEach(function(plot) {{
                    Plotly.relayout(plot, {{height: 400}});
                }});
            }}
        }});
    </script>
</body>
</html>
"""

        # Salva arquivo
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html_template)

        print(f"\n✓ Dashboard HTML salvo: {caminho}")
        print(f"  Abra o arquivo no navegador para visualizar")
        print(f"  Para exportar como PDF: Ctrl+P > Salvar como PDF")

        return caminho
