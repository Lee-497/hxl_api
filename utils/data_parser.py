"""
数据解析工具
用于处理和解析不同格式的数据
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class DataParser:
    """数据解析器"""
    
    @staticmethod
    def find_column(df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """
        在DataFrame中查找可能的列名
        
        Args:
            df: DataFrame
            possible_names: 可能的列名列表
            
        Returns:
            找到的列名，未找到返回None
        """
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    @staticmethod
    def get_column_info(df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取DataFrame的列信息
        
        Args:
            df: DataFrame
            
        Returns:
            包含列信息的字典
        """
        return {
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'shape': df.shape,
            'null_counts': df.isnull().sum().to_dict()
        }
    
    @staticmethod
    def filter_by_values(df: pd.DataFrame, column: str, exclude_values: List[str]) -> pd.DataFrame:
        """
        根据指定值过滤DataFrame
        
        Args:
            df: DataFrame
            column: 列名
            exclude_values: 要排除的值列表
            
        Returns:
            过滤后的DataFrame
        """
        if column not in df.columns:
            logger.warning(f"列 '{column}' 不存在于DataFrame中")
            return df
        
        original_count = len(df)
        filtered_df = df[~df[column].isin(exclude_values)]
        filtered_count = original_count - len(filtered_df)
        
        if filtered_count > 0:
            logger.info(f"从列 '{column}' 中过滤掉 {filtered_count} 行数据")
        
        return filtered_df
    
    @staticmethod
    def get_unique_values(df: pd.DataFrame, column: str, limit: int = 20) -> List[str]:
        """
        获取指定列的唯一值
        
        Args:
            df: DataFrame
            column: 列名
            limit: 返回的最大数量
            
        Returns:
            唯一值列表
        """
        if column not in df.columns:
            return []
        
        unique_values = df[column].unique()
        return list(unique_values[:limit])
    
    @staticmethod
    def print_data_summary(df: pd.DataFrame, name: str = "数据"):
        """
        打印数据摘要信息
        
        Args:
            df: DataFrame
            name: 数据名称
        """
        print(f"\n=== {name} 摘要 ===")
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {', '.join(df.columns[:10])}")
        if len(df.columns) > 10:
            print(f"... 还有 {len(df.columns) - 10} 列")
        
        # 显示缺失值情况
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print("缺失值情况:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"  {col}: {count} 个缺失值")
        else:
            print("无缺失值")
    
    @staticmethod
    def safe_merge(left_df: pd.DataFrame, right_df: pd.DataFrame, 
                   on: str, how: str = 'left') -> pd.DataFrame:
        """
        安全的DataFrame合并操作
        
        Args:
            left_df: 左侧DataFrame
            right_df: 右侧DataFrame
            on: 合并键
            how: 合并方式
            
        Returns:
            合并后的DataFrame
        """
        try:
            if on not in left_df.columns:
                logger.error(f"左侧DataFrame中不存在列 '{on}'")
                return left_df
            
            if on not in right_df.columns:
                logger.error(f"右侧DataFrame中不存在列 '{on}'")
                return left_df
            
            merged_df = pd.merge(left_df, right_df, on=on, how=how)
            logger.info(f"成功合并数据: {len(left_df)} + {len(right_df)} -> {len(merged_df)} 行")
            
            return merged_df
            
        except Exception as e:
            logger.error(f"数据合并失败: {str(e)}")
            return left_df


def get_data_parser() -> DataParser:
    """获取数据解析器实例"""
    return DataParser()