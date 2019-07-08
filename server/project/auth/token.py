from calendar import timegm
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.utils.timezone import is_naive, make_aware
from rest_framework import exceptions, status

from project.utils import now

from jose import JOSEError, jwt


def make_utc(datetime_):
    if settings.USE_TZ and is_naive(datetime_):
        return make_aware(datetime_, timezone=pytz.timezone(settings.TIME_ZONE))

    return datetime_


class InvalidToken(exceptions.AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail_dict = {}

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail_dict["detail"] = detail

        if code is not None:
            self.detail_dict["code"] = code

        super(InvalidToken, self).__init__(self.detail_dict)


class Token:
    token_type = None
    lifetime = None

    def __init__(self, token=None, verify=True):
        if self.token_type is None:
            raise InvalidToken("Nie można utworzyc tokenu bez zdefiniowanego typu.")

        if self.lifetime is None:
            raise InvalidToken("CNie można utworzyć tokenu bez zdefiniowanego czasu.")

        self.token = token
        self.current_time = datetime.utcnow()

        if token is not None:
            self.payload = self.decode()

            if verify:
                self.verify()
        else:
            self.payload = {settings.JWT_AUTH["TOKEN_TYPE_CLAIM"]: self.token_type}
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)

    def encode(self):
        token = jwt.encode(
            self.payload,
            settings.JWT_AUTH["SIGNING_KEY"],
            algorithm=settings.JWT_AUTH["ALGORITHM"],
        )
        return token

    def decode(self):
        try:
            return jwt.decode(
                self.token,
                settings.JWT_AUTH["SIGNING_KEY"],
                algorithms=[settings.JWT_AUTH["ALGORITHM"]],
            )
        except JOSEError:
            raise InvalidToken("Niewłaściwy lub nieaktualny token")

    def verify(self, valid_time=None):
        """
        Performs additional validation steps.
        """

        if valid_time:
            return self.additional_verification(valid_time)

        self.check_exp()
        self.verify_token_type()

    def additional_verification(self, valid_time, claim="exp"):
        if not valid_time:
            return

        try:
            _claim_value = self.payload["_" + claim]
        except KeyError:
            raise InvalidToken(f"Token nie ma czasu użyteczności '{claim}'.")

        _claim_time = make_utc(datetime.utcfromtimestamp(_claim_value))
        print(_claim_value)
        print(int(valid_time.timestamp()))
        #
        # if _claim_time < valid_time:
        #     raise InvalidToken(f"Czas '{claim}' wygasł.")

        if _claim_value < int(valid_time.timestamp()):
            raise InvalidToken(f"Czas '{claim}' wygasł.")

    def verify_token_type(self):
        """
        Ensures that the token type claim is present and has the correct value.
        """
        try:
            token_type = self.payload[settings.JWT_AUTH["TOKEN_TYPE_CLAIM"]]
        except KeyError:
            raise InvalidToken("Token nie ma zdefiniowanego typu.")

        if self.token_type != token_type:
            raise InvalidToken("Token ma zdefiniowany niepoprawny typ.")

    def set_exp(self, claim="exp", from_time=None, lifetime=None):
        """
        Updates the expiration time of a token.
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = timegm((from_time + lifetime).utctimetuple())
        self.payload["_" + claim] = timegm((from_time).utctimetuple())

    def check_exp(self, claim="exp", current_time=None):
        """
        Checks whether a timestamp value in the given claim has passed.
        """
        if current_time is None:
            current_time = make_utc(self.current_time)

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise InvalidToken(f"Token nie ma czasu użyteczności '{claim}'.")

        claim_time = make_utc(datetime.utcfromtimestamp(claim_value))

        if claim_time <= current_time:
            raise InvalidToken(f"Czas '{claim}' wygasł.")

    @classmethod
    def get_token_for_user(cls, user, remember_me=False):
        """
        Returns an authorization token for the given user.
        """
        user_id = getattr(user, settings.JWT_AUTH["USER_ID_FIELD"])

        token = cls()
        token.payload[settings.JWT_AUTH["USER_ID_CLAIM"]] = user_id

        if remember_me:
            token.set_exp(
                lifetime=settings.JWT_AUTH["REMEMBER_ME_REFRESH_TOKEN_LIFETIME"]
            )

        return token


class RefreshToken(Token):
    token_type = "refresh"
    lifetime = settings.JWT_AUTH["REFRESH_TOKEN_LIFETIME"]

    @property
    def access_token(self):
        """
        Returns an access token created from this refresh token.
        """
        access = AccessToken()
        access.set_exp(from_time=self.current_time)

        for claim, value in self.payload.items():
            if claim in [settings.JWT_AUTH["TOKEN_TYPE_CLAIM"], "exp"]:
                continue
            access.payload[claim] = value

        return access


class AccessToken(Token):
    token_type = "access"
    lifetime = settings.JWT_AUTH["ACCESS_TOKEN_LIFETIME"]


class PassResetToken(Token):
    token_type = "pass_reset"
    lifetime = settings.JWT_AUTH["PASS_RESET_TOKEN_LIFETIME"]
