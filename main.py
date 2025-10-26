#!/usr/bin/env python3
"""
構造計算プログラム - メイン実行スクリプト

このスクリプトは、構造計算プログラムのデモンストレーションを行います。
"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.input_handler import InputHandler
from src.calculator import StructuralCalculator
from src.report_generator import ReportGenerator


def main():
    """メイン関数"""
    
    print("=" * 80)
    print("構造計算プログラム".center(80))
    print("=" * 80)
    print()
    
    # サンプル設計を作成
    print("サンプル設計を作成中...")
    design = InputHandler.create_sample_design()
    print(f"✓ 設計 '{design.name}' を作成しました")
    print()
    
    # 設計情報を表示
    print("【設計情報】")
    print(design)
    print()
    
    # 構造要素の詳細を表示
    print("【構造要素の詳細】")
    for i, element in enumerate(design.elements, 1):
        print(f"\n{i}. {element}")
    print()
    
    # 構造計算を実行
    print("構造計算を実行中...")
    calculator = StructuralCalculator()
    results = calculator.calculate_design(design)
    print(f"✓ {len(results)}個の構造要素について計算が完了しました")
    print()
    
    # 結果を表示
    calculator.print_results()
    print()
    
    # レポートを生成
    print("レポートを生成中...")
    report_gen = ReportGenerator(design, results)
    
    # テキストレポート
    text_report = report_gen.generate_text_report("構造計算レポート.txt")
    print("✓ テキストレポートを '構造計算レポート.txt' に保存しました")
    
    # CSVレポート
    report_gen.generate_csv_report("構造計算レポート.csv")
    print("✓ CSVレポートを '構造計算レポート.csv' に保存しました")
    
    # JSONレポート
    report_gen.generate_json_report("構造計算レポート.json")
    print("✓ JSONレポートを '構造計算レポート.json' に保存しました")
    
    # HTMLレポート
    report_gen.generate_html_report("構造計算レポート.html")
    print("✓ HTMLレポートを '構造計算レポート.html' に保存しました")
    print()
    
    print("=" * 80)
    print("全ての処理が完了しました！")
    print("生成されたレポートファイルをご確認ください。")
    print("=" * 80)


def demo_json_input():
    """JSON形式からの読み込みデモ"""
    
    print("\n" + "=" * 80)
    print("JSON形式からの読み込みデモ".center(80))
    print("=" * 80)
    print()
    
    json_file = "examples/sample_design.json"
    
    if not Path(json_file).exists():
        print(f"エラー: '{json_file}' が見つかりません")
        return
    
    print(f"'{json_file}' から設計を読み込み中...")
    design = InputHandler.load_design_from_json(json_file)
    print(f"✓ 設計 '{design.name}' を読み込みました")
    print()
    
    print(design)
    print()
    
    # 構造計算を実行
    print("構造計算を実行中...")
    calculator = StructuralCalculator()
    
    # 要素タイプを指定（JSONファイルの要素名に基づく）
    element_types = {}
    for elem in design.elements:
        if '梁' in elem.name:
            element_types[elem.name] = 'beam'
        elif '柱' in elem.name:
            element_types[elem.name] = 'column'
    
    results = calculator.calculate_design(design, element_types)
    print(f"✓ {len(results)}個の構造要素について計算が完了しました")
    print()
    
    # 結果を表示
    calculator.print_results()


if __name__ == "__main__":
    # 基本デモを実行
    main()
    
    # JSON読み込みデモを実行
    demo_json_input()
