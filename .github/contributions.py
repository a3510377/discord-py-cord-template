import base64
import os
import requests

TOKEN = os.getenv("TOKEN")
repository = os.getenv("repository", "a3510377/discord-py-cord-template")
repo_owner, repo_name = repository.split("/")

r = requests.get(
    f"https://api.github.com/repos/{repository}/contributors",
    headers={
        "Accept": "application/vnd.github+json",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    },
)

data = r.json()


def set_contributors_xy(
    index: int,
    max: int = 2,
    padding: int = 5,
    height_width: int = 64,
):
    x_index = index % max
    y_index = int(index / max)

    x = x_index * height_width + padding * (x_index + 1)
    y = y_index * height_width + padding * (y_index + 1)

    return f'x="{x}" y="{y}"'


def get_image_base64(url: str):
    response = requests.get(url)
    return (
        f"data:{response.headers['Content-Type']};"
        f"base64,{base64.b64encode(response.content)}"
    )


svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink">'
    "<style>a[href]{cursor:pointer;}</style>"
    + "".join(
        f'<a xlink:href="{da["html_url"]}" target="_blank" rel="nofollow sponsored">'
        f"<image {set_contributors_xy(index)} "
        f'width="64" height="64" xlink:href="{get_image_base64(da["avatar_url"])}" '
        'clip-path="inset(0% round 50%)"/>'
        "</a>"
        for index, da in enumerate(data)
    )
    + "</svg>"
)

with open("./.github/contributors.svg", "w", encoding="utf-8") as file:
    file.write(svg)
