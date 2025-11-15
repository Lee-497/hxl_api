# 配置指南

> **更新日期**: 2025-11-15  
> **版本**: v2.1 - 优化配置设计

---

## 📋 配置结构说明

项目配置分为**三个独立部分**，职责清晰：

```python
# 1️⃣ 模块启用开关 - 控制是否执行数据采集
MODULE_SWITCHES = {
    "module_name": True/False
}

# 2️⃣ 模块参数配置 - 为需要灵活参数的模块提供配置
MODULE_PARAMS = {
    "module_name": {...}
}

# 3️⃣ 加工报表配置 - 控制是否生成加工报表
PROCESSING_SWITCHES = {
    "report_name": True/False
}
```

---

## 🎯 设计原则

### **职责分离**

| 配置项 | 职责 | 示例 |
|--------|------|------|
| `MODULE_SWITCHES` | ✅ **只管启用/禁用** | `True` = 启用, `False` = 禁用 |
| `MODULE_PARAMS` | ⚙️ **只管参数配置** | 模板名、日期范围、门店ID等 |
| `PROCESSING_SWITCHES` | 🔧 **只管报表生成** | `True` = 生成报表, `False` = 跳过 |

### **为什么这样设计？**

✅ **清晰**: 一看就知道哪些模块启用了  
✅ **统一**: 所有模块都是 `True/False` 控制  
✅ **灵活**: 参数配置独立，不影响启用逻辑  
✅ **易维护**: 修改参数不需要改启用状态

---

## 📝 完整配置示例

### **场景1: 只采集数据（不加工）**

```python
MODULE_SWITCHES = {
    "store_product_attr": False,
    "inventory_query": True,      # ✅ 启用库存查询
    "store_management": True,      # ✅ 启用门店管理
    "sales_analysis": False,
}

MODULE_PARAMS = {
    # 库存查询和门店管理无需参数配置
}

PROCESSING_SWITCHES = {
    "inventory_summary_report": False,  # ❌ 不生成加工报表
    "sales_analysis_report": False,
}
```

**结果**: 
- ✅ 下载库存数据到 `storage/downloads/`
- ✅ 下载门店数据到 `storage/downloads/`
- ❌ 不生成加工报表

---

### **场景2: 采集 + 加工（完整流程）**

```python
MODULE_SWITCHES = {
    "store_product_attr": True,   # ✅ 采集门店商品属性
    "inventory_query": True,      # ✅ 采集库存数据
    "org_product_info": True,     # ✅ 采集组织商品档案
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

**结果**:
- ✅ 下载原始数据（3个文件）
- ✅ 生成库存汇总报表（清洗、关联、透视）

---

### **场景3: 销售分析（使用模板）**

```python
MODULE_SWITCHES = {
    "store_product_attr": False,
    "inventory_query": False,
    "org_product_info": False,
    "store_management": False,
    "sales_analysis": True,        # ✅ 启用销售分析
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",  # 使用冷藏乳饮模板
    }
}

PROCESSING_SWITCHES = {
    "inventory_summary_report": False,
    "sales_analysis_report": True,  # ✅ 生成销售分析报表
}
```

**结果**:
- ✅ 下载销售数据（使用dairy_cold_drinks模板参数）
- ✅ 生成销售分析报表（清洗、计算毛利率、多维度汇总）

---

### **场景4: 销售分析（覆盖部分参数）**

```python
MODULE_SWITCHES = {
    "sales_analysis": True,  # ✅ 启用
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",  # 基于模板
        "bizday": ["2025-11-14", "2025-11-14"],  # ✅ 覆盖业务日期
        "store_ids": [6868800000595, 6868800000674],  # ✅ 覆盖门店ID
    }
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,
}
```

**结果**:
- ✅ 使用模板的其他参数
- ✅ 只修改指定的日期和门店

---

### **场景5: 销售分析（完全自定义）**

```python
MODULE_SWITCHES = {
    "sales_analysis": True,
}

MODULE_PARAMS = {
    "sales_analysis": {
        "custom_params": {  # ✅ 不使用模板，完全自定义
            "bizday": ["2025-11-01", "2025-11-30"],
            "company_id": 66666,
            "date_range": "MONTH",
            "item_category_ids": [6666600000591, 6666600001229],
            "operator_store_id": 6666600004441,
            "query_count": True,
            "query_no_tax": False,
            "query_year_compare": False,
            "sale_mode": "DIRECT",
            "store_ids": [6868800000595],
            "summary_types": ["STORE", "CATEGORY_LV1", "ITEM"]
        }
    }
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,
}
```

**结果**:
- ✅ 完全按照自定义参数请求数据
- ✅ 不受模板限制

---

### **场景6: 快速迭代（调试加工逻辑）**

```python
MODULE_SWITCHES = {
    "sales_analysis": False,  # ❌ 不重新采集数据
}

