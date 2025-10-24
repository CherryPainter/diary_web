#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成示例PDF文件，用于测试PDF清洗工具
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os

def generate_sample_pdf():
    """生成包含英文单词和中文翻译的示例PDF"""
    pdf_path = "sample_words.pdf"
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 定义样式
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    
    # 创建单词和翻译数据
    word_data = [
        ("freedom", "自由，自主，自由度"),
        ("example", "例子，实例，范例"),
        ("technology", "技术，科技，工艺"),
        ("opportunity", "机会，机遇，时机"),
        ("challenge", "挑战，难题，质疑"),
        ("solution", "解决方案，解答，溶解"),
        ("development", "发展，开发，发育"),
        ("innovation", "创新，革新，新观念"),
        ("communication", "交流，沟通，通讯"),
        ("collaboration", "合作，协作，共同研究"),
        ("efficiency", "效率，效能，功效"),
        ("effectiveness", "有效性，效果，影响"),
        ("responsibility", "责任，职责，义务"),
        ("integrity", "诚实，正直，完整"),
        ("creativity", "创造力，创造性，创意"),
        ("leadership", "领导力，领导阶层，领导才能"),
        ("teamwork", "团队合作，协同工作"),
        ("quality", "质量，品质，特性"),
        ("excellence", "卓越，优秀，杰出"),
        ("professionalism", "专业精神，专业主义，专业技巧")
    ]
    
    # 构建PDF内容
    story = []
    
    # 添加标题
    title = Paragraph("英语单词与中文翻译示例", title_style)
    story.append(title)
    story.append(Spacer(1, 1*cm))
    
    # 添加说明
    intro = Paragraph("本PDF文件包含英语单词及其中文翻译，用于测试PDF清洗工具。每个单词可能有多个中文释义，用逗号分隔。", normal_style)
    story.append(intro)
    story.append(Spacer(1, 1*cm))
    
    # 添加单词表格
    table_data = [['英文单词', '中文翻译']]
    for word, translation in word_data:
        table_data.append([word, translation])
    
    table = Table(table_data, colWidths=[6*cm, 10*cm])
    
    # 设置表格样式
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 2*cm))
    
    # 添加更多示例（不同格式）
    format_note = Paragraph("不同格式的单词翻译示例：", styles['Heading2'])
    story.append(format_note)
    
    # 格式1：单词 - 翻译
    format1_text = "<br/><br/>"
    format1_text += "freedom - 自由；自主<br/>"
    format1_text += "example - 例子；实例<br/>"
    format1_text += "technology - 技术；科技<br/>"
    format1_text = Paragraph(format1_text, normal_style)
    story.append(format1_text)
    story.append(Spacer(1, 1*cm))
    
    # 格式2：单词: 翻译
    format2_text = "<br/><br/>"
    format2_text += "opportunity: 机会，机遇<br/>".replace(':', ': ')
    format2_text += "challenge: 挑战，难题<br/>".replace(':', ': ')
    format2_text += "solution: 解决方案，解答<br/>".replace(':', ': ')
    format2_text = Paragraph(format2_text, normal_style)
    story.append(format2_text)
    
    # 构建PDF
    doc.build(story)
    
    print(f"示例PDF文件已生成：{os.path.abspath(pdf_path)}")
    print("\nPDF文件包含以下内容：")
    print("1. 20个英语单词及其中文翻译（表格形式）")
    print("2. 不同格式的单词翻译示例")
    print("3. 多义词用逗号和分号分隔的翻译")
    print("\n您现在可以使用此PDF文件测试PDF清洗工具：")
    print(f"python pdf_cleaner.py {pdf_path} -o output.json")

def main():
    """主函数"""
    print("生成示例PDF文件...")
    generate_sample_pdf()

if __name__ == "__main__":
    main()