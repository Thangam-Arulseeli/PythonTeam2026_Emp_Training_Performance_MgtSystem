from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictException
from app.models.enrollment import Enrollment
from app.models.batch import Batch
from app.repositories.interfaces.enrollment_interface import EnrollmentInterface


class EnrollmentRepository(EnrollmentInterface):
    def __init__(self, db:AsyncSession)-> None:
        self.db = db

    # Method to find is the employee already enrolled in a batch or not
    async def count_active_by_employee(self, employee_id:int)-> int:    
        query = select(
            func.count(Enrollment.enrollment_id)).where(
                Enrollment.employee_id ==employee_id,
                Enrollment.status.in_(["enrolled","paused"])
            )
        result = await self.db.execute(query)
        return result.scalar_one()


    # Method to create enrollment
    async def create(self, data: dict[str, object]) -> Enrollment:
        enrollment = Enrollment(**data)
        self.db.add(enrollment)

        try:
            await self.db.commit()
            await self.db.refresh(enrollment)
        except IntegrityError as exc:
            await self.db.rollback()
            raise ConflictException(
                "Enrollment conflicts with the existing database record"
            )from exc

        return enrollment


    # To get by the enrollment_id
    async def get_by_id(self, enrollment_id : int) -> Enrollment | None:
        return await self.db.get(Enrollment, enrollment_id)


    # GET ALL ENROLLMENTS
    async def get_all(
        self,
        skip:int ,
        limit:int,
        status:str|None=None,
        trainer_id: int |None=None
    )-> tuple[list[Enrollment],int]:
        query = select(Enrollment)
        count_query = select(func.count(Enrollment.enrollment_id))

        if status:
            query = query.where(Enrollment.status == status)
            count_query = count_query.where(Enrollment.status == status)

        if trainer_id is not None:
            query = query.join(
                Batch,
                Enrollment.batch_id ==  Batch.id
            ).where(Batch.trainer_id == trainer_id)

            count_query = count_query.join(
                Batch,
                Enrollment.batch_id == Batch.id
            ).where(Batch.trainer_id == trainer_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        query = (
            query
            .order_by(Enrollment.enrollment_id.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        enrollments = list(result.scalars().all())
        return enrollments, total


    # to get the enrollments by employee_id
    async def get_by_employee_id(self, employee_id : int, trainer_id :int | None= None)->list[Enrollment]:
        query = select(Enrollment).where(Enrollment.employee_id==employee_id)

        #filter by trainer assigned batch
        if trainer_id is not None:
            query = query.join(
                Batch,
                Enrollment.batch_id == Batch.id
            )
        query = query.order_by(Enrollment.enrollment_date.desc())
        result=await self.db.execute(query)
        return list(result.scalars().all())


    # to update the status
    async def update(self,enrollment: Enrollment)-> Enrollment:
        self.db.add(enrollment)
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment


    # to get enrollment by batch id
    async def get_by_batch_id(
        self, 
        batch_id : int , 
        trainer_id : int | None = None
    )->list[Enrollment]:
        query = select(Enrollment).where(Enrollment.batch_id==batch_id)

        if trainer_id is not None:
            query = query.join(Batch,Enrollment.batch_id == Batch.id).where(
                Batch.trainer_id == trainer_id
            )

        query = query.order_by(Enrollment.enrollment_date)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    


    