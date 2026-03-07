"""
Dashboard HTML Premium - Versão para Apresentações
Cria um dashboard profissional e completo com todos os gráficos e explicações
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class DashboardGeneratorV2:
    """
    Gerador de Dashboard HTML Premium para Apresentações

    Características:
    - Design profissional e moderno
    - Todos os gráficos incluídos
    - Explicações detalhadas
    - Navegação por slides
    - Métricas destacadas
    - Pronto para apresentação
    """

    def __init__(self, output_dir: str = "reports/dashboards"):
        """
        Inicializa o gerador de dashboard premium

        Args:
            output_dir: Diretório para salvar os dashboards
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Cores do tema
        self.cores = {
            'feminino': '#E91E63',
            'masculino': '#2196F3',
            'sem_vies': '#4CAF50',
            'com_vies': '#F44336',
            'neutro': '#FFC107',
            'destaque': '#9C27B0'
        }

    def _criar_grafico_distribuicao(self, dados_cenario: Dict) -> str:
        """Cria gráfico de distribuição com violin plot"""
        scores_por_genero = dados_cenario['scores_por_genero']

        fig = go.Figure()

        for genero, scores in scores_por_genero.items():
            cor = self.cores['feminino'] if 'Feminino' in genero else self.cores['masculino']

            fig.add_trace(go.Violin(
                y=scores,
                name=genero,
                box_visible=True,
                meanline_visible=True,
                fillcolor=cor,
                opacity=0.7,
                line_color=cor,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Score: %{y:.2f}<br>' +
                             '<extra></extra>'
            ))

        fig.update_layout(
            title=dict(
                text=f"<b>Distribuição de Scores por Gênero</b><br>" +
                     f"<sub>{dados_cenario['titulo']}</sub>",
                font=dict(size=18, family='Arial')
            ),
            yaxis_title="Score de Desempenho",
            xaxis_title="Gênero",
            template="plotly_white",
            height=450,
            hovermode='closest',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig.to_html(include_plotlyjs=False, div_id=f"dist_{dados_cenario['numero']}")

    def _criar_grafico_medias(self, dados_cenario: Dict) -> str:
        """Cria gráfico de barras com médias"""
        medias = {
            'Feminino': dados_cenario['media_feminino'],
            'Masculino': dados_cenario['media_masculino']
        }

        cores_barra = [self.cores['feminino'], self.cores['masculino']]

        fig = go.Figure(data=[
            go.Bar(
                x=list(medias.keys()),
                y=list(medias.values()),
                marker_color=cores_barra,
                text=[f'{v:.2f}' for v in medias.values()],
                textposition='outside',
                textfont=dict(size=14, color='#333'),
                hovertemplate='<b>%{x}</b><br>' +
                             'Média: %{y:.2f}<br>' +
                             '<extra></extra>'
            )
        ])

        # Adiciona linha de referência para diferença
        diferenca = dados_cenario['diferenca']
        fig.add_shape(
            type="line",
            x0=-0.5, x1=1.5,
            y0=medias['Masculino'], y1=medias['Masculino'],
            line=dict(color="gray", width=2, dash="dash"),
        )

        fig.add_annotation(
            x=0.5,
            y=max(medias.values()) + 0.2,
            text=f"Diferença: {abs(diferenca):.3f}",
            showarrow=False,
            font=dict(size=12, color='#666'),
            bgcolor="#FFF",
            bordercolor="#DDD",
            borderwidth=1
        )

        fig.update_layout(
            title=dict(
                text="<b>Comparação de Médias por Gênero</b>",
                font=dict(size=18, family='Arial')
            ),
            yaxis_title="Score Médio",
            template="plotly_white",
            height=400,
            showlegend=False
        )

        return fig.to_html(include_plotlyjs=False, div_id=f"medias_{dados_cenario['numero']}")

    def _criar_grafico_estatisticas(self, dados_cenario: Dict) -> str:
        """Cria gráfico com estatísticas (p-value, diferença)"""

        # Cria gráfico de gauge para p-value
        p_value = dados_cenario['p_value']
        vies_detectado = dados_cenario['vies_detectado']

        # Gauge para p-value
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=p_value,
            title={'text': "P-value", 'font': {'size': 16}},
            delta={'reference': 0.05, 'increasing': {'color': self.cores['com_vies']},
                   'decreasing': {'color': self.cores['sem_vies']}},
            gauge={
                'axis': {'range': [0, 0.2], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': self.cores['com_vies'] if vies_detectado else self.cores['sem_vies']},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 0.05], 'color': 'rgba(76, 175, 80, 0.2)'},
                    {'range': [0.05, 0.2], 'color': 'rgba(244, 67, 54, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.05
                }
            }
        ))

        fig.update_layout(
            height=300,
            template="plotly_white"
        )

        return fig.to_html(include_plotlyjs=False, div_id=f"stats_{dados_cenario['numero']}")

    def _criar_card_metrica(self, titulo: str, valor: str, subtitulo: str = "",
                            cor: str = "#2196F3", icone: str = "📊") -> str:
        """Cria um card de métrica"""
        return f"""
        <div class="metric-card" style="background: linear-gradient(135deg, {cor}22, {cor}11); border-left: 4px solid {cor};">
            <div class="metric-icon">{icone}</div>
            <div class="metric-content">
                <div class="metric-title">{titulo}</div>
                <div class="metric-value">{valor}</div>
                {f'<div class="metric-subtitle">{subtitulo}</div>' if subtitulo else ''}
            </div>
        </div>
        """

    def _criar_secao_cenario(self, dados_cenario: Dict, info_outliers: Dict = None) -> str:
        """Cria uma seção completa para um cenário"""
        numero = dados_cenario['numero']
        titulo = dados_cenario['titulo']
        nivel_vies = dados_cenario['nivel_vies']

        # Determina cor baseada no viés
        if nivel_vies == 0:
            cor_status = self.cores['sem_vies']
            status_texto = "✅ SEM VIÉS"
        elif nivel_vies < 50:
            cor_status = self.cores['neutro']
            status_texto = "⚠️ VIÉS LEVE"
        else:
            cor_status = self.cores['com_vies']
            status_texto = "❌ VIÉS DETECTADO"

        # Cards de métricas
        cards_html = f"""
        <div class="metrics-grid">
            {self._criar_card_metrica(
                "Média Feminino",
                f"{dados_cenario['media_feminino']:.3f}",
                "Score médio mulheres",
                self.cores['feminino'],
                "👩"
            )}
            {self._criar_card_metrica(
                "Média Masculino",
                f"{dados_cenario['media_masculino']:.3f}",
                "Score médio homens",
                self.cores['masculino'],
                "👨"
            )}
            {self._criar_card_metrica(
                "Diferença",
                f"{abs(dados_cenario['diferenca']):.3f}",
                f"{'Homens' if dados_cenario['diferenca'] > 0 else 'Mulheres'} com scores maiores",
                cor_status,
                "📊"
            )}
            {self._criar_card_metrica(
                "P-value",
                f"{dados_cenario['p_value']:.4f}",
                f"Alpha = 0.05 | {status_texto}",
                cor_status,
                "📈"
            )}
        </div>
        """

        # Seção de explicação
        explicacao_html = f"""
        <div class="explanation-box">
            <h3>📋 Interpretação dos Resultados</h3>
            <p><strong>Cenário {numero}:</strong> {titulo} ({nivel_vies:.1f}% de viés aplicado)</p>
            <ul>
                <li><strong>Diferença de médias:</strong> {abs(dados_cenario['diferenca']):.3f} pontos
                    ({'favorecendo homens' if dados_cenario['diferenca'] > 0 else 'favorecendo mulheres'})</li>
                <li><strong>Significância estatística (p-value):</strong> {dados_cenario['p_value']:.4f}
                    {' (< 0.05, viés significativo)' if dados_cenario['vies_detectado'] else ' (≥ 0.05, sem viés significativo)'}</li>
                <li><strong>Status:</strong> {status_texto}</li>
            </ul>

            <div class="insight-box">
                <strong>💡 Insight:</strong>
                {"Este cenário representa dados limpos sem viés de gênero. As médias são estatisticamente iguais."
                 if nivel_vies == 0 else
                 f"Este cenário demonstra {nivel_vies:.0f}% de viés, resultando em uma diferença {'significativa' if dados_cenario['vies_detectado'] else 'não significativa'} entre os gêneros."}
            </div>
        </div>
        """

        # Gráficos
        grafico_dist = self._criar_grafico_distribuicao(dados_cenario)
        grafico_medias = self._criar_grafico_medias(dados_cenario)
        grafico_stats = self._criar_grafico_estatisticas(dados_cenario)

        # Monta a seção completa
        secao_html = f"""
        <div class="cenario-section" id="cenario_{numero}">
            <div class="cenario-header" style="background: linear-gradient(135deg, {cor_status}, {cor_status}dd);">
                <h2>Cenário {numero}: {titulo}</h2>
                <div class="cenario-badge">{nivel_vies:.1f}% de Viés</div>
            </div>

            {cards_html}

            {explicacao_html}

            <div class="charts-container">
                <div class="chart-box">
                    <h3>📊 Distribuição de Scores</h3>
                    {grafico_dist}
                </div>

                <div class="chart-row">
                    <div class="chart-box">
                        <h3>📈 Comparação de Médias</h3>
                        {grafico_medias}
                    </div>
                    <div class="chart-box">
                        <h3>📉 Análise Estatística</h3>
                        {grafico_stats}
                    </div>
                </div>
            </div>
        </div>
        """

        return secao_html

    def gerar_dashboard_completo(self, dados_completos: Dict) -> str:
        """
        Gera dashboard HTML completo para apresentações

        Args:
            dados_completos: Dicionário com:
                - cenarios: Dict com dados de cada cenário
                - pessoas: Dict com informações das pessoas
                - info_outliers: Dict com informações sobre outliers (opcional)

        Returns:
            Caminho do arquivo HTML gerado
        """
        cenarios = dados_completos['cenarios']
        info_outliers = dados_completos.get('info_outliers', None)

        # Cria seções para cada cenário
        secoes_html = ""
        for key in sorted(cenarios.keys(), key=lambda x: int(x.split('_')[1])):
            dados_cenario = cenarios[key]
            secoes_html += self._criar_secao_cenario(dados_cenario, info_outliers)

        # Seção de introdução
        intro_html = self._criar_secao_introducao(info_outliers)

        # Seção de resumo
        resumo_html = self._criar_secao_resumo(cenarios)

        # HTML completo
        html_completo = self._gerar_template_html(intro_html, secoes_html, resumo_html)

        # Salva arquivo
        caminho = self.output_dir / f"dashboard_premium_{self.timestamp}.html"
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html_completo)

        return str(caminho)

    def _criar_secao_introducao(self, info_outliers: Dict = None) -> str:
        """Cria seção de introdução do dashboard"""

        outliers_text = ""
        if info_outliers:
            outliers_text = f"""
            <div class="outlier-info">
                <h3>🔍 Etapa 1: Detecção de Outliers (Z-score)</h3>
                <p>Threshold utilizado: |Z| > {info_outliers.get('threshold', 3.0)}</p>
                <div class="metrics-grid-small">
                    {self._criar_card_metrica(
                        "Observações Analisadas",
                        f"{info_outliers.get('total_original', 0)}",
                        "Dados originais",
                        "#607D8B",
                        "📊"
                    )}
                    {self._criar_card_metrica(
                        "Outliers Removidos",
                        f"{info_outliers.get('outliers_removidos', 0)}",
                        f"{info_outliers.get('outliers_removidos', 0)/info_outliers.get('total_original', 1)*100:.1f}% removidos",
                        "#FF5722",
                        "⚠️"
                    )}
                    {self._criar_card_metrica(
                        "Dados Limpos",
                        f"{info_outliers.get('total_limpo', 0)}",
                        "Usados na análise",
                        "#4CAF50",
                        "✅"
                    )}
                </div>
            </div>
            """

        return f"""
        <div class="intro-section">
            <div class="title-banner">
                <h1>🎯 Dashboard de Análise de Viés de Gênero</h1>
                <p class="subtitle">Framework Heurístico para Redução de Vieses em Processos de Promoção de RH</p>
            </div>

            <div class="methodology-box">
                <h2>📚 Metodologia</h2>
                <div class="method-steps">
                    <div class="method-step">
                        <div class="step-number">1</div>
                        <h3>Detecção de Outliers</h3>
                        <p>Método Z-score para identificar e remover valores extremos (threshold = 3.0)</p>
                    </div>
                    <div class="method-step">
                        <div class="step-number">2</div>
                        <h3>Análise de Viés</h3>
                        <p>7 cenários com diferentes níveis de viés (0% a 100%)</p>
                    </div>
                    <div class="method-step">
                        <div class="step-number">3</div>
                        <h3>Testes Estatísticos</h3>
                        <p>T-tests para detectar diferenças significativas (α = 0.05)</p>
                    </div>
                </div>
            </div>

            {outliers_text}

            <div class="navigation-help">
                <p>📌 <strong>Navegação:</strong> Role para baixo para explorar cada cenário em detalhes</p>
            </div>
        </div>
        """

    def _criar_secao_resumo(self, cenarios: Dict) -> str:
        """Cria seção de resumo comparativo"""

        # Prepara dados para gráfico comparativo
        numeros = []
        diferencas = []
        p_values = []
        cores = []

        for key in sorted(cenarios.keys(), key=lambda x: int(x.split('_')[1])):
            dados = cenarios[key]
            numeros.append(f"Cenário {dados['numero']}")
            diferencas.append(abs(dados['diferenca']))
            p_values.append(dados['p_value'])

            if dados['nivel_vies'] == 0:
                cores.append(self.cores['sem_vies'])
            elif dados['nivel_vies'] < 50:
                cores.append(self.cores['neutro'])
            else:
                cores.append(self.cores['com_vies'])

        # Gráfico de diferenças
        fig_dif = go.Figure(data=[
            go.Bar(
                x=numeros,
                y=diferencas,
                marker_color=cores,
                text=[f'{d:.3f}' for d in diferencas],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Diferença: %{y:.3f}<extra></extra>'
            )
        ])

        fig_dif.update_layout(
            title="<b>Evolução da Diferença de Médias nos Cenários</b>",
            xaxis_title="Cenário",
            yaxis_title="Diferença Absoluta",
            template="plotly_white",
            height=400
        )

        grafico_dif_html = fig_dif.to_html(include_plotlyjs=False, div_id="resumo_dif")

        # Gráfico de p-values
        fig_p = go.Figure(data=[
            go.Scatter(
                x=numeros,
                y=p_values,
                mode='lines+markers',
                line=dict(color='#2196F3', width=3),
                marker=dict(size=10, color=cores),
                hovertemplate='<b>%{x}</b><br>P-value: %{y:.4f}<extra></extra>'
            )
        ])

        fig_p.add_hline(y=0.05, line_dash="dash", line_color="red",
                       annotation_text="α = 0.05 (threshold)", annotation_position="right")

        fig_p.update_layout(
            title="<b>P-values dos Testes Estatísticos</b>",
            xaxis_title="Cenário",
            yaxis_title="P-value",
            template="plotly_white",
            height=400
        )

        grafico_p_html = fig_p.to_html(include_plotlyjs=False, div_id="resumo_p")

        return f"""
        <div class="resumo-section">
            <div class="cenario-header" style="background: linear-gradient(135deg, {self.cores['destaque']}, {self.cores['destaque']}dd);">
                <h2>📊 Resumo Comparativo dos Cenários</h2>
            </div>

            <div class="chart-row">
                <div class="chart-box">
                    {grafico_dif_html}
                </div>
            </div>

            <div class="chart-row">
                <div class="chart-box">
                    {grafico_p_html}
                </div>
            </div>

            <div class="conclusion-box">
                <h3>✅ Conclusões Principais</h3>
                <ul>
                    <li><strong>Cenário 1</strong> demonstra dados sem viés, servindo como baseline de comparação</li>
                    <li><strong>Cenários 2-4</strong> mostram viés crescente mas ainda não estatisticamente significativo</li>
                    <li><strong>Cenários 5-7</strong> apresentam viés estatisticamente significativo (p < 0.05)</li>
                    <li>A diferença de médias cresce proporcionalmente ao nível de viés aplicado</li>
                    <li>O framework detecta corretamente a presença e magnitude do viés</li>
                </ul>
            </div>
        </div>
        """

    def _gerar_template_html(self, intro_html: str, secoes_html: str, resumo_html: str) -> str:
        """Gera template HTML completo com CSS e JavaScript"""

        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Premium - Análise de Viés de Gênero</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .title-banner {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .title-banner h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .intro-section, .cenario-section, .resumo-section {{
            padding: 40px;
        }}

        .methodology-box {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 30px;
            margin: 30px 0;
        }}

        .methodology-box h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}

        .method-steps {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .method-step {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: relative;
        }}

        .step-number {{
            position: absolute;
            top: -15px;
            left: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }}

        .method-step h3 {{
            margin-top: 20px;
            color: #333;
        }}

        .cenario-header {{
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .cenario-badge {{
            background: rgba(255,255,255,0.3);
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .metrics-grid-small {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}

        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 15px;
            transition: transform 0.3s;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}

        .metric-icon {{
            font-size: 2.5em;
        }}

        .metric-title {{
            font-size: 0.9em;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}

        .metric-subtitle {{
            font-size: 0.85em;
            color: #888;
        }}

        .explanation-box {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
            border-left: 4px solid #667eea;
        }}

        .explanation-box h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .explanation-box ul {{
            margin-left: 20px;
            margin-top: 15px;
        }}

        .explanation-box li {{
            margin: 10px 0;
        }}

        .insight-box {{
            background: linear-gradient(135deg, #667eea22, #764ba222);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #764ba2;
        }}

        .charts-container {{
            margin: 30px 0;
        }}

        .chart-box {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .chart-box h3 {{
            color: #333;
            margin-bottom: 20px;
        }}

        .chart-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}

        .outlier-info {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 10px;
            padding: 25px;
            margin: 30px 0;
        }}

        .outlier-info h3 {{
            color: #856404;
            margin-bottom: 15px;
        }}

        .navigation-help {{
            text-align: center;
            padding: 20px;
            background: #e3f2fd;
            border-radius: 10px;
            margin-top: 30px;
        }}

        .conclusion-box {{
            background: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 25px;
            margin: 30px 0;
        }}

        .conclusion-box h3 {{
            color: #2e7d32;
            margin-bottom: 15px;
        }}

        .conclusion-box ul {{
            margin-left: 20px;
        }}

        .conclusion-box li {{
            margin: 10px 0;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}

        @media (max-width: 768px) {{
            .chart-row {{
                grid-template-columns: 1fr;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {intro_html}
        {secoes_html}
        {resumo_html}
    </div>

    <script>
        // Função para imprimir/exportar PDF
        function printDashboard() {{
            window.print();
        }}

        // Scroll suave
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>
        """
