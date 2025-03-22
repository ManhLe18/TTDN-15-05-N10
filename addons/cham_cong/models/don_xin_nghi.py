from odoo import models, fields, api

class DonXinNghi(models.Model):
    _name = 'don_xin_nghi'
    _description = 'Đơn xin nghỉ'
    _rec_name = 'nhan_vien_id'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    dang_ky_lam_viec_id = fields.Many2one('dang_ky_lam_viec', string="Ca làm đã đăng ký")  
    # ngay_lam = fields.Date("Ngày làm việc", required=True)
    # gio_bat_dau = fields.Datetime("Giờ đăng ký vào", required=True, help="Chọn giờ vào")
    # gio_ket_thuc = fields.Datetime("Giờ đăng ký về", required=True, help="Chọn giờ ra")
    nghi_tu_ngay = fields.Date("Nghỉ từ ngày", required=True, help="Chọn ngày nghỉ từ")
    nghi_den_ngay = fields.Date("Nghỉ đến ngày", required=True, help="Chọn ngày nghỉ đến")
    so_ngay_nghi = fields.Integer("Số ngày nghỉ", compute="_compute_so_ngay_nghi", store=True)
    ly_do = fields.Text("Lý do")
    trang_thai = fields.Selection([
        ('draft', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối')
    ], string="Trạng thái", default='draft')

    file_dinh_kem = fields.Binary("Tệp đính kèm")
    file_ten = fields.Char("Tên tệp")
    
    @api.depends('nghi_tu_ngay', 'nghi_den_ngay')
    def _compute_so_ngay_nghi(self):
        """Tính số ngày nghỉ dựa vào khoảng thời gian từ 'nghi_tu_ngay' đến 'nghi_den_ngay'"""
        for record in self:
            if record.nghi_tu_ngay and record.nghi_den_ngay:
                delta = (record.nghi_den_ngay - record.nghi_tu_ngay).days + 1  # Tính cả ngày bắt đầu
                record.so_ngay_nghi = max(delta, 0)  # Không để số ngày âm
            else:
                record.so_ngay_nghi = 0

    # @api.onchange('dang_ky_lam_viec_id')
    # def _onchange_dang_ky_lam_viec(self):
    #     """Tự động điền ngày làm và giờ ca làm việc"""
    #     if self.dang_ky_lam_viec_id:
    #         self.ngay_lam = self.dang_ky_lam_viec_id.ngay_lam
    #         # self.gio_bat_dau = self.dang_ky_lam_viec_id.gio_bat_dau
    #         # self.gio_ket_thuc = self.dang_ky_lam_viec_id.gio_ket_thuc

    def action_approve(self):
        """Duyệt đơn xin nghỉ"""
        for record in self:
            record.trang_thai = 'approved'

    def action_reject(self):
        """Từ chối đơn xin nghỉ"""
        for record in self:
            record.trang_thai = 'rejected'

