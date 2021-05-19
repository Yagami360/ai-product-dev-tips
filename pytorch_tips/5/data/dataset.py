import os
import numpy as np
import random
import pandas as pd
import re
import math
from PIL import Image, ImageDraw, ImageOps
import cv2

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

# PyTorch
import torch
import torch.utils.data as data
import torchvision.transforms as transforms
from torchvision.utils import save_image

from data.transforms.random_erasing import RandomErasing
from data.transforms.tps_transform import TPSTransform
from utils import set_random_seed, numerical_sort

IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

class TempleteDataset(data.Dataset):
    def __init__(self, args, root_dir, datamode = "train", image_height = 128, image_width = 128, data_augument_types = "none", debug = False ):
        super(TempleteDataset, self).__init__()
        self.args = args
        self.datamode = datamode
        self.data_augument_types = data_augument_types
        self.image_height = image_height
        self.image_width = image_width
        self.debug = debug

        self.image_s_dir = os.path.join( root_dir, "image_s" )
        self.image_t_dir = os.path.join( root_dir, "image_t" )
        self.image_s_names = sorted( [f for f in os.listdir(self.image_s_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )
        self.image_t_names = sorted( [f for f in os.listdir(self.image_t_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )

        # transform
        transform_list = []
        transform_mask_list = []
        transform_mask_woToTensor_list = []

        if( "resize" in data_augument_types ):
            transform_list.append(transforms.Resize( (args.image_height, args.image_width), interpolation=Image.LANCZOS ))
            transform_mask_list.append(transforms.Resize( (args.image_height, args.image_width), interpolation=Image.NEAREST ))
            transform_mask_woToTensor_list.append(transforms.Resize( (args.image_height, args.image_width), interpolation=Image.NEAREST ))
        if( "crop" in data_augument_types ):
            transform_list.append(transforms.CenterCrop( size = (args.image_height, args.image_width) ))
            transform_mask_list.append(transforms.CenterCrop( size = (args.image_height, args.image_width) ))
            transform_mask_woToTensor_list.append(transforms.CenterCrop( size = (args.image_height, args.image_width) ))
        if( "tps" in data_augument_types ):
            transform_list.append(TPSTransform(tps_points_per_dim=5))
            transform_mask_list.append(TPSTransform(tps_points_per_dim=5))
            transform_mask_woToTensor_list.append(TPSTransform(tps_points_per_dim=5))
        if( "hflip" in data_augument_types ):
            transform_list.append(transforms.RandomHorizontalFlip())
            transform_mask_list.append(transforms.RandomHorizontalFlip())
            transform_mask_woToTensor_list.append(transforms.RandomHorizontalFlip())
        if( "vflip" in data_augument_types ):
            transform_list.append(transforms.RandomVerticalFlip())
            transform_mask_list.append(transforms.RandomVerticalFlip())
            transform_mask_woToTensor_list.append(transforms.RandomVerticalFlip())
        if( "affine" in data_augument_types ):
            transform_list.append(transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.BICUBIC))
            transform_mask_list.append(transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.NEAREST))
            transform_mask_woToTensor_list.append(transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.NEAREST))
        if( "perspect" in data_augument_types ):
            transform_list.append(transforms.RandomPerspective())
            transform_mask_list.append(transforms.RandomPerspective())
            transform_mask_woToTensor_list.append(transforms.RandomPerspective())
        if( "color" in data_augument_types ):
            transform_list.append(transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5))

        transform_list.append(transforms.ToTensor())
        transform_mask_list.append(transforms.ToTensor())

        transform_list.append(transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5]))
        transform_mask_list.append(transforms.Normalize([0.5],[0.5]))

        if( "erase" in data_augument_types ):
            transform_list.append(RandomErasing( probability = 0.5, sl = 0.02, sh = 0.2, r1 = 0.3, mean=[-1.0, -1.0, -1.0] ))
            transform_mask_list.append(RandomErasing( probability = 0.5, sl = 0.02, sh = 0.2, r1 = 0.3, mean=[-1.0] ))
            transform_mask_woToTensor_list.append(RandomErasing( probability = 0.5, sl = 0.02, sh = 0.2, r1 = 0.3, mean=[-1.0] ))

        self.transform = transforms.Compose(transform_list)
        self.transform_mask = transforms.Compose(transform_mask_list)
        self.transform_mask_woToTensor = transforms.Compose(transform_mask_woToTensor_list)

        if( self.debug ):
            print( "self.image_s_dir :", self.image_s_dir)
            print( "self.image_t_dir :", self.image_t_dir)
            print( "len(self.image_s_names) :", len(self.image_s_names))
            print( "self.image_s_names[0:5] :", self.image_s_names[0:5])
            print( "self.transform :", self.transform)
            print( "self.transform_mask :", self.transform_mask)
            print( "self.transform_mask_woToTensor :", self.transform_mask_woToTensor)
            
        return

    def __len__(self):
        return len(self.image_s_names)

    def __getitem__(self, index):
        image_s_name = self.image_s_names[index]
        image_t_name = self.image_t_names[index]
        self.seed_da = random.randint(0,10000)

        #---------------------
        # image_s
        #---------------------
        image_s = Image.open( os.path.join(self.image_s_dir,image_s_name) ).convert('RGB')
        if not( "none" in self.data_augument_types ):
            set_random_seed( self.seed_da )

        image_s = self.transform(image_s)

        #---------------------
        # image_t
        #---------------------
        if( self.datamode == "train" ):
            image_t = Image.open( os.path.join(self.image_t_dir, image_t_name) ).convert('RGB')
            if not( "none" in self.data_augument_types ):
                set_random_seed( self.seed_da )

            image_t = self.transform_mask(image_t)
            #image_t = torch.from_numpy( np.asarray(self.transform_mask_woToTensor(image_t)).astype("float32") ).unsqueeze(0)

        #---------------------
        # returns
        #---------------------
        if( self.datamode == "train" ):
            results_dict = {
                "image_s_name" : image_s_name,
                "image_t_name" : image_t_name,
                "image_s" : image_s,
                "image_t" : image_t,
            }
        else:
            results_dict = {
                "image_s_name" : image_s_name,
                "image_s" : image_s,
            }

        return results_dict


class TempleteDataLoader(object):
    def __init__(self, dataset, batch_size = 1, shuffle = True, n_workers = 4, pin_memory = True):
        super(TempleteDataLoader, self).__init__()
        self.data_loader = torch.utils.data.DataLoader(
                dataset, 
                batch_size = batch_size, 
                shuffle = shuffle,
                num_workers = n_workers,
                pin_memory = pin_memory,
        )

        self.dataset = dataset
        self.batch_size = batch_size
        self.data_iter = self.data_loader.__iter__()

    def next_batch(self):
        try:
            batch = self.data_iter.__next__()
        except StopIteration:
            self.data_iter = self.data_loader.__iter__()
            batch = self.data_iter.__next__()

        return batch