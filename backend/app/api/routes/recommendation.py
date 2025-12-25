import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.dependencies import get_current_active_user
from app.models.cvs import CV
from app.models.jobs import Job
from app.schemas.recommendations import JobRecommendationResponse
from app.dependencies import get_current_active_user
from typing import List
from app.core.recommender import job_recommender
from app.utils.logging import create_log

router = APIRouter(
    prefix="/recommendations",
    tags=["reccomendations"]
)


@router.get("/{cv_id}", response_model=List[JobRecommendationResponse])
async def get_recommendations(
    cv_id: int,
    top_k: int = 10,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job recommendations for a CV"""
    start_time = time.perf_counter()
    cv = db.query(CV).filter(
        CV.id == cv_id
    ).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    category = cv.category

    jobs = db.query(Job).filter(
        Job.company_industry == category,
        Job.is_expired == False
    ).all()
    jobs_dict = [job.__dict__ for job in jobs]
    try:
        recommendations = job_recommender.match_cv_to_jobs(cv.__dict__, jobs_dict, top_k=top_k)

        recommendations = [JobRecommendationResponse(**rec) for rec in recommendations]
        return recommendations
    
    except Exception as e:
        create_log(
            db=db,
            log_name="get_recommendations_failed",
            log_type="ERROR",
            function_name="get_recommendations",
            description=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )
