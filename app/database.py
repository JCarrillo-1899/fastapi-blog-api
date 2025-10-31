from sqlmodel import create_engine, Session

database_url = "postgresql://postgres:postgres@localhost:5432/Blog"
engine = create_engine(database_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session