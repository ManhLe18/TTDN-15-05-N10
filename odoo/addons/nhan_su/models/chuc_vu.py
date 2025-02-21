from odoo import models, fields, api

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ")
# lich_su_cong_tac_ids = fields.One2many("lich_su_cong_tac", inverse_name= "chuc_vu_id", string="Lịch sử công tác")