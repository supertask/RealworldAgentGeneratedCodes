"""
構造計算モジュール

このモジュールは、構造要素の応力、変形、安全性などを計算します。
基本的な構造計算の手法を実装しています。
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .models import StructuralElement, Design, Load, LoadType


@dataclass
class CalculationResult:
    """
    計算結果を格納するクラス
    
    Attributes:
        element_name: 構造要素名
        max_stress: 最大応力 (N/m²)
        allowable_stress: 許容応力 (N/m²)
        stress_ratio: 応力比（最大応力/許容応力）
        max_deflection: 最大たわみ (m)
        is_safe: 安全かどうか
        details: 詳細情報
    """
    element_name: str
    max_stress: float
    allowable_stress: float
    stress_ratio: float
    max_deflection: float
    is_safe: bool
    details: Dict[str, any]
    
    def __str__(self) -> str:
        status = "✓ 安全" if self.is_safe else "✗ 危険"
        return (f"【{self.element_name}】\n"
                f"  最大応力: {self.max_stress/1e6:.2f} MPa\n"
                f"  許容応力: {self.allowable_stress/1e6:.2f} MPa\n"
                f"  応力比: {self.stress_ratio:.2%}\n"
                f"  最大たわみ: {self.max_deflection*1000:.2f} mm\n"
                f"  判定: {status}")


class StructuralCalculator:
    """
    構造計算を実行するクラス
    
    このクラスは、梁や柱などの構造要素に対して、
    応力、たわみ、安全性の計算を行います。
    """
    
    def __init__(self):
        """コンストラクタ"""
        self.results: List[CalculationResult] = []
    
    def calculate_beam_stress(
        self, 
        element: StructuralElement,
        support_type: str = "simple"
    ) -> CalculationResult:
        """
        梁の応力とたわみを計算
        
        単純支持梁を仮定し、中央集中荷重の場合の計算を行います。
        
        Args:
            element: 構造要素（梁）
            support_type: 支持条件 ("simple": 単純支持, "fixed": 固定支持)
            
        Returns:
            計算結果
        """
        L = element.length  # 梁の長さ (m)
        I = element.moment_of_inertia  # 断面二次モーメント (m⁴)
        E = element.material.youngs_modulus  # ヤング率 (N/m²)
        A = element.cross_section_area  # 断面積 (m²)
        
        # 合計荷重を計算（自重を含む）
        total_load = element.total_load() + element.self_weight()
        
        # 断面係数の計算（矩形断面を仮定）
        # Z = I / (h/2) where h = sqrt(I/A*12) for rectangular section
        # 簡略化: Z ≈ I / sqrt(A/6)
        section_modulus = I / math.sqrt(A / 6) if A > 0 else I * 2
        
        if support_type == "simple":
            # 単純支持梁、中央集中荷重の場合
            # 最大曲げモーメント: M = P*L/4
            max_moment = total_load * L / 4
            
            # 最大応力: σ = M / Z
            max_stress = max_moment / section_modulus
            
            # 最大たわみ: δ = P*L³/(48*E*I)
            max_deflection = (total_load * L**3) / (48 * E * I)
            
        elif support_type == "fixed":
            # 固定支持梁、中央集中荷重の場合
            # 最大曲げモーメント: M = P*L/8
            max_moment = total_load * L / 8
            max_stress = max_moment / section_modulus
            
            # 最大たわみ: δ = P*L³/(192*E*I)
            max_deflection = (total_load * L**3) / (192 * E * I)
            
        else:
            raise ValueError(f"未対応の支持条件: {support_type}")
        
        # 許容応力
        allowable_stress = element.material.allowable_stress()
        
        # 応力比
        stress_ratio = max_stress / allowable_stress
        
        # 安全性の判定
        # 応力比が1.0以下、かつたわみがL/250以下であれば安全
        deflection_limit = L / 250  # たわみの制限値
        is_safe = (stress_ratio <= 1.0) and (max_deflection <= deflection_limit)
        
        result = CalculationResult(
            element_name=element.name,
            max_stress=max_stress,
            allowable_stress=allowable_stress,
            stress_ratio=stress_ratio,
            max_deflection=max_deflection,
            is_safe=is_safe,
            details={
                "element_type": "梁",
                "support_type": support_type,
                "total_load": total_load,
                "max_moment": max_moment,
                "section_modulus": section_modulus,
                "deflection_limit": deflection_limit,
                "deflection_ratio": max_deflection / deflection_limit
            }
        )
        
        self.results.append(result)
        return result
    
    def calculate_column_stress(
        self, 
        element: StructuralElement,
        effective_length_factor: float = 1.0
    ) -> CalculationResult:
        """
        柱の応力と座屈を計算
        
        軸圧縮力を受ける柱の計算を行います。
        
        Args:
            element: 構造要素（柱）
            effective_length_factor: 有効座屈長さ係数
            
        Returns:
            計算結果
        """
        L = element.length  # 柱の長さ (m)
        A = element.cross_section_area  # 断面積 (m²)
        I = element.moment_of_inertia  # 断面二次モーメント (m⁴)
        E = element.material.youngs_modulus  # ヤング率 (N/m²)
        
        # 有効座屈長さ
        Le = L * effective_length_factor
        
        # 合計荷重（軸力）
        total_load = element.total_load() + element.self_weight()
        
        # 直接応力: σ = P / A
        direct_stress = total_load / A
        
        # オイラー座屈荷重: Pcr = π²*E*I / Le²
        euler_buckling_load = (math.pi**2 * E * I) / (Le**2)
        
        # 細長比: λ = Le / r, where r = sqrt(I/A)
        radius_of_gyration = math.sqrt(I / A)
        slenderness_ratio = Le / radius_of_gyration
        
        # 座屈応力
        buckling_stress = euler_buckling_load / A
        
        # 許容応力（座屈を考慮）
        # 細長比が大きい場合は座屈を考慮した許容応力を使用
        material_allowable = element.material.allowable_stress()
        
        if slenderness_ratio > 100:
            # 長柱の場合、座屈を考慮
            allowable_stress = min(material_allowable, buckling_stress / 2.0)
        else:
            # 短柱の場合
            allowable_stress = material_allowable
        
        # 応力比
        stress_ratio = direct_stress / allowable_stress
        
        # 座屈安全率
        buckling_safety_factor = euler_buckling_load / total_load if total_load > 0 else float('inf')
        
        # 安全性の判定
        # 応力比が1.0以下、かつ座屈安全率が2.0以上であれば安全
        is_safe = (stress_ratio <= 1.0) and (buckling_safety_factor >= 2.0)
        
        # たわみは柱の場合は考慮しないが、仮の値を設定
        max_deflection = 0.0
        
        result = CalculationResult(
            element_name=element.name,
            max_stress=direct_stress,
            allowable_stress=allowable_stress,
            stress_ratio=stress_ratio,
            max_deflection=max_deflection,
            is_safe=is_safe,
            details={
                "element_type": "柱",
                "total_load": total_load,
                "direct_stress": direct_stress,
                "euler_buckling_load": euler_buckling_load,
                "buckling_stress": buckling_stress,
                "slenderness_ratio": slenderness_ratio,
                "buckling_safety_factor": buckling_safety_factor,
                "effective_length_factor": effective_length_factor
            }
        )
        
        self.results.append(result)
        return result
    
    def calculate_design(
        self, 
        design: Design,
        element_types: Optional[Dict[str, str]] = None
    ) -> List[CalculationResult]:
        """
        設計全体の構造計算を実行
        
        Args:
            design: 設計オブジェクト
            element_types: 要素名をキー、要素タイプ("beam"/"column")を値とする辞書
            
        Returns:
            全要素の計算結果のリスト
        """
        self.results = []
        
        if element_types is None:
            # デフォルトの要素タイプ判定（名前に基づく）
            element_types = {}
            for elem in design.elements:
                if '梁' in elem.name or 'beam' in elem.name.lower():
                    element_types[elem.name] = 'beam'
                elif '柱' in elem.name or 'column' in elem.name.lower():
                    element_types[elem.name] = 'column'
                else:
                    # デフォルトは梁とする
                    element_types[elem.name] = 'beam'
        
        for element in design.elements:
            elem_type = element_types.get(element.name, 'beam')
            
            if elem_type == 'beam':
                self.calculate_beam_stress(element, support_type="simple")
            elif elem_type == 'column':
                self.calculate_column_stress(element, effective_length_factor=1.0)
            else:
                print(f"警告: 未知の要素タイプ '{elem_type}' for {element.name}")
        
        return self.results
    
    def get_summary(self) -> Dict[str, any]:
        """
        計算結果のサマリーを取得
        
        Returns:
            サマリー情報の辞書
        """
        if not self.results:
            return {
                "total_elements": 0,
                "safe_elements": 0,
                "unsafe_elements": 0,
                "max_stress_ratio": 0.0,
                "overall_safe": True
            }
        
        safe_count = sum(1 for r in self.results if r.is_safe)
        unsafe_count = len(self.results) - safe_count
        max_stress_ratio = max(r.stress_ratio for r in self.results)
        
        return {
            "total_elements": len(self.results),
            "safe_elements": safe_count,
            "unsafe_elements": unsafe_count,
            "max_stress_ratio": max_stress_ratio,
            "overall_safe": unsafe_count == 0
        }
    
    def print_results(self) -> None:
        """計算結果を出力"""
        print("=" * 60)
        print("構造計算結果")
        print("=" * 60)
        
        for result in self.results:
            print(result)
            print("-" * 60)
        
        summary = self.get_summary()
        print("\n【総合評価】")
        print(f"  総要素数: {summary['total_elements']}")
        print(f"  安全な要素: {summary['safe_elements']}")
        print(f"  危険な要素: {summary['unsafe_elements']}")
        print(f"  最大応力比: {summary['max_stress_ratio']:.2%}")
        
        if summary['overall_safe']:
            print("  総合判定: ✓ 全ての要素が安全です")
        else:
            print("  総合判定: ✗ 一部の要素に問題があります")
        
        print("=" * 60)
