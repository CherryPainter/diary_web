#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF清洗工具：将PDF文件每一页转为图像，识别文本，提取英文单词和中文翻译，生成指定格式的JSON文件
"""

import os
import re
import json
import logging
import argparse
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from langdetect import detect
import fitz  # PyMuPDF

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_cleaner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFCleaner:
    def __init__(self, pdf_path, output_json, lang='chi_sim+eng', tesseract_cmd=None):
        """初始化PDF清洗器"""
        self.pdf_path = pdf_path
        self.output_json = output_json
        self.lang = lang
        
        # 设置tesseract命令路径（如果提供）
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
        
        # 存储结果的字典
        self.word_dict = {}
    
    def preprocess_image(self, image):
        """图像预处理以提高OCR准确率"""
        # 转换为灰度图
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # 应用自适应阈值处理
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 应用中值滤波减少噪声
        processed = cv2.medianBlur(thresh, 3)
        
        return Image.fromarray(processed)
        
    def _custom_preprocess(self, image, threshold_value):
        """使用自定义参数进行图像预处理"""
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # 使用不同的阈值参数
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, threshold_value, 2
        )
        
        return Image.fromarray(thresh)
    
    def extract_text_from_pdf(self):
        """从PDF中提取文本，确保能够提取所有页面的文本内容"""
        all_text = []
        doc = None
        
        try:
            # 方法1：使用PyMuPDF直接提取文本（适用于可复制文本的PDF）
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            logger.info(f"开始处理PDF，共 {total_pages} 页")
            
            for page_num in range(total_pages):
                page = doc[page_num]
                logger.info(f"处理第 {page_num+1}/{total_pages} 页")
                
                # 使用不同的提取格式以确保捕获所有可能的文本
                formats_to_try = ["text", "blocks", "words", "rawdict", "dict"]
                all_page_texts = []
                
                for fmt in formats_to_try:
                    try:
                        if fmt == "text":
                            text = page.get_text()
                        elif fmt == "blocks":
                            text = "\n".join([block[4] for block in page.get_text("blocks") if block[4].strip()])
                        elif fmt == "words":
                            # 提取单词及其位置信息
                            words_with_pos = page.get_text("words")
                            # 按垂直位置(y坐标)排序，然后是水平位置(x坐标)
                            words_with_pos.sort(key=lambda w: (w[1], w[0]))
                            text = " ".join([word[4] for word in words_with_pos if word[4].strip()])
                        elif fmt in ["rawdict", "dict"]:
                            # 提取结构化数据
                            doc_data = page.get_text(fmt)
                            if isinstance(doc_data, dict) and "blocks" in doc_data:
                                block_texts = []
                                for block in doc_data["blocks"]:
                                    if "lines" in block:
                                        for line in block["lines"]:
                                            if "spans" in line:
                                                line_text = "".join([span["text"] for span in line["spans"]])
                                                block_texts.append(line_text)
                                text = "\n".join(block_texts)
                            else:
                                text = str(doc_data)
                        else:
                            text = page.get_text(fmt)
                        
                        if text.strip():
                            all_page_texts.append((fmt, text))
                    except Exception as e:
                        logger.warning(f"使用格式 {fmt} 提取第 {page_num+1} 页失败: {e}")
                
                # 如果普通文本提取不理想，尝试OCR作为备选
                if not all_page_texts:
                    logger.info(f"第 {page_num+1} 页常规文本提取失败，使用OCR")
                    try:
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        
                        # 尝试多种预处理参数以提高OCR准确率
                        ocr_results = []
                        
                        # 标准预处理
                        processed_img = self.preprocess_image(img)
                        ocr_text = pytesseract.image_to_string(processed_img, lang=self.lang)
                        ocr_results.append(("标准OCR", ocr_text))
                        
                        # 尝试不同阈值的预处理
                        for threshold in [10, 12, 15]:
                            custom_processed = self._custom_preprocess(img, threshold)
                            custom_ocr = pytesseract.image_to_string(custom_processed, lang=self.lang)
                            ocr_results.append((f"自定义阈值OCR({threshold})", custom_ocr))
                        
                        # 选择OCR结果
                        best_ocr = max(ocr_results, key=lambda x: len(x[1]))
                        all_page_texts.append(best_ocr)
                    except Exception as e:
                        logger.error(f"第 {page_num+1} 页OCR失败: {e}")
                
                # 合并所有提取结果
                combined_text = "\n\n".join([text for _, text in all_page_texts])
                all_text.append(combined_text)
                logger.info(f"第 {page_num+1} 页提取完成，获得文本长度: {len(combined_text)} 字符")
            
            doc.close()
        except Exception as e:
            if doc:
                doc.close()
            logger.error(f"PyMuPDF提取失败，尝试使用pdf2image和OCR: {e}")
            # 方法2：转换为图像后使用OCR（适用于扫描版PDF）
            try:
                images = convert_from_path(self.pdf_path)
                for i, image in enumerate(images):
                    logger.info(f"使用pdf2image处理页面 {i+1}/{len(images)} 的OCR识别")
                    processed_img = self.preprocess_image(image)
                    ocr_text = pytesseract.image_to_string(processed_img, lang=self.lang)
                    all_text.append(ocr_text)
            except Exception as e2:
                logger.error(f"OCR处理失败: {e2}")
                raise
        
        # 合并所有页面的文本
        final_text = "\n\n".join(all_text)
        logger.info(f"PDF文本提取完成，总字符数: {len(final_text)}")
        return final_text
    
    def extract_word_translations(self, text):
        """从文本中提取英文单词和中文翻译，确保所有单词都被提取并去重"""
        logger.info(f"原始文本内容（前200字符）：{text[:200]}...")
        
        # 增强的文本预处理 - 更彻底地清理PDF特有噪声
        processed_text = text
        # 1. 移除重复的I字符（PDF表格常见问题）
        processed_text = re.sub(r'I{2,}', ' ', processed_text)
        # 2. 移除PDF相关噪声词
        processed_text = re.sub(r'\bPDF\b', ' ', processed_text)
        # 3. 移除其他可能的干扰字符
        processed_text = re.sub(r'[\x00-\x1f\x7f]', ' ', processed_text)
        # 4. 标准化空白字符
        processed_text = re.sub(r'\s+', ' ', processed_text)
        # 5. 移除行首行尾的空白
        processed_text = '\n'.join(line.strip() for line in processed_text.split('\n'))
        # 6. 按段落分割（保留更多结构信息）
        processed_text = re.sub(r'\s*\n\s*', '\n', processed_text)
        
        logger.info(f"预处理后文本（前200字符）：{processed_text[:200]}...")
        
        # 分割文本为行
        lines = [line for line in processed_text.split('\n') if line.strip()]
        logger.info(f"总共提取了 {len(lines)} 行非空文本")
        
        # 提取所有可能的英文单词（使用更宽松的模式）
        all_words = set()
        
        # 方法1：标准单词匹配（提取所有单词，不限制数量）
        standard_words = re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b', processed_text)
        all_words.update([word.lower() for word in standard_words if len(word) > 1])
        
        # 方法2：尝试匹配可能被错误分割的单词
        for line in lines:
            # 尝试匹配被空格分割的连续字母序列
            parts = line.split()
            i = 0
            while i < len(parts):
                if re.match(r'^[a-zA-Z]+$', parts[i]) and len(parts[i]) > 1:
                    # 检查是否是独立单词或可能是被分割的单词的一部分
                    all_words.add(parts[i].lower())
                i += 1
        
        # 方法3：从每行提取所有可能的单词
        for line in lines:
            # 尝试更宽松的单词提取
            relaxed_words = re.findall(r'[a-zA-Z]+(?:-[a-zA-Z]+)*', line)
            all_words.update([word.lower() for word in relaxed_words if len(word) > 1])
        
        # 转换为列表并排序以确保处理顺序一致
        unique_words = sorted(list(all_words))
        logger.info(f"提取到的唯一英文单词数量: {len(unique_words)}")
        
        # 尝试不同的中文提取模式
        chinese_blocks = []
        # 模式1：标准中文块
        chinese_blocks.extend(re.findall(r'[\u4e00-\u9fa5，；,;\s]+', processed_text))
        # 模式2：可能包含英文的中文段落
        for line in lines:
            if any('\u4e00' <= char <= '\u9fa5' for char in line):
                chinese_blocks.append(line)
        
        chinese_blocks = list(set(chinese_blocks))  # 去重
        logger.info(f"提取到的中文块数量: {len(chinese_blocks)}")
        
        # 初始化已处理的单词集合
        processed_words = set()
        
        # 直接提取所有单词，不依赖复杂的翻译匹配逻辑
        for word in unique_words:
            self._add_translation_direct(word)
            processed_words.add(word)
        
        # 尝试查找可能的翻译
        if chinese_blocks:
            self._find_possible_translations(lines, unique_words, processed_words)
        
        # 验证最终结果
        logger.info(f"单词提取完成，成功提取 {len(self.word_dict)} 个单词")
    
    def _add_translation_direct(self, word):
        """直接添加单词到字典，增强噪声词过滤"""
        # 过滤掉太短或可能不是单词的内容
        if len(word) < 2:
            return
        
        # 过滤噪声词 - 连续相同字符
        if re.search(r'(.)\1{2,}', word):  # 3个或更多连续相同字符
            logger.debug(f"过滤噪声词（连续字符）: '{word}'")
            return
        
        # 过滤明显的PDF噪声词
        noise_words = ['pdf', 'ipdf', 'if']
        if word.lower() in noise_words:
            logger.debug(f"过滤噪声词（已知噪声）: '{word}'")
            return
        
        # 简化的单词验证 - 只检查是否只包含字母和连字符
        if not re.match(r'^[a-zA-Z]+(?:-[a-zA-Z]+)*$', word):
            return
        
        # 将单词添加到字典中，暂时没有翻译
        if word not in self.word_dict:
            self.word_dict[word] = []
            logger.info(f"直接添加单词: '{word}'")
    
    def _find_possible_translations(self, lines, unique_words, processed_words):
        """增强的翻译匹配逻辑，使用多种策略找到可能的翻译"""
        logger.info("开始尝试查找可能的单词翻译...")
        
        # 增强的翻译匹配模式
        translation_patterns = [
            # 模式1: word: 中文翻译 或 word:中文翻译
            (r'(\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b)\s*[:：]\s*([\u4e00-\u9fa5，；,;]+)', 1, 2),
            # 模式2: word - 中文翻译 或 word-中文翻译
            (r'(\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b)\s*[-－]\s*([\u4e00-\u9fa5，；,;]+)', 1, 2),
            # 模式3: word = 中文翻译 或 word=中文翻译
            (r'(\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b)\s*[=＝]\s*([\u4e00-\u9fa5，；,;]+)', 1, 2),
            # 模式4: 中文翻译: word
            (r'([\u4e00-\u9fa5]+)\s*[:：]\s*(\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b)', 2, 1),
            # 模式5: 中文翻译 - word
            (r'([\u4e00-\u9fa5]+)\s*[-－]\s*(\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b)', 2, 1),
        ]
        
        # 策略1: 使用正则表达式模式匹配
        for line in lines:
            for pattern, word_group, trans_group in translation_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if len(match.groups()) >= max(word_group, trans_group):
                        word = match.group(word_group).lower()
                        translation = match.group(trans_group)
                        
                        if word in self.word_dict:
                            self._add_translation(word, translation)
                            logger.info(f"模式匹配: '{word}' -> '{translation}'")
        
        # 策略2: 行内同时有英文和中文的情况（放宽条件）
        for line in lines:
            has_english = bool(re.search(r'\b[a-zA-Z]+\b', line))
            has_chinese = any('\u4e00' <= char <= '\u9fa5' for char in line)
            
            if has_english and has_chinese:
                # 提取行中的所有英文单词
                words_in_line = re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b', line)
                # 提取行中的所有中文部分
                chinese_parts = re.findall(r'[\u4e00-\u9fa5]+', line)
                
                if words_in_line and chinese_parts:
                    # 如果一行只有一个英文单词，很可能与该行的中文部分对应
                    if len(words_in_line) == 1:
                        word = words_in_line[0].lower()
                        chinese_text = ''.join(chinese_parts)
                        if word in self.word_dict:
                            self._add_translation(word, chinese_text)
                            logger.info(f"单行单单词匹配: '{word}' -> '{chinese_text}'")
                    # 否则尝试匹配单词和最近的中文
                    else:
                        # 将行分割为段落或短语
                        segments = re.split(r'[;；.。!！?？]', line)
                        for segment in segments:
                            seg_words = re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b', segment)
                            seg_chinese = re.findall(r'[\u4e00-\u9fa5]+', segment)
                            if seg_words and seg_chinese:
                                for word in seg_words:
                                    word = word.lower()
                                    if word in self.word_dict:
                                        self._add_translation(word, ''.join(seg_chinese))
                                        logger.info(f"段落匹配: '{word}' -> '{''.join(seg_chinese)}'")
        
        # 策略3: 行对行匹配（英文行后面是中文行）
        for i in range(len(lines) - 1):
            current_line = lines[i].strip()
            next_line = lines[i + 1].strip()
            
            # 检查当前行是否主要是英文，下一行是否主要是中文
            current_has_english = bool(re.search(r'\b[a-zA-Z]+\b', current_line))
            current_has_chinese = any('\u4e00' <= char <= '\u9fa5' for char in current_line)
            next_has_chinese = any('\u4e00' <= char <= '\u9fa5' for char in next_line)
            
            # 放宽条件：只要当前行有英文且下一行有中文就尝试匹配
            if current_has_english and next_has_chinese:
                words_in_line = re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b', current_line)
                # 提取下一行中的所有中文
                next_chinese = ''.join(re.findall(r'[\u4e00-\u9fa5]+', next_line))
                
                if words_in_line and next_chinese:
                    # 如果当前行只有一个单词，很可能与下一行的中文对应
                    if len(words_in_line) == 1:
                        word = words_in_line[0].lower()
                        if word in self.word_dict:
                            self._add_translation(word, next_chinese)
                            logger.info(f"单行对单行匹配: '{word}' -> '{next_chinese}'")
                    else:
                        # 尝试匹配每个单词
                        for word in words_in_line:
                            word = word.lower()
                            if word in self.word_dict:
                                # 对于多行多词的情况，仍然尝试匹配，但记录为低置信度
                                self._add_translation(word, next_chinese)
                                logger.info(f"多行多词匹配: '{word}' -> '{next_chinese}'")
        
        # 策略4: 检查特殊格式如表格或列表
        for line in lines:
            # 尝试匹配类似表格的格式
            if '\t' in line or '|' in line or '  ' in line:  # 可能是表格分隔符
                parts = re.split(r'[\t|]|\s{2,}', line)
                for part in parts:
                    part = part.strip()
                    if part:
                        # 检查每个部分是否包含单词和翻译
                        words = re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b', part)
                        chinese = ''.join(re.findall(r'[\u4e00-\u9fa5]+', part))
                        
                        if words and chinese:
                            for word in words:
                                word = word.lower()
                                if word in self.word_dict:
                                    self._add_translation(word, chinese)
                                    logger.info(f"表格格式匹配: '{word}' -> '{chinese}'")
    
    def _recursive_extract(self, text, lines, unique_words, sample_translations, processed_words, max_depth=5):
        """递归提取单词和翻译，此方法保持兼容但不再作为主要提取方式"""
        # 由于我们已经在extract_word_translations中直接提取了所有单词，这里可以简化
        logger.info("使用递归提取方法补充查找翻译...")
        
        # 如果sample_translations有内容，仍可使用
        if sample_translations:
            for word in unique_words:
                if word in sample_translations and word in self.word_dict:
                    self._add_translation(word, sample_translations[word])
                    logger.info(f"使用样本翻译: '{word}' -> '{sample_translations[word]}'")
    
    def _add_translation(self, word, translation):
        """增强的翻译添加逻辑，优化去重和清理"""
        # 过滤掉太短或可能不是单词的内容
        if len(word) < 2:
            return
        
        # 简化的单词验证 - 只检查是否只包含字母和连字符
        if not re.match(r'^[a-zA-Z]+(?:-[a-zA-Z]+)*$', word):
            return
        
        # 记录处理的单词和翻译
        logger.debug(f"处理单词: '{word}'，原始翻译: '{translation}'")
        
        # 确保单词存在于字典中
        if word not in self.word_dict:
            self.word_dict[word] = []
        
        # 提取所有中文内容
        chinese_only = ''.join([char for char in translation if '\u4e00' <= char <= '\u9fa5'])
        
        if chinese_only:
            # 更智能的多义词分割 - 尝试多种分隔符
            split_chars = ['，', ',', '；', ';', '、', ' ', '和', '或', '及']
            
            # 先尝试使用标准标点分割
            translations = re.split(r'[,，;；、]', chinese_only)
            
            # 如果分割后只有一个元素，尝试其他分隔方式
            if len(translations) == 1:
                # 尝试基于字符数进行启发式分割（简单的多义词识别）
                char_count = len(chinese_only)
                if 2 < char_count <= 4:  # 可能是两个2字词语
                    translations = [chinese_only[:2], chinese_only[2:]]
                elif 4 < char_count <= 6:  # 可能是三个2字词语或两个3字词语
                    if char_count % 2 == 0:
                        translations = [chinese_only[i:i+2] for i in range(0, char_count, 2)]
                    else:
                        # 简单分割为前3后3
                        translations = [chinese_only[:3], chinese_only[3:]]
            
            # 清理每个翻译项
            cleaned_translations = []
            for trans in translations:
                trans = trans.strip()
                # 只保留有效的中文翻译（至少1个中文字符）
                if trans and any('\u4e00' <= char <= '\u9fa5' for char in trans):
                    cleaned_translations.append(trans)
            
            # 添加新的翻译，确保去重
            original_count = len(self.word_dict[word])
            for trans in cleaned_translations:
                if trans not in self.word_dict[word]:
                    self.word_dict[word].append(trans)
                    logger.debug(f"  添加翻译到字典: '{word}' -> '{trans}'")
            
            # 记录去重情况
            new_count = len(self.word_dict[word])
            if new_count > original_count:
                logger.info(f"  单词 '{word}' 新增 {new_count - original_count} 个翻译")
    
    def save_to_json(self):
        """保存结果到JSON文件，确保输出干净的结果"""
        # 最终清理：移除明显的噪声词和不合理的条目
        final_result = {}
        
        # 定义最终的噪声词列表
        final_noise_words = {'pdf', 'ipdf', 'if', 'i', 'ii', 'iii', 'iiii', 'iiiiii', 'iiiiiii'}
        
        for word, translations in self.word_dict.items():
            # 最终过滤
            if word.lower() not in final_noise_words and len(word) >= 1:
                final_result[word] = translations
        
        # 按字母顺序排序结果，使输出更有条理
        sorted_result = {k: final_result[k] for k in sorted(final_result.keys())}
        
        with open(self.output_json, 'w', encoding='utf-8') as f:
            json.dump(sorted_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到 {self.output_json}")
        logger.info(f"共提取了 {len(sorted_result)} 个单词及其翻译")
    
    def process(self):
        """处理PDF文件的主函数，实现完整的单词提取"""
        logger.info(f"开始处理PDF文件: {self.pdf_path}")
        
        # 初始化结果字典
        self.word_dict = {}
        
        # 提取文本
        text = self.extract_text_from_pdf()
        logger.info(f"成功提取文本，共 {len(text)} 个字符")
        
        # 首先直接提取所有英文单词，但使用增强的过滤方法
        logger.info("直接提取所有英文单词...")
        all_words = set(re.findall(r'\b[a-zA-Z]+(?:-[a-zA-Z]+)*\b', text))
        
        # 使用增强的_add_translation_direct方法过滤并添加单词
        for word in all_words:
            self._add_translation_direct(word)
        
        logger.info(f"初始提取到 {len(self.word_dict)} 个英文单词")
        
        # 提取单词和翻译（主要是为了匹配翻译）
        self.extract_word_translations(text)
        
        # 增强的备用提取逻辑 - 无论单词数量多少都尝试
        logger.info("运行增强的翻译匹配逻辑...")
        
        # 分割文本为行
        lines = [line for line in text.split('\n') if line.strip()]
        
        # 再次运行翻译匹配
        self._find_possible_translations(lines, list(self.word_dict.keys()), set())
        
        # 过滤最终结果，移除可疑的噪声词
        clean_dict = {}
        # 定义常见的短单词（避免误过滤有意义的短单词）
        common_short_words = {'to', 'it', 'is', 'in', 'on', 'at', 'of', 'for', 'and', 'the', 'by', 'an', 'as', 'be', 'we', 'he', 'she', 'me', 'my', 'you'}
        
        for word, trans in self.word_dict.items():
            # 过滤噪声词规则 - 保留大多数有效单词
            if len(word) >= 2 or word.lower() in common_short_words:
                # 只过滤明显不合理的单词（如连续5个相同字母）
                if not re.search(r'(.)\1{4,}', word.lower()):
                    clean_dict[word] = trans
        
        self.word_dict = clean_dict
        logger.info(f"过滤后保留 {len(self.word_dict)} 个有效单词")
        
        # 统计有翻译的单词数量
        translated_words_count = sum(1 for trans in self.word_dict.values() if trans)
        logger.info(f"翻译匹配完成，{translated_words_count} 个单词找到中文翻译")
        
        # 确保至少提取了一些单词
        if len(self.word_dict) == 0:
            logger.error("未能提取到任何单词，检查PDF内容或格式")
        
        # 保存到JSON
        self.save_to_json()
        
        logger.info("PDF清洗完成！")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PDF清洗工具')
    parser.add_argument('pdf_path', nargs='?', help='PDF文件路径')
    parser.add_argument('-o', '--output', default='output.json', help='输出JSON文件路径')
    parser.add_argument('-l', '--lang', default='chi_sim+eng', help='OCR语言设置')
    parser.add_argument('-t', '--tesseract', help='Tesseract-OCR命令路径')
    
    args = parser.parse_args()
    
    # 如果没有通过命令行提供PDF路径，提示用户输入
    if args.pdf_path is None:
        print("欢迎使用PDF清洗工具！")
        print("请输入PDF文件的路径：")
        args.pdf_path = input().strip()
        
        # 如果用户输入的路径不包含文件扩展名，提示用户
        if not args.pdf_path.lower().endswith('.pdf'):
            print(f"警告：输入的路径 '{args.pdf_path}' 可能不是PDF文件")
            print("是否继续处理？(y/n): ")
            if input().strip().lower() != 'y':
                print("程序已取消。")
                return
    
    # 检查PDF文件是否存在
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF文件不存在: {args.pdf_path}")
        print(f"错误：PDF文件不存在: {args.pdf_path}")
        print("请检查文件路径是否正确。")
        return
    
    # 创建并运行PDF清洗器
    cleaner = PDFCleaner(
        pdf_path=args.pdf_path,
        output_json=args.output,
        lang=args.lang,
        tesseract_cmd=args.tesseract
    )
    
    try:
        cleaner.process()
    except Exception as e:
        logger.error(f"处理过程中出错: {e}")
        raise

if __name__ == "__main__":
    main()