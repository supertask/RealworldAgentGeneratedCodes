"""
モデルクラスのテスト
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


class TestMaterial(unittest.TestCase):
    """Materialクラスのテスト"""
    
    def setUp(self):
        """テストの準備"""
        self.material = Material(
            name="テスト材料",
            material_type=MaterialType.STEEL,
            density=7850,
            youngs_modulus=205e9,
            yield_strength=245e6,
            ultimate_strength=400e6,
            safety_factor=1.5
        )
    
    def test_material_creation(self):
        """材料オブジェクトの作成テスト"""
        self.assertEqual(self.material.name, "テスト材料")
        self.assertEqual(self.material.material_type, MaterialType.STEEL)
        self.assertEqual(self.material.density, 7850)
    
    def test_allowable_stress(self):
        """許容応力の計算テスト"""
        expected = 245e6 / 1.5
        self.assertAlmostEqual(self.material.allowable_stress(), expected)
    
    def test_standard_materials(self):
        """標準材料のテスト"""
        self.assertIn("SS400", STANDARD_MATERIALS)
        self.assertIn("C24", STANDARD_MATERIALS)
        self.assertIn("SUGI", STANDARD_MATERIALS)
        
        ss400 = STANDARD_MATERIALS["SS400"]
        self.assertEqual(ss400.material_type, MaterialType.STEEL)
        self.assertGreater(ss400.allowable_stress(), 0)


class TestLoad(unittest.TestCase):
    """Loadクラスのテスト"""
    
    def test_load_creation(self):
        """荷重オブジェクトの作成テスト"""
        load = Load(
            load_type=LoadType.DEAD,
            magnitude=1000,
            location=2.5,
            description="テスト荷重"
        )
        
        self.assertEqual(load.load_type, LoadType.DEAD)
        self.assertEqual(load.magnitude, 1000)
        self.assertEqual(load.location, 2.5)
        self.assertEqual(load.description, "テスト荷重")


class TestStructuralElement(unittest.TestCase):
    """StructuralElementクラスのテスト"""
    
    def setUp(self):
        """テストの準備"""
        self.material = STANDARD_MATERIALS["SS400"]
        self.element = StructuralElement(
            name="テスト梁",
            material=self.material,
            length=5.0,
            cross_section_area=0.01,
            moment_of_inertia=0.0001
        )
    
    def test_element_creation(self):
        """構造要素の作成テスト"""
        self.assertEqual(self.element.name, "テスト梁")
        self.assertEqual(self.element.length, 5.0)
        self.assertEqual(len(self.element.loads), 0)
    
    def test_self_weight(self):
        """自重の計算テスト"""
        # Volume = 0.01 * 5.0 = 0.05 m³
        # Mass = 0.05 * 7850 = 392.5 kg
        # Weight = 392.5 * 9.81 ≈ 3850.725 N
        expected_weight = 0.01 * 5.0 * 7850 * 9.81
        self.assertAlmostEqual(self.element.self_weight(), expected_weight, places=2)
    
    def test_total_load(self):
        """合計荷重の計算テスト"""
        self.element.loads.append(Load(LoadType.DEAD, 1000, 2.5))
        self.element.loads.append(Load(LoadType.LIVE, 500, 2.5))
        
        self.assertEqual(self.element.total_load(), 1500)
        self.assertEqual(self.element.total_load(LoadType.DEAD), 1000)
        self.assertEqual(self.element.total_load(LoadType.LIVE), 500)


class TestDesign(unittest.TestCase):
    """Designクラスのテスト"""
    
    def setUp(self):
        """テストの準備"""
        self.design = Design(
            name="テスト設計",
            description="テスト用の設計"
        )
        self.material = STANDARD_MATERIALS["SS400"]
    
    def test_design_creation(self):
        """設計の作成テスト"""
        self.assertEqual(self.design.name, "テスト設計")
        self.assertEqual(len(self.design.elements), 0)
        self.assertEqual(len(self.design.materials), 0)
    
    def test_add_element(self):
        """要素追加のテスト"""
        element = StructuralElement(
            name="梁1",
            material=self.material,
            length=5.0,
            cross_section_area=0.01,
            moment_of_inertia=0.0001
        )
        
        self.design.add_element(element)
        
        self.assertEqual(len(self.design.elements), 1)
        self.assertEqual(len(self.design.materials), 1)
        self.assertIn(self.material, self.design.materials)
    
    def test_total_weight(self):
        """総重量の計算テスト"""
        element1 = StructuralElement(
            name="梁1",
            material=self.material,
            length=5.0,
            cross_section_area=0.01,
            moment_of_inertia=0.0001
        )
        element1.loads.append(Load(LoadType.DEAD, 1000, 2.5))
        
        element2 = StructuralElement(
            name="柱1",
            material=self.material,
            length=3.0,
            cross_section_area=0.015,
            moment_of_inertia=0.00015
        )
        element2.loads.append(Load(LoadType.DEAD, 2000, 1.5))
        
        self.design.add_element(element1)
        self.design.add_element(element2)
        
        expected_weight = (
            element1.self_weight() + element1.total_load() +
            element2.self_weight() + element2.total_load()
        )
        
        self.assertAlmostEqual(self.design.total_weight(), expected_weight, places=2)


if __name__ == '__main__':
    unittest.main()
