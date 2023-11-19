from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set up the engine and sessionmaker
engine = create_engine('sqlite:///:memory:')  # using an in-memory SQLite database for testing
Session = sessionmaker(bind=engine)

# Create a new session
session = Session()

# Query to extract the week from the date
query = text("SELECT strftime('%W', '2023-10-10')")
week_number = session.execute(query).scalar()

# Print the extracted week
print(f'The extracted week is: {week_number}')

# Close the session
session.close()