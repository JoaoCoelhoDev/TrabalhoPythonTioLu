# Joao Vitor Coelho de Souza
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ─── Hash de senha ────────────────────────────────────────────

def get_password_hash(password: str) -> str:
    """Gera hash bcrypt da senha"""
    salt   = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

# ─── JWT Token ────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Gera um token JWT com os dados do usuário"""
    to_encode = data.copy()
    expire    = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decodifica e valida o token JWT"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

# ─── Dependências de autenticação ─────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Retorna o usuário logado a partir do token"""
    return decode_token(token)

def require_grupo(grupo: int):
    """Verifica se o usuário pertence ao grupo exigido"""
    def check(current_user: dict = Depends(get_current_user)):
        if current_user.get("grupo") != grupo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Apenas grupo {grupo} pode realizar esta operação."
            )
        return current_user
    return check
