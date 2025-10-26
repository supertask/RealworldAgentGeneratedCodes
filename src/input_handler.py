"""
入力データ処理モジュール

このモジュールは、スプレッドシート形式のデータを読み込み、
構造計算用のデータモデルに変換します。
"""

import csv
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

from .models import (
    Material, MaterialType, StructuralElement, 
    Design, Load, LoadType, STANDARD_MATERIALS
)


class InputHandler:
    """
    入力データを処理するクラス
    
    CSV、Excel、JSONなどの形式から構造計算用のデータを読み込みます。
    """
    
    @staticmethod
    def load_materials_from_csv(file_path: str) -> List[Material]:
        """
        CSV形式から材料情報を読み込む
        
        CSVフォーマット:
        name,material_type,density,youngs_modulus,yield_strength,ultimate_strength,safety_factor
        
        Args:
            file_path: CSVファイルのパス
            
        Returns:
            材料オブジェクトのリスト
        """
        materials = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 材料タイプの変換
                material_type_map = {
                    '鋼材': MaterialType.STEEL,
                    'STEEL': MaterialType.STEEL,
                    'コンクリート': MaterialType.CONCRETE,
                    'CONCRETE': MaterialType.CONCRETE,
                    '木材': MaterialType.WOOD,
                    'WOOD': MaterialType.WOOD,
                    '複合材': MaterialType.COMPOSITE,
                    'COMPOSITE': MaterialType.COMPOSITE,
                }
                
                material = Material(
                    name=row['name'],
                    material_type=material_type_map.get(
                        row['material_type'], MaterialType.STEEL
                    ),
                    density=float(row['density']),
                    youngs_modulus=float(row['youngs_modulus']),
                    yield_strength=float(row['yield_strength']),
                    ultimate_strength=float(row['ultimate_strength']),
                    safety_factor=float(row.get('safety_factor', 1.5))
                )
                materials.append(material)
        
        return materials
    
    @staticmethod
    def load_materials_from_excel(file_path: str, sheet_name: str = 'materials') -> List[Material]:
        """
        Excel形式から材料情報を読み込む
        
        Args:
            file_path: Excelファイルのパス
            sheet_name: シート名
            
        Returns:
            材料オブジェクトのリスト
        """
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        materials = []
        
        material_type_map = {
            '鋼材': MaterialType.STEEL,
            'STEEL': MaterialType.STEEL,
            'コンクリート': MaterialType.CONCRETE,
            'CONCRETE': MaterialType.CONCRETE,
            '木材': MaterialType.WOOD,
            'WOOD': MaterialType.WOOD,
            '複合材': MaterialType.COMPOSITE,
            'COMPOSITE': MaterialType.COMPOSITE,
        }
        
        for _, row in df.iterrows():
            material = Material(
                name=row['name'],
                material_type=material_type_map.get(
                    row['material_type'], MaterialType.STEEL
                ),
                density=float(row['density']),
                youngs_modulus=float(row['youngs_modulus']),
                yield_strength=float(row['yield_strength']),
                ultimate_strength=float(row['ultimate_strength']),
                safety_factor=float(row.get('safety_factor', 1.5))
            )
            materials.append(material)
        
        return materials
    
    @staticmethod
    def load_elements_from_csv(
        file_path: str, 
        materials: Dict[str, Material]
    ) -> List[StructuralElement]:
        """
        CSV形式から構造要素を読み込む
        
        CSVフォーマット:
        name,material_name,length,cross_section_area,moment_of_inertia
        
        Args:
            file_path: CSVファイルのパス
            materials: 材料名をキーとする材料の辞書
            
        Returns:
            構造要素オブジェクトのリスト
        """
        elements = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                material_name = row['material_name']
                if material_name not in materials:
                    raise ValueError(f"材料 '{material_name}' が見つかりません")
                
                element = StructuralElement(
                    name=row['name'],
                    material=materials[material_name],
                    length=float(row['length']),
                    cross_section_area=float(row['cross_section_area']),
                    moment_of_inertia=float(row['moment_of_inertia'])
                )
                elements.append(element)
        
        return elements
    
    @staticmethod
    def load_loads_from_csv(file_path: str) -> List[Load]:
        """
        CSV形式から荷重情報を読み込む
        
        CSVフォーマット:
        load_type,magnitude,location,description
        
        Args:
            file_path: CSVファイルのパス
            
        Returns:
            荷重オブジェクトのリスト
        """
        loads = []
        
        load_type_map = {
            '固定荷重': LoadType.DEAD,
            'DEAD': LoadType.DEAD,
            '積載荷重': LoadType.LIVE,
            'LIVE': LoadType.LIVE,
            '風荷重': LoadType.WIND,
            'WIND': LoadType.WIND,
            '地震荷重': LoadType.SEISMIC,
            'SEISMIC': LoadType.SEISMIC,
        }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                load = Load(
                    load_type=load_type_map.get(row['load_type'], LoadType.DEAD),
                    magnitude=float(row['magnitude']),
                    location=float(row['location']),
                    description=row.get('description', '')
                )
                loads.append(load)
        
        return loads
    
    @staticmethod
    def load_design_from_json(file_path: str) -> Design:
        """
        JSON形式から設計情報を読み込む
        
        Args:
            file_path: JSONファイルのパス
            
        Returns:
            設計オブジェクト
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 材料の読み込み
        materials = {}
        for mat_data in data.get('materials', []):
            material = Material(
                name=mat_data['name'],
                material_type=MaterialType[mat_data['material_type']],
                density=mat_data['density'],
                youngs_modulus=mat_data['youngs_modulus'],
                yield_strength=mat_data['yield_strength'],
                ultimate_strength=mat_data['ultimate_strength'],
                safety_factor=mat_data.get('safety_factor', 1.5)
            )
            materials[material.name] = material
        
        # 構造要素の読み込み
        elements = []
        for elem_data in data.get('elements', []):
            material = materials[elem_data['material_name']]
            
            # 荷重の読み込み
            loads = []
            for load_data in elem_data.get('loads', []):
                load = Load(
                    load_type=LoadType[load_data['load_type']],
                    magnitude=load_data['magnitude'],
                    location=load_data['location'],
                    description=load_data.get('description', '')
                )
                loads.append(load)
            
            element = StructuralElement(
                name=elem_data['name'],
                material=material,
                length=elem_data['length'],
                cross_section_area=elem_data['cross_section_area'],
                moment_of_inertia=elem_data['moment_of_inertia'],
                loads=loads
            )
            elements.append(element)
        
        # 設計の作成
        design = Design(
            name=data.get('name', 'Unnamed Design'),
            description=data.get('description', ''),
            elements=elements,
            materials=list(materials.values()),
            metadata=data.get('metadata', {})
        )
        
        return design
    
    @staticmethod
    def create_sample_design() -> Design:
        """
        サンプル設計を作成
        
        Returns:
            サンプルの設計オブジェクト
        """
        # 標準材料を使用
        steel = STANDARD_MATERIALS["SS400"]
        
        # 梁の作成
        beam = StructuralElement(
            name="主梁-1",
            material=steel,
            length=6.0,  # 6m
            cross_section_area=0.01,  # 100cm²
            moment_of_inertia=0.0001  # 1000cm⁴
        )
        
        # 荷重の追加
        beam.loads.append(Load(
            load_type=LoadType.DEAD,
            magnitude=5000,  # 5kN = 5000N
            location=3.0,  # 中央
            description="固定荷重（床スラブ等）"
        ))
        
        beam.loads.append(Load(
            load_type=LoadType.LIVE,
            magnitude=3000,  # 3kN = 3000N
            location=3.0,  # 中央
            description="積載荷重"
        ))
        
        # 柱の作成
        column = StructuralElement(
            name="柱-1",
            material=steel,
            length=3.5,  # 3.5m
            cross_section_area=0.015,  # 150cm²
            moment_of_inertia=0.00015  # 1500cm⁴
        )
        
        column.loads.append(Load(
            load_type=LoadType.DEAD,
            magnitude=10000,  # 10kN
            location=3.5,  # 柱頭
            description="上階からの荷重"
        ))
        
        # 設計の作成
        design = Design(
            name="サンプル構造設計",
            description="シンプルな梁-柱構造のサンプル",
            elements=[beam, column],
            materials=[steel],
            metadata={
                "建物用途": "事務所",
                "階数": 3,
                "設計者": "構造計算システム"
            }
        )
        
        return design
