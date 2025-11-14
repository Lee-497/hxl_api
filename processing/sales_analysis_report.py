"""
销售分析报表
处理销售分析原始数据，生成汇总报表
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from config.settings import PROCESSED_DIR
from utils.data_loader import get_data_loader
from utils.data_parser import get_data_parser
from utils.logger import get_logger
from utils.file_utils import generate_timestamped_filename

logger = get_logger(__name__)

# 声明依赖的原始数据模块
DEPENDENCIES = ["商品销售数据"]


def run() -> Optional[Path]:
    """
    执行销售分析报表生成
    
    Returns:
        生成的报表文件路径，失败返回None
    """
    logger.info("开始处理销售分析报表数据")
    
    try:
        # 1. 加载销售分析数据
        data_loader = get_data_loader()
        sales_df = data_loader.load_latest_module_data("商品销售数据")
        
        if sales_df is None or sales_df.empty:
            logger.error("销售分析数据加载失败或为空")
            return None
        
        logger.info(f"原始销售分析数据: {len(sales_df)} 行")
        
        # 打印数据摘要
        data_parser = get_data_parser()
        data_parser.print_data_summary(sales_df, "销售分析数据")
        
        # 2. 数据清洗和处理
        processed_df = process_sales_data(sales_df)
        
        if processed_df is None or processed_df.empty:
            logger.error("销售数据处理失败")
            return None
        
        logger.info(f"处理后销售数据: {len(processed_df)} 行")
        
        # 3. 生成汇总统计
        summary_stats = generate_summary_statistics(processed_df)
        logger.info(f"销售汇总统计: {summary_stats}")
        
        # 4. 保存处理后的报表
        output_filename = generate_timestamped_filename("销售分析报表", "xlsx")
        output_path = PROCESSED_DIR / output_filename
        
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用ExcelWriter创建多个工作表
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 主数据表
            processed_df.to_excel(writer, sheet_name='销售明细', index=False)
            
            # 汇总统计表
            if summary_stats:
                summary_df = pd.DataFrame([summary_stats])
                summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
            
            # 按门店汇总
            if '门店名称' in processed_df.columns:
                store_summary = processed_df.groupby('门店名称').agg({
                    '销售金额': 'sum',
                    '销售数量': 'sum'
                }).reset_index()
                store_summary.to_excel(writer, sheet_name='门店汇总', index=False)
            
            # 按商品分类汇总
            if '商品分类' in processed_df.columns:
                category_summary = processed_df.groupby('商品分类').agg({
                    '销售金额': 'sum',
                    '销售数量': 'sum'
                }).reset_index()
                category_summary.to_excel(writer, sheet_name='分类汇总', index=False)
        
        logger.info(f"销售分析报表生成成功: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"销售分析报表生成失败: {str(e)}")
        return None


def process_sales_data(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    处理销售数据
    
    Args:
        df: 原始销售数据
        
    Returns:
        处理后的数据框
    """
    try:
        logger.info("开始处理销售数据")
        
        # 创建数据副本
        processed_df = df.copy()
        
        # 数据类型转换和清洗
        numeric_columns = ['销售金额', '销售数量', '成本金额', '毛利金额']
        for col in numeric_columns:
            if col in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').fillna(0)
        
        # 日期列处理
        date_columns = ['销售日期', '业务日期']
        for col in date_columns:
            if col in processed_df.columns:
                processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
        
        # 计算毛利率
        if '销售金额' in processed_df.columns and '毛利金额' in processed_df.columns:
            processed_df['毛利率'] = processed_df.apply(
                lambda row: (row['毛利金额'] / row['销售金额'] * 100) if row['销售金额'] > 0 else 0,
                axis=1
            )
        
        # 过滤异常数据
        # 移除销售金额为负数的记录
        if '销售金额' in processed_df.columns:
            negative_count = len(processed_df[processed_df['销售金额'] < 0])
            if negative_count > 0:
                logger.warning(f"发现 {negative_count} 条销售金额为负数的记录，将被移除")
                processed_df = processed_df[processed_df['销售金额'] >= 0]
        
        # 移除空的商品名称
        if '商品名称' in processed_df.columns:
            empty_name_count = len(processed_df[processed_df['商品名称'].isna() | (processed_df['商品名称'] == '')])
            if empty_name_count > 0:
                logger.warning(f"发现 {empty_name_count} 条商品名称为空的记录，将被移除")
                processed_df = processed_df[processed_df['商品名称'].notna() & (processed_df['商品名称'] != '')]
        
        logger.info(f"数据处理完成，处理后数据量: {len(processed_df)} 行")
        return processed_df
        
    except Exception as e:
        logger.error(f"销售数据处理失败: {str(e)}")
        return None


def generate_summary_statistics(df: pd.DataFrame) -> Optional[dict]:
    """
    生成汇总统计信息
    
    Args:
        df: 处理后的销售数据
        
    Returns:
        统计信息字典
    """
    try:
        stats = {}
        
        # 基本统计
        stats['总记录数'] = len(df)
        
        # 销售金额统计
        if '销售金额' in df.columns:
            stats['总销售金额'] = df['销售金额'].sum()
            stats['平均销售金额'] = df['销售金额'].mean()
            stats['最大单笔销售'] = df['销售金额'].max()
            stats['最小单笔销售'] = df['销售金额'].min()
        
        # 销售数量统计
        if '销售数量' in df.columns:
            stats['总销售数量'] = df['销售数量'].sum()
            stats['平均销售数量'] = df['销售数量'].mean()
        
        # 毛利统计
        if '毛利金额' in df.columns:
            stats['总毛利金额'] = df['毛利金额'].sum()
            stats['平均毛利金额'] = df['毛利金额'].mean()
        
        if '毛利率' in df.columns:
            stats['平均毛利率'] = df['毛利率'].mean()
            stats['最高毛利率'] = df['毛利率'].max()
            stats['最低毛利率'] = df['毛利率'].min()
        
        # 门店统计
        if '门店名称' in df.columns:
            stats['涉及门店数'] = df['门店名称'].nunique()
        
        # 商品统计
        if '商品名称' in df.columns:
            stats['涉及商品数'] = df['商品名称'].nunique()
        
        # 分类统计
        if '商品分类' in df.columns:
            stats['涉及分类数'] = df['商品分类'].nunique()
        
        return stats
        
    except Exception as e:
        logger.error(f"生成汇总统计失败: {str(e)}")
        return None


def get_description() -> str:
    """获取报表描述"""
    return "销售分析数据处理报表，包含销售明细、汇总统计、门店汇总、分类汇总等"


if __name__ == "__main__":
    # 测试运行
    result = run()
    if result:
        print(f"测试成功，报表路径: {result}")
    else:
        print("测试失败")
