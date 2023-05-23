from typing import TypedDict

from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
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
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class GamePayload(TypedDict):
    date: str
    enemy: str
    enemyScore: str
    score: str


class ResultResponse(BaseModel):
    data: list[GamePayload]


class NameResponse(BaseModel):
    name: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("api/guild/results/{guild_id}")
async def get_results(guild_id: int) -> ResultResponse:
    """Get the game results for a guild.

    Parameters
    ----------
    guild_id : int
        The ID of the guild to get the results for.

    Returns
    -------
    dict[str, list[ResultResponse]

    Raises
    ------
    HTTPException
        If no results are found for the guild.
    """

    db = deta.Base("results")
    results = db.get(str(guild_id))

    if results is None or not results["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    else:
        return ResultResponse(data=results["data"])


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
async def guild_details(request: Request, guild_id: int):
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

    if response is None or not response["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    else:
        return templates.TemplateResponse(
            "guild_details.html",
            context={
                "request": request,
                "key": str(guild_id),
                "data": response["data"]
            }
        )