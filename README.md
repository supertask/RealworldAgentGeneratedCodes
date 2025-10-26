# 構造計算プログラム

建築構造計算を行うためのPythonプログラムです。非専門家でも理解しやすいように設計されており、スプレッドシート形式のデータから構造要素の安全性を計算できます。

## 特徴

- **分かりやすい設計**: 建築の専門知識がなくても、コードの流れを理解できる
- **柔軟な入力形式**: CSV、Excel、JSON形式のデータに対応
- **包括的な計算**: 梁と柱の応力、たわみ、座屈を計算
- **詳細なレポート**: テキスト、CSV、JSON、HTML形式でレポート出力
- **標準材料プリセット**: 一般的な建築材料（鋼材、コンクリート、木材）を事前定義

## 機能概要

### 1. データモデル
- **Material**: 材料情報（密度、ヤング率、強度など）
- **StructuralElement**: 構造要素（梁、柱など）
- **Load**: 荷重情報（固定荷重、積載荷重など）
- **Design**: 設計全体の情報

### 2. 構造計算
- 梁の応力とたわみ計算（単純支持、固定支持）
- 柱の軸応力と座屈計算
- 安全性の自動判定（応力比、たわみ比）

### 3. 入力処理
- CSV/Excel形式からの材料・構造要素の読み込み
- JSON形式での設計データの一括読み込み
- サンプルデータの自動生成

### 4. レポート生成
- テキスト形式の詳細レポート
- CSV形式（表計算ソフトで利用可能）
- JSON形式（プログラムで再利用可能）
- HTML形式（ブラウザで表示可能）

## インストール

### 前提条件
- Python 3.8以上

### セットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd workspace

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使い方

### 基本的な使用例

```python
from src.models import STANDARD_MATERIALS, StructuralElement, Design, Load, LoadType
from src.calculator import StructuralCalculator
from src.report_generator import ReportGenerator

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
    magnitude=5000,  # 5kN
    location=3.0,  # 中央
    description="固定荷重"
))

# 設計の作成
design = Design(
    name="サンプル構造設計",
    description="簡単な梁の設計例"
)
design.add_element(beam)

# 構造計算の実行
calculator = StructuralCalculator()
results = calculator.calculate_design(design)

# 結果の表示
calculator.print_results()

# レポートの生成
report_gen = ReportGenerator(design, results)
report_gen.generate_html_report("report.html")
```

### サンプルプログラムの実行

```python
from src.input_handler import InputHandler
from src.calculator import StructuralCalculator
from src.report_generator import ReportGenerator

# サンプル設計を作成
design = InputHandler.create_sample_design()

# 構造計算を実行
calculator = StructuralCalculator()
results = calculator.calculate_design(design)

# 結果を表示
calculator.print_results()

# レポートを生成
report_gen = ReportGenerator(design, results)
report_gen.generate_text_report("report.txt")
report_gen.generate_html_report("report.html")
```

### CSV形式からのデータ読み込み

材料情報のCSVファイル例（`materials.csv`）:
```csv
name,material_type,density,youngs_modulus,yield_strength,ultimate_strength,safety_factor
SS400,STEEL,7850,205e9,245e6,400e6,1.5
C24,CONCRETE,2400,25e9,16e6,24e6,3.0
```

構造要素のCSVファイル例（`elements.csv`）:
```csv
name,material_name,length,cross_section_area,moment_of_inertia
主梁-1,SS400,6.0,0.01,0.0001
柱-1,SS400,3.5,0.015,0.00015
```

読み込みコード:
```python
from src.input_handler import InputHandler

# 材料を読み込み
materials = InputHandler.load_materials_from_csv("materials.csv")
materials_dict = {mat.name: mat for mat in materials}

# 構造要素を読み込み
elements = InputHandler.load_elements_from_csv("elements.csv", materials_dict)
```

## プロジェクト構成

```
workspace/
├── src/                    # ソースコード
│   ├── __init__.py
│   ├── models.py          # データモデル定義
│   ├── input_handler.py   # 入力データ処理
│   ├── calculator.py      # 構造計算ロジック
│   └── report_generator.py # レポート生成
├── tests/                  # テストコード
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_calculator.py
│   └── test_input_handler.py
├── examples/               # サンプルデータ
├── README.md              # このファイル
├── requirements.txt       # 依存パッケージ
└── LICENSE                # ライセンス
```

## テストの実行

```bash
# 全テストを実行
python3 -m pytest tests/

# 特定のテストファイルを実行
python3 -m pytest tests/test_models.py

# カバレッジ付きでテスト実行
python3 -m pytest tests/ --cov=src --cov-report=html
```

## 構造計算の理論

### 梁の計算

単純支持梁、中央集中荷重の場合：

- **最大曲げモーメント**: M = P×L/4
- **最大応力**: σ = M / Z （Z: 断面係数）
- **最大たわみ**: δ = P×L³/(48×E×I)

### 柱の計算

軸圧縮を受ける柱：

- **直接応力**: σ = P / A
- **オイラー座屈荷重**: Pcr = π²×E×I / Le²
- **細長比**: λ = Le / r （r: 断面二次半径）

### 安全性の判定基準

- **応力比**: σmax / σallow ≤ 1.0
- **たわみ**: δ ≤ L/250
- **座屈安全率**: Pcr / P ≥ 2.0

## 標準材料

プログラムには以下の標準材料が事前定義されています：

1. **SS400** - 一般構造用圧延鋼材
2. **C24** - コンクリート（設計基準強度24N/mm²）
3. **SUGI** - 杉材（構造用）

## 注意事項

このプログラムは教育・学習目的で作成されたものです。実際の建築設計には、より詳細な検討と専門家の確認が必要です。

- 実際の構造計算では、より複雑な荷重組み合わせを考慮する必要があります
- 地震荷重、風荷重などの動的解析は簡略化されています
- 断面形状は簡略化された仮定を使用しています
- 実務では建築基準法や各種指針に基づいた計算が必要です

## ライセンス

このプロジェクトのライセンスについては、LICENSEファイルを参照してください。

## 貢献

バグ報告や機能追加の提案は、GitHubのIssueでお願いします。

## サポート

質問や問題がある場合は、GitHubのIssueで報告してください。

---

**開発者**: 構造計算システムチーム  
**バージョン**: 0.1.0  
**最終更新**: 2025年10月
