# PDF清洗工具

## 功能介绍

本工具可以将PDF文件的每一页转换为图像，通过OCR技术识别其中的文本，提取英文单词及其中文翻译，并将结果保存为指定格式的JSON文件。

JSON输出格式：
```json
{
  "freedom": [
    "自由",
    "其他汉译"
  ],
  "example": [
    "例子",
    "实例"
  ]
}
```

## 环境要求

### 1. Python环境

- Python 3.7+

### 2. 安装依赖包

```bash
pip install -r requirements.txt
```

### 3. 安装Tesseract OCR

本工具依赖Tesseract OCR进行文字识别，请确保已正确安装：

#### Windows系统

1. 下载Tesseract OCR安装包：[GitHub Release](https://github.com/UB-Mannheim/tesseract/wiki)
2. 安装时记住安装路径（例如：`C:\Program Files\Tesseract-OCR\tesseract.exe`）
3. 安装中文语言包（可选，但推荐）

#### Linux系统

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-chi-sim  # 安装中文简体语言包
```

#### macOS系统

```bash
brew install tesseract
brew install tesseract-lang  # 安装语言包
```

## 使用方法

### 基本使用

```bash
python pdf_cleaner.py your_pdf_file.pdf -o output.json
```

### 完整参数说明

```bash
python pdf_cleaner.py -h

# 参数说明
# pdf_path: PDF文件路径（必需）
# -o, --output: 输出JSON文件路径（可选，默认为output.json）
# -l, --lang: OCR语言设置（可选，默认为chi_sim+eng）
# -t, --tesseract: Tesseract-OCR命令路径（可选，如果未在系统PATH中）
```

### 示例

```bash
# 指定Tesseract路径的示例（Windows）
python pdf_cleaner.py document.pdf -o result.json -t "C:\Program Files\Tesseract-OCR\tesseract.exe"

# 指定Tesseract路径的示例（Linux/macOS）
python pdf_cleaner.py document.pdf -o result.json -t "/usr/local/bin/tesseract"
```

## 注意事项

1. 本工具对PDF格式有一定要求，最佳效果是处理包含英文单词和中文翻译对照的文档
2. 对于扫描版PDF，识别准确率可能受图像质量影响
3. 多义词的中文翻译会按逗号(,)、分号(;)、中文逗号(，)、中文分号(；)进行分割
4. 如果遇到识别错误，可以尝试调整图像预处理参数或更换Tesseract版本

## 常见问题

### 1. TesseractNotFoundError错误

这表示系统找不到Tesseract OCR。请确保已正确安装Tesseract，并使用`-t`参数指定其路径。

### 2. 中文识别效果不佳

请确保已安装中文语言包，并在OCR参数中包含`chi_sim`（简体中文）或`chi_tra`（繁体中文）。

### 3. PDF转换失败

对于某些特殊格式的PDF，可能需要安装额外的依赖，如`poppler`。Windows用户可以从[这里](http://blog.alivate.com.au/poppler-windows/)下载并将其`bin`目录添加到系统PATH中。

## 日志

工具会生成`pdf_cleaner.log`文件，记录处理过程中的详细信息，便于排查问题。