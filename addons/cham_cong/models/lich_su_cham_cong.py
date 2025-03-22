# from odoo import models, fields, api
# from odoo.exceptions import ValidationError

# class LichSuChamCong(models.Model):
#     _name = 'lich_su_cham_cong'
#     _description = 'Lịch sử chấm công'
#     _order = 'ngay_lam desc'
    
#     cham_cong_id = fields.Many2one('cham_cong', string="Chấm công liên quan")
#     nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
#     ngay_lam = fields.Date("Ngày làm việc", required=True)
#     gio_check_in = fields.Datetime("Giờ check-in", required=True)
#     gio_check_out = fields.Datetime("Giờ check-out", required=True)
#     thoi_gian_lam_viec = fields.Float("Thời gian làm việc (giờ)", required=True)
#     ghi_chu = fields.Char("Ghi chú")

# class ChamCong(models.Model):
#     _inherit = 'cham_cong'

#     @api.constrains('gio_check_in', 'gio_check_out')
#     def _tao_lich_su_cham_cong(self):
#         for record in self:
#             if record.gio_check_in and record.gio_check_out:
#                 lich_su_vals = {
#                     'nhan_vien_id': record.nhan_vien_id.id,
#                     'ngay_lam': record.ngay_lam,
#                     'gio_check_in': record.gio_check_in,
#                     'gio_check_out': record.gio_check_out,
#                     'thoi_gian_lam_viec': record.thoi_gian_lam_viec,
#                     'ghi_chu': record.ghi_chu,
#                 }
#                 self.env['lich_su_cham_cong'].create(lich_su_vals)

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LichSuChamCong(models.Model):
    _name = 'lich_su_cham_cong'
    _description = 'Lịch sử chấm công'
    _order = 'ngay_lam desc'
    
    cham_cong_id = fields.Many2one('cham_cong', string="Chấm công liên quan")
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    # phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", compute="_compute_phong_ban_chuc_vu", required=True)
    # chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ",  compute="_compute_phong_ban_chuc_vu", required=True)
    # lich_su_cong_tac_id = fields.Many2one('lich_su_cong_tac', string="Lịch sử cộng tác")
    ngay_lam = fields.Date("Ngày làm việc", required=True)
    gio_check_in = fields.Datetime("Giờ check-in", required=True)
    gio_check_out = fields.Datetime("Giờ check-out", required=True)
    thoi_gian_lam_viec = fields.Float("Thời gian làm việc (giờ)", required=True)
    ghi_chu = fields.Char("Ghi chú")

    _sql_constraints = [
        ('unique_nhan_vien_ngay', 'unique(nhan_vien_id, ngay_lam)', 'Nhân viên chỉ có thể có một bản ghi lịch sử chấm công cho mỗi ngày!')
    ]

    # @api.depends('nhan_vien_id')
    # def _compute_phong_ban_chuc_vu(self):
    #     """Lấy phòng ban & chức vụ từ lịch sử công tác của nhân viên"""
    #     for record in self:
    #         if record.nhan_vien_id:
    #             lich_su_cong_tac = self.env['lich_su_cong_tac'].search([
    #                 ('nhan_vien_id', '=', record.nhan_vien_id.id),
    #                 ('loai_chuc_vu', '=', 'Chính')
    #             ], order="id desc", limit=1)  # Lấy bản ghi mới nhất

    #             record.phong_ban_id = lich_su_cong_tac.phong_ban_id.id if lich_su_cong_tac else False
    #             record.chuc_vu_id = lich_su_cong_tac.chuc_vu_id.id if lich_su_cong_tac else False
    #         else:
    #             record.phong_ban_id = False
    #             record.chuc_vu_id = False

class ChamCong(models.Model):
    _inherit = 'cham_cong'

    @api.constrains('gio_check_in', 'gio_check_out')
    def _tao_lich_su_cham_cong(self):
        for record in self:
            if record.gio_check_in and record.gio_check_out:
                existing_record = self.env['lich_su_cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_lam', '=', record.ngay_lam)
                ], limit=1)

                if existing_record:
                    # Cập nhật bản ghi cũ thay vì tạo mới
                    existing_record.write({
                        'gio_check_in': record.gio_check_in,
                        'gio_check_out': record.gio_check_out,
                        'thoi_gian_lam_viec': record.thoi_gian_lam_viec,
                        'ghi_chu': record.ghi_chu,
                    })
                else:
                    # Tạo mới nếu chưa có
                    self.env['lich_su_cham_cong'].create({
                        'nhan_vien_id': record.nhan_vien_id.id,
                        'ngay_lam': record.ngay_lam,
                        'gio_check_in': record.gio_check_in,
                        'gio_check_out': record.gio_check_out,
                        'thoi_gian_lam_viec': record.thoi_gian_lam_viec,
                        'ghi_chu': record.ghi_chu,
                    })
