from typing import List, Optional, Literal
from pydantic import BaseModel

class SearchPlan(BaseModel):
    sources: List[Literal["amazon", "flipkart", "web"]]
    query: str
    max_results: int = 10
    max_price: Optional[int] = None
