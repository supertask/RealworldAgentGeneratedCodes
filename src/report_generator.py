"""
レポート生成モジュール

このモジュールは、構造計算の結果をレポート形式で出力します。
テキスト、HTML、CSVなど、複数の形式に対応しています。
"""

import json
import csv
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from .models import Design, StructuralElement
from .calculator import CalculationResult, StructuralCalculator


class ReportGenerator:
    """
    レポート生成クラス
    
    構造計算の結果を様々な形式で出力します。
    """
    
    def __init__(self, design: Design, results: List[CalculationResult]):
        """
        コンストラクタ
        
        Args:
            design: 設計オブジェクト
            results: 計算結果のリスト
        """
        self.design = design
        self.results = results
        self.timestamp = datetime.now()
    
    def generate_text_report(self, output_path: Optional[str] = None) -> str:
        """
        テキスト形式のレポートを生成
        
        Args:
            output_path: 出力ファイルパス（Noneの場合は文字列を返すのみ）
            
        Returns:
            レポートの文字列
        """
        lines = []
        lines.append("=" * 80)
        lines.append("構造計算レポート".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        # 設計情報
        lines.append("【設計情報】")
        lines.append(f"  設計名: {self.design.name}")
        lines.append(f"  説明: {self.design.description}")
        lines.append(f"  作成日時: {self.timestamp.strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append(f"  構造要素数: {len(self.design.elements)}")
        lines.append(f"  使用材料数: {len(self.design.materials)}")
        lines.append("")
        
        # メタデータ
        if self.design.metadata:
            lines.append("【メタデータ】")
            for key, value in self.design.metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        # 使用材料
        lines.append("【使用材料】")
        for i, material in enumerate(self.design.materials, 1):
            lines.append(f"\n{i}. {material.name}")
            lines.append(f"   種類: {material.material_type.value}")
            lines.append(f"   密度: {material.density:.1f} kg/m³")
            lines.append(f"   ヤング率: {material.youngs_modulus/1e9:.1f} GPa")
            lines.append(f"   降伏強度: {material.yield_strength/1e6:.1f} MPa")
            lines.append(f"   許容応力: {material.allowable_stress()/1e6:.1f} MPa")
        lines.append("")
        
        # 構造要素
        lines.append("【構造要素】")
        for i, element in enumerate(self.design.elements, 1):
            lines.append(f"\n{i}. {element.name}")
            lines.append(f"   材料: {element.material.name}")
            lines.append(f"   長さ: {element.length:.2f} m")
            lines.append(f"   断面積: {element.cross_section_area*1e4:.2f} cm²")
            lines.append(f"   自重: {element.self_weight():.2f} N")
            lines.append(f"   荷重数: {len(element.loads)}")
            for load in element.loads:
                lines.append(f"     - {load}")
        lines.append("")
        
        # 計算結果
        lines.append("【計算結果】")
        for i, result in enumerate(self.results, 1):
            status = "✓ 安全" if result.is_safe else "✗ 危険"
            lines.append(f"\n{i}. {result.element_name}")
            lines.append(f"   要素タイプ: {result.details.get('element_type', '不明')}")
            lines.append(f"   最大応力: {result.max_stress/1e6:.2f} MPa")
            lines.append(f"   許容応力: {result.allowable_stress/1e6:.2f} MPa")
            lines.append(f"   応力比: {result.stress_ratio:.2%}")
            
            if result.details.get('element_type') == '梁':
                lines.append(f"   最大たわみ: {result.max_deflection*1000:.2f} mm")
                lines.append(f"   たわみ制限: {result.details.get('deflection_limit', 0)*1000:.2f} mm")
                lines.append(f"   たわみ比: {result.details.get('deflection_ratio', 0):.2%}")
            elif result.details.get('element_type') == '柱':
                lines.append(f"   細長比: {result.details.get('slenderness_ratio', 0):.1f}")
                lines.append(f"   座屈安全率: {result.details.get('buckling_safety_factor', 0):.2f}")
            
            lines.append(f"   判定: {status}")
        lines.append("")
        
        # 総合評価
        safe_count = sum(1 for r in self.results if r.is_safe)
        unsafe_count = len(self.results) - safe_count
        max_stress_ratio = max(r.stress_ratio for r in self.results) if self.results else 0.0
        
        lines.append("【総合評価】")
        lines.append(f"  総要素数: {len(self.results)}")
        lines.append(f"  安全な要素: {safe_count}")
        lines.append(f"  危険な要素: {unsafe_count}")
        lines.append(f"  最大応力比: {max_stress_ratio:.2%}")
        
        if unsafe_count == 0:
            lines.append("  総合判定: ✓ 全ての要素が安全です")
        else:
            lines.append("  総合判定: ✗ 一部の要素に問題があります")
            lines.append("\n  【推奨事項】")
            for result in self.results:
                if not result.is_safe:
                    if result.stress_ratio > 1.0:
                        lines.append(f"  - {result.element_name}: 断面を大きくするか、より強度の高い材料を使用してください")
                    if result.details.get('deflection_ratio', 0) > 1.0:
                        lines.append(f"  - {result.element_name}: たわみが大きすぎます。剛性を上げてください")
        
        lines.append("")
        lines.append("=" * 80)
        
        report_text = "\n".join(lines)
        
        # ファイル出力
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text
    
    def generate_csv_report(self, output_path: str) -> None:
        """
        CSV形式のレポートを生成
        
        Args:
            output_path: 出力ファイルパス
        """
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # ヘッダー
            writer.writerow([
                '要素名', '要素タイプ', '材料',
                '最大応力(MPa)', '許容応力(MPa)', '応力比',
                '最大たわみ(mm)', '判定'
            ])
            
            # データ行
            for result in self.results:
                element = next(
                    (e for e in self.design.elements if e.name == result.element_name),
                    None
                )
                
                writer.writerow([
                    result.element_name,
                    result.details.get('element_type', '不明'),
                    element.material.name if element else '不明',
                    f"{result.max_stress/1e6:.2f}",
                    f"{result.allowable_stress/1e6:.2f}",
                    f"{result.stress_ratio:.4f}",
                    f"{result.max_deflection*1000:.2f}",
                    '安全' if result.is_safe else '危険'
                ])
    
    def generate_json_report(self, output_path: str) -> None:
        """
        JSON形式のレポートを生成
        
        Args:
            output_path: 出力ファイルパス
        """
        report_data = {
            "design": {
                "name": self.design.name,
                "description": self.design.description,
                "metadata": self.design.metadata
            },
            "timestamp": self.timestamp.isoformat(),
            "materials": [
                {
                    "name": mat.name,
                    "type": mat.material_type.value,
                    "density": mat.density,
                    "youngs_modulus": mat.youngs_modulus,
                    "yield_strength": mat.yield_strength,
                    "allowable_stress": mat.allowable_stress()
                }
                for mat in self.design.materials
            ],
            "elements": [
                {
                    "name": elem.name,
                    "material": elem.material.name,
                    "length": elem.length,
                    "cross_section_area": elem.cross_section_area,
                    "self_weight": elem.self_weight(),
                    "total_load": elem.total_load()
                }
                for elem in self.design.elements
            ],
            "results": [
                {
                    "element_name": res.element_name,
                    "element_type": res.details.get('element_type', '不明'),
                    "max_stress": res.max_stress,
                    "allowable_stress": res.allowable_stress,
                    "stress_ratio": res.stress_ratio,
                    "max_deflection": res.max_deflection,
                    "is_safe": res.is_safe,
                    "details": res.details
                }
                for res in self.results
            ],
            "summary": {
                "total_elements": len(self.results),
                "safe_elements": sum(1 for r in self.results if r.is_safe),
                "unsafe_elements": sum(1 for r in self.results if not r.is_safe),
                "max_stress_ratio": max(r.stress_ratio for r in self.results) if self.results else 0.0,
                "overall_safe": all(r.is_safe for r in self.results)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    def generate_html_report(self, output_path: str) -> None:
        """
        HTML形式のレポートを生成
        
        Args:
            output_path: 出力ファイルパス
        """
        html_template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>構造計算レポート - {design_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #34495e;
            color: white;
        }}
        .safe {{
            color: #27ae60;
            font-weight: bold;
        }}
        .unsafe {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .summary-item {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .summary-label {{
            font-weight: bold;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>構造計算レポート</h1>
        <p>{design_name}</p>
        <p>作成日時: {timestamp}</p>
    </div>
    
    {content}
</body>
</html>
"""
        
        # コンテンツ生成
        content_parts = []
        
        # 設計情報
        content_parts.append('<div class="section">')
        content_parts.append('<h2>設計情報</h2>')
        content_parts.append(f'<p><strong>説明:</strong> {self.design.description}</p>')
        content_parts.append(f'<p><strong>構造要素数:</strong> {len(self.design.elements)}</p>')
        content_parts.append(f'<p><strong>使用材料数:</strong> {len(self.design.materials)}</p>')
        content_parts.append('</div>')
        
        # 計算結果テーブル
        content_parts.append('<div class="section">')
        content_parts.append('<h2>計算結果</h2>')
        content_parts.append('<table>')
        content_parts.append('<tr>')
        content_parts.append('<th>要素名</th><th>タイプ</th><th>最大応力(MPa)</th>')
        content_parts.append('<th>許容応力(MPa)</th><th>応力比</th><th>判定</th>')
        content_parts.append('</tr>')
        
        for result in self.results:
            status_class = 'safe' if result.is_safe else 'unsafe'
            status_text = '✓ 安全' if result.is_safe else '✗ 危険'
            
            content_parts.append('<tr>')
            content_parts.append(f'<td>{result.element_name}</td>')
            content_parts.append(f'<td>{result.details.get("element_type", "不明")}</td>')
            content_parts.append(f'<td>{result.max_stress/1e6:.2f}</td>')
            content_parts.append(f'<td>{result.allowable_stress/1e6:.2f}</td>')
            content_parts.append(f'<td>{result.stress_ratio:.2%}</td>')
            content_parts.append(f'<td class="{status_class}">{status_text}</td>')
            content_parts.append('</tr>')
        
        content_parts.append('</table>')
        content_parts.append('</div>')
        
        # 総合評価
        safe_count = sum(1 for r in self.results if r.is_safe)
        unsafe_count = len(self.results) - safe_count
        max_stress_ratio = max(r.stress_ratio for r in self.results) if self.results else 0.0
        overall_status = '✓ 全ての要素が安全です' if unsafe_count == 0 else '✗ 一部の要素に問題があります'
        overall_class = 'safe' if unsafe_count == 0 else 'unsafe'
        
        content_parts.append('<div class="section">')
        content_parts.append('<h2>総合評価</h2>')
        content_parts.append('<div class="summary">')
        content_parts.append(f'<div class="summary-item"><span class="summary-label">総要素数:</span> {len(self.results)}</div>')
        content_parts.append(f'<div class="summary-item"><span class="summary-label">安全な要素:</span> {safe_count}</div>')
        content_parts.append(f'<div class="summary-item"><span class="summary-label">危険な要素:</span> {unsafe_count}</div>')
        content_parts.append(f'<div class="summary-item"><span class="summary-label">最大応力比:</span> {max_stress_ratio:.2%}</div>')
        content_parts.append(f'<p class="{overall_class}" style="font-size: 18px; margin-top: 15px;">{overall_status}</p>')
        content_parts.append('</div>')
        content_parts.append('</div>')
        
        # HTML生成
        html = html_template.format(
            design_name=self.design.name,
            timestamp=self.timestamp.strftime('%Y年%m月%d日 %H:%M:%S'),
            content='\n'.join(content_parts)
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
