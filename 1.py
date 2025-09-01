import streamlit as st
import pandas as pd
import re

# 设置页面标题
st.title("材料分析工具")
st.write("上传包含材料信息的Excel文件，系统将自动分析并展示结果")

# 文件上传组件
uploaded_file = st.file_uploader("选择Excel文件", type=["xlsx", "xls"])

def analyze_materials(df):
    # 设置显示所有行（不省略）
    pd.set_option('display.max_rows', None)

    # 仅按符号分割，保留完整信息（材料名称+重量）
    def extract_ingredients(ingredient_str):
        # 按多种符号（逗号、顿号等）切割成单个材料条目
        materials = re.split(r'[,，、]', ingredient_str)
        
        # 仅去除前后空格，保留完整信息
        pure_materials = []
        for mat in materials:
            mat_stripped = mat.strip()  # 只去除前后空格
            if mat_stripped:  # 跳过空字符串
                pure_materials.append(mat_stripped)
        
        return pure_materials

    # 应用函数，得到包含完整信息的材料列表
    df['材料列表'] = df['包含材料'].apply(extract_ingredients)

    # 展开列表，使每个材料单独成一行
    expanded_df = df.explode('材料列表')

    # 统计完全相同的材料条目（名称+重量完全一致）的出现次数
    ingredient_counts = expanded_df['材料列表'].value_counts().reset_index()
    ingredient_counts.columns = ['材料（含重量）', '出现次数']

    # 统计完全相同的材料条目对应的做货数量总和
    ingredient_quantity_sum = expanded_df.groupby('材料列表')['做货数量'].sum().reset_index()
    ingredient_quantity_sum.columns = ['材料（含重量）', '做货数量总和']

    # 整合所有信息：合并相同材料的统计数据
    consolidated_df = pd.merge(ingredient_counts, ingredient_quantity_sum, 
                               on='材料（含重量）', how='inner')

    # 按出现次数降序排列
    return consolidated_df.sort_values(by='出现次数', ascending=False)

if uploaded_file is not None:
    try:
        # 读取Excel文件
        excel_file = pd.ExcelFile(uploaded_file)
        df = excel_file.parse('Sheet1')
        
        # 显示原始数据预览
        st.subheader("原始数据预览")
        st.dataframe(df.head())
        
        # 执行分析
        result_df = analyze_materials(df)
        
        # 显示分析结果
        st.subheader("整合后的材料统计信息（包含重量）：")
        st.dataframe(result_df)
        
    except Exception as e:
        st.error(f"处理文件时出错：{str(e)}")
        st.error("请确保上传的文件格式正确，并且包含'Sheet1'工作表以及'包含材料'和'做货数量'列")
    