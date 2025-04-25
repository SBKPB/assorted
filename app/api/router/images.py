from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.api.deps import SessionDep

router = APIRouter()


@router.get("/images")
def get_images(db: SessionDep):
    return {"message": "Hello World"}


@router.post(
    "/images",
)
async def create_image(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
    db: SessionDep,
):

    return {"filenames": [file.filename for file in files]}
