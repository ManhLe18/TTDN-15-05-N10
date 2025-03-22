from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Chấm công nhân viên'
    
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", compute="_compute_phong_ban_chuc_vu", store=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", compute="_compute_phong_ban_chuc_vu", store=True)
    ma_dinh_danh = fields.Char(string="Mã định danh", related="nhan_vien_id.ma_dinh_danh", readonly=True)
    lich_su_cong_tac_id = fields.Many2one('lich_su_cong_tac', string="Lịch sử cộng tác")

    dang_ky_lam_viec_id = fields.Many2one('dang_ky_lam_viec', string="Ca làm đã đăng ký") 
    ngay_lam = fields.Date("Ngày làm việc", required=True, default=fields.Date.context_today)
    ngay_lam_da_dang_ky = fields.Date("Ngày làm việc đã đăng ký")

    gio_check_in = fields.Datetime("Giờ check-in", help="Thời gian bắt đầu làm việc", readonly=True)
    gio_check_out = fields.Datetime("Giờ check-out", help="Thời gian kết thúc làm việc",  readonly=True)

    gio_bat_dau_dang_ky = fields.Datetime("Giờ bắt đầu đã đăng ký", required=True, default=lambda self: fields.Datetime.now().replace(hour=8, minute=0, second=0))
    gio_ket_thuc_dang_ky = fields.Datetime("Giờ kết thúc đã đăng ký", required=True, default=lambda self: fields.Datetime.now().replace(hour=17, minute=0, second=0))

    phut_di_lam_som = fields.Integer("Số phút đi làm sớm", compute="_compute_phut_di_lam", store=True)
    phut_di_lam_muon = fields.Integer("Số phút đi làm muộn", compute="_compute_phut_di_lam", store=True)

    so_ngay_cong = fields.Integer(related="dem_ngay_cong_id.so_ngay_cong", string="Số ngày công", store=True)
    so_ngay_di_muon = fields.Integer(related="dem_ngay_cong_id.so_ngay_di_muon", string="Số ngày đi muộn", store=True)
    so_ngay_nghi = fields.Integer("Số ngày nghỉ", compute="_compute_so_ngay_nghi", store=True)

    dem_ngay_cong_id = fields.Many2one(
        'dem_ngay_cong', string="Số ngày công",
        compute="_compute_dem_ngay_cong", store=True
    )
    
    @api.depends('nhan_vien_id', 'ngay_lam')
    def _compute_so_ngay_nghi(self):
        for record in self:
            if record.nhan_vien_id and record.ngay_lam:
                don_xin_nghi = self.env['don_xin_nghi'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('nghi_tu_ngay', '<=', record.ngay_lam),
                    ('nghi_den_ngay', '>=', record.ngay_lam),
                    ('trang_thai', '=', 'approved')
                ])
                record.so_ngay_nghi = len(don_xin_nghi)  
            else:
                record.so_ngay_nghi = 0


    @api.depends('nhan_vien_id', 'so_ngay_nghi')
    def _compute_dem_ngay_cong(self):
        for record in self:
            dem_ngay_cong = self.env['dem_ngay_cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id)
            ], limit=1)
            if dem_ngay_cong:
                record.dem_ngay_cong_id = dem_ngay_cong.id
                record.so_ngay_cong = max(dem_ngay_cong.so_ngay_cong - record.so_ngay_nghi, 0)
            else:
                record.dem_ngay_cong_id = False
                record.so_ngay_cong = 0


    
    
    lich_su_cham_cong_ids = fields.One2many(
        'lich_su_cham_cong', 'cham_cong_id', string="Lịch sử chấm công",
        compute="_compute_lich_su_cham_cong", store=False
    )
    
    @api.depends('nhan_vien_id')
    def _compute_lich_su_cham_cong(self):
        """Tự động lấy lịch sử chấm công của nhân viên hiện tại"""
        for record in self:
            if record.nhan_vien_id:
                lich_su_ids = self.env['lich_su_cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id)
                ]).ids
                record.lich_su_cham_cong_ids = [(6, 0, lich_su_ids)]  # Sử dụng danh sách ID
            else:
                record.lich_su_cham_cong_ids = [(5,)]  # Xóa nếu không có dữ liệu
                
    def action_check_in(self):
        """Hàm xử lý khi nhân viên bấm nút check-in"""
        for record in self:
            if not record.gio_check_in:
                record.gio_check_in = fields.Datetime.now()
            # elif record.gio_check_in.Date != record.ngay_lam:
            #     record.gio_check_in = fields.Datetime.now()
            else:
                raise ValidationError("Bạn đã check-in trước đó!")

    def action_check_out(self):
        """Hàm xử lý khi nhân viên bấm nút check-out"""
        for record in self:
            if not record.gio_check_in:
                raise ValidationError("Bạn cần check-in trước khi check-out!")
            if not record.gio_check_out:
                record.gio_check_out = fields.Datetime.now()
            else:
                raise ValidationError("Bạn đã check-out trước đó!")


    trang_thai_check_in = fields.Selection([
        ('chua_check_in', 'Chưa Check-in'),
        ('da_check_in', 'Đã Check-in'),
    ], string="Trạng thái Check-in", compute="_compute_trang_thai_check_in", store=True)

    trang_thai_check_out = fields.Selection([
        ('chua_check_out', 'Chưa Check-out'),
        ('da_check_out', 'Đã Check-out'),
    ], string="Trạng thái Check-out", compute="_compute_trang_thai_check_out", store=True)

    trang_thai_lam_viec = fields.Selection([
        ('chua_bat_dau', 'Chưa bắt đầu'),
        ('dang_lam_viec', 'Đang làm việc'),
        ('da_lam_viec', 'Đã làm việc'),
    ], string="Trạng thái làm việc", compute="_compute_trang_thai_lam_viec", store=True)

    thoi_gian_lam_viec = fields.Float("Thời gian làm việc (giờ)", compute="_compute_thoi_gian", store=True)
    ghi_chu = fields.Char("Ghi chú", readonly=True)
    
    @api.depends('gio_check_in', 'thoi_gian_bat_dau')
    def _compute_phut_di_lam(self):
        """Tính số phút đi làm sớm hoặc muộn"""
        for record in self:
            if record.gio_check_in and record.thoi_gian_bat_dau:
                check_in = fields.Datetime.to_datetime(record.gio_check_in)
                bat_dau = fields.Datetime.to_datetime(record.thoi_gian_bat_dau)
                delta = (bat_dau - check_in).total_seconds() / 60
                if delta > 0:
                    record.phut_di_lam_som = int(delta)
                    record.phut_di_lam_muon = 0
                else:
                    record.phut_di_lam_muon = abs(int(delta))
                    record.phut_di_lam_som = 0
            else:
                record.phut_di_lam_som = 0
                record.phut_di_lam_muon = 0
                
    @api.constrains('thoi_gian_bat_dau')
    def _check_ngay_lam_va_check_in(self):
        for record in self:
            if record.gio_check_in:
                ngay_check_in = fields.Datetime.now()
                if ngay_check_in != record.thoi_gian_bat_dau:
                    raise ValidationError("Ca làm chưa tới hoặc ca làm đã chấm công.")

    @api.depends('gio_check_in', 'gio_check_out')
    def _compute_thoi_gian(self):
        for record in self:
            if record.gio_check_out and record.gio_check_in:
                duration = (record.gio_check_out - record.gio_check_in).total_seconds() / 3600
                record.thoi_gian_lam_viec = max(duration, 0)
            else:
                record.thoi_gian_lam_viec = 0.0

    @api.depends('gio_check_in')
    def _compute_trang_thai_check_in(self):
        for record in self:
            record.trang_thai_check_in = 'da_check_in' if record.gio_check_in else 'chua_check_in'

    @api.depends('gio_check_out')
    def _compute_trang_thai_check_out(self):
        for record in self:
            record.trang_thai_check_out = 'da_check_out' if record.gio_check_out else 'chua_check_out'
    
    @api.depends('gio_check_in', 'gio_check_out', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'buoi_lam_viec')
    def _compute_trang_thai_lam_viec(self):
        for record in self:
            if not record.thoi_gian_bat_dau or not record.thoi_gian_ket_thuc:
                record.trang_thai_lam_viec = 'chua_bat_dau'
                continue
            
            if not record.gio_check_in:
                record.trang_thai_lam_viec = 'chua_bat_dau'
            elif record.gio_check_in and not record.gio_check_out:
                if record.thoi_gian_bat_dau <= record.gio_check_in <= record.thoi_gian_ket_thuc or record.gio_check_in < record.thoi_gian_bat_dau:
                    record.trang_thai_lam_viec = 'dang_lam_viec'
                else:
                    record.trang_thai_lam_viec = 'chua_bat_dau'  
            elif record.gio_check_out:
                if record.gio_check_in < record.gio_check_out:
                    record.trang_thai_lam_viec = 'da_lam_viec'
                else:
                    record.trang_thai_lam_viec = 'chua_bat_dau'  



    @api.constrains('gio_check_in', 'gio_check_out', 'phut_di_lam_muon')
    def _check_gio_lam_viec(self):
        for record in self:
            if record.gio_check_in and record.gio_check_out and record.gio_check_in > record.gio_check_out:
                raise ValidationError("Giờ check-in không được lớn hơn giờ check-out.")
            
            if record.phut_di_lam_muon > 0:
                record.ghi_chu = "Đi muộn"
            else:
                record.ghi_chu = "Đúng giờ"

    # @api.constrains('nhan_vien_id', 'ngay_lam', 'gio_check_in')
    # def _check_dang_ky_lam_viec(self):
    #     for record in self:
    #         dang_ky = self.env['dang_ky_lam_viec'].search([
    #             ('nhan_vien_ids', 'in', [record.nhan_vien_id.id]), 
    #             ('ngay_lam', '=', record.ngay_lam),
    #             ('trang_thai', '=', 'approved')
    #         ], limit=1)

    #         if not dang_ky:
    #             raise ValidationError("Nhân viên chưa đăng ký giờ làm hoặc chưa được duyệt!")

    @api.depends('nhan_vien_id')
    def _compute_phong_ban_chuc_vu(self):
        """Lấy phòng ban & chức vụ từ lịch sử công tác của nhân viên"""
        for record in self:
            if record.nhan_vien_id:
                lich_su_cong_tac = self.env['lich_su_cong_tac'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('loai_chuc_vu', '=', 'Chính')
                ], order="id desc", limit=1)  # Lấy bản ghi mới nhất

                record.phong_ban_id = lich_su_cong_tac.phong_ban_id.id if lich_su_cong_tac else False
                record.chuc_vu_id = lich_su_cong_tac.chuc_vu_id.id if lich_su_cong_tac else False
            else:
                record.phong_ban_id = False
                record.chuc_vu_id = False
    
    buoi_lam_viec = fields.Selection([
        ('sang', 'Sáng (8h-12h)'),
        ('chieu', 'Chiều (13h-17h)'),
        ('ca_ngay', 'Cả ngày (8h-17h)')
    ], string='Buổi làm việc', required=True)
    
    @api.depends('ngay_lam', 'buoi_lam_viec')
    def _compute_thoi_gian(self):
        for record in self:
            if record.ngay_lam and record.buoi_lam_viec:
                ngay = record.ngay_lam
                if record.buoi_lam_viec == 'sang':
                    record.thoi_gian_bat_dau = datetime.combine(ngay, datetime.min.time().replace(hour=1, minute=0))
                    record.thoi_gian_ket_thuc = datetime.combine(ngay, datetime.min.time().replace(hour=5, minute=0))
                elif record.buoi_lam_viec == 'chieu':
                    record.thoi_gian_bat_dau = datetime.combine(ngay, datetime.min.time().replace(hour=6, minute=0))
                    record.thoi_gian_ket_thuc = datetime.combine(ngay, datetime.min.time().replace(hour=10, minute=0))
                else:  # ca_ngay
                    record.thoi_gian_bat_dau = datetime.combine(ngay, datetime.min.time().replace(hour=1, minute=0))
                    record.thoi_gian_ket_thuc = datetime.combine(ngay, datetime.min.time().replace(hour=10, minute=0))
            else:
                record.thoi_gian_bat_dau = False
                record.thoi_gian_ket_thuc = False
    
    
    thoi_gian_bat_dau = fields.Datetime(string='Thời gian bắt đầu', compute='_compute_thoi_gian', store=True)
    thoi_gian_ket_thuc = fields.Datetime(string='Thời gian kết thúc', compute='_compute_thoi_gian', store=True)
    
    # @api.onchange('dang_ky_lam_viec_id')
    # def _onchange_dang_ky_lam_viec(self):
    #     """Tự động điền ngày làm và giờ đăng ký từ ca làm việc"""
    #     if self.dang_ky_lam_viec_id:
    #         self.ngay_lam_da_dang_ky = self.dang_ky_lam_viec_id.ngay_lam
    #         self.gio_bat_dau_dang_ky = self.dang_ky_lam_viec_id.gio_bat_dau
    #         self.gio_ket_thuc_dang_ky = self.dang_ky_lam_viec_id.gio_ket_thuc
            
    @api.onchange('nhan_vien_id', 'ngay_lam')
    def _onchange_nhan_vien_ngay(self):
        if self.nhan_vien_id and self.ngay_lam:
            ten_nhan_vien = self.nhan_vien_id.ho_va_ten 
            
            don_xin_nghi = self.env['don_xin_nghi'].search([
                ('nhan_vien_id', '=', self.nhan_vien_id.id),
                ('nghi_tu_ngay', '<=', self.ngay_lam),
                ('nghi_den_ngay', '>=', self.ngay_lam),
                ('trang_thai', '=', 'approved')
            ], limit=1)
            
            if don_xin_nghi:
                self.nhan_vien_id = False  
                return {
                    'warning': {
                        'title': 'Cảnh báo',
                        'message': f'Nhân viên {ten_nhan_vien} đã có đơn xin nghỉ phép được duyệt vào ngày {self.ngay_lam}!'
                    }
                }
                
            if don_xin_nghi:
                self.so_ngay_nghi = len(don_xin_nghi)
                return {
                    'warning': {
                        'title': 'Cảnh báo',
                        'message': f'Nhân viên {ten_nhan_vien} đã có đơn xin nghỉ phép vào ngày {self.ngay_lam}!'
                    }
                }




    _sql_constraints = [
        ('unique_nhan_vien_ngay', 'unique(nhan_vien_id, ngay_lam)', 'Nhân viên chỉ có thể chấm công một lần mỗi ngày!')
    ]
