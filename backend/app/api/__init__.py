"""API 路由集合 - 透传模块，便于 from app.api import contents, authors, stats, sync"""
# 显式 import 各子模块以触发其副作用（注册 router 对象到模块命名空间）
from app.api import contents  # noqa: F401
from app.api import authors  # noqa: F401
from app.api import stats  # noqa: F401
from app.api import sync  # noqa: F401
from app.api import md  # noqa: F401
