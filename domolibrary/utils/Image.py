# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/Image.ipynb.

# %% auto 0
__all__ = ['domo_default_img', 'isBase64', 'handle_string_to_bytes_and_decode', 'handle_string_to_bytes_and_encode', 'to_bytes',
           'crop_square', 'are_same_image']

# %% ../../nbs/utils/Image.ipynb 2
from PIL.Image import Image

# %% ../../nbs/utils/Image.ipynb 3
from typing import Union
import types
import PIL
import numpy as np

import os
import io
import base64

from nbdev.showdoc import patch_to

# %% ../../nbs/utils/Image.ipynb 4
def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False


def handle_string_to_bytes_and_decode(data: Union[str, bytes]):

    if isinstance(data, str):
        data = bytes(data)

    if isBase64(data):
        data = base64.b64decode(data)

    return data


def handle_string_to_bytes_and_encode(data: Union[str, bytes]):

    if isinstance(data, str):
        data = bytes(data)

    if not isBase64(data):
        data = base64.b64encode(data)

    return data

# %% ../../nbs/utils/Image.ipynb 5
def to_bytes(self) -> bytes:
    byte_arr = io.BytesIO()

    if not hasattr(self, "area"):
        self.area = self

    self.area.save(byte_arr, format=self.format)

    self.data = byte_arr.getvalue()

    return self.data


def crop_square(self):

    width, height = self.size  # Get dimensions

    new_edge = min(width, height)

    left = (width - new_edge) / 2
    top = (height - new_edge) / 2
    right = (width + new_edge) / 2
    bottom = (height + new_edge) / 2

    # Crop the center of the image
    self.area = self.crop((left, top, right, bottom))

    self.to_bytes()

    return self.area


@patch_to(Image, cls_method=True)
def from_image_file(cls, image_path: str) -> Image:
    if not os.path.exists(image_path):
        raise FileNotFoundError(image_path)

    with open(image_path, "rb") as file:
        data = file.read()

    data = handle_string_to_bytes_and_decode(data)

    im = PIL.Image.open(io.BytesIO(data))

    im.to_bytes = types.MethodType(to_bytes, im)
    im.crop_square = types.MethodType(crop_square, im)

    return im

# %% ../../nbs/utils/Image.ipynb 8
@patch_to(Image, cls_method=True)
def from_bytestr(cls, data: Union[str, bytes]) -> Image:

    data = handle_string_to_bytes_and_decode(data)

    im = PIL.Image.open(io.BytesIO(data))

    im.to_bytes = types.MethodType(to_bytes, im)
    im.crop_square = types.MethodType(crop_square, im)

    return im

