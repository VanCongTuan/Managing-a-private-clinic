from server_app import app, db
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from server_app.models import Thuoc, DonViThuoc, Role,NguoiDung
from flask_login import current_user, logout_user, login_user
from flask import redirect ,request
from flask_admin import Admin, expose ,AdminIndexView
import utils

from datetime import datetime



# admin.add_view(DonViThuocView(DonViThuoc, db.session))
# admin.add_view(MedicineView(Thuoc, db.session))


class AuthenticateModelView(ModelView):
     def is_accessible(self):
         return current_user.is_authenticated and current_user.loaiNguoiDung.__eq__(Role.Admin)


class ThuocView(AuthenticateModelView):
    column_list = ['tenThuoc', 'ngaySX', 'hanSD', 'donGia', 'donViThuoc']  # Add 'donViThuoc' to the list
class DonViThuocView(AuthenticateModelView):
    column_list = ['donVi', 'thuoc']
class MedicineView(ThuocView):
    can_view_details = True
    can_export = True
    column_searchable_list = ['tenThuoc', 'donGia']
    column_labels = {
        'tenThuoc': 'Ten Thuoc',
        'ngaySX': 'Ngay san xuat',
        'hanSD': 'Han su dung',
        'donGia': 'Don gia'
    }
    column_filters = ['tenThuoc', 'donGia']

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

class StatsView(BaseView):
    @expose('/')

    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date= request.args.get('to_date')
        year=request.args.get('year', datetime.now().year)
        return self.render('stats.html',sales_data=utils.sales_reports(kw=kw,from_date=from_date,to_date=to_date),sales_datas=utils.total_amount_by_year(year=year))
    # kiểm tra người dùng
    def is_accessible(self):
        return current_user.is_authenticated and current_user.loaiNguoiDung == Role.Admin

class StatsViews(BaseView):
    @expose('/')
    def index(self):
        kw1 = request.args.get('kw1')
        # fromdate = request.args.get('fromdate')
        # todate= request.args.get('todate')

        return self.render('drug_statistics.html', medication_data=utils.medicine_stats(kw1=kw1))
    def is_accessible(self):
        return current_user.is_authenticated and current_user.loaiNguoiDung == Role.Admin

class MyAdmin(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin_page.html', stats=utils.sales_report())


admin = Admin(app=app, name='Quan tri phòng mạch', template_mode='bootstrap4', index_view=MyAdmin())
admin.add_view(AuthenticateModelView(DonViThuoc,db.session))
admin.add_view(MedicineView(Thuoc,db.session))
admin.add_view(StatsViews(name='Thong ke thuoc'))
admin.add_view(StatsView(name='Thong ke doanh thu'))
admin.add_view(LogoutView(name='Logout'))
