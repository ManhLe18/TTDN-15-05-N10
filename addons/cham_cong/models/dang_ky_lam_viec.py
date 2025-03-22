from odoo import models, fields, api
from datetime import timedelta

class DangKyLamViec(models.Model):
    _name = 'dang_ky_lam_viec'
    _description = 'Đăng ký giờ làm việc'
    _rec_name = 'ca_lam'

    nhan_vien_ids = fields.Many2many('nhan_vien', string="Nhân viên", required=True)
    ngay_lam = fields.Date("Ngày làm việc", required=True, default=fields.Date.context_today)
    ca_lam = fields.Char(string="Ca làm", compute="_compute_ca_lam", store=True)
    gio_bat_dau = fields.Datetime("Giờ bắt đầu", required=True, default=lambda self: fields.Datetime.now().replace(hour=8, minute=0, second=0))
    gio_ket_thuc = fields.Datetime("Giờ kết thúc", required=True, default=lambda self: fields.Datetime.now().replace(hour=17, minute=0, second=0))
    trang_thai = fields.Selection([
        ('draft', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('cancelled', 'Đã hủy')
    ], string="Trạng thái", default='draft')
    
    check_box_tao_ngay_moi = fields.Boolean(string="Tạo bản ghi cho ngày tiếp theo")

    @api.model
    def create(self, vals):
        record = super(DangKyLamViec, self).create(vals)

        # Nếu checkbox được tick, tạo bản ghi mới cho ngày tiếp theo
        if vals.get("check_box_tao_ngay_moi"):
            ngay_tiep_theo = record.ngay_lam + timedelta(days=1)
            self.create({
                'nhan_vien_ids': [(6, 0, record.nhan_vien_ids.ids)],
                'ngay_lam': ngay_tiep_theo,
                'gio_bat_dau': record.gio_bat_dau,
                'gio_ket_thuc': record.gio_ket_thuc,
                'trang_thai': 'draft'
            })

        return record

    # @api.depends('nhan_vien_ids', 'ngay_lam')
    # def _compute_ca_lam(self):
    #     for record in self:
    #         # ten_nhan_vien = ", ".join(record.nhan_vien_ids.mapped('ho_va_ten'))
    #         record.ca_lam = f"{ten_nhan_vien} - {record.ngay_lam}" if ten_nhan_vien else str(record.ngay_lam)

    def action_approve_multi(self):
        """Duyệt hàng loạt đơn đăng ký giờ làm việc"""
        for record in self:
            if record.trang_thai == 'draft':
                record.action_approve()

    
    @api.depends('ngay_lam')
    def _compute_ca_lam(self):
        for record in self:
            record.ca_lam = f"{record.ngay_lam}"

    def action_approve(self):
        """Duyệt đơn đăng ký và tạo lịch làm việc cho từng nhân viên"""
        for record in self:
            record.trang_thai = 'approved'

            for nhan_vien in record.nhan_vien_ids:
                lich_ton_tai = self.env['lich_lam_viec'].search([
                    ('nhan_vien_id', '=', nhan_vien.id),
                    ('ngay', '=', record.ngay_lam)
                ])
                if not lich_ton_tai:
                    self.env['lich_lam_viec'].create({
                        'ngay': record.ngay_lam,
                        'dang_ky_lam_viec_id': record.id,
                        'nhan_vien_id': nhan_vien.id,
                        'trang_thai': 'chua_vao'
                    })

    def action_cancel(self):
        """Hủy đơn đăng ký"""
        for record in self:
            record.trang_thai = 'cancelled'

