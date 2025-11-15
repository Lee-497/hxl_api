# 快速配置指南

> 这是一个快速配置参考，展示最常用的配置场景。  
> 详细说明请查看：`CONFIG_GUIDE.md`

---

## 🎯 核心配置三要素

```python
# 1️⃣ 启用/禁用模块
MODULE_SWITCHES = {"module_name": True/False}

# 2️⃣ 配置模块参数（仅灵活参数模块需要）
MODULE_PARAMS = {"module_name": {...}}

# 3️⃣ 启用/禁用报表加工
PROCESSING_SWITCHES = {"report_name": True/False}
```

---

## 📝 常用配置场景

### **场景1: 销售分析（完整流程）**

采集冷藏乳饮销售数据 + 生成分析报表

```python
# ✅ 第一步：启用销售分析模块
MODULE_SWITCHES = {
    "store_product_attr": False,
    "inventory_query": False,
    "org_product_info": False,
    "store_management": False,
    "sales_analysis": True,  # ✅ 启用
}

# ✅ 第二步：配置销售分析参数
MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",  # 使用冷藏乳饮模板
    }
}

# ✅ 第三步：启用报表加工
PROCESSING_SWITCHES = {
    "inventory_summary_report": False,
    "sales_analysis_report": True,  # ✅ 生成销售分析报表
}
```

**执行结果**:
- ✅ 下载原始数据: `storage/downloads/商品销售数据_20251115_xxx.xlsx`
- ✅ 生成分析报表: `storage/processed/销售分析报表_20251115_xxx.xlsx`

---

### **场景2: 自定义销售日期**

采集指定日期的销售数据

```python
MODULE_SWITCHES = {
    "sales_analysis": True,
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",  # 基于模板
        "bizday": ["2025-11-01", "2025-11-30"],  # ✅ 覆盖日期为11月全月
    }
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,
}
```

---

### **场景3: 自定义门店范围**

采集指定门店的销售数据

```python
MODULE_SWITCHES = {
    "sales_analysis": True,
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",
        "store_ids": [6868800000595, 6868800000674, 6868800000680],  # ✅ 多个门店
    }
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,
}
```

---

### **场景4: 完全自定义参数**

不使用模板，完全自定义所有参数

```python
MODULE_SWITCHES = {
    "sales_analysis": True,
}

MODULE_PARAMS = {
    "sales_analysis": {
        "custom_params": {  # ✅ 完全自定义
            "bizday": ["2025-10-01", "2025-10-31"],  # 10月数据
            "company_id": 66666,
            "date_range": "MONTH",
            "item_category_ids": [123, 456, 789],  # 自定义商品分类
            "store_ids": [100, 200, 300],  # 自定义门店
            "summary_types": ["STORE", "ITEM"],
        }
    }
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,
}
```

---

### **场景5: 库存汇总报表**

采集库存相关数据 + 生成库存汇总报表

```python
MODULE_SWITCHES = {
    "store_product_attr": True,  # ✅ 门店商品属性
    "inventory_query": True,     # ✅ 库存查询
    "org_product_info": True,    # ✅ 组织商品档案
    "store_management": False,
    "sales_analysis": False,
}

MODULE_PARAMS = {
    # 这些模块使用固定参数，无需配置
}

PROCESSING_SWITCHES = {
    "inventory_summary_report": True,  # ✅ 生成库存汇总报表
    "sales_analysis_report": False,
}
```

**执行结果**:
- ✅ 下载3个原始数据文件
- ✅ 生成库存汇总报表（包含清洗、关联、透视）

---

### **场景6: 只采集数据（不加工）**

只下载原始数据，不生成加工报表

```python
MODULE_SWITCHES = {
    "sales_analysis": True,
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",
    }
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": False,  # ❌ 不生成报表
}

# 或者直接禁用总开关
ENABLE_PROCESSING = False
```

---

### **场景7: 只加工已有数据**

使用之前下载的原始数据，重新生成报表（用于调试）

```python
MODULE_SWITCHES = {
    "sales_analysis": False,  # ❌ 不重新采集
}

MODULE_PARAMS = {}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,  # ✅ 只运行加工逻辑
}
```

**优点**: 节省采集时间，快速迭代报表逻辑

---

## 🔄 切换不同销售报表

### **方法1: 修改配置后重新运行**

```python
# 第一次运行：冷藏乳饮
MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",
    }
}
# 运行脚本...

# 第二次运行：休闲食品（修改配置）
MODULE_PARAMS = {
    "sales_analysis": {
        "custom_params": {
            "bizday": ["2025-11-14", "2025-11-14"],
            "item_category_ids": [888, 999],  # 休闲食品分类
            "store_ids": [6868800000595],
        }
    }
}
# 再次运行脚本...
```

---

### **方法2: 使用注释快速切换**

```python
MODULE_PARAMS = {
    "sales_analysis": {
        # 当前使用：冷藏乳饮
        "template_name": "dairy_cold_drinks",
        
        # 备选1：休闲食品（取消注释即可使用）
        # "custom_params": {
        #     "item_category_ids": [888, 999],
        #     "store_ids": [6868800000595],
        # },
        
        # 备选2：全门店月度
        # "custom_params": {
        #     "bizday": ["2025-11-01", "2025-11-30"],
        #     "date_range": "MONTH",
        #     "store_ids": [],  # 所有门店
        # },
    }
}
```

---

## 📊 配置检查清单

运行前检查以下配置：

### ✅ **数据采集**
- [ ] `MODULE_SWITCHES` 中启用了需要的模块
- [ ] `MODULE_PARAMS` 中配置了正确的参数（如有需要）

### ✅ **报表加工**
- [ ] 确认已有原始数据（或启用了采集模块）
- [ ] `PROCESSING_SWITCHES` 中启用了需要的报表
- [ ] `ENABLE_PROCESSING = True`

---

## ⚠️ 常见错误

### ❌ **错误1: 忘记启用模块**

```python
# 错误配置
MODULE_SWITCHES = {
    "sales_analysis": False,  # ❌ 忘记启用
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",  # 配置了但不会生效
    }
}
```

**修复**: 将 `MODULE_SWITCHES` 中的 `sales_analysis` 改为 `True`

---

### ❌ **错误2: 加工报表缺少原始数据**

```python
# 错误配置
MODULE_SWITCHES = {
    "sales_analysis": False,  # ❌ 没有采集数据
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,  # 要生成报表
}
```

**修复**: 先启用 `sales_analysis` 采集数据，或确保 `storage/downloads/` 中已有数据

---

### ❌ **错误3: 参数配置格式错误**

```python
# 错误配置
MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",
        "custom_params": {...},  # ❌ 不能同时使用
    }
}
```

**修复**: 选择一种配置方式，不能混用

---

## 📚 更多帮助

- **详细配置指南**: `CONFIG_GUIDE.md`
- **架构设计文档**: `ARCHITECTURE.md`
- **参数模板定义**: `config/params_config.py`
- **API接口配置**: `config/api_config.py`

---

## 🚀 开始使用

1. 根据需求选择上面的配置场景
2. 复制配置到 `main.py`
3. 运行: `python main.py`
4. 查看结果:
   - 原始数据: `storage/downloads/`
   - 加工报表: `storage/processed/`

---

**最后更新**: 2025-11-15  
**版本**: v2.1