MODULE_PARAMS = {}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,  # ✅ 只运行加工逻辑
}
```

**结果**:
- ❌ 不下载新数据（节省时间）
- ✅ 使用已有的原始数据重新生成报表
- 💡 **适合**: 调试报表生成逻辑时

---

## 🔄 数据流程图

```
┌─────────────────────────────────────────┐
│  MODULE_SWITCHES (启用/禁用)             │
│  - sales_analysis: True                 │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  MODULE_PARAMS (参数配置)                │
│  - template_name: "dairy_cold_drinks"   │
│  - bizday: ["2025-11-14", ...]          │
└──────────────┬──────────────────────────┘
               │
               ↓
         [调用BI系统]
               │
               ↓
    storage/downloads/商品销售数据.xlsx
         (原始数据，未加工)
               │
               ↓
┌─────────────────────────────────────────┐
│  PROCESSING_SWITCHES (报表生成)          │
│  - sales_analysis_report: True          │
└──────────────┬──────────────────────────┘
               │
               ↓
    [读取] → [清洗] → [计算] → [汇总]
               │
               ↓
    storage/processed/销售分析报表.xlsx
    (多工作表: 明细、汇总、门店、分类)
```

---

## 📚 参数优先级

对于销售分析模块，参数优先级为：

```
custom_params > 模板+覆盖 > 默认模板
```

### **示例说明**

```python
# 优先级1: 完全自定义（最高优先级）
MODULE_PARAMS = {
    "sales_analysis": {
        "custom_params": {...}  # ✅ 忽略模板，使用这个
    }
}

# 优先级2: 模板 + 覆盖
MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks",  # 基础模板
        "bizday": ["2025-11-14", "2025-11-14"],  # ✅ 覆盖模板的bizday
    }
}

# 优先级3: 默认模板
MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks"  # ✅ 完全使用模板参数
    }
}
```

---

## ⚠️ 常见错误

### **错误1: 只启用加工报表，没启用采集**

```python
# ❌ 错误
MODULE_SWITCHES = {
    "sales_analysis": False,  # 没有采集数据
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,  # 要生成报表
}
```

**结果**: ❌ 报表生成失败（没有原始数据）

**正确做法**:
```python
# ✅ 正确 - 先采集，再加工
MODULE_SWITCHES = {
    "sales_analysis": True,  # 先采集数据
}

PROCESSING_SWITCHES = {
    "sales_analysis_report": True,  # 再生成报表
}
```

---

### **错误2: 参数配置了，但没启用模块**

```python
# ❌ 错误
MODULE_SWITCHES = {
    "sales_analysis": False,  # 模块未启用
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks"  # 配置了参数但不会生效
    }
}
```

**结果**: ❌ 参数不会生效（模块未启用）

**正确做法**:
```python
# ✅ 正确
MODULE_SWITCHES = {
    "sales_analysis": True,  # 必须先启用
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks"
    }
}
```

---

## 🔧 向后兼容

**旧配置格式**（仍然支持，但不推荐）:

```python
MODULE_SWITCHES = {
    "sales_analysis": "dairy_cold_drinks",  # ⚠️ 旧格式
}
```

**新配置格式**（推荐）:

```python
MODULE_SWITCHES = {
    "sales_analysis": True,  # ✅ 新格式
}

MODULE_PARAMS = {
    "sales_analysis": {
        "template_name": "dairy_cold_drinks"
    }
}
```

**迁移建议**: 请逐步迁移到新格式，旧格式会在日志中产生警告。

---

## 📊 配置对照表

| 需求 | MODULE_SWITCHES | MODULE_PARAMS | PROCESSING_SWITCHES |
|------|----------------|---------------|---------------------|
| 只下载数据 | `True` | 可选 | `False` |
| 下载+加工 | `True` | 可选 | `True` |
| 只加工已有数据 | `False` | - | `True` |
| 禁用所有 | `False` | - | `False` |

---

## 💡 最佳实践

1. **日常使用**: 启用采集 + 启用加工（完整流程）
2. **快速迭代**: 禁用采集 + 启用加工（节省时间）
3. **只需原始数据**: 启用采集 + 禁用加工
4. **灵活参数**: 使用 `MODULE_PARAMS` 配置，保持 `MODULE_SWITCHES` 简洁

---

## 📖 相关文档

- **架构设计**: `ARCHITECTURE.md`
- **优化总结**: `REFACTORING_SUMMARY.md`
- **参数模板**: `config/params_config.py`
- **API配置**: `config/api_config.py`

---

**最后更新**: 2025-11-15  
**版本**: v2.1
