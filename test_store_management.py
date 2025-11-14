"""
门店管理模块测试脚本
"""

from modules.store_management import StoreManagement
from utils.logger import get_logger
import json

logger = get_logger(__name__)


def test_basic_query():
    """测试基础门店查询"""
    print("=== 测试基础门店查询 ===")
    
    store_mgmt = StoreManagement()
    result = store_mgmt.query_stores()
    
    if "error" not in result:
        print("✅ 基础查询成功")
        
        # 打印响应结构
        print(f"响应类型: {type(result)}")
        if isinstance(result, dict):
            print(f"响应键: {list(result.keys())}")
            
            if 'data' in result:
                data = result['data']
                print(f"数据类型: {type(data)}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"门店数量: {len(data)}")
                    print(f"第一个门店字段: {list(data[0].keys()) if isinstance(data[0], dict) else '非字典类型'}")
                    
                    # 显示前3个门店的基本信息
                    for i, store in enumerate(data[:3]):
                        if isinstance(store, dict):
                            store_id = store.get('id', '未知ID')
                            store_name = store.get('name', store.get('store_name', '未知名称'))
                            print(f"  门店 {i+1}: ID={store_id}, 名称={store_name}")
            
            if 'total' in result:
                print(f"总数: {result['total']}")
                
    else:
        print(f"❌ 基础查询失败: {result['error']}")
    
    print()


def test_pagination_query():
    """测试分页查询"""
    print("=== 测试分页查询 ===")
    
    store_mgmt = StoreManagement()
    result = store_mgmt.query_stores_with_pagination(0, 5)
    
    if "error" not in result:
        print("✅ 分页查询成功")
        
        if isinstance(result, dict) and 'data' in result:
            data = result['data']
            print(f"返回门店数量: {len(data) if isinstance(data, list) else '非列表类型'}")
    else:
        print(f"❌ 分页查询失败: {result['error']}")
    
    print()


def test_custom_params():
    """测试自定义参数查询"""
    print("=== 测试自定义参数查询 ===")
    
    store_mgmt = StoreManagement()
    
    # 测试指定门店组查询
    custom_params = {
        "page_size": 10,
        "store_group_ids": [6666600000143, 6666600000172]
    }
    
    result = store_mgmt.query_stores(custom_params)
    
    if "error" not in result:
        print("✅ 自定义参数查询成功")
        
        if isinstance(result, dict) and 'data' in result:
            data = result['data']
            print(f"指定门店组查询结果: {len(data) if isinstance(data, list) else '非列表类型'} 个门店")
    else:
        print(f"❌ 自定义参数查询失败: {result['error']}")
    
    print()


def test_get_all_stores():
    """测试获取所有门店"""
    print("=== 测试获取所有门店 ===")
    
    store_mgmt = StoreManagement()
    result = store_mgmt.get_all_stores()
    
    if "error" not in result:
        print("✅ 获取所有门店成功")
        
        if result.get("success", False):
            total = result.get("total", 0)
            print(f"总门店数量: {total}")
            
            data = result.get("data", [])
            if isinstance(data, list) and len(data) > 0:
                print(f"实际获取数量: {len(data)}")
                
                # 显示门店分布统计
                store_groups = {}
                for store in data:
                    if isinstance(store, dict):
                        group_id = store.get('store_group_id', '未知组')
                        store_groups[group_id] = store_groups.get(group_id, 0) + 1
                
                print(f"门店组分布: {len(store_groups)} 个组")
                for group_id, count in list(store_groups.items())[:5]:  # 显示前5个组
                    print(f"  组 {group_id}: {count} 个门店")
                    
    else:
        print(f"❌ 获取所有门店失败: {result['error']}")
    
    print()


def main():
    """主测试函数"""
    print("🏪 门店管理模块测试开始")
    print("=" * 50)
    
    # 执行各项测试
    test_basic_query()
    test_pagination_query()
    test_custom_params()
    test_get_all_stores()
    
    print("=" * 50)
    print("🏪 门店管理模块测试完成")


if __name__ == "__main__":
    main()
