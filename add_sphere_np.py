import numpy as np
from PIL import Image
def add_sphere_np(image: Image, radius: float, value: float =1.0)-> None:
    array=mp.asarray(image)
    if array.ndim==2:
        array=array[None, :, :]
    elif array.ndim!=3:
        raise ValueError('Image must be 2D or 3D')
    z,y,x=np.ogrid[:array.shape[0],:array.shape[1],:array.shape[2]]
    center_z=(array.shape[0]/2)
    center_y=(array.shape[1]/2)
    center_x=(array.shape[2]/2)
    mask = ((z - center_z) ** 2 + (y - center_y) ** 2 + (x - center_x) ** 2) <= radius ** 2
    array[mask]+=value



