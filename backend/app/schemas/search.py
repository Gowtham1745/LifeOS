from pydantic import BaseModel, Field
from typing import List, Optional


class SearchResultItem(BaseModel):
    id: str
    type: str  # task, habit, goal, note, journal, transaction
    title: str
    subtitle: Optional[str] = None
    url: str
    category: Optional[str] = None
    date: Optional[str] = None


class GlobalSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem] = Field(default_factory=list)
