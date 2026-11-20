import asyncio
from datetime import date, datetime
import smtplib
from email.message import EmailMessage
from email.utils import formatdate

from app.core.config import get_settings    
from app.utils.logger import logger

class EmailService:
    def __init__(self)->None:
        self.settings = get_settings()

    def send_email(
        self,
        subject: str,
        body: str,
        recipient : str | None=None
    )-> bool:
        sender =self.settings.email_sender
        password = self.settings.email_password

        if not sender or not password:
            logger.error("Email configuration is missing")
            return False

        if not recipient:
            logger.error("Email recipient is mising")
            return False

        message= EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["subject"] = subject
        message["Date"] = formatdate(localtime=True)

        message.set_content(body)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=15)as server:
                server.login(sender, password)
                server.send_message(message)

            logger.info("Email sent successfully to %s", recipient)
            return True

        except (smtplib.SMTPException, OSError):
            logger.exception("Failed to send email to %s", recipient)
            return False


    def send_enrollment_confirmation(
        self,
        employee_name: str,
        employee_email: str,
        enrollment_id: int,
        enrollment_date: datetime,
        course_name: str,
        batch_name: str,
        start_date: date,
        end_date: date,
        duration_value: int,
        duration_unit: str,
        trainer_name: str
    ) -> bool:

        subject = "Enrollment Confirmation"

        body = ( (
            f"Dear {employee_name},\n\n"
            "Congratulations!\n\n"
            "Your enrollment has been successfully registered in our Training Management System.\n\n "

            "REGISTRATION DETAILS\n"
            f"Enrollment ID: {enrollment_id}\n"
            f"Employee Name: {employee_name}\n"
            f"Registration Date: {enrollment_date:%d-%m-%Y}\n"
            "Enrollment Status: Enrolled\n\n"

            "COURSE DETAILS\n"
            f"Course Name: {course_name}\n"
            f"Course Duration: {duration_value} {duration_unit}\n\n"

            "BATCH DETAILS\n"
            f"Batch Name: {batch_name}\n"
            f"Start Date: {start_date:%d-%m-%Y}\n"
            f"End Date: {end_date:%d-%m-%Y}\n"
            f"Assigned Trainer: {trainer_name}\n\n"

            "We wish you a successful learning experience.\n"
            "Regards,\n"
            "Training Management Team"
        )
        )

        return self.send_email(
            subject=subject,
            body=body,
            recipient=employee_email
        )

    async def send_enrollment_confirmation_async(
        self,
        employee_name: str,
        employee_email: str,
        enrollment_id: int,
        enrollment_date: datetime,
        course_name: str,
        batch_name: str,
        start_date: date,
        end_date: date,
        duration_value: int,
        duration_unit: str,
        trainer_name: str
    ) -> bool:

        return await asyncio.to_thread(
            self.send_enrollment_confirmation,
            employee_name,
            employee_email,
            enrollment_id,
            enrollment_date,
            course_name,
            batch_name,
            start_date,
            end_date,
            duration_value,
            duration_unit,
            trainer_name
        )


    def send_enrollment_status_email(
        self,
        employee_name: str,
        employee_email: str,
        enrollment_id: int,
        batch_name: str,
        course_name:str,
        old_status: str,
        new_status: str,
        remarks: str | None = None,
    ) -> bool:

        subject_mapping = {
            "Enrolled": "Enrollment Resumed",
            "Paused": "Enrollment Paused",
            "Cancelled": "Enrollment Cancelled",
            "Completed": "Training Completed",
        }

        subject = subject_mapping.get(
            new_status,
            "Enrollment Status Updated"
        )

        body = (
            f"Dear {employee_name},\n\n"

            "ENROLLMENT DETAILS\n"
            f"Enrollment ID: {enrollment_id}\n"
            f"Employee Name: {employee_name}\n"
            f"Batch Name: {batch_name}\n"
            f"Course Name: {course_name}\n\n"

            "STATUS UPDATE\n"
            f"Previous Status: {old_status}\n"
            f"Current Status: {new_status}\n"
            f"Remarks: {remarks or 'No additional remarks'}\n\n"

            "For any questions or assistance, please contact the training team.\n\n"
            "Regards,\n"
            "Training Management Team"
        )

        return self.send_email(
            subject=subject,
            body=body,
            recipient=employee_email,
        )

    # ASYNC STATUS CHANGE EMAIL
    async def send_enrollment_status_email_async(
        self,
        employee_name: str,
        employee_email: str,
        enrollment_id: int,
        batch_name: str,
        course_name: str,
        old_status: str,
        new_status: str,
        remarks: str | None = None,
    ) -> bool:

        return await asyncio.to_thread(
            self.send_enrollment_status_email,
            employee_name,
            employee_email,
            enrollment_id,
            batch_name,
            course_name,
            old_status,
            new_status,
            remarks,
        )



