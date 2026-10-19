from PIL import Image, ImageOps, ImageFilter
import argparse
import sys


# Для контуров палитра не важна — рисуем одним символом,
# но оставим возможность менять (например, "#" плотнее, "." легче).
CONTOUR_CHAR = "#"


def resize_image(image, new_width=100):
    """Меняем размер с сохранением пропорций.
    Коэффициент 0.5 компенсирует то, что символы в консоли выше, чем шире."""
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * 0.5)
    return image.resize((new_width, new_height), Image.LANCZOS)


def grayify(image):
    """В оттенки серого + автоконтраст + выделение границ."""
    gray = ImageOps.autocontrast(image.convert("L"))
    # FIND_EDGES: тёмные пиксели = границы, светлые = заливка/фон
    return gray.filter(ImageFilter.FIND_EDGES)


def pixels_to_contours(image, threshold=40):
    """Пиксели темнее порога — контур, остальные — пробел."""
    return "".join(
        CONTOUR_CHAR if p < threshold else " " for p in image.getdata()
    )


def image_to_ascii(image_path, width=100, threshold=40):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Ошибка открытия изображения: {e}", file=sys.stderr)
        return None

    image = resize_image(image, width)
    image = grayify(image)

    ascii_str = pixels_to_contours(image, threshold)

    img_width = image.width
    lines = []
    for i in range(0, len(ascii_str), img_width):
        line = ascii_str[i:i + img_width]
        # обрезаем правый хвост из пробелов
        lines.append(line.rstrip())

    # убираем пустые строки сверху и снизу
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Преобразование изображения в контурный ASCII-арт"
    )
    parser.add_argument("image", help="Путь к изображению")
    parser.add_argument(
        "-w", "--width", type=int, default=100,
        help="Ширина ASCII-арта в символах (по умолчанию: 100)"
    )
    parser.add_argument(
        "-t", "--threshold", type=int, default=40,
        help="Порог контура: меньше — только сильные границы, больше — жирнее (по умолчанию: 40)"
    )
    parser.add_argument(
        "-o", "--output", help="Файл для сохранения (по умолчанию вывод в консоль)"
    )
    args = parser.parse_args()

    ascii_art = image_to_ascii(args.image, args.width, args.threshold)
    if ascii_art is None:
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(ascii_art)
        print(f"Контурный ASCII-арт сохранён в {args.output}")
    else:
        print(ascii_art)


if __name__ == "__main__":
    main()