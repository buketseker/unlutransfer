# -*- coding: utf-8 -*-
{
    'name': "nitro_development",

    'summary': """
        Nitro Bilişim Development""",

    'description': """
        Nitro Bilişim için gerçekleştirilen özelleştirmeleri içeren paket uygulama
    """,

    'author': "MechSoft",
    'website': "https://www.mechsoft.com.tr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stok',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'web', 'account', 'sale', 'sale_stock', 'stock_account', 'sale_margin'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/stock_account_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}