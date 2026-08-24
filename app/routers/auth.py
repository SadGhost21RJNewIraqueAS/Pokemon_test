from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.database import get_db
from app.models.usuario import Administrador, Pesquisador, Treinador, Usuario
from app.schemas.usuario import (
    LoginRequest,
    RecuperarSenhaRequest,
    RedefinirSenhaConfirm,
    Token,
    TipoUsuario,
    UsuarioCreate,
    UsuarioRead,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])

_SUBCLASSE_POR_TIPO = {
    TipoUsuario.TREINADOR: Treinador,
    TipoUsuario.PESQUISADOR: Pesquisador,
    TipoUsuario.ADMINISTRADOR: Administrador,
}


@router.post("/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def register_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra o usuário e armazena somente o hash da senha.

    ``tipo_usuario`` decide qual subclasse será criada: Treinador,
    Pesquisador ou Administrador.
    """
    if db.query(Usuario).filter(Usuario.email == payload.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    Subclasse = _SUBCLASSE_POR_TIPO[payload.tipo_usuario]
    usuario = Subclasse(
        nome=payload.nome,
        email=payload.email,
        senha_hash=get_password_hash(payload.senha),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica o usuário e entrega um JWT para acessar as rotas protegidas.

    Por convenção do OAuth2, o formulário chama o campo de ``username``;
    nesta API ele deve receber o e-mail do usuário.
    """
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not usuario or not usuario.ativo or not usuario.autenticar(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )
    # O token não contém a senha: somente a identificação necessária para
    # recuperar o usuário nas próximas requisições.
    token = create_access_token(subject_email=usuario.email)
    return Token(access_token=token)


@router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
def solicitar_recuperacao_senha(payload: RecuperarSenhaRequest, db: Session = Depends(get_db)):
    """Caso de uso Recuperar Senha, delegado à API de Autenticação externa."""
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if usuario:
        usuario.recuperar_senha()
    return {"message": "Se o e-mail existir, um link de recuperação será enviado."}


@router.post("/password-reset", status_code=status.HTTP_200_OK)
def confirmar_redefinicao_senha(payload: RedefinirSenhaConfirm, db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Integração com API de Autenticação não implementada")
