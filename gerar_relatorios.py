#!/usr/bin/env python3
"""
Script Simples para Gerar Relatórios

Execute este script para gerar todos os relatórios:
    python gerar_relatorios.py

Os relatórios serão salvos em:
    - reports/graficos/     (42 gráficos PNG)
    - reports/powerpoint/   (Apresentação PowerPoint)
    - reports/excel/        (Relatório Excel)
    - reports/dashboards/   (Dashboard HTML)
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Gera todos os relatórios automaticamente"""

    print("=" * 80)
    print("GERADOR DE RELATÓRIOS - BiasRemoveFramework".center(80))
    print("=" * 80)
    print()
    print("Este script irá gerar:")
    print("  ✓ 42 gráficos PNG em alta resolução (300 DPI)")
    print("  ✓ Apresentação PowerPoint completa (~50 slides)")
    print("  ✓ Relatório Excel formatado (4 abas)")
    print("  ✓ Dashboard HTML interativo")
    print()
    print("Aguarde... este processo pode levar alguns minutos.")
    print()

    # Importa e executa o demo_relatorios
    try:
        # Remove a pasta reports antiga se existir
        import shutil
        reports_dir = Path("reports")
        if reports_dir.exists():
            print("Limpando relatórios antigos...")
            for item in reports_dir.iterdir():
                if item.is_dir() and item.name in ['powerpoint', 'excel', 'dashboards', 'graficos']:
                    shutil.rmtree(item)
                    item.mkdir()
            print("✓ Limpeza concluída\n")

        # Executa a geração
        from demo_relatorios import main as demo_main
        demo_main()

        print()
        print("=" * 80)
        print("RELATÓRIOS GERADOS COM SUCESSO!".center(80))
        print("=" * 80)
        print()
        print("Os arquivos foram salvos em:")
        print()

        # Lista os arquivos gerados
        ppt_files = list(Path("reports/powerpoint").glob("*.pptx"))
        excel_files = list(Path("reports/excel").glob("*.xlsx"))
        html_files = list(Path("reports/dashboards").glob("*.html"))
        png_count = len(list(Path("reports/graficos").glob("**/*.png")))

        if ppt_files:
            print(f"  📑 PowerPoint: {ppt_files[0]}")
        if excel_files:
            print(f"  📋 Excel:      {excel_files[0]}")
        if html_files:
            print(f"  🌐 Dashboard:  {html_files[0]}")
        print(f"  🎨 Gráficos:   {png_count} arquivos PNG em reports/graficos/")
        print()

        print("Como usar:")
        print("  - PowerPoint: Abra com MS PowerPoint, LibreOffice ou Google Slides")
        print("  - Excel:      Abra com MS Excel, LibreOffice Calc ou Google Sheets")
        print("  - Dashboard:  Abra o arquivo .html no seu navegador")
        print("  - Gráficos:   Visualize os arquivos PNG em qualquer visualizador")
        print()

    except ImportError as e:
        print()
        print("❌ ERRO: Dependências não instaladas!")
        print()
        print("Por favor, instale as dependências primeiro:")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ ERRO ao gerar relatórios: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
