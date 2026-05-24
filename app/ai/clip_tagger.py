from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
from PIL import Image

logger = logging.getLogger(__name__)

CATEGORIES = [
    "t-shirt", "dress shirt", "blouse", "sweater", "hoodie", "tank top",
    "jacket", "coat", "blazer", "vest",
    "jeans", "trousers", "shorts", "skirt", "leggings", "joggers",
    "sneakers", "boots", "loafers", "heels", "sandals", "flats",
    "dress", "jumpsuit", "suit",
    "scarf", "hat", "belt", "bag", "sunglasses", "watch", "jewelry",
]

CATEGORY_ROLE = {
    "t-shirt": "top", "dress shirt": "top", "blouse": "top",
    "sweater": "top", "hoodie": "top", "tank top": "top",
    "jacket": "outerwear", "coat": "outerwear", "blazer": "outerwear", "vest": "outerwear",
    "jeans": "bottom", "trousers": "bottom", "shorts": "bottom",
    "skirt": "bottom", "leggings": "bottom", "joggers": "bottom",
    "sneakers": "footwear", "boots": "footwear", "loafers": "footwear",
    "heels": "footwear", "sandals": "footwear", "flats": "footwear",
    "dress": "full_outfit", "jumpsuit": "full_outfit", "suit": "full_outfit",
    "scarf": "accessory", "hat": "accessory", "belt": "accessory",
    "bag": "accessory", "sunglasses": "accessory", "watch": "accessory",
    "jewelry": "accessory",
}

STYLE_TAGS = [
    "casual", "formal", "smart casual", "streetwear", "athleisure",
    "minimalist", "bohemian", "preppy", "vintage", "elegant",
    "sporty", "business", "romantic", "edgy",
]

SEASONS = ["spring", "summer", "fall", "winter"]

FORMALITY_MAP = {
    "t-shirt": 0.1, "tank top": 0.05, "hoodie": 0.1, "joggers": 0.1,
    "jeans": 0.3, "shorts": 0.1, "sneakers": 0.2, "sandals": 0.15,
    "sweater": 0.4, "blouse": 0.5, "loafers": 0.5, "flats": 0.4,
    "dress shirt": 0.8, "trousers": 0.65, "blazer": 0.75, "coat": 0.6,
    "jacket": 0.5, "boots": 0.5, "heels": 0.75,
    "dress": 0.6, "suit": 0.95, "jumpsuit": 0.5,
    "scarf": 0.3, "hat": 0.2, "belt": 0.4, "bag": 0.4,
    "sunglasses": 0.2, "watch": 0.5, "jewelry": 0.5, "vest": 0.5,
}

WARMTH_MAP = {
    "tank top": 0.0, "shorts": 0.05, "sandals": 0.05, "t-shirt": 0.1,
    "flats": 0.2, "dress": 0.2, "skirt": 0.15, "blouse": 0.2,
    "jeans": 0.4, "sneakers": 0.3, "loafers": 0.35,
    "sweater": 0.6, "hoodie": 0.55, "trousers": 0.5, "jacket": 0.6,
    "blazer": 0.5, "boots": 0.65, "leggings": 0.4,
    "coat": 0.85, "vest": 0.5, "joggers": 0.45,
    "scarf": 0.7, "hat": 0.5, "dress shirt": 0.3,
    "suit": 0.55, "jumpsuit": 0.4, "belt": 0.0, "bag": 0.0,
    "sunglasses": 0.0, "watch": 0.0, "jewelry": 0.0, "heels": 0.25,
}


class FashionTagger:
    _instance = None
    _model = None
    _processor = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        if self._loaded:
            return
        try:
            from transformers import CLIPModel, CLIPProcessor
            logger.info("Loading FashionCLIP model…")
            self._model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
            self._processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")
            self._model.eval()
            self._loaded = True
            logger.info("FashionCLIP loaded ✓")
        except Exception as e:
            logger.error(f"Failed to load FashionCLIP: {e}")
            raise

    def _get_image_embedding(self, image: Image.Image) -> list[float]:
        import torch
        inputs = self._processor(images=image, return_tensors="pt")
        with torch.no_grad():
            vision_outputs = self._model.vision_model(pixel_values=inputs["pixel_values"])
            emb = self._model.visual_projection(vision_outputs.pooler_output)
            emb = torch.nn.functional.normalize(emb, p=2, dim=-1)
        return emb[0].tolist()

    def _classify(self, image: Image.Image, candidates: list[str]) -> tuple[str, float]:
        import torch
        inputs = self._processor(
            text=candidates,
            images=image,
            return_tensors="pt",
            padding=True,
        )
        with torch.no_grad():
            vision_outputs = self._model.vision_model(pixel_values=inputs["pixel_values"])
            image_features = self._model.visual_projection(vision_outputs.pooler_output)
            image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
            text_outputs = self._model.text_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"]
            )
            text_features = self._model.text_projection(text_outputs.pooler_output)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)
            similarity = (image_features @ text_features.T)[0]
            probs = similarity.softmax(dim=0)
        best_idx = probs.argmax().item()
        return candidates[best_idx], probs[best_idx].item()

    def tag_image(self, image_path: str | Path) -> dict[str, Any]:
        if not self._loaded:
            raise RuntimeError("FashionTagger not loaded. Call .load() first.")
        image = Image.open(image_path).convert("RGB")
        embedding = self._get_image_embedding(image)
        category, cat_confidence = self._classify(image, CATEGORIES)
        role = CATEGORY_ROLE.get(category, "other")
        style_scores = []
        for tag in STYLE_TAGS:
            _, score = self._classify(image, [tag, f"not {tag}"])
            style_scores.append((tag, score))
        style_scores.sort(key=lambda x: x[1], reverse=True)
        top_style_tags = [t for t, _ in style_scores[:3]]
        season_scores = []
        for season in SEASONS:
            _, score = self._classify(image, [f"{season} clothing", "other season clothing"])
            season_scores.append((season, score))
        season_scores.sort(key=lambda x: x[1], reverse=True)
        top_seasons = [s for s, _ in season_scores[:2]]
        formality = FORMALITY_MAP.get(category, 0.5)
        warmth = WARMTH_MAP.get(category, 0.5)
        return {
            "embedding": embedding,
            "category": category,
            "role": role,
            "style_tags": top_style_tags,
            "season": top_seasons,
            "formality_score": formality,
            "warmth_score": warmth,
            "ai_confidence": cat_confidence,
            "attributes": {"detected_category_raw": category, "role": role},
        }


fashion_tagger = FashionTagger()