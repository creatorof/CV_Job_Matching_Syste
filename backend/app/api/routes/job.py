from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session


from app.database.db import get_db, SessionLocal
from app.models.jobs import Job, JobEmbedding
from app.schemas.jobs import JobCreate, JobUpdate, JobResponse
from app.dependencies import get_current_active_user
from app.models.users import User
from app.core.vector_store import vector_store

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_job = Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    job_text = job.to_embedding_text()

    embeddings = vector_store.generate_embedding(job_text)
    job_embedding = JobEmbedding(
            job_id=db_job.id,    
            embedding=embeddings,
            model_name = ""
    )
        
    db.add(job_embedding)
    db.commit()
    db.refresh(job_embedding)
    return db_job


@router.get("/", response_model=list[JobResponse])
def read_jobs(skip: int = 0, limit: int = 100, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def read_job(job_id: int, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    job.updated_at = datetime.utcnow()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job_update.model_dump(exclude_unset=True).items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}