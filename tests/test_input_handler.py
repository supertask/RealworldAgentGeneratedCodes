"""
入力処理機能のテスト
"""

import unittest
import sys
import tempfile
import csv
import json
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import MaterialType, LoadType
from src.input_handler import InputHandler


class TestInputHandler(unittest.TestCase):
    """InputHandlerクラスのテスト"""
    
    def test_sample_design_creation(self):
        """サンプル設計の作成テスト"""
        design = InputHandler.create_sample_design()
        
        self.assertEqual(design.name, "サンプル構造設計")
        self.assertGreater(len(design.elements), 0)
        self.assertGreater(len(design.materials), 0)
        self.assertIn("建物用途", design.metadata)
    
    def test_load_materials_from_csv(self):
        """CSV形式からの材料読み込みテスト"""
        # 一時CSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'material_type', 'density', 'youngs_modulus', 
                           'yield_strength', 'ultimate_strength', 'safety_factor'])
            writer.writerow(['テスト鋼材', 'STEEL', '7850', '205e9', '245e6', '400e6', '1.5'])
            temp_file = f.name
        
        try:
            materials = InputHandler.load_materials_from_csv(temp_file)
            
            self.assertEqual(len(materials), 1)
            self.assertEqual(materials[0].name, 'テスト鋼材')
            self.assertEqual(materials[0].material_type, MaterialType.STEEL)
            self.assertEqual(materials[0].density, 7850)
        finally:
            Path(temp_file).unlink()
    
    def test_load_elements_from_csv(self):
        """CSV形式からの構造要素読み込みテスト"""
        # 一時CSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'material_name', 'length', 'cross_section_area', 'moment_of_inertia'])
            writer.writerow(['梁1', 'SS400', '5.0', '0.01', '0.0001'])
            temp_file = f.name
        
        try:
            from src.models import STANDARD_MATERIALS
            materials_dict = {name: mat for name, mat in STANDARD_MATERIALS.items()}
            
            elements = InputHandler.load_elements_from_csv(temp_file, materials_dict)
            
            self.assertEqual(len(elements), 1)
            self.assertEqual(elements[0].name, '梁1')
            self.assertEqual(elements[0].length, 5.0)
        finally:
            Path(temp_file).unlink()
    
    def test_load_loads_from_csv(self):
        """CSV形式からの荷重読み込みテスト"""
        # 一時CSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['load_type', 'magnitude', 'location', 'description'])
            writer.writerow(['DEAD', '5000', '2.5', 'テスト荷重'])
            temp_file = f.name
        
        try:
            loads = InputHandler.load_loads_from_csv(temp_file)
            
            self.assertEqual(len(loads), 1)
            self.assertEqual(loads[0].load_type, LoadType.DEAD)
            self.assertEqual(loads[0].magnitude, 5000)
            self.assertEqual(loads[0].location, 2.5)
        finally:
            Path(temp_file).unlink()
    
    def test_load_design_from_json(self):
        """JSON形式からの設計読み込みテスト"""
        # テストデータ
        test_data = {
            "name": "JSON テスト設計",
            "description": "JSONからのテスト",
            "materials": [
                {
                    "name": "テスト材料",
                    "material_type": "STEEL",
                    "density": 7850,
                    "youngs_modulus": 205e9,
                    "yield_strength": 245e6,
                    "ultimate_strength": 400e6,
                    "safety_factor": 1.5
                }
            ],
            "elements": [
                {
                    "name": "梁1",
                    "material_name": "テスト材料",
                    "length": 6.0,
                    "cross_section_area": 0.01,
                    "moment_of_inertia": 0.0001,
                    "loads": [
                        {
                            "load_type": "DEAD",
                            "magnitude": 5000,
                            "location": 3.0,
                            "description": "テスト荷重"
                        }
                    ]
                }
            ],
            "metadata": {
                "test_key": "test_value"
            }
        }
        
        # 一時JSONファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            design = InputHandler.load_design_from_json(temp_file)
            
            self.assertEqual(design.name, "JSON テスト設計")
            self.assertEqual(len(design.materials), 1)
            self.assertEqual(len(design.elements), 1)
            self.assertEqual(design.elements[0].name, "梁1")
            self.assertEqual(len(design.elements[0].loads), 1)
            self.assertEqual(design.metadata["test_key"], "test_value")
        finally:
            Path(temp_file).unlink()


if __name__ == '__main__':
    unittest.main()
