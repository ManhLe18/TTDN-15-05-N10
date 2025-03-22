from odoo import models, fields, api

class ThongKeChamCong(models.Model):
    _name = 'thong_ke_cham_cong'
    _description = 'Thống kê chấm công nhân viên'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    tu_ngay = fields.Date(string="Từ ngày", required=True)
    den_ngay = fields.Date(string="Đến ngày", required=True)

    tong_gio_lam_viec = fields.Float(string="Tổng giờ làm việc", compute="_compute_thong_ke", store=True)
    so_ngay_di_muon = fields.Integer(string="Số ngày đi muộn", compute="_compute_thong_ke", store=True)
    so_ngay_ve_som = fields.Integer(string="Số ngày về sớm", compute="_compute_thong_ke", store=True)
    so_ngay_nghi = fields.Integer(string="Số ngày nghỉ phép", compute="_compute_thong_ke", store=True)

    @api.depends('nhan_vien_id', 'tu_ngay', 'den_ngay')
    def _compute_thong_ke(self):
        for record in self:
            if not record.nhan_vien_id or not record.tu_ngay or not record.den_ngay:
                continue

            # 📌 Lấy dữ liệu từ `cham_cong` để tính giờ làm và đi muộn
            danh_sach_cham_cong = self.env['cham_cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('ngay_lam', '>=', record.tu_ngay),
                ('ngay_lam', '<=', record.den_ngay)
            ])

            total_hours = 0.0
            late_days = 0

            for cham_cong in danh_sach_cham_cong:
                total_hours += cham_cong.thoi_gian_lam_viec  # Tổng giờ làm việc

                # 📌 Kiểm tra đơn xin đến muộn
                don_den_muon = self.env['don_xin_den_muon'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_lam', '=', cham_cong.ngay_lam),
                    ('trang_thai', '=', 'approved')
                ], limit=1)

                if not don_den_muon and cham_cong.phut_di_lam_muon > 0:
                    late_days += 1

            # 📌 Kiểm tra đơn xin nghỉ phép
            don_nghi = self.env['don_xin_nghi'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('trang_thai', '=', 'approved'),
                ('nghi_tu_ngay', '<=', record.den_ngay),
                ('nghi_den_ngay', '>=', record.tu_ngay)
            ])

            total_leave_days = 0
            for don in don_nghi:
                start_date = max(don.nghi_tu_ngay, record.tu_ngay)
                end_date = min(don.nghi_den_ngay, record.den_ngay)
                
                if start_date <= end_date:
                    total_leave_days += (end_date - start_date).days + 1

            # 📌 Lấy dữ liệu từ `don_xin_ve_som`
            don_ve_som = self.env['don_xin_ve_som'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('ngay_lam', '>=', record.tu_ngay),
                ('ngay_lam', '<=', record.den_ngay),
                ('trang_thai', '=', 'approved')
            ])

            # Số ngày về sớm được duyệt
            total_early_leave_days = len(don_ve_som)

            # 📌 Cập nhật các trường thống kê
            record.tong_gio_lam_viec = total_hours
            record.so_ngay_di_muon = late_days
            record.so_ngay_ve_som = total_early_leave_days
            record.so_ngay_nghi = total_leave_days
