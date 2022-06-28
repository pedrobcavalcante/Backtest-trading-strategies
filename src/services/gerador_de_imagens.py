# %%
from PIL import Image, ImageFont, ImageDraw
import os, datetime


# %%
fontName = os.path.join(
    "..", "..", "assets", "fonts", "Lora", "static", "Lora-Regular.ttf"
)
fontTitle = ImageFont.truetype(fontName, 40)
fontSubtitle = ImageFont.truetype(fontName, 30)
path = os.path.join("..", "..", "assets", "background img.jpg")
img = Image.open(path)
I1 = ImageDraw.Draw(img)


# %%
def GerarCarteiraDaSemana(texts: list, saveImg: bool = True):

    W, H = img.size
    header = "Carteira da semana:"
    w, h = I1.textsize(header, fontTitle)
    I1.text(((W - w) / 2, 20), header, fill=(255, 255, 255), font=fontTitle)
    lastPad = 100
    for text in texts:
        w, h = I1.textsize(text, fontSubtitle)
        I1.text(((W - w) / 2, lastPad), text, fill=(255, 255, 255), font=fontSubtitle)
        lastPad += 60
    if saveImg:
        img.save(
            os.path.join(
                "..",
                "..",
                "assets",
                "generated",
                "carteira_semanal_{0}.jpg".format(datetime.datetime.now().date()),
            )
        )
    else:
        img.show()


# %%
def GerarDadosTecnicosDoAtivo(ativo: str, texts: list, saveImg: bool = True):
    header = ativo + ":"
    I1.text((20, 20), header, fill=(255, 255, 255), font=fontTitle)
    lastPad = 100
    for text in texts:
        w, h = I1.textsize(text, fontSubtitle)
        I1.text((40, lastPad), text, fill=(255, 255, 255), font=fontSubtitle)
        lastPad += 60
    if saveImg:
        img.save(
            os.path.join(
                "..",
                "..",
                "assets",
                "generated",
                "carteira_semanal_{0}.jpg".format(datetime.datetime.now().date()),
            )
        )
    else:
        img.show()
