from httpx import AsyncClient,  ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
import pytest
from app.main import app
from app.database import get_db
# Imports to create a test client 
from app.auth.service import create_user
from app.core.security import create_access_token
from app.auth.schemas import UserCreate




# Database connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.test_database_name}"

test_engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)




# creates a session to perform tests then clear the database after ech test is completed
@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection) 
    yield session

    session.close()
    transaction.rollback()

    connection.close()



# Client fixture
# This is a basic test client with no authentication - use in endpoints that require no login
@pytest.fixture
async def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client: 
        yield client
    app.dependency_overrides.clear()


# Create fixture to create an user in the database then return it
@pytest.fixture
def test_user(db_session):
    user_data = UserCreate(email="user1@example.com", password="pass123", name="John")
    new_user = create_user(db_session, user_data)
    yield new_user


# Create a fixture that will pass an authenticated user to any test
@pytest.fixture
async def authenticated_client(db_session, test_user): 
    # reference this from core/security.py -> payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #email = payload.get("sub")
    user_token = create_access_token({"sub": test_user.email})

    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test" , headers={"Authorization": f"Bearer {user_token}"}) as client:
        yield client
    app.dependency_overrides.clear()