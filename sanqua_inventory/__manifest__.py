# -*- coding: utf-8 -*-
{
    "name": "Inventory Arjun Chandra Sasongko",
    "summary": """
        Aplikasi Inventory
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
        "stock",
        
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/stock_quant_views_inherit.xml",

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
