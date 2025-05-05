import io
import os
import shutil
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image
from sqlmodel import delete, select

from app.api.deps import SessionDep
from app.models import Album, AlbumCreate, AlbumPublic, ImagePublic
from app.models import Image as ImageModel

router = APIRouter(prefix="/albums", tags=["Album"])
UPLOAD_DIR = "./app/static/uploads"

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
def get_album(album_id: UUID, db: SessionDep):
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
    album_id: UUID,
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
    db: SessionDep,
):
    """
    新增圖片

    新增圖片時，會將圖片轉換為正常版和縮圖版，並存放在相簿的資料夾中
    """
    album = db.exec(select(Album).where(Album.id == album_id)).one_or_none()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    normal_dir = os.path.join(UPLOAD_DIR, str(album_id), "normal")
    thumb_dir = os.path.join(UPLOAD_DIR, str(album_id), "thumbnail")

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

        relative_normal_path = os.path.relpath(normal_path, UPLOAD_DIR)

        # 縮圖版轉換（裁成正方形512x512）
        thumb = original.copy()
        thumb.thumbnail((512, 512))
        thumb = crop_center(thumb, 512, 512)
        thumb_filename = f"{uuid4().hex}.webp"
        thumb_path = os.path.join(thumb_dir, thumb_filename)
        thumb.save(thumb_path, "WEBP")

        relative_thumb_path = os.path.relpath(thumb_path, UPLOAD_DIR)

        uploaded_files.append(
            {"normal": relative_normal_path, "thumbnail": relative_thumb_path}
        )

        static_url = "/static/uploads/"

        image = ImageModel(
            album_id=album_id,
            original_filename=file.filename,
            normal_url=static_url + relative_normal_path,
            thumbnail_url=static_url + relative_thumb_path,
        )
        db.add(image)
        db.commit()
        db.refresh(image)

    return {"filenames": [file.filename for file in files]}


@router.get("/{album_id}/images", response_model=list[ImagePublic])
def get_images(album_id: UUID, db: SessionDep):
    images = db.exec(select(ImageModel).where(ImageModel.album_id == album_id)).all()

    return images


@router.get("/{album_id}/images/{image_id}", response_model=ImagePublic)
def get_image(album_id: UUID, image_id: UUID, db: SessionDep):
    image = db.exec(
        select(ImageModel).where(
            ImageModel.album_id == album_id, ImageModel.id == image_id
        )
    ).one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return image


@router.delete("/{album_id}/images/{image_id}", status_code=204)
def delete_image(album_id: UUID, image_id: UUID, db: SessionDep):
    image = db.exec(
        select(ImageModel).where(
            ImageModel.album_id == album_id, ImageModel.id == image_id
        )
    ).one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(image)
    db.commit()

    normal_is_exist = os.path.exists("./app" + image.normal_url)
    thumb_is_exist = os.path.exists("./app" + image.thumbnail_url)

    if normal_is_exist:
        os.remove("./app" + image.normal_url)

    if thumb_is_exist:
        os.remove("./app" + image.thumbnail_url)

    return None


@router.delete("/{album_id}", status_code=204)
def delete_album(album_id: UUID, db: SessionDep):
    """
    刪除相簿

    刪除相簿時，會刪除相簿內的所有圖片
    """
    album = db.exec(select(Album).where(Album.id == album_id)).one_or_none()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    db.exec(delete(ImageModel).where(ImageModel.album_id == album_id))
    db.delete(album)
    db.commit()

    album_dir = os.path.join(UPLOAD_DIR, str(album_id))
    if os.path.exists(album_dir):
        try:
            shutil.rmtree(album_dir)
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove album directory: {e.strerror}",
            )

    return None
