#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色名字自动链接脚本 - 手动指定简称版本
功能：使用手动指定的角色名字和简称映射，将文档中的角色名字转换为可点击的链接
"""

import os
import re

def get_relative_path(from_file, to_file):
    """计算从 from_file 到 to_file 的相对路径"""
    from_dir = os.path.dirname(from_file)
    return os.path.relpath(to_file, from_dir)

# 手动指定的角色名字映射（包含全名和简称）
CHARACTER_MAPPING = {
    '无月临光（乔光凝）': '03-异次元之融合/角色/无月临光（乔光凝）.md',
    '森口智子': '02-过往未来/角色/森口智子.md',
    '阳蒿六水': '03-异次元之融合/角色/阳蒿六水.md',
    '无月游穹': '03-异次元之融合/角色/无月游穹.md',
    'XCIX': '03-异次元之融合/角色/XCIX.md',
    '梅比兰德': '01-星海余晖/角色/梅比兰德.md',
    '维尔妮娅': '01-星海余晖/角色/维尔妮娅.md',
    '七劫千秋': '01-星海余晖/角色/七劫千秋.md',
    '露世芽樱': '01-星海余晖/角色/露世芽樱.md',
    '格蕾薇娅': '01-星海余晖/角色/格蕾薇娅.md',
    '钟悚灵': '02-过往未来/角色/钟悚灵.md',
    '光凝': '03-异次元之融合/角色/无月临光（乔光凝）.md',
    '石早月': '03-异次元之融合/角色/石早月.md',
    '孔天谋': '03-异次元之融合/角色/天谋.md',
    '零亚娜': '01-星海余晖/角色/零亚娜.md',
    '符仪华': '01-星海余晖/角色/符仪华.md',
    '帕绮娜': '01-星海余晖/角色/帕绮娜.md',
    '阿希亚': '01-星海余晖/角色/阿希亚.md',
    '伊琳娜': '01-星海余晖/角色/伊琳娜.md',
    '鸢一娑': '01-星海余晖/角色/娑.md',
    '忌克斯': '01-星海余晖/角色/忌克斯.md',
    '温劫': '02-过往未来/角色/温劫.md',
    '智子': '02-过往未来/角色/森口智子.md',
    '戴尔': '02-过往未来/角色/戴尔·蓉莉·李(Zone).md',
    'Zone': '02-过往未来/角色/戴尔·蓉莉·李(Zone).md',
    '悚灵': '02-过往未来/角色/钟悚灵.md',
    '六水': '03-异次元之融合/角色/阳蒿六水.md',
    '乔伊': '03-异次元之融合/角色/乔伊·弗罗斯特2.md',
    '游穹': '03-异次元之融合/角色/无月游穹.md',
    '早月': '03-异次元之融合/角色/石早月.md',
    '蒙星': '03-异次元之融合/角色/蒙星.md',
    '天谋': '03-异次元之融合/角色/天谋.md',
    '昔雅': '01-星海余晖/角色/昔雅.md',
    '凯文（ai）': '01-星海余晖/角色/凯文.md',
    '仪华': '01-星海余晖/角色/符仪华.md',
    '临光': '03-异次元之融合/角色/无月临光（乔光凝）.md',
    '娑': '01-星海余晖/角色/娑.md',
    '千秋': '01-星海余晖/角色/七劫千秋.md',
    '芽樱': '01-星海余晖/角色/露世芽樱.md',
    '薇娅': '01-星海余晖/角色/格蕾薇娅.md',
}

def build_char_map(docs_dir):
    """根据手动映射构建角色名字到完整路径的映射"""
    char_map = {}
    docs_base = docs_dir.rstrip('/')
    
    for name, rel_path in CHARACTER_MAPPING.items():
        full_path = os.path.join(docs_base, rel_path)
        # 验证文件是否存在
        if os.path.exists(full_path):
            char_map[name] = full_path
        else:
            print(f"⚠️  警告：文件不存在 - {rel_path} (对应名字：{name})")
    
    return char_map

def replace_names_with_links(content, char_map, current_file):
    """将内容中的角色名字替换为链接 - 最终修复版本"""
    lines = content.split('\n')
    # 按长度降序排序，确保长名字优先匹配
    sorted_names = sorted(char_map.keys(), key=len, reverse=True)
    
    for line_idx, line in enumerate(lines):
        # 跳过标题行
        if line.strip().startswith('#'):
            continue
        
        # 收集所有需要替换的位置
        replacements = []  # (start, end, name, rel_path)
        
        # 找出所有已经存在的链接 [text](url) 的范围
        protected_ranges = []
        for match in re.finditer(r'\[([^\]]+)\]\([^)]+\)', line):
            protected_ranges.append((match.start(), match.end()))
        
        # 找出所有图片引用 ![alt](url) 的范围
        for match in re.finditer(r'!\[[^\]]*\]\([^)]+\)', line):
            protected_ranges.append((match.start(), match.end()))
        
        def is_protected(start, end):
            """检查某个范围是否在已保护的范围内"""
            for p_start, p_end in protected_ranges:
                if start >= p_start and end <= p_end:
                    return True
            return False
        
        def is_overlap(start, end, existing_replacements):
            """检查是否与已有替换重叠"""
            for r_start, r_end, _, _ in existing_replacements:
                if not (end <= r_start or start >= r_end):
                    return True
            return False
        
        # 查找所有角色名字的出现位置（按长度从长到短处理）
        for name in sorted_names:
            filepath = char_map[name]
            rel_path = get_relative_path(current_file, filepath)
            
            pos = 0
            while True:
                idx = line.find(name, pos)
                if idx == -1:
                    break
                
                end_idx = idx + len(name)
                
                # 检查是否在已保护范围内
                if not is_protected(idx, end_idx):
                    # 检查是否与已有的替换重叠
                    if not is_overlap(idx, end_idx, replacements):
                        # 检查前后字符边界
                        before_char = line[idx-1] if idx > 0 else ' '
                        after_char = line[end_idx] if end_idx < len(line) else ' '
                        
                        # 边界检查：前后应该是标点、空格或中文
                        valid_before = before_char in ' \t\n，。、；：！？）】>"\'（「」『』【】…—' or '\u4e00' <= before_char <= '\u9fff'
                        valid_after = after_char in ' \t\n，。、；：！？）】>"\'（「」『』【】…—' or '\u4e00' <= after_char <= '\u9fff'
                        
                        # 特别注意：如果名字在另一个中文字符串中间（如"钟悚灵"中的"悚灵"），需要更严格的检查
                        is_inside_chinese = False
                        if '\u4e00' <= before_char <= '\u9fff' and '\u4e00' <= after_char <= '\u9fff':
                            # 前后都是中文，可能是部分匹配，跳过
                            is_inside_chinese = True
                        
                        if not is_inside_chinese and valid_before and valid_after:
                            replacements.append((idx, end_idx, name, rel_path))
                
                pos = end_idx
        
        # 按位置排序替换（从后往前替换，避免影响前面的位置）
        replacements.sort(key=lambda x: x[0], reverse=True)
        
        # 执行替换
        new_line = line
        for start, end, name, rel_path in replacements:
            new_line = new_line[:start] + f'[{name}]({rel_path})' + new_line[end:]
        
        lines[line_idx] = new_line
    
    return '\n'.join(lines)

def process_markdown_files(docs_dir, char_map):
    """处理所有 Markdown 文件"""
    processed_count = 0
    modified_count = 0
    
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            new_content = replace_names_with_links(original_content, char_map, filepath)
            
            if new_content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modified_count += 1
                print(f"✓ 修改：{filepath}")
            
            processed_count += 1
    
    return processed_count, modified_count

def main():
    docs_dir = '/workspace/docs'
    
    print("🔍 构建角色名字映射...")
    char_map = build_char_map(docs_dir)
    
    print(f"\n📋 共配置 {len(CHARACTER_MAPPING)} 个角色名字（包含简称）:")
    for name, rel_path in sorted(CHARACTER_MAPPING.items(), key=lambda x: len(x[0]), reverse=True):
        print(f"  '{name}' → {rel_path}")
    
    # 检查实际存在的文件数量
    existing_count = len(char_map)
    if existing_count < len(CHARACTER_MAPPING):
        print(f"\n⚠️  注意：有 {len(CHARACTER_MAPPING) - existing_count} 个文件未找到，已跳过")
    
    print(f"\n🔗 开始处理 Markdown 文件...")
    processed, modified = process_markdown_files(docs_dir, char_map)
    
    print(f"\n✅ 完成！")
    print(f"   处理文件：{processed} 个")
    print(f"   修改文件：{modified} 个")

if __name__ == '__main__':
    main()
