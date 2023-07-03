from fastapi import FastAPI
from api import users, fish, events

app = FastAPI(
    title="Carnet du Pêcheur API",
    description="""
## Items

You can **read items**.

## Utilisateur

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).

* **Add fish** (_not implemented_).
* **Read fish** (_not implemented_).

* **Add Events** (_not implemented_).
* **Read Events** (_not implemented_).

""",
    summary="Everything needed for the development of the Fishing App for Abenakis Fishers.",
    version="0.0.1",
    contact={
        "name": "Nassim Massaudi",
        "email": "naelm31@ulaval.ca",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


app.include_router(users.router, prefix="/api/v1")
app.include_router(fish.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")

