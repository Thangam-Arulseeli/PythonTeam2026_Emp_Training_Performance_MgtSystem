from typing import Annotated

from fastapi import APIRouter, Depends, File, Path, UploadFile, status

from app.api.dependencies.assessment_dependencies import (
    get_assessment_result_service,
    get_assessment_service,
)
from app.api.dependencies.auth import get_current_user, require_roles
from app.models.assessment import Assessment
from app.models.assessment_result import AssessmentResult
from app.models.user import User
from app.schemas.assessment_result_schema import (
    AssessmentAssignResponse,
    AssessmentCancelRequest,
    AssessmentDetailResponse,
    AssessmentGradeRequest,
    AssessmentResultResponse,
    TraineeAssessmentDetailResponse,
)
from app.schemas.assessment_schema import (
    AssessmentActivation,
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentListResponse,
    AssessmentPatch,
    AssessmentResponse,
)
from app.services.interfaces.assessment_result_service import (
    AssessmentResultServiceInterface,
)
from app.services.interfaces.assessment_service import AssessmentServiceInterface

router = APIRouter(prefix="/api/assessment", tags=["Assessments"])

Assessment_Service = Annotated[
    AssessmentServiceInterface, Depends(get_assessment_service)
]
Assessment_Result_Service = Annotated[
    AssessmentResultServiceInterface, Depends(get_assessment_result_service)
]


