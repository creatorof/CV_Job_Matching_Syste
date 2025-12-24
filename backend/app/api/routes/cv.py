from fastapi import APIRouter, Depends, FastAPI, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.core.parser import parser
from sqlalchemy.orm import Session

from app.core.extractor import cv_extractor
from app.schemas.cvs import CVResponse
from app.models.cvs import CV, CVEmbedding
from app.dependencies import get_current_active_user
from app.models.users import User
from app.database.db import get_db
from app.core.vector_store import vector_store

router = APIRouter(
    prefix="/cvs",
    tags=["cvs"]
)  

@router.post("/upload")
async def parse_pdf(file: UploadFile = File(...), current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    try:
        pdf_bytes = await file.read()

        result = await run_in_threadpool(
            parser.parse_pdf,
            pdf_bytes,
            file.filename
        )
        cv_text = result['raw_text']
        extracted = cv_extractor.extract(cv_text)
        cv = CV(
            user_id=current_user.id,  
            name=extracted.get("name"),
            email=extracted.get("email"),
            phone=extracted.get("phone"),
            location=extracted.get("location"),
            summary=extracted.get("summary"),
            work=extracted.get("work"),
            education=extracted.get("education"),
            skills=extracted.get("skills"),
            languages=extracted.get("languages"),
            certifications=extracted.get("certifications"),
            category=extracted.get("category"),
        )
        db.add(cv)
        db.commit()
        db.refresh(cv)

        embeddings = vector_store.generate_embedding(cv_text)
        cv_embedding = CVEmbedding(
            cv_id=cv.id,    
            embedding=embeddings
        )
        
        db.add(cv_embedding)
        db.commit()
        db.refresh(cv_embedding)

        return {"extracted_data": extracted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cv_id}", response_model=CVResponse)
def read_cv(cv_id: int, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if cv is None:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv     


@router.get("/", response_model=list[CVResponse])
def read_cvss(skip: int = 0, limit: int = 100, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    cvs = db.query(CV).offset(skip).limit(limit).all()
    return cvs

