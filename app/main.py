from app.api.fishes import router as fish_router
from app.api.events import router as event_router
from app.api.users import router as user_router
from app.api.export import router as export_router

from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Carnet de Pêche API",
    description="""

## Utilisateur

You will be able to:

* **Create users** (_implemented_).
* **Read users** (_implemented_).
* **Get new user password** (_implemented_).

* **Add fish** (_implemented_).
* **Read fish** (_implemented_).

* **Add Events** (_implemented_).
* **Read Events** (_implemented_).

* **Visualize fishing zone** (_implemented_).
* **Visualize fishing history** (_implemented_).


""",
    summary="Everything needed for the development of the Fishing App for Abenakis Fishers. 🚀",
    version="1.3.0",
    contact={
        "name": "Nassim Massaudi",
        "email": "naelm31@ulaval.ca",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins. Adjust this in a production setting.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(fish_router)
app.include_router(event_router)
app.include_router(export_router)

handler = Mangum(app)