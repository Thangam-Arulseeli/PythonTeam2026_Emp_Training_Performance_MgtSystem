from datetime import date
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.models.trainer import Trainer
from app.schemas.trainer import TrainerCreate, TrainerUpdate
from app.services.implementations.trainer_service import TrainerServiceImpl


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def trainer_service(mock_repository):
    return TrainerServiceImpl(mock_repository)


@pytest.fixture
def trainer_data():
    return TrainerCreate(
        trainer_name="Test Trainer",
        dob="1990-05-10",
        experience=5,
        joining_date="2022-01-01",
        specialization=["Python"],
        qualification="MCA",
        email="testtrainer@gmail.com",
        phone_number="9876543210",
        address="Coimbatore",
    )


@pytest.fixture
def existing_trainer():
    return Trainer(
        trainer_id=1,
        trainer_name="Test Trainer",
        dob=date(1990, 5, 10),
        experience=5,
        joining_date=date(2022, 1, 1),
        specialization=["Python"],
        qualification="MCA",
        email="testtrainer@gmail.com",
        phone_number="9876543210",
        address="Coimbatore",
        is_active=True,
    )


# CREATE TRAINER


@pytest.mark.asyncio
async def test_create_trainer_success(
    trainer_service,
    mock_repository,
    trainer_data,
):
    expected_trainer = Trainer(
        trainer_id=1,
        trainer_name="Test Trainer",
        dob=date(1990, 5, 10),
        experience=5,
        joining_date=date(2022, 1, 1),
        specialization=["Python"],
        qualification="MCA",
        email="testtrainer@gmail.com",
        phone_number="9876543210",
        address="Coimbatore",
        is_active=True,
    )

    mock_repository.get_trainer_by_email.return_value = None
    mock_repository.get_trainer_by_phone.return_value = None
    mock_repository.create_trainer.return_value = expected_trainer

    result = await trainer_service.create_trainer(trainer_data)

    assert result is expected_trainer


@pytest.mark.asyncio
async def test_create_trainer_duplicate_email(
    trainer_service, mock_repository, trainer_data, existing_trainer
):
    mock_repository.get_trainer_by_email.return_value = existing_trainer

    with pytest.raises(HTTPException) as exc_info:
        await trainer_service.create_trainer(trainer_data)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already exists"


@pytest.mark.asyncio
async def test_create_trainer_duplicate_phone(
    trainer_service, mock_repository, trainer_data, existing_trainer
):
    mock_repository.get_trainer_by_email.return_value = None
    mock_repository.get_trainer_by_phone.return_value = existing_trainer

    with pytest.raises(HTTPException) as exc_info:
        await trainer_service.create_trainer(trainer_data)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Phone number already exists"


# GET TRAINER BY ID


@pytest.mark.asyncio
async def test_get_trainer_by_id_success(
    trainer_service,
    mock_repository,
    existing_trainer,
):
    mock_repository.get_trainer_by_id.return_value = existing_trainer

    result = await trainer_service.get_trainer_by_id(1)

    assert result is existing_trainer


@pytest.mark.asyncio
async def test_get_trainer_by_id_not_found(
    trainer_service,
    mock_repository,
):
    mock_repository.get_trainer_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await trainer_service.get_trainer_by_id(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Trainer not found"


@pytest.mark.asyncio
async def test_update_trainer_success(
    trainer_service,
    mock_repository,
    existing_trainer,
):
    trainer_update_data = TrainerUpdate(
        qualification="bsc",
    )

    mock_repository.get_trainer_by_id.return_value = existing_trainer
    mock_repository.get_trainer_by_email.return_value = None
    mock_repository.get_trainer_by_phone.return_value = None
    mock_repository.update_trainer.return_value = existing_trainer

    result = await trainer_service.update_trainer(
        1,
        trainer_update_data,
    )

    assert result is existing_trainer


@pytest.mark.asyncio
async def test_update_trainer_not_found(
    trainer_service,
    mock_repository,
):
    trainer_update_data = TrainerUpdate(
        qualification="PhD",
    )

    mock_repository.get_trainer_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await trainer_service.update_trainer(
            999,
            trainer_update_data,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Trainer not found"
