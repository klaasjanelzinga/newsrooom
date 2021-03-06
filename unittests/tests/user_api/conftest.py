import pyotp
import pytest
from faker import Faker

from api.security import TokenVerifier
from api.user_api import start_totp_registration, confirm_totp, TOTPVerificationRequest
from core_lib.application_data import Repositories
from core_lib.repositories import User
from core_lib.user import _generate_hash, _generate_salt
from core_lib.utils import bytes_to_str_base64


@pytest.fixture
def generate_password_salt() -> bytes:
    return _generate_salt()


@pytest.fixture
def signed_up_user_email_address(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def signed_up_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def signed_up_bearer_token(faker: Faker, signed_up_user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(signed_up_user)}"


@pytest.fixture
def signed_up_user_password_hash(signed_up_user_password: str, generate_password_salt: bytes) -> bytes:
    return _generate_hash(signed_up_user_password, generate_password_salt)


@pytest.fixture
async def signed_up_user(
    faker: Faker,
    repositories: Repositories,
    signed_up_user_email_address: str,
    signed_up_user_password_hash: bytes,
    generate_password_salt: bytes,
) -> User:
    user = User(
        email_address=signed_up_user_email_address,
        display_name=faker.name(),
        password_hash=bytes_to_str_base64(signed_up_user_password_hash),
        password_salt=bytes_to_str_base64(generate_password_salt),
        is_approved=False,
    )
    user = await repositories.user_repository.upsert(user)
    return user


@pytest.fixture
def approved_up_user_email_address(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def approved_up_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def approved_up_user_password_hash(approved_up_user_password: str, generate_password_salt: bytes) -> bytes:
    return _generate_hash(approved_up_user_password, generate_password_salt)


@pytest.fixture
async def approved_up_user(
    faker: Faker,
    repositories: Repositories,
    approved_up_user_email_address: str,
    approved_up_user_password_hash: bytes,
    generate_password_salt: bytes,
) -> User:
    user = User(
        email_address=approved_up_user_email_address,
        display_name=faker.name(),
        password_hash=bytes_to_str_base64(approved_up_user_password_hash),
        password_salt=bytes_to_str_base64(generate_password_salt),
        is_approved=True,
    )
    user = await repositories.user_repository.upsert(user)
    return user


@pytest.fixture
def approved_up_bearer_token(faker: Faker, approved_up_user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(approved_up_user)}"


@pytest.fixture
def totp_user_email_address(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def totp_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def totp_user_password_hash(totp_user_password: str, generate_password_salt: bytes) -> bytes:
    return _generate_hash(totp_user_password, generate_password_salt)


@pytest.fixture
async def totp_user(
    faker: Faker,
    repositories: Repositories,
    totp_user_email_address: str,
    totp_user_password_hash: bytes,
    generate_password_salt: bytes,
) -> User:
    user = User(
        email_address=totp_user_email_address,
        display_name=faker.name(),
        password_hash=bytes_to_str_base64(totp_user_password_hash),
        password_salt=bytes_to_str_base64(generate_password_salt),
        is_approved=True,
    )
    totp_bearer = f"Bearer {TokenVerifier.create_token(user)}"
    user = await repositories.user_repository.upsert(user)
    totp_response = await start_totp_registration(authorization=totp_bearer)
    verification_code = pyotp.TOTP(totp_response.generated_secret).now()
    await confirm_totp(TOTPVerificationRequest(totp_value=verification_code), totp_bearer)

    return await repositories.user_repository.fetch_user_by_email(user.email_address)


@pytest.fixture
def totp_bearer_token(faker: Faker, totp_user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(totp_user)}"
