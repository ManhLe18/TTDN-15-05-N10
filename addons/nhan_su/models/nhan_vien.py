from odoo import models, fields, api

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten' 
    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    
    ho_va_ten_dem = fields.Char(string="Họ và tên đệm")
    ten = fields.Char(string="Tên")
    ho_va_ten = fields.Char(string="Họ và Tên", compute="_compute_ho_va_ten", store=True)

    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", domain="[]", context="{}", ondelete="restrict")
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", domain="[]", context="{}", ondelete="restrict")
    lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac", inverse_name="nhan_vien_id", string="Lịch sử công tác")

    @api.depends('ho_va_ten_dem', 'ten')
    def _compute_ho_va_ten(self):  # Sửa tên function để trùng với compute
        for record in self:
            record.ho_va_ten = f"{record.ho_va_ten_dem or ''} {record.ten or ''}".strip()
