import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResult:
    def __init__(
        self,
        job_name: str,
        status: JobStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration_seconds: Optional[float] = None,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        error_details: Optional[str] = None
    ):
        self.job_name = job_name
        self.status = status
        self.started_at = started_at
        self.completed_at = completed_at
        self.duration_seconds = duration_seconds
        self.message = message
        self.data = data or {}
        self.error_details = error_details

    def replace(self, **kwargs):
        """Create a new JobResult with updated fields."""
        result = JobResult(
            job_name=self.job_name,
            status=self.status,
            started_at=self.started_at,
            completed_at=self.completed_at,
            duration_seconds=self.duration_seconds,
            message=self.message,
            data=self.data,
            error_details=self.error_details
        )
        for key, value in kwargs.items():
            setattr(result, key, value)
        return result


class BaseJob(ABC):
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger(f"job.{name}")
        self._cancelled = False
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> JobResult:
        """Execute the job and return the result."""
        pass
    
    def cancel(self):
        """Cancel the job."""
        self._cancelled = True
        self.logger.info(f"Job {self.name} has been marked for cancellation")
    
    @property
    def is_cancelled(self) -> bool:
        return self._cancelled
    
    def create_result(
        self,
        status: JobStatus,
        message: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        data: Optional[Dict[str, Any]] = None,
        error_details: Optional[str] = None
    ) -> JobResult:
        """Create a JobResult with timing information."""
        if started_at and completed_at:
            duration = (completed_at - started_at).total_seconds()
        else:
            duration = None
            
        return JobResult(
            job_name=self.name,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            message=message,
            data=data,
            error_details=error_details
        )


class JobRunner:
    def __init__(self):
        self.logger = logging.getLogger("job_runner")
    
    async def run_job(self, job: BaseJob, *args, **kwargs) -> JobResult:
        """Run a job and handle errors and cancellation."""
        started_at = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting job: {job.name}")
            result = await job.execute(*args, **kwargs)
            
            # Fill in missing timing info if job didn't provide it
            if result.started_at is None:
                result = result.replace(started_at=started_at)
            if result.completed_at is None:
                result = result.replace(completed_at=datetime.utcnow())
            if result.duration_seconds is None and result.started_at and result.completed_at:
                duration = (result.completed_at - result.started_at).total_seconds()
                result = result.replace(duration_seconds=duration)
                
            self.logger.info(f"Job {job.name} completed with status: {result.status}")
            return result
            
        except Exception as e:
            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()
            
            self.logger.error(f"Job {job.name} failed with error: {str(e)}")
            return JobResult(
                job_name=job.name,
                status=JobStatus.FAILED,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                message=f"Job failed due to unhandled exception",
                error_details=str(e)
            )
        except asyncio.CancelledError:
            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()
            
            self.logger.warning(f"Job {job.name} was cancelled")
            return JobResult(
                job_name=job.name,
                status=JobStatus.CANCELLED,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                message="Job was cancelled"
            )