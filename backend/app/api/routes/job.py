from datetime import datetime
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.database.db import get_db, SessionLocal
from app.models.jobs import Job, JobEmbedding
from app.schemas.jobs import JobCreate, JobUpdate, JobResponse
from app.dependencies import get_current_active_user
from app.models.users import User
from app.core.vector_store import vector_store
from app.utils.logging import create_log

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Create a new job"""
    start_time = time.perf_counter()
    try:
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
    
    except Exception as e:
        create_log(
            db=db,
            log_name="job_create_failed",
            log_type="ERROR",
            function_name="create_job",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="job_create",
            log_type="PERF",
            function_name="create_job",
            time_taken=total_time
        )



@router.get("/", response_model=list[JobResponse])
def read_jobs(skip: int = 0, limit: int = 100, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Retrieve jobs"""
    strart_time = time.perf_counter()
    try:
        jobs = db.query(Job).offset(skip).limit(limit).all()
        return jobs
    except Exception as e:
        create_log(
            db=db,
            log_name="read_jobs_failed",
            log_type="ERROR",
            function_name="read_jobs",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))   
    finally:
        total_time = time.perf_counter() - strart_time
        create_log(
            db=db,
            log_name="read_jobs",
            log_type="PERF",
            function_name="read_jobs",
            time_taken=total_time
        )


@router.get("/{job_id}", response_model=JobResponse)
def read_job(job_id: int, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Retrieve a job by ID"""
    start_time = time.perf_counter()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        create_log(
            db=db,
            log_name="read_job_failed",
            log_type="ERROR",
            function_name="read_job",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="read_job",
            log_type="PERF",
            function_name="read_job",
            time_taken=total_time
        )


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Update a job by ID"""
    start_time = time.perf_counter()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        job.updated_at = datetime.utcnow()
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        for key, value in job_update.model_dump(exclude_unset=True).items():
            setattr(job, key, value)
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        create_log(
            db=db,
            log_name="update_job_failed",
            log_type="ERROR",
            function_name="update_job",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="update_job",
            log_type="PERF",
            function_name="update_job",
            time_taken=total_time
        )

@router.delete("/{job_id}")
def delete_job(job_id: int, current_user:User= Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Delete a job by ID"""
    start_time = time.perf_counter()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        db.delete(job)
        db.commit()
        return {"message": "Job deleted successfully"}
    except Exception as e:
        create_log(
            db=db,
            log_name="delete_job_failed",
            log_type="ERROR",
            function_name="delete_job",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="delete_job",
            log_type="PERF",
            function_name="delete_job",
            time_taken=total_time
        )

@router.post("/bulk.insert", response_model=List[JobResponse])
async def create_jobs(jobs: List[JobCreate], db: Session = Depends(get_db)):
    """Create multiple jobs in bulk"""
    start_time = time.perf_counter()
    try:
        job_data = [job.model_dump() for job in jobs]

        db.bulk_insert_mappings(Job, job_data)
        db.commit()

        inserted_jobs = db.query(Job).order_by(Job.id.desc()).limit(len(jobs)).all()

        return inserted_jobs
    except Exception as e:
        create_log(
            db=db,
            log_name="bulk_job_create_failed",
            log_type="ERROR",
            function_name="create_jobs",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        total_time = time.perf_counter() - start_time
        create_log(
            db=db,
            log_name="bulk_job_create",
            log_type="PERF",
            function_name="create_jobs",
            time_taken=total_time
        )
