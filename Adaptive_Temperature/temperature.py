from PIL import Image
from math import sqrt
from time import time
from threading import Thread


def adaptive_temp(src_img, resize_factor: int, rgb_mul_vals: tuple):
    start_time = time()

    # -----FUNCTIONS-----

    def adjust_temp(img, mid_point: int, rgb_mul: tuple):
        for x in range(img.width):
            for y in range(img.height):
                pix = list(img.getpixel((x, y)))
                pix_luminance = round(sqrt(0.299 * pix[0] ** 2 + 0.587 * pix[1] ** 2 + 0.114 * pix[2] ** 2))

                if pix_luminance < 0:
                    pix_luminance = 0

                elif pix_luminance > 255:
                    pix_luminance = 255

                new_pix = pix.copy()

                darkness_dif = mid_point - pix_luminance

                r_add = darkness_dif * rgb_mul[0]
                g_add = darkness_dif * rgb_mul[1]
                b_add = darkness_dif * rgb_mul[2]

                new_pix[0] += r_add
                new_pix[1] += g_add
                new_pix[2] += b_add

                if new_pix[0] < 0:
                    new_pix[0] = 0

                elif new_pix[0] > 255:
                    new_pix[0] = 255

                if new_pix[1] < 0:
                    new_pix[1] = 0

                elif new_pix[1] > 255:
                    new_pix[1] = 255

                if new_pix[2] < 0:
                    new_pix[2] = 0

                elif new_pix[2] > 255:
                    new_pix[2] = 255

                new_pix[0] = round(new_pix[0])
                new_pix[1] = round(new_pix[1])
                new_pix[2] = round(new_pix[2])

                img.putpixel((x, y), tuple(new_pix))

    def concat_img(img1, img2):
        concat = Image.new('RGB', (img1.width + img2.width, img1.height))
        concat.paste(img1, (0, 0))
        concat.paste(img2, (img1.width, 0))
        return concat

    def concat_imgs(img1, img2, img3, img4):
        concat = Image.new("RGB", (img1.width + img2.width, img1.height + img3.height))
        concat.paste(img1, (0, 0))
        concat.paste(img2, (img1.width, 0))
        concat.paste(img3, (0, img1.height))
        concat.paste(img4, (img1.width, img1.height))

        return concat

    # -----INPUT-----
    src_img = src_img.resize((src_img.width // resize_factor, src_img.height // resize_factor))
    img_pix = src_img.resize((1, 1)).getpixel((0, 0))
    middle_point = round(sqrt(0.299 * img_pix[0] ** 2 + 0.587 * img_pix[1] ** 2 + 0.114 * img_pix[2] ** 2))
    # print(middle_point)
    img_out1 = src_img.crop((0, 0, src_img.width // 2, src_img.height // 2))
    img_out2 = src_img.crop((src_img.width // 2, 0, src_img.width, src_img.height // 2))
    img_out3 = src_img.crop((0, src_img.height // 2, src_img.width // 2, src_img.height))
    img_out4 = src_img.crop((src_img.width // 2, src_img.height // 2, src_img.width, src_img.height))

    # -----MODIFICATION-----
    quad_1_thread = Thread(target=adjust_temp, args=(img_out1, middle_point, rgb_mul_vals,))
    quad_1_thread.start()

    quad_2_thread = Thread(target=adjust_temp, args=(img_out2, middle_point, rgb_mul_vals,))
    quad_2_thread.start()

    quad_3_thread = Thread(target=adjust_temp, args=(img_out3, middle_point, rgb_mul_vals,))
    quad_3_thread.start()

    quad_4_thread = Thread(target=adjust_temp, args=(img_out4, middle_point, rgb_mul_vals,))
    quad_4_thread.start()

    quad_1_thread.join()
    quad_2_thread.join()
    quad_3_thread.join()
    quad_4_thread.join()

    # print(f"Finished in {time() - start_time} seconds.")
    # concat_img(src_img, concat_imgs(img_out1, img_out2, img_out3, img_out4)).show()
    return concat_img(src_img, concat_imgs(img_out1, img_out2, img_out3, img_out4))

