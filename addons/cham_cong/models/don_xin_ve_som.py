from odoo import models, fields, api

class DonXinVeSom(models.Model):
    _name = 'don_xin_ve_som'
    _description = 'Đơn xin về sớm'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    dang_ky_lam_viec_id = fields.Many2one('dang_ky_lam_viec', string="Ca làm đã đăng ký")  
    ngay_lam = fields.Date("Ngày làm việc", required=True)
    # gio_bat_dau = fields.Datetime("Giờ đăng ký vào", required=True, help="Chọn giờ vào")
    # gio_ket_thuc = fields.Datetime("Giờ đăng ký về", required=True, help="Chọn giờ ra")
    gio_ve_som = fields.Datetime("Giờ về sớm", required=True, help="Chọn giờ ra")
    ly_do = fields.Text("Lý do")
    trang_thai = fields.Selection([
        ('draft', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối')
    ], string="Trạng thái", default='draft')

    file_dinh_kem = fields.Binary("Tệp đính kèm")
    file_ten = fields.Char("Tên tệp")

    @api.onchange('dang_ky_lam_viec_id')
    def _onchange_dang_ky_lam_viec(self):
        """Tự động điền ngày làm và giờ ca làm việc"""
        if self.dang_ky_lam_viec_id:
            self.ngay_lam = self.dang_ky_lam_viec_id.ngay_lam
            # self.gio_bat_dau = self.dang_ky_lam_viec_id.gio_bat_dau
            # self.gio_ket_thuc = self.dang_ky_lam_viec_id.gio_ket_thuc

    def action_approve(self):
        """Duyệt đơn xin về sớm"""
        for record in self:
            record.trang_thai = 'approved'

    def action_reject(self):
        """Từ chối đơn xin về sớm"""
        for record in self:
            record.trang_thai = 'rejected'

