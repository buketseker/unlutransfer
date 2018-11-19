# -*- coding: utf-8 -*-
{
    'name': 'TCMB Live Currency Exchange Rate',
    'version': '2.0',
    'category': 'Accounting',
    'description': """Import exchange rates from the Turkey TCMB Bank.
""",
    'depends': [
        'base',
        'currency_rate_live',
        'account'
    ],
    'data': [
        'views/views.xml',
        'data/data.xml'

    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
