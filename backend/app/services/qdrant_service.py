"""
Qdrant vector database service.

Stores clothing item embeddings and enables similarity search
("find items in my wardrobe similar to this photo").
"""

import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

EMBEDDING_DIM = 512   # FashionCLIP output dimension


class QdrantService:
    _client: QdrantClient | None = None

    def get_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        return self._client

    def ensure_collection(self):
        """Create the wardrobe collection if it doesn't exist."""
        client = self.get_client()
        existing = [c.name for c in client.get_collections().collections]
        if settings.qdrant_collection not in existing:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {settings.qdrant_collection}")

    def upsert_item(
        self,
        item_db_id: str,
        user_id: str,
        embedding: list[float],
        payload: dict,
    ) -> str:
        """Store or update a clothing item embedding. Returns the Qdrant point ID."""
        client = self.get_client()
        point_id = str(uuid.uuid4())

        client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "item_db_id": item_db_id,
                        "user_id": user_id,
                        **payload,
                    },
                )
            ],
        )
        return point_id

    def search_similar(
        self,
        query_embedding: list[float],
        user_id: str,
        top_k: int = 10,
    ) -> list[dict]:
        """Find the most similar items in a user's wardrobe."""
        client = self.get_client()
        results = client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=top_k,
        )
        return [
            {"item_db_id": r.payload["item_db_id"], "score": r.score, **r.payload}
            for r in results
        ]

    def delete_item(self, qdrant_id: str):
        client = self.get_client()
        client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=[qdrant_id],
        )


qdrant_service = QdrantService()
