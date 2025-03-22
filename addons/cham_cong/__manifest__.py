{
    'name': 'Chấm công',
    'version': '1.0',
    'author': 'Mạnh',
    'category': 'Nhân sự',
    'summary': 'Quản lý chấm công nhân viên',
    'depends': ['base', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/cham_cong.xml',
        'views/dang_ky_lam_viec.xml',
        'views/lich_lam_viec.xml',
        # 'views/quan_ly_don.xml',
        'views/don_xin_den_muon.xml',
        'views/don_xin_ve_som.xml',
        'views/don_xin_nghi.xml',
        'views/lich_su_cham_cong.xml',
        'views/thong_ke_cham_cong.xml',
        # Load action trước
    'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