# %% ../../nbs/utils/Image.ipynb 11
default_img_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01,\x00\x00\x01,\x08\x06\x00\x00\x00y}\x8eu\x00\x00\x0eUIDATx\x9c\xed\xdd\xe9r\xda\xd8\x16@\xe1-\x81\x84\x18M\x02\xb1\x93T\xbf\xff\xa3\xb9\xc1\x063\nM\xe8\xe8\xfe\xe86\x95\xdc\x0c\x9d86\xe7\xec\xa3\xf5UQvuW%;\x12Z\x80&\x82\xcdf\xd3\x08\x00(\x10\xda\x1e\x00\x00~\x15\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0\x06\xc1\x02\xa0F\xd7\xf6\x00\xd0\xabi\x1a1\xc6\x881F\x9a\xa6\x91\xa6iDD\xc4\x18#""a\xf8\xcf\xeba\x10\x04\x12\x04\x81\x84a(a\x18J\x10\x04\xd6f\x86n\x04\x0b\xbf\xa4\xaek\xc9\xf3\\\xf2<\x97\xaa\xaa\xa4,K\xa9\xaa\xeaE\x7fV\x14E\x12\xc7\xb1DQ$I\x92H\x92$\xd2\xe9t^yb\xf8\x88`\xe1\x87\xb2,\x93\xd3\xe9$Y\x96IQ\x14\xaf\xf6\xe7VU\xf5M\xecz\xbd\x9e\xf4\xfb}\x19\x0c\x06\xd2\xef\xf7_\xed\xef\x82_\x82\xcdf\xd3\xd8\x1e\x02\xee\xa8\xaaJ\x0e\x87\x83\x1c\x8f\xc7\x17\xbf\x83\xfaSQ\x14\xc9h4\x92\xf1x,Q\x14Y\x99\x01n"X\x10\x11\x914Me\xbb\xddJ\x9e\xe7\xb6G\xf9J\x92$2\x9dNe8\x1c\xda\x1e\x05\x0e X-w8\x1cd\xbb\xddJY\x96\xb6G\xf9\xa98\x8ee:\x9d\xcax<\xb6=\n,"X-\x95\xa6\xa9\xac\xd7kk\x1f\xfb^*\x8a"\x99\xcdf\xbc\xe3j)\x82\xd52\xe7\xf3Y\x1e\x1f\x1f\xe5t:\xd9\x1e\xe5\x8f\x0c\x06\x03\xf9\xf0\xe1\x83t\xbb\x1c7j\x13\x82\xd5\x12M\xd3\xc8f\xb3\x91\xedv{9_J\xbb \x08d:\x9d\xca\xbbw\xef8\xb7\xab%\x08V\x0bTU%\xcb\xe5\xf2UOMpI\xaf\xd7\x93\xbb\xbb;\x8e(\xb6\x00\xc1\xf2\\\x9a\xa6\xf2\xf0\xf0p9\xfb\xdcWa\x18\xca\xed\xed-\xfb\xb6<G\xb0<\xb6^\xafe\xbb\xdd\xda\x1e\xe3\xaa\xa6\xd3\xa9\xccf3\xdbc\xe0\x8d\xb0\xc7\xd2CM\xd3\xc8\xc3\xc3\x83\x1c\x8fG\xdb\xa3\\\xddv\xbb\x95\xf3\xf9,\xb7\xb7\xb7\xec\xd7\xf2\x10\xc1\xf2\x8c1F\x16\x8b\x85dYf{\x14k\x8e\xc7\xa3\xd4u-\x1f?~\xbc\\\x80\r?\xb06=b\x8c\x91\xfb\xfb\xfbV\xc7\xeaY\x96er\x7f\x7f\xef\xfd\xbe\xbb\xb6!X\x9ex\x8e\x95\xafG\x02_\xa2(\n\xa2\xe5\x19\x82\xe5\x81\xa6i\xbc>m\xe1O\x14E!\xcb\xe5\xd2\x9bs\xcf\xda\x8e`y\xc0\x873\xd7\xdf\xd2\xe9t\x92\xc7\xc7G\xdbc\xe0\x15\x10,\xe5\x9e\x9e\x9e\xe4p8\xd8\x1e\xc3y\x87\xc3A\x9e\x9e\x9el\x8f\x81?D\xb0\x14\xcb\xf3\\6\x9b\x8d\xed1\xd4\xd8l6\xce\xdd>\x07\xbf\x87`)U\xd7\xb5,\x16\x0b\xdbc\xa8\xb3X,\xa4\xaek\xdbc\xe0\x85\x08\x96R\xcb\xe5\x92\r\xef\x05\xea\xba\x96\xe5ri{\x0c\xbc\x10\xc1Rh\xbf\xdfs\xae\xd5\x1f\xc8\xb2L\xf6\xfb\xbd\xed1\xf0\x02\x04K\x19c\x8c\xac\xd7k\xdbc\xa8\xb7^\xaf9?K!\x82\xa5\xccj\xb5bC{\x05\xc6\x18Y\xadV\xb6\xc7\xc0o"X\x8a\xe4y\xce)\x0c\xaf\xe8p8p\xd4P\x19\x82\xa5\x08\x1f\x05_\x1f\xcbT\x17\x82\xa5\xc4\xf3\xb7.\xe3u\xb1\\u!XJp\x82\xe8\xdba\xd9\xeaA\xb0\x14(\x8a\x82k\x05\xdf\xd0\xe9t\xe2\xc2q%\x08\x96\x02\xbb\xdd\xce\xf6\x08\xdec\x19\xeb@\xb0\x1cg\x8c\x914Mm\x8f\xe1\xbd4M9]D\x01\x82\xe586\xa4\xeb\xe0\x85A\x07\x82\xe58\xce\xbb\xba\x1e\x96\xb5\xfb\x08\x96\xc3\xea\xba\xe6\x9a\xc1+\xca\xb2\x8c\x0b\xca\x1dG\xb0\x1cF\xac\xae\x8fe\xee6\x82\xe506\x9e\xebc\x99\xbb\x8d`9\x8cs\xaf\xae\x8fe\xee6\x82\xe5\xa8\xaa\xaa\xe4|>\xdb\x1e\xa3u\xce\xe7\xb3TUe{\x0c\xfc\x00\xc1r\x14g^\xdb\xc3\xb2w\x17\xc1r\x14\xaf\xf2\xf6\xb0\xec\xddE\xb0\x1c\xc5Fc\x0f\xcb\xde]\x04\xcbQeY\xda\x1e\xa1\xb5X\xf6\xee"X\x8e\xe2U\xde\x1e\x96\xbd\xbb\x08\x96\x83\x9a\xa6\xe1\xfaA\x8b\x8c1\xd24\x8d\xed1\xf0\x1d\x04\xcbA\xc4\xca>\xd6\x81\x9b\x08\x96\x83xu\xb7\x8fu\xe0&\x82\xe5 .\xc0\xb5\x8fu\xe0&\x82\xe5 ^\xdd\xedc\x1d\xb8\x89`9(\x08\x02\xdb#\xb4\x1e\xeb\xc0M\x04\xcbAl,\xf6\xb1\x0e\xdcD\xb0\x1c\x14\x86\xac\x16\xdbX\x07nb\xad8\x88Ww\xfbX\x07n"X\x0e\xeat:\xb6Gh=\xd6\x81\x9b\x08\x96\xa3\xba\xdd\xae\xed\x11Z\x8be\xef.\x82\xe5\xa88\x8em\x8f\xd0Z,{w\x11,G\xb1\xd1\xd8\xc3\xb2w\x17\xc1rT\x14E\xb6Gh-\x96\xbd\xbb\x08\x96\xa3\xd8h\xeca\xd9\xbb\x8b`9*I\x12\x0e\xad[\x10\x04\x81$Ib{\x0c\xfc\x00\xc1r\x14\x1b\x8e\x1d\xbcP\xb8\x8d`9\xac\xdf\xef\xdb\x1e\xa1uX\xe6n#X\x0ec\xe3\xb9>\x96\xb9\xdb\x08\x96\xc3\x92$\xe1$\xc6+\xeav\xbb|\x0cw\x1c\xc1r\xdch4\xb2=Bk\xb0\xac\xddG\xb0\x1c7\x1e\x8fm\x8f\xd0\x1a,k\xf7\x11,\xc7\xc5q\xcc\x99\xd7W\xc0r\xd6\x81`)0\x99Ll\x8f\xe0=\x96\xb1\x0e\x04K\x81\xc9d\xc2\xedN\xdeP\xa7\xd3!XJ\x10,\x05\x82 \x90\xe9tj{\x0coM\xa7SN\x16U\x82`)1\x99L\xb8m\xef\x1b\x08\xc3\x90wW\x8a\xb0\x05(\x11\x86\xa1\xdc\xdc\xdc\xd8\x1e\xc3;777\xbc\x10(\xc2\x9aRd:\x9dr\'\x81W\x14E\x11\x1f\xb5\x95!X\x8a\x84a(\xb3\xd9\xcc\xf6\x18\xde\x98\xcdf\xbc\xbbR\x86\xb5\xa5\xccp8\x94\xe1ph{\x0c\xf5X\x8e:\x11,\x85\xe6\xf39\xef\x0c\xfe@\x18\x862\x9f\xcfm\x8f\x81\x17\xe0Y\xafP\xb7\xdbe\x83\xfb\x03\xf3\xf9\x9c\x8b\xca\x95"XJ\x8d\xc7c\xae}{\x01\x96\x9bn\x04K\xb1\xf9|\xce\xf5o\xbf!\x8ec\xde\x99*G\xb0\x14\x0b\xc3P\xee\xee\xee\xd8\x9f\xf5\x0bXV~`\xed)\x17\xc7\xb1|\xfa\xf4\x89KK~"\x08\x02\xf9\xf4\xe9\x13\xefF=@\xb0<\x90$\x89\xdc\xdd\xdd\xd9\x1e\xc3Ywww\xdcI\xd4\x13\x04\xcb\x13\xc3\xe1Pnoom\x8f\xe1\x9c\xdb\xdb[\xce\xb7\xf2\x08\xc1\xf2\xc8x<&Z_\xb8\xbd\xbd\xe5\x88\xa0g8\x19\xc53\xe3\xf1X:\x9d\x8e,\x97K1\xc6\xd8\x1e\xc7\x8a\xe7\x1d\xec\x83\xc1\xc0\xf6(xe\xbc\xc3\xf2\xd0`0\x90\xcf\x9f?\xb7\xf2\x88X\x18\x86\xf2\xf9\xf3gb\xe5\xa9\xf6=\xa3[\xa2\xd7\xeb\xc9_\x7f\xfd%\xbd^\xcf\xf6(W\xd3\xc6\x7fs\xdb\x04\x9b\xcd\xa6\xb1=\x04\xdeN\xd34\xb2^\xafe\xb7\xdb\xd9\x1e\xe5M\xdd\xdc\xdc\xc8l6\xe3\xf4\x0e\xcf\x11\xac\x96H\xd3T\x1e\x1e\x1e\xbc\xdb\xaf\x15\x86!G\x02[\x84`\xb5\x881F\xd6\xeb\xb5\xec\xf7{\xdb\xa3\xbc\x8a\xc9d\xc2=\xadZ\x86`\xb5P\x9e\xe7\xf2\xf8\xf8(eY\xda\x1e\xe5E\xe28\x96\x0f\x1f>p2h\x0b\x11\xac\x16\xdb\xef\xf7\xb2\xddn\xa5\xaa*\xdb\xa3\xfc\x92\xe7[\x1a\xf3\xa5\x11\xedE\xb0 \xc7\xe3Q\xb6\xdb\xad\x14Ea{\x94\xef\xea\xf5z2\x9dNe4\x1a\xd9\x1e\x05\x96\x11,\\\x9cN\'9\x1c\x0e\x92\xa6\xa94\x8d\xdd\xa7E\x10\x042\x1c\x0ee<\x1esN\x15.\x08\x16\xbea\x8c\x914Me\xbf\xdfK\x9e\xe7W\xfd\xbb\x93$\x91\xc9d"\xc3\xe1\x90\x9d\xe9\xf8\x06\xc1\xc2O\x19c$\xcfs9\x9dN\x92e\xd9\xab\xef\xa8\x8f\xe3X\xfa\xfd\xbe\x0c\x06\x03I\x92\x84H\xe1\xa7\x08\x16~\x8b1F\xaa\xaa\x92\xb2,\xe5|>_~\x1ac.\x8f\xe7\x8f\x93A\x10H\x18\x86\x97G\xb7\xdb\x958\x8e/?\xa3("P\xf8-\\\xfc\x8c\xdf\x12\x86\xa1\xf4z=.\x7f\x81\x15\xbc\xbc\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83`\x01P\x83\xef%\xc4\x0f5M#u]\xcb\xf9|\x96\xba\xae\xa5\xaek1\xc6|\xf5{\xd34b\x8c\x11\x11\xf9\xe6\xe7\xf3\x97\xa4~\xf9\xf3\xf9\xcbU;\x9d\x8et:\x9d\xaf~\xefv\xbb\xd2\xe9t$\x08\x02\x0b\xffZh@\xb0Z\xee\xcboo~~TUu\xf9\xdd\x86n\xb7+\xddnW\xa2(\xba\xfc\xfe\xe5\xb7F\xa3\xbdX\xfb-q>\x9f\xa5(\x8a\xcb\xd7\xcc??\x9e\xbfV\xde%\xcf\xb1\xcc\xf3\xfc\x9b\xff\x17\x04\x81\xc4q|yDQ$\xbd^\x8f\x90\xb5\x04k\xd9CUUI\x9e\xe7R\x96\xa5\xe4y.EQ8\x19\xa6\x97h\x9aF\x8a\xa2\x90\xa2(\xbe\xfa\xefA\x10H\xaf\xd7\x93$I$\x8ecI\x92D\xa2(\xb24%\xde\n\xc1R\xce\x18#Y\x96IQ\x14\x978=\xefCj\x93\xa6i$\xcf\xf3\xaf\xde\x95\x85ax\x89X\xaf\xd7\x93~\xbf\x7f\xd9\x9f\x06\x9d\x82\xcdf\xe3\xc7KoK\xd4u-y\x9eK\x96e\x97@\xe1\xd7=\x07\xac\xdf\xefK\x92$\xd2\xe9tl\x8f\x84\xdf@\xb0\x1c\xd74\x8ddYvy\x10\xa8\xd7\xf5\xfc\xce\xeb\xf9\xc1\x11J\xb7\x11,\x07\xd5u-\xa7\xd3I\xd24\x95\xd3\xe9\xe4\xcd\xfe\'\xd7\x05A \x83\xc1@\x86\xc3\xa1\x0c\x06\x03\xde}9\x88`9\xa2,\xcbK\xa4\xbewt\x0c\xd7\x97$\xc9%^q\x1c\xdb\x1e\x07B\xb0\xac\xaa\xaaJ\x8e\xc7\xa3\x1c\x0e\x07\xa9\xaa\xca\xf68\xf8\x89(\x8ad<\x1e\xcbh4\xe2\xe8\xa3E\x04\xeb\xca\x8c1\x97H\xf1NJ\xa7$I.\xf1\xe2\xa8\xe3u\x11\xac+h\x9aFN\xa7\x93\x1c\x0e\x07\xf6Iy\xe4y\x9f\xd7x<\x96\xc1`\xc0\x0e\xfb+ Xo\xe8|>\xcb~\xbf\x97\xfd~/u]\xdb\x1e\x07o\xa8\xd3\xe9\xc8d2\x91\xc9d\xc2Y\xf7o\x88`\xbd\x81\xa2(d\xb7\xdb\xc9\xf1x\xe4\xddT\xcb\x04A \xa3\xd1Hnnn\xa4\xd7\xeb\xd9\x1e\xc7;\x04\xeb\x15\xa5i*\xdb\xed\x96}S\x10\x91\x7f\xf6uM\xa7S\x19\x0e\x87\xb6G\xf1\x06\xc1z\x05\x87\xc3A6\x9b\rG\xfa\xf0]Q\x14\xc9\xbbw\xefd<\x1e\xdb\x1eE=\x82\xf5\x07\x8e\xc7\xa3<==\x11*\xfc\x92(\x8a\xe4\xfd\xfb\xf72\x1a\x8dl\x8f\xa2\x16\xc1z\x81\xd3\xe9$\xeb\xf5Z\xca\xb2\xb4=\n\x14\x8a\xe3Xf\xb3\x99\x0c\x06\x03\xdb\xa3\xa8C\xb0~C\x9e\xe7\xf2\xf4\xf4$Y\x96\xd9\x1e\x05\x1e\xe8\xf7\xfb\xf2\xfe\xfd{I\x92\xc4\xf6(j\x10\xac_`\x8c\x91\xf5z-\xfb\xfd\xde\xf6(\xf0\xd0d2\x91\xd9l\xc6I\xa8\xbf\x80`\xfd\x874Me\xb5ZY\xbb]0\xda\xa1\xdb\xed\xca|>\xe7\x88\xe2\x7f X?P\xd7\xb5\xacV+9\x1e\x8f\xb6GA\x8b\x8cF#\x99\xcf\xe7\xdc)\xe2\x07\x08\xd6w\x1c\x0e\x07Y\xadV\xad\xbcs\'\xec\x0b\xc3P\xe6\xf39\xa7A|\x07\xd7\x10\xfc\x9f\xd5j%\xbb\xdd\xce\xf6\x18h1c\x8c<<<HQ\x142\x9f\xcfm\x8f\xe3\x14\x82\xf5/c\x8c\xfc\xfd\xf7\xdf\x9c\xa5\x0eg\xecv;)\x8aB>}\xfa\xc4\x0e\xf9\x7f\xf1\x91P\xfe\xb9\xf6o\xb1X\xb0c\x1dN\xeav\xbb\xf2\xf1\xe3G\xaeM\x14\xbe\xaa^\xd24\x95\xfb\xfb{b\x05g\x9d\xcfg\xb9\xbf\xbf\x974Mm\x8fb]\xab\x83\xb5\xdb\xedd\xb1X\xb0s\x1d\xce3\xc6\xc8b\xb1h\xfd\xfe\xd5\xd6\x06k\xb7\xdb\xc9j\xb5\xb2=\x06\xf0[\xda~P\xa8\x95\xc1z>m\x01\xd0h\xb5Z\xc9\xe1p\xb0=\x86\x15\xad\x0bV\x96e\xf2\xf0\xf0`{\x0c\xe0\x8f<<<\xb4\xf2\x9a\xd6V\x05\xab,KY,\x16\xb6\xc7\x00^\xc5b\xb1h\xdd\x1dCZ\x13\xac\xa6id\xb9\\\xb2\x83\x1d\xde0\xc6\xc8r\xb9l\xd5m\xb8[\x13,\xee_\x05\x1f\x95e)\xeb\xf5\xda\xf6\x18W\xd3\x8a`eY\xd6\xea#+\xf0\xdbn\xb7k\xcd\xfe\xacV\x04\x8b#\x82\xf0][\x9e\xe3\xde\x07k\xb7\xdb\xf1Q\x10\xde+\xcb\xb2\x15\x9f"\xbc\x0eV\xd34\xb2\xd9ll\x8f\x01\\\xc5f\xb3\xf1~\x07\xbc\xd7\xc1:\x1e\x8f|\xe32Z\xa3\xaek\xefo8\xe9u\xb0\xda\xf0\x16\x19\xf8\x92\xef\xcfyo\x83U\x96\xa5\x14Ea{\x0c\xe0\xaa\x8a\xa2\xf0z\x9f\xad\xb7\xc1\xe2V\x1ch+\x9f\x9f\xfb\xde\x06\xebt:\xd9\x1e\x01\xb0\xc2\xe7\xe7\xbe\xb7\xc1\xe2\xe3 \xda\xca\xe7\xe7\xbe\x97\xc1\xaa\xeb\xda\xfb\xc3\xbb\xc0\x8f4M\xe3\xed\xd1qo\x83\x05\xb4\x99\xaf\xdb\x80\x97\xc1\x02\xe0\'/\x83\xc5-d\xd0v\xben\x03^\x06\x8b\xfdWh;_\xb7\x01/\x83\x15\x04\x81\xed\x11\x00\xab|\xdd\x06\xbc\x0c\x16\x00?\x11,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x10,\x00j\x04\x9b\xcd\xc6\xbb/03\xc6HY\x96\xb6\xc7\x00\xac\x89\xe3X\xc2\xd0\xbf\xf7#]\xdb\x03\xbc\x850\x0c%I\x12\xdbc\x00xe\xfe%\x18\x80\xb7\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\x08\x16\x005\xfe\x07\xc7\x90\x82NM<\xd04\x00\x00\x00\x00IEND\xaeB`\x82'

# %% ../../nbs/utils/Image.ipynb 12
domo_default_img = Image.from_bytestr(default_img_bytes)


def are_same_image(image1, image2):
    try:
        img_chop = PIL.ImageChops.difference(image1, image2)

        print(np.sum(np.array(img_chop.getdata())))

        if np.sum(np.array(img_chop.getdata())) == 0:
            return True
        return False

    except ValueError as e:
        print(e)
        return False
