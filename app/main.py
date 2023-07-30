from app.api.fishes import router as fish_router
from app.api.events import router as event_router
from app.api.users import router as user_router

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(
    title="Carnet du Pêcheur API",
    description="""

## Utilisateur

You will be able to:

* **Create users** 
* **Login** 

* **Add fish** 
* **Read fish**

* **Add Events**
* **Read Events**

""",
    summary="Everything needed for the development of the Fishing App for Abenakis Fishers. 🚀",
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

lambda_handler = Mangum(app)

app.include_router(user_router)
app.include_router(fish_router)
app.include_router(event_router)