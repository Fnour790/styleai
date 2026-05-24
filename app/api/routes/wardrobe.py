import json
import uuid
import os
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import WardrobeItem
from app.schemas.wardrobe import WardrobeItemResponse, WardrobeUploadResponse, WardrobeItemUpdate
from app.ai.clip_tagger import fashion_tagger
from app.ai.color_extractor import extract_colors
from app.services.qdrant_service import qdrant_service
from app.core.config import get_settings

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])
settings = get_settings()
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def get_current_user_id() -> str:
    return "test-user"


def item_to_dict(item):
    return {
        "id": str(item.id),
        "category": item.category,
        "subcategory": item.subcategory,
        "colors": json.loads(item.colors) if isinstance(item.colors, str) else (item.colors or []),
        "attributes": json.loads(item.attributes) if isinstance(item.attributes, str) else (item.attributes or {}),
        "style_tags": json.loads(item.style_tags) if isinstance(item.style_tags, str) else (item.style_tags or []),
        "season": json.loads(item.season) if isinstance(item.season, str) else (item.season or []),
        "formality_score": item.formality_score,
        "warmth_score": item.warmth_score,
        "image_url": item.image_url,
        "brand": item.brand,
        "times_worn": item.times_worn,
        "last_worn_at": item.last_worn_at,
        "created_at": item.created_at,
    }


@router.post("/upload", response_model=WardrobeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_clothing_item(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Use JPEG, PNG, or WebP.")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large.")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_ext = Path(file.filename or "image.jpg").suffix
    save_name = f"{uuid.uuid4()}{file_ext}"
    save_path = upload_dir / save_name

    with open(save_path, "wb") as f:
        f.write(contents)

    try:
        tag_result = fashion_tagger.tag_image(str(save_path))
        colors = extract_colors(str(save_path))
    except Exception as e:
        os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"AI tagging failed: {str(e)}")

    user_id = get_current_user_id()
    image_url = f"/uploads/{save_name}"

    item = WardrobeItem(
        user_id=user_id,
        category=tag_result["category"],
        subcategory=None,
        colors=json.dumps(colors),
        attributes=json.dumps(tag_result.get("attributes", {})),
        style_tags=json.dumps(tag_result.get("style_tags", [])),
        season=json.dumps(tag_result.get("season", [])),
        formality_score=tag_result.get("formality_score", 0.5),
        warmth_score=tag_result.get("warmth_score", 0.5),
        image_url=image_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return WardrobeUploadResponse(
        item=WardrobeItemResponse.model_validate(item_to_dict(item)),
        ai_confidence=round(tag_result.get("ai_confidence", 0.0), 3),
        message=f"Detected: {item.category}",
    )


@router.get("", response_model=list[WardrobeItemResponse])
def list_wardrobe(db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    items = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == user_id,
        WardrobeItem.is_active == True,
    ).order_by(WardrobeItem.created_at.desc()).all()
    return [WardrobeItemResponse.model_validate(item_to_dict(i)) for i in items]


@router.get("/{item_id}", response_model=WardrobeItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == user_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return WardrobeItemResponse.model_validate(item_to_dict(item))


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == user_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_active = False
    db.commit()