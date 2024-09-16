import json
import os.path
from server_app import app ,db
from server_app.models  import Thuoc ,Role, NguoiDung, ToaThuoc, PhieuKham,HoaDon ,DonViThuoc
from flask_login import current_user
import hashlib
from sqlalchemy import func
from datetime import datetime




def load_medicine(kw=None,page=1):
    thuocs =Thuoc.query.filter(Thuoc.active.__eq__(True))

    if kw:
        thuocs = thuocs.filter(Thuoc.tenThuoc.contains(kw))

    page_size =app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end =start + page_size
    return thuocs.slice(start,end).all()
    # return thuocs

def count_medicine():
    return Thuoc.query.filter(Thuoc.active.__eq__(True)).count()


def get_medicine_by_id(medicine_name):
    return Thuoc.query.filter(medicine_name)

def check_login(username,password,role=Role.Admin):
    if password and username:
        password =str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return NguoiDung.query.filter(NguoiDung.username.__eq__(username.strip()),NguoiDung.password.__eq__(password),NguoiDung.loaiNguoiDung.__eq__(role)).first()



def counter_medicine(medicine):
    total_quantity,total_price = 0,0
    if medicine:
        for c in medicine.values():
            total_quantity += c['quantity']
            total_price += c['quantity']*c['donGia']
    return {'total_quantity': total_quantity,
            'total_price': total_price}


def add_receipt(medicine):
    if medicine:
        receipt = PhieuKham(user=current_user)
        a="3 lan"
        b = "3 lan"
        db.session.add(receipt)
        for c in medicine.values():
            d =ToaThuoc(receipt=receipt,medicine_id=c['id'],soLuong=c['quantity'],lieuLuong=a,cachDung=b)
            db.session.add(d)
        db.session.commit()




def sales_report():
    specific_columns = HoaDon.query.with_entities(HoaDon.id, HoaDon.tienKham, HoaDon.tienThuoc,HoaDon.tongTien,HoaDon.ngayLap,HoaDon.thuNgan_id,HoaDon.phieuKham_id).all()
    return  specific_columns


def total_amount_by_year(year):
        result = db.session.query(func.extract('month', HoaDon.ngayLap).label('Thang_thu_tien'),
            func.sum(HoaDon.tongTien).label('Doanh_thu'),
            func.count(HoaDon.ngayLap).label('benh_nhan')
        ).filter(func.extract('year', HoaDon.ngayLap) == year).group_by('Thang_thu_tien').order_by(func.extract('month', HoaDon.ngayLap).asc()).all()
        return result

def medicine_stats(kw1=None,fromdate=None,todate=None):# Hàm báo cáo thống kê thuốc *****************************************************************************
    result = db.session.query(
        func.sum(ToaThuoc.soLuong).label('So_luong'),
        Thuoc.tenThuoc.label('Ten_thuoc'),
        DonViThuoc.donVi.label('Don_vi'),
        func.count(Thuoc.donViThuoc_id).label('So_lan_dung')
        ).join(Thuoc, ToaThuoc.thuoc_id == Thuoc.id) \
        .join(DonViThuoc, Thuoc.donViThuoc_id == DonViThuoc.id) \
        .join(PhieuKham, ToaThuoc.phieuKham_id == PhieuKham.id) \
        .group_by(Thuoc.tenThuoc, DonViThuoc.donVi).all()
    if kw1:
        result= db.session.query(
        func.sum(ToaThuoc.soLuong).label('So_luong'),
        Thuoc.tenThuoc.label('Ten_thuoc'),
        DonViThuoc.donVi.label('Don_vi'),
        func.count(Thuoc.donViThuoc_id).label('So_lan_dung')
        ).join(Thuoc, ToaThuoc.thuoc_id == Thuoc.id) \
        .join(DonViThuoc, Thuoc.donViThuoc_id == DonViThuoc.id) \
        .join(PhieuKham, ToaThuoc.phieuKham_id == PhieuKham.id) \
        .filter(Thuoc.tenThuoc.like(f"%{kw1}%")) \
        .group_by(Thuoc.tenThuoc, DonViThuoc.donVi).all()
    # if fromdate:
    #     fromdate = datetime.strptime(fromdate, "%Y-%m-%d")
    #     result = db.session.query(
    #         func.sum(ToaThuoc.soLuong).label('So_luong'),
    #         Thuoc.tenThuoc.label('Ten_thuoc'),
    #         DonViThuoc.donVi.label('Don_vi'),
    #         func.count(Thuoc.donViThuoc_id).label('So_lan_dung')
    #     ).join(Thuoc, ToaThuoc.thuoc_id == Thuoc.id) \
    #         .join(DonViThuoc, Thuoc.donViThuoc_id == DonViThuoc.id) \
    #         .join(PhieuKham, ToaThuoc.phieuKham_id == PhieuKham.id) \
    #         .filter(PhieuKham.ngayLap >= fromdate) \
    #         .group_by(Thuoc.tenThuoc, DonViThuoc.donVi).all()
    # if todate:
    #     todate = datetime.strptime(todate, "%Y-%m-%d")
    #     result = db.session.query(
    #         func.sum(ToaThuoc.soLuong).label('So_luong'),
    #         Thuoc.tenThuoc.label('Ten_thuoc'),
    #         DonViThuoc.donVi.label('Don_vi'),
    #         func.count(Thuoc.donViThuoc_id).label('So_lan_dung')
    #     ).join(Thuoc, ToaThuoc.thuoc_id == Thuoc.id) \
    #         .join(DonViThuoc, Thuoc.donViThuoc_id == DonViThuoc.id) \
    #         .join(PhieuKham, ToaThuoc.phieuKham_id == PhieuKham.id) \
    #         .filter(PhieuKham.ngayLap <= todate) \
    #         .group_by(Thuoc.tenThuoc, DonViThuoc.donVi).all()
    # if fromdate and todate:
    #     fromdate = datetime.strptime(fromdate, "%Y-%m-%d")
    #     todate = datetime.strptime(todate, "%Y-%m-%d")
    #     result = db.session.query(
    #         func.sum(ToaThuoc.soLuong).label('So_luong'),
    #         Thuoc.tenThuoc.label('Ten_thuoc'),
    #         DonViThuoc.donVi.label('Don_vi'),
    #         func.count(Thuoc.donViThuoc_id).label('So_lan_dung')
    #     ).join(Thuoc, ToaThuoc.thuoc_id == Thuoc.id) \
    #         .join(DonViThuoc, Thuoc.donViThuoc_id == DonViThuoc.id) \
    #         .join(PhieuKham, ToaThuoc.phieuKham_id == PhieuKham.id) \
    #         .filter(PhieuKham.ngayLap >= fromdate).filter(PhieuKham.ngayLap <= todate) \
    #         .group_by(Thuoc.tenThuoc, DonViThuoc.donVi).all()
    return result