@router.get(
    "/my-assessments",
    response_model=list[TraineeAssessmentDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get my assigned assessments",
    description="Fetch all assessment records assigned to the currently authenticated trainee (employee), including evaluation status, awarded marks, schedule, and batch details.",
)
async def get_my_assessments(
    service: Assessment_Result_Service,
    current_user: User = Depends(get_current_user),
) -> list[TraineeAssessmentDetailResponse]:
    return await service.get_my_assessments(current_user)


@router.get(
    "/results/{result_id}",
    response_model=TraineeAssessmentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assessment result details",
    description="Retrieve details of a single assessment result attempt. Trainees can only view their own results; trainers and administrators can view any result.",
)
async def get_result_by_id(
    result_id: Annotated[
        int, Path(description="Unique ID of the assessment result record", ge=1)
    ],
    service: Assessment_Result_Service,
    current_user: User = Depends(get_current_user),
) -> TraineeAssessmentDetailResponse:
    return await service.get_result_by_id(result_id, current_user)


@router.get(
    "/{assessment_id}/results",
    response_model=list[AssessmentDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="List trainee results for an assessment",
    description="Retrieve all trainee submissions, marks, and grading statuses for a specific assessment. Restricted to trainers and administrators.",
)
async def get_results_by_assessment_id(
    assessment_id: Annotated[
        int, Path(description="Unique ID of the assessment", ge=1)
    ],
    service: Assessment_Result_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> list[AssessmentDetailResponse]:
    return await service.get_results_by_assessment_id(assessment_id)


@router.post(
    "/results/{result_id}/submit",
    response_model=AssessmentResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit an assessment attempt",
    description="Submit work for an assessment with an file upload. Validates that the assessment and enrollment are active and that the test has started. Trainees must submit on the scheduled date before midnight; trainers and administrators can submit anytime as an override.",
)
async def submit_assessment(
    result_id: Annotated[
        int, Path(description="Unique ID of the assessment result record", ge=1)
    ],
    service: Assessment_Result_Service,
    file: Annotated[
        UploadFile | None, File(description="submission file (e.g. PDF or document)")
    ] = None,
    current_user: User = Depends(get_current_user),
) -> AssessmentResult:
    return await service.submit_assessment(
        result_id=result_id,
        file=file,
        current_user=current_user,
    )


@router.post(
    "/results/{result_id}/grade",
    response_model=AssessmentResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Grade a submitted assessment",
    description="Award marks, assign an optional grade, and provide feedback for a submitted assessment attempt. Validates that the mark does not exceed the total marks. If no grade is specified, PASS/FAIL is auto-derived based on the pass mark. Restricted to trainers and administrators.",
)
async def grade_assessment(
    result_id: Annotated[
        int, Path(description="Unique ID of the assessment result record", ge=1)
    ],
    payload: AssessmentGradeRequest,
    service: Assessment_Result_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> AssessmentResult:
    return await service.grade_assessment(
        result_id=result_id,
        payload=payload,
    )


@router.patch(
    "/results/{result_id}/cancel",
    response_model=AssessmentResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a pending assessment attempt",
    description="Cancel a trainee's assessment attempt with an optional reason. Only attempts currently in 'pending' status can be cancelled; already submitted or graded records cannot be cancelled. Restricted to trainers and administrators.",
)
async def cancel_assessment_result(
    result_id: Annotated[
        int, Path(description="Unique ID of the assessment result record", ge=1)
    ],
    payload: AssessmentCancelRequest,
    service: Assessment_Result_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> AssessmentResult:
    return await service.cancel_assessment_result(
        result_id=result_id,
        payload=payload,
    )


@router.get(
    "/{id}",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assessment definition by ID",
    description="Fetch the assessment data, type, and schedule of a specific assessment definition.",
)
async def get_assessment_by_id(
    id: Annotated[int, Path(description="Unique ID of the assessment", ge=1)],
    service: Assessment_Service,
    current_user: User = Depends(get_current_user),
) -> Assessment:
    return await service.get_assessment_by_id(id)


@router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assessment",
    description="Schedule a new assessment for a batch. Validates that the batch is active and not completed, the scheduled date falls within batch start and end dates, and pass mark does not exceed total mark. Restricted to trainers and administrators. Assessment types are (quiz,interview,exam)",
)
async def create_assessment(
    assessment_data: AssessmentCreate,
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> Assessment:
    return await service.create_assessment(assessment_data)


@router.patch(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an assessment",
    description="Partially update an existing assessment's title, description, schedule, or marks. Re-validates batch schedule dates and mark thresholds if updated. Restricted to trainers and administrators.",
)
async def patch_assessment(
    assessment_id: Annotated[
        int, Path(description="Unique ID of the assessment to update", ge=1)
    ],
    assessment_data: AssessmentPatch,
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> Assessment:
    return await service.patch_assessment(assessment_id, assessment_data)


@router.patch(
    "/{assessment_id}/activation",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update assessment active status",
    description="Activate or deactivate an assessment. Re-activation requires the parent batch to be active and not completed. Restricted to trainers and administrators.",
)
async def update_assessment_activation(
    assessment_id: Annotated[
        int, Path(description="Unique ID of the assessment", ge=1)
    ],
    status_data: AssessmentActivation,
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> Assessment:
    return await service.update_assessment_activation(
        assessment_id, status_data.is_active
    )


@router.get(
    "/",
    response_model=AssessmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List assessments with pagination and filters",
    description="Retrieve a paginated list of assessments with optional filters for batch ID, active status, assessment type, title, marks, and scheduled date. Restricted to trainers and administrators.",
)
async def get_all_assessments(
    filter_params: Annotated[AssessmentFilterParams, Depends()],
    service: Assessment_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> AssessmentListResponse:
    return await service.get_all_assessments(filter_params)


@router.post(
    "/{assessment_id}/assign",
    response_model=AssessmentAssignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign assessment to all active batch trainees",
    description="Bulk assign an active assessment to all trainees currently enrolled in its batch. Automatically initializes result records with 'pending' status and skips trainees already assigned. Restricted to trainers and administrators.",
)
async def assign_assessment(
    assessment_id: Annotated[
        int, Path(description="Unique ID of the assessment to assign", ge=1)
    ],
    service: Assessment_Result_Service,
    current_user: User = Depends(require_roles("admin", "trainer")),
) -> AssessmentAssignResponse:
    return await service.assign_assessment_to_batch(assessment_id)
