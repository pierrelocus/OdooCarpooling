# -*- coding: utf-8 -*-
{
    'name': "Carpooling",

    'summary': """
        Carpooling App""",

    'description': """
        Carpooling App
        v0.1: LOP - 03 2020 - Init
    """,

    'author': "Odoo Sustainability Team",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_geolocalize', 'mail'],

    # always loaded
    'data': [
        'views/carpooler_views.xml',
        'views/utils_views.xml',
        'views/menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}