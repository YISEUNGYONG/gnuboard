from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models
from common import *


router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)
# 파이썬 함수 및 변수를 jinja2 에서 사용할 수 있도록 등록
# TODO: admin/base.html에서만 사용하는 함수이므로 이동이 필요함
templates.env.globals["get_admin_menus"] = get_admin_menus
# TODO: form에서 공용으로 사용하는 함수이므로 이동이 필요함
templates.env.globals["generate_one_time_token"] = generate_one_time_token


@router.get("/faq_master_list")
def faq_master_list(request: Request, db: Session = Depends(get_db)):
    """FAQ관리 목록"""
    model = models.FaqMaster
    request.session["menu_key"] = "300700"

    faq_masters = db.query(model).order_by(model.fm_order).all()

    return templates.TemplateResponse(
        "admin/faq_master_list.html", {"request": request, "faq_masters": faq_masters}
    )


@router.get("/faq_master_form")
def faq_master_add_form(request: Request):
    """FAQ관리 등록 폼"""

    return templates.TemplateResponse(
        "admin/faq_master_form.html", {"request": request, "faq_master": None}
    )


@router.post("/faq_master_form/add")
def faq_master_add(
        request: Request,
        db: Session = Depends(get_db),
        token: str = Form(...),
        fm_subject: str = Form(...),
        fm_head_html: str = Form(None),
        fm_tail_html: str = Form(None),
        fm_mobile_head_html: str = Form(None),
        fm_mobile_tail_html: str = Form(None),
        fm_order: int = Form(0)
    ):
    """FAQ관리 등록 처리"""
    # 토큰 검사
    if not validate_one_time_token(token):
        raise HTTPException(status_code=403, detail="Invalid token.")

    faq_master = models.FaqMaster(
        fm_subject=fm_subject
        , fm_head_html=fm_head_html
        , fm_tail_html=fm_tail_html
        , fm_mobile_head_html=fm_mobile_head_html
        , fm_mobile_tail_html=fm_mobile_tail_html
        , fm_order=fm_order
    )
    db.add(faq_master)
    db.commit()

    return RedirectResponse(f"/admin/faq_master_form/{faq_master.fm_id}", status_code=303)


@router.get("/faq_master_form/{fm_id}")
def faq_master_update_form(fm_id: int, request: Request, db: Session = Depends(get_db)):
    """FAQ관리 수정 폼"""
    faq_master = db.query(models.FaqMaster).filter(models.FaqMaster.fm_id == fm_id).first()

    return templates.TemplateResponse(
        "admin/faq_master_form.html", {"request": request, "faq_master": faq_master}
    )


@router.post("/faq_master_form/{fm_id}")
def faq_master_update(
        fm_id: int,
        request: Request,
        db: Session = Depends(get_db),
        token: str = Form(...),
        fm_subject: str = Form(...),
        fm_head_html: str = Form(None),
        fm_tail_html: str = Form(None),
        fm_mobile_head_html: str = Form(None),
        fm_mobile_tail_html: str = Form(None),
        fm_order: int = Form(0)
    ):
    """FAQ관리 수정 처리"""
    # 토큰 검사
    if not validate_one_time_token(token):
        raise HTTPException(status_code=403, detail="Invalid token.")

    faq_master = db.query(models.FaqMaster).filter(models.FaqMaster.fm_id == fm_id).first()

    faq_master.fm_subject = fm_subject
    faq_master.fm_head_html = fm_head_html
    faq_master.fm_tail_html = fm_tail_html
    faq_master.fm_mobile_head_html = fm_mobile_head_html
    faq_master.fm_mobile_tail_html = fm_mobile_tail_html
    faq_master.fm_order = fm_order
    db.commit()

    return RedirectResponse(f"/admin/faq_master_form/{faq_master.fm_id}", status_code=303)


@router.delete("/faq_master_form/{fm_id}/delete")
def faq_master_delete(
        fm_id: int,
        request: Request,
        db: Session = Depends(get_db),
    ):
    """FAQ관리 삭제 처리"""
    # 토큰 검사
    # DELETE 요청일 경우, Body에 토큰이 없으므로 쿼리스트링에서 토큰을 얻는다.
    token = request.query_params.get("token")
    if not validate_one_time_token(token):
        raise HTTPException(status_code=403, detail="Invalid token.")
    
    faq_master = db.query(models.FaqMaster).filter(models.FaqMaster.fm_id == fm_id).first()
    db.delete(faq_master)
    db.commit()

    return {"message": "FAQ가 성공적으로 삭제되었습니다."}


