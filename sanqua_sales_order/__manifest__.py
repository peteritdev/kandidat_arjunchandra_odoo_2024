# -*- coding: utf-8 -*-
{
    "name": "Sales Order Arjun Chandra Sasongko",
    "summary": """
        Aplikasi Sales Order
    """,
    "description": """
        Long description of module's purpose
    """,
    "author": "Arjun Chandra Sasongko",
    "website": "",
    "category": "Services",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "mail",
        "base",
        "sale",
        "account",
        "sanqua_inventory",
        
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/sales_order_views_inherit.xml",
        "views/sales_division_views.xml",
        "views/partner_credit_limit_views.xml",
        "views/res_partner_views_inherit.xml",
        "views/product_template_views_inherit.xml",
        "wizard/sale_order_warning_wizard.xml",

    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    "license": "LGPL-3",
    "demo": [],
    "qweb": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
