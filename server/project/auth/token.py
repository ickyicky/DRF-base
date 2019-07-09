from calendar import timegm

from django.conf import settings
from rest_framework import status, exceptions

from jose import JOSEError, jwt
from project.utils import now, datetime, make_naive_utc


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
            raise InvalidToken("Cannot create token without defined type.")

        if self.lifetime is None:
            raise InvalidToken("Cannot create token without defined lifetime.")

        self.token = token
        self.current_time = now()

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
        """
        Addictional verification makes sure that user didn't change password
        since this token was created. You can disable this option by setting
        JWT_AUTH.LOGOUT_AFTER_PASS_CHANGE to False
        """
        if (
            not settings.JWT_AUTH.get("LOGOUT_AFTER_PASS_CHANGE", True)
            or not valid_time
        ):
            return

        valid_time = make_naive_utc(valid_time.replace(microsecond=0))

        try:
            _claim_value = self.payload["_" + claim]
        except KeyError:
            raise InvalidToken(f"Token nie ma czasu użyteczności '{claim}'.")

        _claim_time = datetime.utcfromtimestamp(_claim_value)

        if _claim_time <= valid_time:
            raise InvalidToken(f"Czas '{claim}' wygasł.")

    def verify_token_type(self):
        """
        Ensures that the token type claim is present and has the correct value.
        """
        try:
            token_type = self.payload[settings.JWT_AUTH["TOKEN_TYPE_CLAIM"]]
        except KeyError:
            raise InvalidToken("Token has no defined type.")

        if self.token_type != token_type:
            raise InvalidToken("Token has incorrect type.")

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
            current_time = self.current_time

        current_time = make_naive_utc(current_time)

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise InvalidToken(f"Token nie ma czasu użyteczności '{claim}'.")

        claim_time = datetime.utcfromtimestamp(claim_value)

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
