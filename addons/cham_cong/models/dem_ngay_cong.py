from odoo import models, fields, api

class DemNgayCong(models.Model):
    _name = 'dem_ngay_cong'
    _description = 'Đếm ngày công của nhân viên'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade')
    so_ngay_cong = fields.Integer("Số ngày công", default=0, compute="_compute_so_ngay_cong", store=True)
    so_ngay_di_muon = fields.Integer("Số ngày đi muộn", default=0, compute="_compute_so_ngay_di_muon", store=True)

    @api.depends('nhan_vien_id')
    def _compute_so_ngay_cong(self):
        """ Tính số ngày công dựa trên số lần chấm công hợp lệ. """
        for record in self:
            record.so_ngay_cong = self.env['cham_cong'].search_count([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('gio_check_in', '!=', False),  # Đã check-in
                ('gio_check_out', '!=', False)  # Đã check-out
            ])

    @api.depends('nhan_vien_id')
    def _compute_so_ngay_di_muon(self):
        """ Tính số ngày nhân viên đi muộn dựa vào trường 'ghi_chu' trong cham_cong. """
        for record in self:
            record.so_ngay_di_muon = self.env['cham_cong'].search_count([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('ghi_chu', '=', 'Đi muộn')  # Chỉ đếm nếu ghi chú là "Đi muộn"
            ])


    @api.model
    def create(self, vals):
        """ Khi có nhân viên mới, tự động tạo bản ghi đếm ngày công. """
        record = super(DemNgayCong, self).create(vals)
        record._compute_so_ngay_cong()
        record._compute_so_ngay_di_muon()
        return record

    @api.model
    def update_dem_ngay_cong(self):
        """ Hàm này có thể gọi theo cron job để cập nhật số ngày công và số ngày đi muộn. """
        records = self.search([])
        for record in records:
            record._compute_so_ngay_cong()
            record._compute_so_ngay_di_muon()
