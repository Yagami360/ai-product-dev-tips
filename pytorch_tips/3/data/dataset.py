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
    def __init__(self, args, dataset_dir, pairs_file = "train_pairs.csv", datamode = "train", image_height = 128, image_width = 128, batch_size = 4, data_augument_types = "none", use_ddp = False, n_gpus = 1, debug = False ):
        super(TempleteDataset, self).__init__()
        self.args = args
        self.dataset_dir = dataset_dir
        self.datamode = datamode
        self.image_height = image_height
        self.image_width = image_width
        self.batch_size = batch_size
        self.data_augument_types = data_augument_types
        self.use_ddp = use_ddp
        self.n_gpus = n_gpus
        self.debug = debug
        self.df_pairs = pd.read_csv( os.path.join(self.dataset_dir, pairs_file) )

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
            print( self.df_pairs.head() )
            print( "len(self.df_pairs) : ", len(self.df_pairs) )
            print( "self.transform :", self.transform)
            print( "self.transform_mask :", self.transform_mask)
            print( "self.transform_mask_woToTensor :", self.transform_mask_woToTensor)

        return

    def __len__(self):
        if( self.use_ddp ):
            return len(self.df_pairs) // (self.batch_size * self.n_gpus) * (self.batch_size * self.n_gpus)
        else:
            return len(self.df_pairs)

    def __getitem__(self, index):
        image_name = self.df_pairs["image_name"].iloc[index]
        target_name = self.df_pairs["target_name"].iloc[index]
        self.seed_da = random.randint(0,10000)

        # image
        image = Image.open( os.path.join(self.dataset_dir, "image", image_name) ).convert('RGB')
        if not( "none" in self.data_augument_types ):
            set_random_seed( self.seed_da )

        image = self.transform(image)

        # target
        if( self.datamode == "train" or self.datamode == "valid" ):
            target = Image.open( os.path.join(self.dataset_dir, "target", target_name) )
            if not( "none" in self.data_augument_types ):
                set_random_seed( self.seed_da )

            target = self.transform_mask(target)
            #target = torch.from_numpy( np.asarray(self.transform_mask_woToTensor(target)).astype("float32") ).unsqueeze(0)

        if( self.datamode == "train" or self.datamode == "valid" ):
            results_dict = {
                "image" : image,
                "target" : target,
            }
        else:
            results_dict = {
                "image_name" : image_name,
                "image" : image,
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