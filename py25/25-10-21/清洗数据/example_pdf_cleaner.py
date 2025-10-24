#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何使用PDF清洗工具
"""

import os
import sys
from pdf_cleaner import PDFCleaner

def main():
    """主函数：演示PDF清洗工具的使用方法"""
    print("PDF清洗工具使用示例")
    print("=" * 50)
    
    # 检查是否有PDF文件
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("\n错误：当前目录下没有找到PDF文件！")
        print("请将您的PDF文件复制到当前目录，然后重新运行此脚本。")
        print("\n或者，您也可以直接使用命令行运行：")
        print("  python pdf_cleaner.py your_pdf_file.pdf -o output.json")
        return
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件：")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file}")
    
    # 选择第一个PDF文件作为示例
    pdf_path = pdf_files[0]
    output_json = f"output_{os.path.splitext(os.path.basename(pdf_path))[0]}.json"
    
    print(f"\n将处理文件：{pdf_path}")
    print(f"输出将保存到：{output_json}")
    
    # 询问是否继续
    confirm = input("\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作。")
        return
    
    # 创建PDFCleaner实例
    # 注意：如果您的Tesseract未在系统PATH中，请取消下面一行的注释并设置正确路径
    # cleaner = PDFCleaner(pdf_path, output_json, tesseract_cmd="C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
    cleaner = PDFCleaner(pdf_path, output_json)
    
    try:
        # 开始处理
        print("\n开始处理PDF文件...")
        cleaner.process()
        print(f"\n处理完成！结果已保存到：{output_json}")
        
        # 显示处理结果的一部分
        import json
        with open(output_json, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        print(f"\n总共提取了 {len(result)} 个单词及其翻译")
        print("\n前5个单词示例：")
        for i, (word, translations) in enumerate(list(result.items())[:5], 1):
            print(f"  {i}. '{word}': {translations}")
            
    except Exception as e:
        print(f"\n处理过程中出错：{e}")
        print("\n请检查以下几点：")
        print("1. Tesseract OCR是否已正确安装")
        print("2. 如果Tesseract未在系统PATH中，请在代码中指定其路径")
        print("3. PDF文件是否可读且包含英文单词和中文翻译")
        print("\n错误详情：", str(e))

if __name__ == "__main__":
    main()