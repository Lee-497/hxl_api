"""
接口地址配置
"""

# 基础域名
ERP_BASE_URL = "https://erp-web.erp.ali-prod.xlbsoft.com"
EXPORT_BASE_URL = "https://gdp.xlbsoft.com"
BI_BASE_URL = "https://bi-web.bi.ali-prod.xlbsoft.com"

# 导出接口地址（各模块的导出接口）
EXPORT_ENDPOINTS = {
    # 门店商品属性导出接口
    "store_product_attr": f"{ERP_BASE_URL}/erp/hxl.erp.storeitemattr.export",
    
    # 组织商品档案导出接口
    "org_product_info": f"{EXPORT_BASE_URL}/erp-mdm/hxl.erp.org.item.export",
    
    # 库存查询导出接口
    "inventory_query": f"{ERP_BASE_URL}/erp/hxl.erp.stock.export",
    
    # 门店管理导出接口
    "store_management": f"{EXPORT_BASE_URL}/erp-mdm/hxl.erp.store.new.page",
    
    # 商品销售分析导出接口
    "sales_analysis": f"{BI_BASE_URL}/bi/hxl.bi.pos.itemanalyse.export",

    # 配送分析（占位）导出接口
    "delivery_analysis": f"{ERP_BASE_URL}/erp/hxl.erp.deliveryreport.deliveryanalyze.export",
}

# 通用下载接口（用于获取导出任务历史和下载文件）
DOWNLOAD_ENDPOINT = f"{EXPORT_BASE_URL}/export/hxl.export.reporthistory.page"
