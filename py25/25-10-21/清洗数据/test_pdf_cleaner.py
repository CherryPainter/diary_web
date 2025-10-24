#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF清洗工具测试脚本
"""

import os
import json
import logging
import subprocess
from pdf_cleaner import PDFCleaner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_with_sample_pdf():
    """测试PDF清洗功能（如果有示例PDF）"""
    # 检查当前目录下是否有PDF文件
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.info("当前目录下没有找到PDF文件，无法进行实际测试")
        logger.info("请手动将PDF文件放入当前目录，然后运行此测试脚本")
        return False
    
    # 使用第一个找到的PDF文件进行测试
    pdf_path = pdf_files[0]
    output_json = f"test_output_{os.path.splitext(os.path.basename(pdf_path))[0]}.json"
    
    logger.info(f"使用PDF文件进行测试: {pdf_path}")
    logger.info(f"输出将保存到: {output_json}")
    
    try:
        # 创建PDFCleaner实例并处理
        cleaner = PDFCleaner(pdf_path, output_json)
        cleaner.process()
        
        # 验证输出文件是否存在
        if os.path.exists(output_json):
            logger.info(f"测试成功！输出文件已生成: {output_json}")
            
            # 读取并显示JSON文件的前几项内容
            with open(output_json, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            logger.info(f"提取到 {len(result)} 个单词")
            logger.info("前5个单词示例:")
            for i, (word, translations) in enumerate(list(result.items())[:5]):
                logger.info(f"  {i+1}. '{word}': {translations}")
            
            return True
        else:
            logger.error("测试失败！输出文件未生成")
            return False
    
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        return False

def test_json_format():
    """测试JSON输出格式是否符合要求"""
    # 创建一个模拟的测试数据
    test_data = {
        "freedom": ["自由", "自由度"],
        "example": ["例子", "实例", "范例"],
        "technology": ["技术", "科技"]
    }
    
    test_json_path = "test_format.json"
    
    # 保存测试数据
    with open(test_json_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    # 验证格式
    try:
        with open(test_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查格式是否正确
        is_valid = True
        for word, translations in data.items():
            if not isinstance(word, str):
                logger.error(f"键 '{word}' 不是字符串类型")
                is_valid = False
            if not isinstance(translations, list):
                logger.error(f"值 '{translations}' 不是列表类型")
                is_valid = False
            else:
                for trans in translations:
                    if not isinstance(trans, str):
                        logger.error(f"翻译项 '{trans}' 不是字符串类型")
                        is_valid = False
        
        if is_valid:
            logger.info("JSON格式测试通过！")
        else:
            logger.error("JSON格式测试失败！")
        
        # 清理测试文件
        os.remove(test_json_path)
        return is_valid
    
    except Exception as e:
        logger.error(f"JSON格式测试出错: {e}")
        return False

def test_command_line_interface():
    """测试命令行接口"""
    try:
        # 运行帮助命令
        result = subprocess.run(
            ['python', 'pdf_cleaner.py', '-h'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if 'usage:' in result.stdout.lower():
            logger.info("命令行接口测试通过！")
            return True
        else:
            logger.error("命令行接口测试失败！")
            return False
    
    except Exception as e:
        logger.error(f"命令行接口测试出错: {e}")
        return False

def main():
    """运行所有测试"""
    logger.info("开始测试PDF清洗工具...")
    
    # 1. 测试JSON格式
    format_test_passed = test_json_format()
    
    # 2. 测试命令行接口
    cli_test_passed = test_command_line_interface()
    
    # 3. 测试实际PDF处理（如果有PDF文件）
    pdf_test_passed = test_with_sample_pdf()
    
    # 总结测试结果
    logger.info("\n测试结果总结:")
    logger.info(f"1. JSON格式测试: {'通过' if format_test_passed else '失败'}")
    logger.info(f"2. 命令行接口测试: {'通过' if cli_test_passed else '失败'}")
    logger.info(f"3. PDF实际处理测试: {'通过' if pdf_test_passed else '未执行或失败'}")
    
    # 给出使用建议
    logger.info("\n使用建议:")
    logger.info("1. 确保已安装所有依赖: pip install -r requirements.txt")
    logger.info("2. 确保已正确安装Tesseract OCR")
    logger.info("3. 使用命令: python pdf_cleaner.py your_pdf_file.pdf -o output.json")
    logger.info("4. 如果Tesseract未在系统PATH中，使用-t参数指定路径")

if __name__ == "__main__":
    main()