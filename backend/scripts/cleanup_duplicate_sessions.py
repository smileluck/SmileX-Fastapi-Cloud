"""一次性清理同 user_id+tenant_id 下重复 (ip, user_agent) 的旧 session。

背景：登录接口在 `BaseUserManager.create_token` 写入新 session 前会清理同 IP+UA
的旧 session（防止反复登录堆积）。本脚本用于一次性清理改造前已堆积的历史
session，让在线用户列表立即去重。

用法：
    cd backend && python -m scripts.cleanup_duplicate_sessions
"""
import asyncio
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.redis import get_redis_util
from core.redis.redis_pool import RedisPool


def _decode(v) -> str:
    return v.decode("utf-8") if isinstance(v, bytes) else v


async def main() -> None:
    await RedisPool.init_pool()
    ru = get_redis_util()
    prefix = settings.JWT.SESSION_PREFIX
    total_removed = 0
    async for key in ru.scan_iter(match=f"{prefix}*"):
        all_fields = await ru.hgetall(key)
        if not all_fields:
            continue

        # 按 (ip, ua) 分组，保留每组 login_time 最大的一条
        groups: dict[tuple[str, str], tuple[str, str]] = {}
        for sid_raw, meta_raw in all_fields.items():
            sid = _decode(sid_raw)
            try:
                meta = json.loads(_decode(meta_raw))
            except (json.JSONDecodeError, TypeError):
                continue
            fingerprint = (meta.get("ip", ""), meta.get("user_agent", ""))
            login_time = meta.get("login_time", "")
            prev_sid, prev_time = groups.get(fingerprint, ("", ""))
            if not prev_sid or login_time > prev_time:
                groups[fingerprint] = (sid, login_time)

        keep_sids = {sid for sid, _ in groups.values()}
        stale = [sid for sid in map(_decode, all_fields.keys()) if sid not in keep_sids]
        if stale:
            await ru.hdel(key, *stale)
            total_removed += len(stale)
            print(f"  {_decode(key)}: removed {len(stale)} duplicate session(s)")
    print(f"Done. Total removed: {total_removed}")


if __name__ == "__main__":
    asyncio.run(main())
