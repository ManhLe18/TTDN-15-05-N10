{
    'name': 'Nhân sự',
    'version': '1.0',
    'author': 'Mạnh',
    'category': 'Nhân sự',
    'summary': 'Quản lý nhân sự',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/nhan_vien.xml',
        'views/phong_ban.xml',
        'views/chuc_vu.xml',
        'views/lich_su_cong_tac.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
