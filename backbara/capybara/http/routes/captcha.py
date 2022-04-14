# -*- coding: utf-8 -*-

"""
GNU AFFERO GENERAL PUBLIC LICENSE
Version 3, 19 November 2007
"""

import base64
import secrets

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from multicolorcaptcha import CaptchaGenerator
from io import BytesIO
from datetime import datetime, timedelta, timezone

from ...resources import Sessions
from ...limiter import LIMITER


generator = CaptchaGenerator(captcha_size_num=1)


class CaptchaResource(HTTPEndpoint):
    @LIMITER.limit("60/minute")
    async def get(self, request: Request) -> JSONResponse:
        captcha = generator.gen_captcha_image(
            margin=False,
            difficult_level=2
        )

        captcha_id = secrets.token_urlsafe()

        await Sessions.mongo.captcha.insert_one({
            "_id": captcha_id,
            "code": captcha.characters,
            "expire": datetime.now(timezone.utc) + timedelta(hours=1)
        })

        buffer = BytesIO()
        captcha.image.save(buffer, format="PNG")

        return JSONResponse({
            "imageB64": "data:image/png;base64," +
            base64.b64encode(buffer.getvalue()).decode(),
            "captchaId": captcha_id
        })
