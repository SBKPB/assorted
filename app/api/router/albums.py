import io
import os
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Album, AlbumCreate, AlbumPublic

router = APIRouter(prefix="/album", tags=["Album"])
UPLOAD_DIR = "./app/uploads"

ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/webp"}


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(
        (
            (img_width - crop_width) // 2,
            (img_height - crop_height) // 2,
            (img_width + crop_width) // 2,
            (img_height + crop_height) // 2,
        )
    )


@router.get("/", response_model=list[AlbumPublic])
def get_albums(db: SessionDep):
    albums = db.exec(select(Album)).all()

    return albums


@router.get("/{album_id}", response_model=AlbumPublic)
def get_album(album_id: str, db: SessionDep):
    album = db.exec(select(Album).where(Album.id == album_id)).one_or_none()

    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    return album


@router.post("/", response_model=AlbumPublic)
def create_album(album_info: AlbumCreate, db: SessionDep):
    album = Album(name=album_info.name)
    db.add(album)
    db.commit()
    db.refresh(album)

    album_public = AlbumPublic(
        id=album.id,
        name=album.name,
        created_at=album.created_at,
    )

    return album_public


@router.post(
    "/{album_id}/images",
)
async def create_image(
    album_id: str,
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
    db: SessionDep,
):
    normal_dir = os.path.join(UPLOAD_DIR, album_id, "normal")
    thumb_dir = os.path.join(UPLOAD_DIR, album_id, "thumbnail")

    os.makedirs(normal_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    uploaded_files = []

    for file in files:

        # 先檢查格式
        if file.content_type not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file type: {file.content_type}"
            )

        contents = await file.read()
        try:
            original = Image.open(io.BytesIO(contents))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        # 正常版轉換（寬最大1920、高最大1080）
        normal = original.copy()
        normal.thumbnail((1920, 1080))
        normal_filename = f"{uuid4().hex}.webp"
        normal_path = os.path.join(normal_dir, normal_filename)
        normal.save(normal_path, "WEBP")

        # 縮圖版轉換（裁成正方形512x512）
        thumb = original.copy()
        thumb.thumbnail((512, 512))
        thumb = crop_center(thumb, 512, 512)
        thumb_filename = f"{uuid4().hex}.webp"
        thumb_path = os.path.join(thumb_dir, thumb_filename)
        thumb.save(thumb_path, "WEBP")

        uploaded_files.append(
            {"normal": f"/{normal_path}", "thumbnail": f"/{thumb_path}"}
        )

    return {"filenames": [file.filename for file in files]}
