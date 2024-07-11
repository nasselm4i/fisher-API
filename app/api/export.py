import io
from typing import Annotated
import zipfile
import csv

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.api.utils.users import get_current_active_user
from app.db.models.user import Code, User, UserInfo
from app.db.db_setup import get_session
from app.db.models.fish import Fish
from app.db.models.event import Event
from app.db.models.report import ExoticFishReport, ProblemReport
from sqlalchemy import inspect

from app.schemas.users import UserDetails


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")  # assuming your HTML files are in a "templates" directory

@router.get("/download_data", response_class=HTMLResponse)
async def get_download_page(request: Request):
    """
    Retrieves the download page for exporting data.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: The template response containing the download form.
    """
    return templates.TemplateResponse("download_form.html", {"request": request})

def model_to_row(instance):
    """
    Convert a SQLAlchemy model instance into a row of data.

    Args:
        instance: The SQLAlchemy model instance to convert.

    Returns:
        A list representing a row of data, where each element corresponds to a column value in the instance's table.
    """
    return [getattr(instance, column.name) for column in instance.__table__.columns]

@router.post("/user_data_zip", response_class=StreamingResponse)
async def read_users_me(code: str = Form(...), filtered: bool = Form(...), session: Session = Depends(get_session)):
    """
    Read user data based on the provided code and filter options.

    Args:
        code (str): The code to authenticate the user.
        filtered (bool): Flag indicating whether to include only specific user_ids for filtered data.
        session (Session): The database session.

    Returns:
        StreamingResponse: The response containing the exported user data in a zip file.
    """
    correct_code = "puHmo4UhotWYAAkjFOCjKT8d1iNI61FyCA"  # Hardcoded code

    if code != correct_code:
        return Response(status_code=400)
    
    if filtered:
        # Include only specific user_ids for filtered data
        user_ids = [212, 232, 233, 251]
        # also include user ids greater than 253
        user_ids.extend([user.user_id for user in session.query(User).filter(User.user_id > 269).all()])
    else:
        # Include all user_ids or a different set of user_ids for non-filtered data
        user_ids = [212, 230, 232, 233, 243, 245, 246, 247, 248, 251]
        # user_ids = [user.user_id for user in session.query(User).all()]  # Example: getting all user_ids
    
    # Fetch users' emails
    users = session.query(User).filter(User.user_id.in_(user_ids)).all()
    emails = [user.email for user in users]

    # Create an in-memory file
    mem_file = io.BytesIO()
    with zipfile.ZipFile(mem_file, 'w') as zip_file:
        # For each table, create a CSV file and add it to the zip
        for table in [Event, Fish, ProblemReport, ExoticFishReport]:
            # Check if the table has 'user_id' and 'email' attributes
            has_user_id = 'user_id' in inspect(table).columns
            has_email = 'email' in inspect(table).columns

            if has_user_id and has_email:
                # Both user_id and email are present in the table
                data = session.query(table).filter((table.user_id.in_(user_ids)) | (table.email.in_(emails))).all()
            elif has_user_id:
                # Only user_id is present in the table
                data = session.query(table).filter(table.user_id.in_(user_ids)).all()
            elif has_email:
                # Only email is present in the table
                data = session.query(table).filter(table.email.in_(emails)).all()
            else:
                # Neither user_id nor email is present, handle accordingly
                data = session.query(table).all()  # or any other default behavior
            
            # Get column names (headers) for the CSV file
            headers = [column.name for column in table.__table__.columns]
            
            # Convert the records to rows
            rows = [model_to_row(record) for record in data]

            if rows:
                s_io = io.StringIO()
                cw = csv.writer(s_io)

                # Write headers
                cw.writerow(headers)
                
                # Write the rows to CSV
                cw.writerows(rows)

                s_io.seek(0)
                zip_file.writestr(f"{table.__tablename__}.csv", s_io.read())

    mem_file.seek(0)
    _headers = {"Content-Disposition": f"attachment; filename=donnee_peche_abenakis.zip"}
    return StreamingResponse(mem_file, media_type="application/zip", headers=_headers)