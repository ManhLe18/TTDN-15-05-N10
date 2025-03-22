from odoo import models, fields, api

class LichLamViec(models.Model):
    _name = 'lich_lam_viec'
    _description = 'Lịch Làm Việc'
    _rec_name = 'nhan_vien_id'

    ngay = fields.Date("Ngày", required=True)
    dang_ky_lam_viec_id = fields.Many2one('dang_ky_lam_viec', string="Ca làm đã đăng ký")
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    trang_thai = fields.Selection([
        ('chua_vao', 'Chưa vào / Chưa ra'),
        ('da_vao', 'Đã vào / Chưa ra'),
        ('hoan_thanh', 'Đã vào / Đã ra'),
        ('nghi', 'Nghỉ')
    ], string="Trạng thái", default='chua_vao')

