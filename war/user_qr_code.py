import qrcode
import os
from django.conf import settings
from cryptography.fernet import Fernet
from django.conf import settings
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from .models import UserData

BASE_DIR = settings.BASE_DIR
get_dir = lambda dir: os.path.join(BASE_DIR, dir)

def encrypt(data: str) -> str:
    try:
        data = data.encode("utf-8")
        f = Fernet(settings.ENCRYPTION_KEY.encode("utf-8"))
        return f.encrypt(data).decode("utf-8")
    except Exception as ex:
        print(ex)
        return "invalid"

def decrypt(data: str) -> str:
    try:
        data = data.encode("utf-8")
        f = Fernet(settings.ENCRYPTION_KEY.encode("utf-8"))
        return f.decrypt(data).decode("utf-8")
    except Exception:
        return "invalid"

def get_qr_code(text: str) -> bytes: 
    # https://www.geeksforgeeks.org/how-to-generate-qr-codes-with-a-custom-logo-using-python/
    Logo_link = get_dir('assets/mekbat.jpg')
    logo = Image.open(Logo_link)
    basewidth = 100
    # adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.LANCZOS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    # generating QR code
    QRcode.add_data(text)
    QRcode.make()
    QRcolor = 'Black'
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')
    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
        (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    # save the QR code generated
    del logo
    return QRimg

def write_text(draw: ImageDraw, rectang, text, position, size, align="left", fill="#000000", bold=False, align_right=100):
    """
    pos = (x, y)
    size = text size in pixel
    align = 'left', 'center', 'right
    """
    w, h = rectang

    # Text Font
    font =  lambda x: ImageFont.truetype(get_dir('assets/Poppins-Regular.ttf'), round(x * 4.1))
    font_bold = lambda x: ImageFont.truetype(get_dir('assets/Poppins-Bold.ttf'), round(x * 4.1))
    txt = text
    txtf = font_bold(size) if (bold == True) else font(size)

    # Text align
    x, y = position
    txt_posy = y
    txt_length = txtf.getlength(text)
    if align == "left":
        txt_posx = x
    elif align == "center":
        txt_posx = (w / 2) - (txt_length / 2)
    elif align == "right":
        txt_posx = align_right - txt_length

    draw.text(
        (txt_posx, txt_posy),
        txt, fill=fill, font=txtf
    )

def get_event_ticket(enc: str, userdata: UserData) -> bytes:
    w, h = 1050, 1350

    # create rectangle
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (w, h)], fill="#FFFFFF")

    # write text
    write_text(draw, (w, h), "Laboratorium Mekanika Batuan", (0, 100), size=12, align="center", bold=True)
    write_text(draw, (w, h), "UPN \"Veteran\" Yogyakarta", (0, 160), size=11, align="center", bold=True)
    write_text(draw, (w, h), userdata.name, (0, 995), size=10, align="center", bold=True)
    write_text(draw, (w, h), str(userdata.nim), (0, 1045), size=10, align="center", bold=True)
    if userdata.schedule:
        write_text(draw, (w, h), f'Kelompok {str(userdata.schedule.group_number)}', (60, 1145), size=8, align="left", bold=False)
        write_text(draw, (w, h), userdata.schedule.name, (60, 1190), size=8, align="left", bold=False)
    write_text(draw, (w, h), f'#{str(userdata.pk).zfill(4)}', (0, 1175), size=8, align="right", align_right=988, bold=False)

    # paste qr code
    qr = get_qr_code(enc)
    qr = qr.resize((716, 716), Image.LANCZOS)
    img.paste(qr, (166, 270))

    # add line
    with Image.open(get_dir('assets/line.jpg')) as line:
        img.paste(line, (60, 977))
        img.paste(line, (60, 1112))

    s = BytesIO()
    img.save(s, "jpeg")
    img.close()
    return s.getvalue()