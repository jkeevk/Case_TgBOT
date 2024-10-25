from random import choice
from PIL import Image, ImageDraw, ImageFont


# получаем случайную подпись
def get_random_caption(captions):
    with open(captions, encoding="utf-8") as f:
        random_caption = choice(f.readlines())
        return random_caption.rstrip()

# наносим подпись на изображение
def add_caption(photo, captions):
    image = Image.open(photo)
    drawer = ImageDraw.Draw(image)

    caption = get_random_caption(captions)

    image_width, image_height = image.size

    font_size = image_height // 12 # размер шрифта соотносим с размером изображения
    font = ImageFont.truetype("fonts/Lobster-Regular.ttf", font_size)

    bbox = drawer.textbbox((0, 0), caption, font=font)
    text_width = bbox[2] - bbox[0]  # Ширина
    text_height = bbox[3] - bbox[1]  # Высота

    x = (image_width - text_width) / 2  # Центрирование по X
    y = image_height - text_height - 20 # Отступ по Y

    drawer.text((x, y), caption, font=font, fill='black')
        
    image.save(photo)
    # image.show()