def sales_reports(kw=None,from_date=None, to_date=None):
    total_tongTien = db.session.query(func.sum(HoaDon.tongTien)).filter(
        func.extract('year', HoaDon.ngayLap) == '').scalar()
    result = db.session.query(
        func.DATE_FORMAT(HoaDon.ngayLap, '%Y-%m-%d').label('Ngay_thu_tien'),
        func.sum(HoaDon.tongTien).label('Doanh_thu'),
        func.count(HoaDon.ngayLap).label('benh_nhan'),
        (func.sum(HoaDon.tongTien) / total_tongTien * 100).label('ty_le')
    ).filter(func.extract('year', HoaDon.ngayLap) == '').group_by('Ngay_thu_tien').all()
    if kw:
        total_tongTien = db.session.query(func.sum(HoaDon.tongTien)).filter(
            func.extract('month', HoaDon.ngayLap) == kw).scalar()
        result = db.session.query(
                                  func.DATE_FORMAT(HoaDon.ngayLap, '%Y-%m-%d').label('Ngay_thu_tien'),
                                  func.sum(HoaDon.tongTien).label('Doanh_thu'),
                                  func.count(HoaDon.ngayLap).label('benh_nhan'),
                                  (func.sum(HoaDon.tongTien) / total_tongTien * 100).label('ty_le')
                                  ).filter(func.extract('month', HoaDon.ngayLap) == kw).group_by('Ngay_thu_tien').all()
    if from_date:
        from_date1 = datetime.strptime(from_date, "%Y-%m-%d")
        total_tongTien = db.session.query(func.sum(HoaDon.tongTien)).filter(
            func.extract('year', HoaDon.ngayLap) == from_date1.year).scalar()
        result = db.session.query(
            func.DATE_FORMAT(HoaDon.ngayLap, '%Y-%m-%d').label('Ngay_thu_tien'),
            func.sum(HoaDon.tongTien).label('Doanh_thu'),
            func.count(HoaDon.ngayLap).label('benh_nhan'),
            (func.sum(HoaDon.tongTien) / total_tongTien * 100).label('ty_le')
        ).filter(HoaDon.ngayLap >= from_date1).group_by('Ngay_thu_tien').all()
    if to_date:

        to_date1 = datetime.strptime(to_date, "%Y-%m-%d")
        total_tongTien = db.session.query(func.sum(HoaDon.tongTien)).filter(
            func.extract('year', HoaDon.ngayLap) == to_date1.year).scalar()
        result = db.session.query(
            func.DATE_FORMAT(HoaDon.ngayLap, '%Y-%m-%d').label('Ngay_thu_tien'),
            func.sum(HoaDon.tongTien).label('Doanh_thu'),
            func.count(HoaDon.ngayLap).label('benh_nhan'),
            (func.sum(HoaDon.tongTien) / total_tongTien * 100).label('ty_le')
        ).filter(HoaDon.ngayLap <= to_date1).group_by('Ngay_thu_tien').all()
    if from_date and to_date:
        from_date1 = datetime.strptime(from_date, "%Y-%m-%d")
        to_date1 = datetime.strptime(to_date, "%Y-%m-%d")
        total_tongTien = db.session.query(func.sum(HoaDon.tongTien)).filter(
            func.extract('year', HoaDon.ngayLap) >= from_date1.year).filter(func.extract('year', HoaDon.ngayLap)<= to_date1.year).scalar()
        result = db.session.query(
            func.DATE_FORMAT(HoaDon.ngayLap, '%Y-%m-%d').label('Ngay_thu_tien'),
            func.sum(HoaDon.tongTien).label('Doanh_thu'),
            func.count(HoaDon.ngayLap).label('benh_nhan'),
            (func.sum(HoaDon.tongTien) / total_tongTien * 100).label('ty_le')
        ).filter(HoaDon.ngayLap >= from_date1).filter(HoaDon.ngayLap <= to_date1).group_by('Ngay_thu_tien').all()
    return result


