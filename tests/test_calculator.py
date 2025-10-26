"""
計算機能のテスト
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    Material, MaterialType, StructuralElement, 
    Design, Load, LoadType, STANDARD_MATERIALS
)
from src.calculator import StructuralCalculator, CalculationResult


class TestStructuralCalculator(unittest.TestCase):
    """StructuralCalculatorクラスのテスト"""
    
    def setUp(self):
        """テストの準備"""
        self.calculator = StructuralCalculator()
        self.material = STANDARD_MATERIALS["SS400"]
        
        # テスト用の梁
        self.beam = StructuralElement(
            name="テスト梁",
            material=self.material,
            length=6.0,
            cross_section_area=0.01,
            moment_of_inertia=0.0001
        )
        self.beam.loads.append(Load(LoadType.DEAD, 5000, 3.0))
        
        # テスト用の柱
        self.column = StructuralElement(
            name="テスト柱",
            material=self.material,
            length=3.5,
            cross_section_area=0.015,
            moment_of_inertia=0.00015
        )
        self.column.loads.append(Load(LoadType.DEAD, 10000, 3.5))
    
    def test_beam_calculation(self):
        """梁の計算テスト"""
        result = self.calculator.calculate_beam_stress(
            self.beam, 
            support_type="simple"
        )
        
        self.assertIsInstance(result, CalculationResult)
        self.assertEqual(result.element_name, "テスト梁")
        self.assertGreater(result.max_stress, 0)
        self.assertGreater(result.allowable_stress, 0)
        self.assertGreater(result.max_deflection, 0)
        self.assertIsInstance(result.is_safe, bool)
    
    def test_column_calculation(self):
        """柱の計算テスト"""
        result = self.calculator.calculate_column_stress(
            self.column,
            effective_length_factor=1.0
        )
        
        self.assertIsInstance(result, CalculationResult)
        self.assertEqual(result.element_name, "テスト柱")
        self.assertGreater(result.max_stress, 0)
        self.assertGreater(result.allowable_stress, 0)
        self.assertIsInstance(result.is_safe, bool)
        
        # 座屈に関する詳細情報の確認
        self.assertIn('slenderness_ratio', result.details)
        self.assertIn('buckling_safety_factor', result.details)
    
    def test_design_calculation(self):
        """設計全体の計算テスト"""
        design = Design(
            name="テスト設計",
            description="計算テスト用"
        )
        design.add_element(self.beam)
        design.add_element(self.column)
        
        results = self.calculator.calculate_design(design)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(len(self.calculator.results), 2)
    
    def test_summary(self):
        """サマリー取得のテスト"""
        design = Design(name="テスト設計")
        design.add_element(self.beam)
        design.add_element(self.column)
        
        self.calculator.calculate_design(design)
        summary = self.calculator.get_summary()
        
        self.assertIn('total_elements', summary)
        self.assertIn('safe_elements', summary)
        self.assertIn('unsafe_elements', summary)
        self.assertIn('max_stress_ratio', summary)
        self.assertIn('overall_safe', summary)
        
        self.assertEqual(summary['total_elements'], 2)
        self.assertIsInstance(summary['overall_safe'], bool)
    
    def test_stress_ratio(self):
        """応力比の計算テスト"""
        result = self.calculator.calculate_beam_stress(self.beam)
        
        # 応力比は max_stress / allowable_stress
        expected_ratio = result.max_stress / result.allowable_stress
        self.assertAlmostEqual(result.stress_ratio, expected_ratio)


class TestCalculationResult(unittest.TestCase):
    """CalculationResultクラスのテスト"""
    
    def test_result_creation(self):
        """計算結果オブジェクトの作成テスト"""
        result = CalculationResult(
            element_name="テスト要素",
            max_stress=100e6,
            allowable_stress=150e6,
            stress_ratio=100e6/150e6,
            max_deflection=0.01,
            is_safe=True,
            details={"test": "data"}
        )
        
        self.assertEqual(result.element_name, "テスト要素")
        self.assertTrue(result.is_safe)
        self.assertLess(result.stress_ratio, 1.0)


if __name__ == '__main__':
    unittest.main()
