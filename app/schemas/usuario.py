from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class TipoUsuario(str, Enum):
    """Espelha as subclasses concretas de Usuario no diagrama."""
    TREINADOR = "treinador"
    PESQUISADOR = "pesquisador"
    ADMINISTRADOR = "administrador"


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str
    tipo_usuario: TipoUsuario


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_usuario: str
    ativo: bool
    criado_em: datetime


# ---- Autenticar Usuario ----
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Recuperar Senha ----
class RecuperarSenhaRequest(BaseModel):
    email: EmailStr


class RedefinirSenhaConfirm(BaseModel):
    token: str
    nova_senha: str
