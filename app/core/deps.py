from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.usuario import Administrador, Pesquisador, Treinador, Usuario

# Lê o token enviado no cabeçalho: Authorization: Bearer <token>.
# O Swagger usa tokenUrl para exibir o fluxo de login corretamente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """Valida o JWT e retorna o usuário associado a ele.

    A consulta por ``Usuario`` retorna a instância já na subclasse correta
    (Treinador, Pesquisador ou Administrador) graças ao carregamento
    polimórfico do SQLAlchemy.

    Isso permite que as funções de permissão abaixo usem ``isinstance``.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.email == payload["sub"]).first()
    if usuario is None or not usuario.ativo:
        raise credentials_exception
    return usuario


def require_treinador(usuario: Usuario = Depends(get_current_user)) -> Treinador:
    """Permite acesso apenas a usuários do tipo Treinador."""
    if not isinstance(usuario, Treinador):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a Treinadores")
    return usuario


def require_pesquisador(usuario: Usuario = Depends(get_current_user)) -> Pesquisador:
    """Permite acesso apenas a usuários do tipo Pesquisador."""
    if not isinstance(usuario, Pesquisador):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a Pesquisadores")
    return usuario


def require_administrador(usuario: Usuario = Depends(get_current_user)) -> Administrador:
    """Permite acesso apenas a usuários do tipo Administrador."""
    if not isinstance(usuario, Administrador):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a Administradores")
    return usuario


def require_pesquisador_ou_administrador(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if not isinstance(usuario, (Pesquisador, Administrador)):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Acesso restrito a Pesquisadores ou Administradores"
        )
    return usuario


def require_treinador_ou_pesquisador(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    if not isinstance(usuario, (Treinador, Pesquisador)):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Acesso restrito a Treinadores ou Pesquisadores"
        )
    return usuario
