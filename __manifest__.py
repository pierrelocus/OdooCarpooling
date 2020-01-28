# -*- coding: utf-8 -*-
{
    'name': "carpooling",

    'summary': """
        Create carpool offers for your coworkers and get info like money economy, CO2 footprint decrease""",

    'description': """
        Long description of module's purpose
    """,

    'author': "LOP",
    'website': "https://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/journey_views.xml',
        'views/carpooling_views.xml',
        'views/menus_views.xml',
        #'views/journey_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
