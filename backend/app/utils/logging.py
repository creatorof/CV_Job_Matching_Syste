from sqlalchemy.orm import Session

from app.models.system_logs import SystemLog


def create_log(db: Session, log_name: str, log_type: str, function_name: str, description: str = None, time_taken: float = None):
    """Create log of a task"""
    log = SystemLog(
        log_name=log_name,
        log_type=log_type,
        function_name=function_name,
        description=description,
        time_taken=time_taken,
    )
    db.add(log)
    db.commit()
