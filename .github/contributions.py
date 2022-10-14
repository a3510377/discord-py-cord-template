import base64
import os
import requests

TOKEN = os.getenv("TOKEN")
repository = os.getenv("repository", "a3510377/discord-py-cord-template")
repo_owner, repo_name = repository.split("/")


BOT = False
MAX = 15
PADDING = 5
HEIGHT_WIDTH = 64

r = requests.get(
    f"https://api.github.com/repos/{repository}/contributors",
    headers={
        "Accept": "application/vnd.github+json",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    },
)

data = r.json()

if not BOT:
    data = list(
        filter(
            lambda el: el["type"] != "Bot" and "actions-user" not in el["login"],
            data,
        )
    )


def make_svg():
    max_index = len(data)
    max_width = (max_width_len := min(max_index, MAX)) * HEIGHT_WIDTH
    max_height = (max_height_len := int(max_index / max_width_len)) * HEIGHT_WIDTH

    def get_image_base64(url: str):
        response = requests.get(url)
        return (
            f"data:{response.headers['Content-Type']};"
            f"base64,{base64.b64encode(response.content).decode('utf-8')}"
        )

    def set_contributors_xy(index: int):
        x_index = index % MAX
        y_index = int(index / MAX)

        x = x_index * HEIGHT_WIDTH + PADDING * (x_index + 1)
        y = y_index * HEIGHT_WIDTH + PADDING * (y_index + 1)

        return f'x="{x}" y="{y}"'

    return (
        # svg start
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{max_width + PADDING * (max_width_len + 1)}" '
        f'height="{max_height + PADDING * (max_height_len + 1)}" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">'
        # style
        "<style>a[href]{cursor:pointer;}</style>"
        + "".join(
            # a[href] start
            f'<a xlink:href="{da["html_url"]}" '
            'target="_blank" rel="nofollow sponsored">'
            # image
            f"<image {set_contributors_xy(index)} "
            f'width="64" height="64" xlink:href="{get_image_base64(da["avatar_url"])}" '
            'clip-path="inset(0% round 50%)"/>'
            # end
            "</a>"
            for index, da in enumerate(data)
        )
        # svg end
        + "</svg>"
    )


svg = make_svg()

with open("./.github/contributors.svg", "w", encoding="utf-8") as file:
    file.write(svg)
