#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文小说广告删除工具
用于自动识别和删除中文小说txt文件中的广告内容
"""

import re
import os
import argparse
from typing import List, Tuple

class ChineseNovelAdRemover:
    def __init__(self):
        # 广告关键词模式
        self.ad_keywords = [
            # 广告标识词
            r'广告', r'推广', r'赞助', r'商业合作', r'商务合作',
            r'联系我们', r'联系方式', r'合作热线',
            
            # 营销词汇
            r'免费', r'下载', r'注册', r'领取', r'优惠', r'折扣',
            r'限时', r'特价', r'促销', r'活动',
            
            # 平台推广
            r'扫一扫', r'二维码', r'公众号', r'微信', r'QQ群?',
            r'微博', r'抖音', r'快手', r'小红书',
            
            # 网址模式
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            
            # 联系方式
            r'\b\d{3}[-.\s]?\d{4}[-.\s]?\d{4}\b',  # 手机号
            r'\b\d{2,4}[-.\s]?\d{7,8}\b',  # 固定电话
            r'QQ[:：]?\s*\d{5,11}',
            r'微信[:：]?\s*[a-zA-Z0-9_-]{6,20}',
            
            # 应用商店
            r'应用商店', r'应用市场', r'App Store', r'Google Play',
            
            # 小说平台
            r'起点', r'纵横', r'晋江', r'红袖', r'潇湘', r'17K',
            r'掌阅', r'书旗', r'QQ阅读'
        ]
        
        # 编译正则表达式
        self.ad_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.ad_keywords]
        
        # 段落长度阈值（过短的段落可能是广告）
        self.min_paragraph_length = 10
        
    def is_advertisement(self, paragraph: str) -> bool:
        """
        判断段落是否为广告
        """
        # 空段落或过短段落
        if len(paragraph.strip()) < self.min_paragraph_length:
            return True
            
        paragraph_lower = paragraph.lower()
        
        # 检查是否包含广告关键词
        for pattern in self.ad_patterns:
            if pattern.search(paragraph_lower):
                return True
                
        # 检查是否包含大量数字（可能是联系方式）
        digit_ratio = sum(c.isdigit() for c in paragraph) / len(paragraph) if paragraph else 0
        if digit_ratio > 0.3:  # 数字占比超过30%
            return True
            
        # 检查是否包含特殊字符比例过高
        special_chars = sum(not c.isalnum() and not c.isspace() for c in paragraph)
        special_ratio = special_chars / len(paragraph) if paragraph else 0
        if special_ratio > 0.4:  # 特殊字符占比超过40%
            return True
            
        return False
    
    def remove_ads_from_text(self, text: str) -> Tuple[str, int]:
        """
        从文本中删除广告
        返回清理后的文本和删除的广告数量
        """
        # 按段落分割（空行分隔）
        paragraphs = text.split('\n\n')
        cleaned_paragraphs = []
        ads_removed = 0
        
        for paragraph in paragraphs:
            # 如果段落不是广告，保留
            if not self.is_advertisement(paragraph.strip()):
                cleaned_paragraphs.append(paragraph)
            else:
                ads_removed += 1
                
        # 重新组合文本
        cleaned_text = '\n\n'.join(cleaned_paragraphs)
        
        return cleaned_text, ads_removed
    
    def process_file(self, input_file: str, output_file: str = None) -> bool:
        """
        处理单个文件
        """
        try:
            # 读取文件
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 删除广告
            cleaned_content, ads_removed = self.remove_ads_from_text(content)
            
            # 确定输出文件路径
            if output_file is None:
                base_name = os.path.splitext(input_file)[0]
                output_file = f"{base_name}_cleaned.txt"
                
            # 写入清理后的内容
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            print(f"✓ 处理完成: {input_file}")
            print(f"✓ 删除广告段落: {ads_removed} 个")
            print(f"✓ 输出文件: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"✗ 处理文件 {input_file} 时出错: {e}")
            return False
    
    def process_directory(self, directory: str, output_dir: str = None) -> bool:
        """
        处理目录中的所有txt文件
        """
        try:
            # 获取目录中的所有txt文件
            txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
            
            if not txt_files:
                print(f"在目录 {directory} 中未找到txt文件")
                return False
                
            # 创建输出目录
            if output_dir is None:
                output_dir = os.path.join(directory, 'cleaned')
            os.makedirs(output_dir, exist_ok=True)
            
            success_count = 0
            total_ads = 0
            
            for txt_file in txt_files:
                input_path = os.path.join(directory, txt_file)
                output_path = os.path.join(output_dir, txt_file)
                
                if self.process_file(input_path, output_path):
                    success_count += 1
                    # 这里可以添加获取删除广告数量的逻辑
                    
            print(f"\n✓ 处理完成: {success_count}/{len(txt_files)} 个文件")
            return True
            
        except Exception as e:
            print(f"✗ 处理目录 {directory} 时出错: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='中文小说广告删除工具')
    parser.add_argument('input', help='输入文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件或目录路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    remover = ChineseNovelAdRemover()
    
    if os.path.isfile(args.input):
        # 处理单个文件
        remover.process_file(args.input, args.output)
    elif os.path.isdir(args.input):
        # 处理目录
        remover.process_directory(args.input, args.output)
    else:
        print(f"错误: 路径 {args.input} 不存在")


if __name__ == "__main__":
    main()
