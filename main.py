from typing import TypedDict, Optional, Literal

from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from deta import Deta
import dotenv
import os


dotenv.load_dotenv()
deta = Deta(os.getenv("DB_KEY"))
templates = Jinja2Templates(directory="templates")
app = FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


class GamePayload(TypedDict):
    idx: int
    date: str
    enemy: str
    enemyScore: str
    score: str
    diff: int


class ResultResponse(BaseModel):
    data: list[GamePayload]


class NameResponse(BaseModel):
    name: str



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/guild/results/{guild_id}")
async def get_results(
    guild_id: int,
    name: Optional[str] = None,
    filter: Literal["win", "lose", "all", "draw"] = "all"
) -> ResultResponse:
    """Get the results of a guild.

    Parameters
    ----------
    guild_id : int
        The ID of the guild to get the results of.
    name : Optional[str], optional
        The name of the enemy guild to filter by, by default None
    filter : Literal[&quot;win&quot;, &quot;lose&quot;, &quot;all&quot;, &quot;draw&quot;], optional
        The filter to apply to the results, by default &quot;all&quot;

    Returns
    -------
    ResultResponse
        The results of the guild. ex: {"data": [{"idx": 0, "date": "2021-01-01", "enemy": "Enemy Guild", "enemyScore": "100", "score": "200", "diff": 100}]}

    Raises
    ------
    HTTPException
        If no results are found.
    """

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
                "enemyScore": game["enemyScore"],
                "score": game["score"],
                "diff": diff
            })

        return ResultResponse(data=new_data)


@app.get("api/guild/name/{guild_id}")
async def get_guild_name(guild_id: int) -> NameResponse:
    """Get the name of a guild.

    Parameters
    ----------
    guild_id : int
        The ID of the guild to get the name of.

    Returns
    -------
    NameResponse
        The name of the guild. ex: {"name": "Guild Name"}

    Raises
    ------
    HTTPException
        If no guild name is found.
    """

    db = deta.Base("guild")
    name_map = db.get(key="name")

    if (name:=name_map.get(str(guild_id))) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No guild name found"
        )
    else:
        return NameResponse(name=name)

@app.get("/api/guild/details/{guild_id}")
async def guild_details(request: Request, guild_id: int) -> HTMLResponse:
    """Get the details of a guild.

    Parameters
    ----------
    guild_id : int
        The ID of the guild to get the details of.

    Returns
    -------
    HTMLResponse
        The details of the guild.
    """

    db = deta.Base("results")
    response = db.get(str(guild_id))

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    else:

        for idx, data in enumerate(response["data"]):
            data.update(
                diff=int(data["score"]) - int(data["enemyScore"]),
                idx = idx
            )

        return templates.TemplateResponse(
            "guild_details.html",
            context={
                "request": request,
                "key": str(guild_id),
                "data": response["data"],
            }
        )