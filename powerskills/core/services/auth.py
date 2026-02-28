"""认证服务"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from passlib.context import CryptContext
from jose import jwt, JWTError

from powerskills.core.config import settings
from powerskills.core.models.user import User
from powerskills.core.models.auth import Token, TokenPayload
from powerskills.core.models.common import UserRole
from powerskills.db.seekdb import seekdb_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务"""

    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: str, email: str, role: UserRole, permissions: list) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role.value,
            "permissions": permissions,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        payload = {"sub": user_id, "exp": expire, "type": "refresh"}
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_token(token: str) -> Optional[TokenPayload]:
        """解码令牌"""
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            return TokenPayload(
                sub=payload.get("sub"),
                email=payload.get("email"),
                role=UserRole(payload.get("role", "free")),
                permissions=payload.get("permissions", []),
            )
        except JWTError:
            return None

    async def register(self, email: str, password: str, name: Optional[str] = None) -> User:
        """用户注册"""
        # 检查邮箱是否已存在
        existing = await seekdb_client.query("users", filters={"email": email}, limit=1)
        if existing:
            raise ValueError("邮箱已被注册")

        user_id = f"usr_{uuid4().hex[:12]}"
        now = datetime.utcnow()

        user_data = {
            "user_id": user_id,
            "email": email,
            "password_hash": self.hash_password(password),
            "name": name or email.split("@")[0],
            "avatar_url": None,
            "role": UserRole.FREE.value,
            "created_at": now,
        }

        await seekdb_client.insert("users", user_data)

        return User(
            user_id=user_id,
            email=email,
            name=name,
            role=UserRole.FREE,
            created_at=now,
            updated_at=now,
        )

    async def login(self, email: str, password: str) -> Token:
        """用户登录"""
        users = await seekdb_client.query("users", filters={"email": email}, limit=1)

        if not users:
            raise ValueError("邮箱或密码错误")

        user = users[0]

        if not self.verify_password(password, user["password_hash"]):
            raise ValueError("邮箱或密码错误")

        # 更新最后登录时间
        await seekdb_client.update("users", user["user_id"], {"last_login_at": datetime.utcnow()})

        # 生成令牌
        role = UserRole(user.get("role", "free"))
        permissions = self._get_permissions(role)

        access_token = self.create_access_token(user["user_id"], email, role, permissions)
        refresh_token = self.create_refresh_token(user["user_id"])

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息"""
        user_data = await seekdb_client.get("users", user_id)
        if not user_data:
            return None

        return User(
            user_id=user_data["user_id"],
            email=user_data["email"],
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            role=UserRole(user_data.get("role", "free")),
            created_at=user_data.get("created_at", datetime.utcnow()),
            updated_at=user_data.get("updated_at", datetime.utcnow()),
            last_login_at=user_data.get("last_login_at"),
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """刷新访问令牌"""
        payload = self.decode_token(refresh_token)
        if not payload or payload.sub is None:
            raise ValueError("无效的刷新令牌")

        user = await self.get_user(payload.sub)
        if not user:
            raise ValueError("用户不存在")

        permissions = self._get_permissions(user.role)
        access_token = self.create_access_token(user.user_id, user.email, user.role, permissions)
        new_refresh_token = self.create_refresh_token(user.user_id)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def _get_permissions(role: UserRole) -> list:
        """获取角色权限"""
        permissions_map = {
            UserRole.FREE: ["skill:read"],
            UserRole.PERSONAL: ["skill:read", "skill:write", "orchestration:execute"],
            UserRole.ENTERPRISE: [
                "skill:read",
                "skill:write",
                "orchestration:execute",
                "analytics:read",
            ],
            UserRole.ADMIN: ["*"],
        }
        return permissions_map.get(role, [])


auth_service = AuthService()
