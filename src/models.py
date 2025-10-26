"""
データモデル定義

このモジュールは、構造計算に必要なデータモデルを定義します。
材料情報、構造要素、設計図などのクラスを含みます。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class MaterialType(Enum):
    """材料の種類"""
    STEEL = "鋼材"
    CONCRETE = "コンクリート"
    WOOD = "木材"
    COMPOSITE = "複合材"


class LoadType(Enum):
    """荷重の種類"""
    DEAD = "固定荷重"  # Dead load
    LIVE = "積載荷重"  # Live load
    WIND = "風荷重"    # Wind load
    SEISMIC = "地震荷重"  # Seismic load


@dataclass
class Material:
    """
    材料情報を表すクラス
    
    Attributes:
        name: 材料名
        material_type: 材料の種類
        density: 密度 (kg/m³)
        youngs_modulus: ヤング率（弾性係数） (N/m²)
        yield_strength: 降伏強度 (N/m²)
        ultimate_strength: 終局強度 (N/m²)
        safety_factor: 安全率
    """
    name: str
    material_type: MaterialType
    density: float  # kg/m³
    youngs_modulus: float  # N/m² (Pa)
    yield_strength: float  # N/m² (Pa)
    ultimate_strength: float  # N/m² (Pa)
    safety_factor: float = 1.5
    
    def allowable_stress(self) -> float:
        """
        許容応力を計算
        
        Returns:
            許容応力値 (N/m²)
        """
        return self.yield_strength / self.safety_factor
    
    def __str__(self) -> str:
        return (f"材料: {self.name} ({self.material_type.value})\n"
                f"  密度: {self.density:.1f} kg/m³\n"
                f"  ヤング率: {self.youngs_modulus:.2e} N/m²\n"
                f"  降伏強度: {self.yield_strength:.2e} N/m²\n"
                f"  許容応力: {self.allowable_stress():.2e} N/m²")


@dataclass
class Load:
    """
    荷重情報を表すクラス
    
    Attributes:
        load_type: 荷重の種類
        magnitude: 荷重の大きさ (N)
        location: 荷重の作用位置 (m)
        description: 荷重の説明
    """
    load_type: LoadType
    magnitude: float  # N
    location: float  # m
    description: str = ""
    
    def __str__(self) -> str:
        return (f"{self.load_type.value}: {self.magnitude:.2f} N "
                f"at {self.location:.2f} m")


@dataclass
class StructuralElement:
    """
    構造要素（梁、柱など）を表すクラス
    
    Attributes:
        name: 要素名
        material: 使用材料
        length: 長さ (m)
        cross_section_area: 断面積 (m²)
        moment_of_inertia: 断面二次モーメント (m⁴)
        loads: 作用する荷重のリスト
    """
    name: str
    material: Material
    length: float  # m
    cross_section_area: float  # m²
    moment_of_inertia: float  # m⁴
    loads: List[Load] = field(default_factory=list)
    
    def total_load(self, load_type: Optional[LoadType] = None) -> float:
        """
        合計荷重を計算
        
        Args:
            load_type: 特定の荷重タイプのみを合計する場合に指定
            
        Returns:
            合計荷重 (N)
        """
        if load_type:
            return sum(load.magnitude for load in self.loads 
                      if load.load_type == load_type)
        return sum(load.magnitude for load in self.loads)
    
    def self_weight(self) -> float:
        """
        自重を計算
        
        Returns:
            自重 (N)
        """
        volume = self.cross_section_area * self.length  # m³
        mass = volume * self.material.density  # kg
        weight = mass * 9.81  # N (重力加速度 9.81 m/s²)
        return weight
    
    def __str__(self) -> str:
        return (f"構造要素: {self.name}\n"
                f"  材料: {self.material.name}\n"
                f"  長さ: {self.length:.2f} m\n"
                f"  断面積: {self.cross_section_area:.4f} m²\n"
                f"  自重: {self.self_weight():.2f} N\n"
                f"  荷重数: {len(self.loads)}")


@dataclass
class Design:
    """
    設計図を表すクラス
    
    Attributes:
        name: 設計名
        description: 設計の説明
        elements: 構造要素のリスト
        materials: 使用材料のリスト
        metadata: その他のメタデータ
    """
    name: str
    description: str = ""
    elements: List[StructuralElement] = field(default_factory=list)
    materials: List[Material] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def add_element(self, element: StructuralElement) -> None:
        """構造要素を追加"""
        self.elements.append(element)
        
        # 材料が未登録の場合は追加
        if element.material not in self.materials:
            self.materials.append(element.material)
    
    def total_weight(self) -> float:
        """
        設計全体の総重量を計算
        
        Returns:
            総重量 (N)
        """
        return sum(elem.self_weight() + elem.total_load() 
                  for elem in self.elements)
    
    def __str__(self) -> str:
        return (f"設計: {self.name}\n"
                f"  説明: {self.description}\n"
                f"  構造要素数: {len(self.elements)}\n"
                f"  使用材料数: {len(self.materials)}\n"
                f"  総重量: {self.total_weight():.2f} N")


# 標準的な材料のプリセット
STANDARD_MATERIALS = {
    "SS400": Material(
        name="SS400 (一般構造用圧延鋼材)",
        material_type=MaterialType.STEEL,
        density=7850,  # kg/m³
        youngs_modulus=205e9,  # 205 GPa
        yield_strength=245e6,  # 245 MPa
        ultimate_strength=400e6,  # 400 MPa
        safety_factor=1.5
    ),
    "C24": Material(
        name="コンクリート24 (設計基準強度24N/mm²)",
        material_type=MaterialType.CONCRETE,
        density=2400,  # kg/m³
        youngs_modulus=25e9,  # 25 GPa
        yield_strength=16e6,  # 16 MPa (圧縮強度の約2/3)
        ultimate_strength=24e6,  # 24 MPa
        safety_factor=3.0
    ),
    "SUGI": Material(
        name="杉材 (構造用)",
        material_type=MaterialType.WOOD,
        density=400,  # kg/m³
        youngs_modulus=7e9,  # 7 GPa
        yield_strength=20e6,  # 20 MPa
        ultimate_strength=30e6,  # 30 MPa
        safety_factor=2.0
    ),
}
