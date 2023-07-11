from typing import Optional, Literal
from typing_extensions import TypedDict

from fastapi import (
    FastAPI,
    HTTPException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from deta import Deta
import dotenv
import os


dotenv.load_dotenv()
deta = Deta(os.getenv("DB_KEY"))
app = FastAPI()


origins = [
    os.environ["ORIGIN"]
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


class GamePayload(TypedDict):
    idx: int
    date: str
    enemy: str
    enemyScore: str
    score: str
    diff: int


class ResultResponse(BaseModel):
    data: list[GamePayload]
    total: int
    name: Optional[str]


@app.get("/api/guild/results/{guild_id}")
async def get_results(
    guild_id: int,
    skip: int = 0,
    pageSize: int = 50,
    name: Optional[str] = None,
    filter: Literal["win", "lose", "all", "draw"] = "all"
) -> ResultResponse:
    """Get the results of a guild.

    Parameters
    ----------
    guild_id : int
        The ID of the guild to get the results of.
    skip : int, optional
        The number of results to skip, by default 0
        Non negative integer.
    pageSize : int, optional
        The number of results to return, by default 50
        note: This value should be in the range from 0 to 50.
    name : Optional[str], optional
        The name of the enemy guild to filter by, by default None
    filter : Literal[&quot;win&quot;, &quot;lose&quot;, &quot;all&quot;, &quot;draw&quot;], optional
        The filter to apply to the results, by default &quot;all&quot;

    Returns
    -------
    ResultResponse
        The results of the guild. ex: {"data": [{"idx": 0, "date": "2021-01-01", "enemy": "Enemy Guild", "enemyScore": "100", "score": "200", "diff": 100}], "total": 1}

    Raises
    ------
    HTTPException
        If no results are found.
    """

    if skip < 0 or pageSize < 0 or pageSize > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skip or pageSize value"
        )

    db = deta.Base("results")
    results = db.get(str(guild_id))

    if results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    else:
        new_data = []

        for idx, game in enumerate(results["data"]):
            diff = int(game["score"]) - int(game["enemyScore"])
            if filter == "all":
                pass
            elif filter == "win":
                if diff <= 0:
                    continue
            elif filter == "lose":
                if diff >= 0:
                    continue
            elif filter == "draw":
                if diff != 0:
                    continue

            if name is not None and not name.lower() in game["enemy"].lower():
                continue

            new_data.append({
                "idx": idx,
                "date": game["date"],
                "enemy": game["enemy"],
                "enemyScore": str(game["enemyScore"]),
                "score": str(game["score"]),
                "diff": diff
            })

        start = skip * pageSize
        end = start + pageSize

        try:
            return ResultResponse(
                data=new_data[start:end],
                total=len(new_data),
                name=deta.Base("guild").get(key="name").get(str(guild_id))
            )
        except IndexError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The number of results is only {len(new_data)} but you are trying to skip {skip} results and return {pageSize} results."
            )