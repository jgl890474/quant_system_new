# -*- coding: utf-8 -*-
"""
批量修复 Streamlit 废弃参数警告
运行: python tools/fix_streamlit_warnings.py
"""

import os
import re
import glob

def fix_use_container_width(file_path):
    """修复单个文件中的 use_container_width"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    changes = []
    
    # 1. 替换 use_container_width=True -> width="stretch"
    pattern1 = r'use_container_width\s*=\s*True\b'
    if re.search(pattern1, content):
        content = re.sub(pattern1, 'width="stretch"', content)
        changes.append("use_container_width=True -> width='stretch'")
    
    # 2. 替换 use_container_width=False -> width="content"
    pattern2 = r'use_container_width\s*=\s*False\b'
    if re.search(pattern2, content):
        content = re.sub(pattern2, 'width="content"', content)
        changes.append("use_container_width=False -> width='content'")
    
    # 3. 修复 st.plotly_chart 的 use_container_width
    pattern3 = r'st\.plotly_chart\((.*?),\s*width=["\']stretch["\']\)'
    if re.search(pattern3, content):
        content = re.sub(pattern3, r'st.plotly_chart(\1, use_container_width=True)', content)
        changes.append("st.plotly_chart width -> use_container_width")
    
    # 4. 修复 st.dataframe 的 use_container_width
    pattern4 = r'st\.dataframe\((.*?),\s*width=["\']stretch["\']'
    if re.search(pattern4, content):
        content = re.sub(pattern4, r'st.dataframe(\1, use_container_width=True)', content)
        changes.append("st.dataframe width -> use_container_width")
    
    # 5. 修复 st.table 的 use_container_width
    pattern5 = r'st\.table\((.*?),\s*width=["\']stretch["\']'
    if re.search(pattern5, content):
        content = re.sub(pattern5, r'st.table(\1, use_container_width=True)', content)
        changes.append("st.table width -> use_container_width")
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {file_path}")
            for change in changes:
                print(f"   - {change}")
            return True
        except:
            return False
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 开始修复 Streamlit 废弃参数警告...")
    print("=" * 60)
    
    # 需要扫描的目录
    target_dirs = ['.', '前端', '核心', '回测', '工具', '脚本']
    
    fixed_count = 0
    total_files = 0
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
        
        if target_dir == '.':
            # 扫描根目录下的py文件
            for file in glob.glob('*.py'):
                if fix_use_container_width(file):
                    fixed_count += 1
                total_files += 1
        else:
            # 扫描子目录
            for root, dirs, files in os.walk(target_dir):
                # 排除缓存目录
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.streamlit', 'venv', 'env', '.git']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        if fix_use_container_width(file_path):
                            fixed_count += 1
                        total_files += 1
    
    print("=" * 60)
    print(f"📊 扫描文件总数: {total_files}")
    print(f"✅ 修复文件数量: {fixed_count}")
    print("=" * 60)
    
    if fixed_count == 0:
        print("🎉 没有发现需要修复的 use_container_width 警告！")
    else:
        print("🎉 修复完成！")
    
    print("\n📝 下一步：")
    print("1. 运行 'streamlit run 启动入口.py' 测试")
    print("2. 检查控制台是否还有警告")
    print("3. 确认无误后提交到 GitHub")

if __name__ == "__main__":
    main()
