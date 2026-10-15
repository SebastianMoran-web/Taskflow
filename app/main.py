from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str


post = Post(
    title="Mi primer post",
    content="Contenido del post"
)

print(post)