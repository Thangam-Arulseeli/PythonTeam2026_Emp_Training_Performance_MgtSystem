import asyncio
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
        batch_name: str,
    ) -> bool:

        subject = "Enrollment Confirmation"

        body = (
            f"Dear {employee_name},\n\n"
            "Your enrollment has been successfully completed.\n\n"
            f"Enrollment ID: {enrollment_id}\n"
            f"Batch Name: {batch_name}\n"
            "Status: Enrolled\n\n"
            "Regards,\n"
            "Training Management Team"
        )

        return self.send_email(
            subject=subject,
            body=body,
            recipient=employee_email,
        )

    async def send_enrollment_confirmation_async(
        self,
        employee_name: str,
        employee_email: str,
        enrollment_id: int,
        batch_name: str,
    ) -> bool:

        return await asyncio.to_thread(
            self.send_enrollment_confirmation,
            employee_name,
            employee_email,
            enrollment_id,
            batch_name,
        )


    def send_enrollment_status_email(
        self,
        employee_name: str,
        employee_email: str,
        enrollment_id: int,
        batch_name: str,
        old_status: str,
        new_status: str,
        remarks: str | None = None,
    ) -> bool:

        subject_mapping = {
            "enrolled": "Enrollment Resumed",
            "paused": "Enrollment Paused",
            "cancelled": "Enrollment Cancelled",
            "completed": "Training Completed",
        }

        subject = subject_mapping.get(
            new_status,
            "Enrollment Status Updated"
        )

        body = (
            f"Dear {employee_name},\n\n"
            "Your enrollment status has been updated.\n\n"
            f"Enrollment ID: {enrollment_id}\n"
            f"Batch Name: {batch_name}\n"
            f"Previous Status: {old_status}\n"
            f"Current Status: {new_status}\n"
            f"Remarks: {remarks or 'No additional remarks'}\n\n"
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
            old_status,
            new_status,
            remarks,
        )