@router.get("/faq_master_form/{fm_id}/list")
def faq_list(fm_id: int, request: Request, db: Session = Depends(get_db)):
    """
    FAQ목록
    """
    request.session["menu_key"] = "300700"

    faq_master = db.query(models.FaqMaster).filter(models.FaqMaster.fm_id == fm_id).first()
    faqs = sorted(faq_master.faqs, key=lambda x: x.fa_order)

    return templates.TemplateResponse(
        "admin/faq_list.html", {"request": request, "faq_master": faq_master, "faqs": faqs}
    )


@router.get("/faq_master_form/{fm_id}/add")
def faq_add_form(fm_id: int, request: Request, db: Session = Depends(get_db)):
    """FAQ관리 등록 폼"""
    faq_master = db.query(models.FaqMaster).filter(models.FaqMaster.fm_id == fm_id).first()

    return templates.TemplateResponse(
        "admin/faq_form.html", {"request": request, "faq_master": faq_master, "faq": None}
    )


@router.post("/faq_master_form/{fm_id}/add")
def faq_add(
        fm_id: int,
        request: Request,
        db: Session = Depends(get_db),
        token: str = Form(...),
        fa_order: str = Form(...),
        fa_subject: str = Form(...),
        fa_content: str = Form(...),
    ):
    """FAQ관리 등록 처리"""
    # 토큰 검사
    if not validate_one_time_token(token):
        raise HTTPException(status_code=403, detail="Invalid token.")

    faq = models.Faq(
        fm_id=fm_id,
        fa_order=fa_order,
        fa_subject=fa_subject,
        fa_content=fa_content,
    )
    db.add(faq)
    db.commit()

    return RedirectResponse(f"/admin/faq_master_form/{fm_id}/faq/{faq.fa_id}", status_code=303)


@router.get("/faq_master_form/{fm_id}/faq/{fa_id}")
def faq_update_form(fa_id: int, request: Request, db: Session = Depends(get_db)):
    """FAQ관리 등록 폼"""
    faq = db.query(models.Faq).filter(models.Faq.fa_id == fa_id).first()
    faq_master = faq.faq_master

    return templates.TemplateResponse(
        "admin/faq_form.html", {"request": request, "faq_master": faq_master, "faq": faq}
    )


@router.post("/faq_master_form/{fm_id}/faq/{fa_id}")
def faq_update(
        fm_id: int,
        fa_id: int,
        request: Request,
        db: Session = Depends(get_db),
        token: str = Form(...),
        fa_order: str = Form(...),
        fa_subject: str = Form(...),
        fa_content: str = Form(...),
    ):
    """FAQ관리 등록 처리"""
    # 토큰 검사
    if not validate_one_time_token(token):
        raise HTTPException(status_code=403, detail="Invalid token.")

    faq = db.query(models.Faq).filter(models.Faq.fa_id == fa_id).first()

    faq.fa_subject = fa_subject
    faq.fa_content = fa_content
    faq.fa_order = fa_order
    db.commit()

    return RedirectResponse(f"/admin/faq_master_form/{fm_id}/faq/{faq.fa_id}", status_code=303)


@router.delete("/faq_master_form/{fm_id}/faq/{fa_id}")
async def faq_delete(
        fa_id: int,
        request: Request,
        db: Session = Depends(get_db),
    ):
    """FAQ 항목 삭제 처리"""
    # 토큰 검사
    # DELETE 요청일 경우, Body에 토큰이 없으므로 쿼리스트링에서 토큰을 얻는다.
    token = request.query_params.get("token")
    if not validate_one_time_token(token):
        raise HTTPException(status_code=403, detail="Invalid token.")

    faq = db.query(models.Faq).filter(models.Faq.fa_id == fa_id).first()
    db.delete(faq)
    db.commit()

    return {"message": "FAQ 항목이 성공적으로 삭제되었습니다."}