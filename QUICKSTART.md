# クイックスタートガイド

構造計算プログラムを今すぐ試してみましょう！

## 1. セットアップ（初回のみ）

```bash
# 依存パッケージをインストール
pip install -r requirements.txt
```

## 2. プログラムの実行

### 基本的な使い方

```bash
# メインプログラムを実行
python3 main.py
```

これにより以下が自動で実行されます：
- サンプル設計の作成
- 構造計算の実行
- 4種類のレポート生成（テキスト、CSV、JSON、HTML）

### 生成されるファイル

実行後、以下のレポートファイルが生成されます：

- `構造計算レポート.txt` - テキスト形式の詳細レポート
- `構造計算レポート.csv` - Excel等で開ける表形式
- `構造計算レポート.json` - プログラムで再利用可能なJSON形式
- `構造計算レポート.html` - ブラウザで見やすいHTML形式

## 3. HTMLレポートの確認

```bash
# ブラウザでHTMLレポートを開く
# Linuxの場合
xdg-open 構造計算レポート.html

# macOSの場合
open 構造計算レポート.html

# Windowsの場合
start 構造計算レポート.html
```

## 4. テストの実行

```bash
# 全テストを実行
python3 -m unittest discover tests -v

# 特定のテストのみ実行
python3 -m unittest tests.test_models -v
```

## 5. カスタムデータの使用

### JSON形式のデータを読み込む

```python
from src.input_handler import InputHandler
from src.calculator import StructuralCalculator
from src.report_generator import ReportGenerator

# JSON形式の設計データを読み込み
design = InputHandler.load_design_from_json("examples/sample_design.json")

# 構造計算を実行
calculator = StructuralCalculator()
results = calculator.calculate_design(design)

# レポートを生成
report_gen = ReportGenerator(design, results)
report_gen.generate_html_report("my_report.html")
```

### CSV形式のデータを読み込む

```python
from src.input_handler import InputHandler

# 材料情報を読み込み
materials = InputHandler.load_materials_from_csv("examples/sample_materials.csv")
materials_dict = {mat.name: mat for mat in materials}

# 構造要素を読み込み
elements = InputHandler.load_elements_from_csv("examples/sample_elements.csv", materials_dict)
```

## 6. プログラムを理解する

### ファイル構成

```
src/
├── models.py          # データ構造の定義
├── calculator.py      # 構造計算のロジック
├── input_handler.py   # データの読み込み
└── report_generator.py # レポートの生成
```

### 基本的な流れ

1. **データ準備** - 材料、構造要素、荷重の定義
2. **設計作成** - Designオブジェクトに要素を追加
3. **計算実行** - StructuralCalculatorで計算
4. **レポート生成** - ReportGeneratorで結果を出力

## 7. よくある質問

### Q1. 材料を追加したい

`src/models.py`の`STANDARD_MATERIALS`に追加するか、カスタムMaterialオブジェクトを作成してください。

### Q2. 計算結果を変更したい

`src/calculator.py`の計算式を修正してください。各計算には詳細なコメントが付いています。

### Q3. 新しいレポート形式を追加したい

`src/report_generator.py`に新しいメソッドを追加してください。

## 8. サンプルファイル

`examples/`ディレクトリには以下のサンプルが含まれています：

- `sample_materials.csv` - 材料データのサンプル
- `sample_elements.csv` - 構造要素のサンプル
- `sample_design.json` - 完全な設計データのサンプル

これらを参考に、独自のデータを作成できます。

## 9. トラブルシューティング

### エラー: No module named 'pandas'

```bash
pip install pandas openpyxl
```

### エラー: No module named 'pytest'

```bash
pip install pytest
```

### 計算結果が予想と違う

- 単位を確認してください（m, N, Pa）
- 荷重の作用位置を確認してください
- 支持条件を確認してください

## 10. 次のステップ

プログラムに慣れたら、以下を試してみてください：

1. 独自の構造設計を作成
2. 新しい材料を追加
3. より複雑な荷重パターンを試す
4. レポート形式をカスタマイズ

詳細は`README.md`を参照してください。

---

**質問やバグ報告は、GitHubのIssueでお願いします。**
