from segmentation_models_pytorch import (DeepLabV3, DeepLabV3Plus, Unet, UnetPlusPlus, UPerNet,
                                         PSPNet, Segformer, Linknet, MAnet, PAN, DPT, FPN)

def create_model_deeplabv3(num_classes):
    model = DeepLabV3(encoder_name='resnet50',
                    encoder_depth=5,
                    encoder_weights='imagenet',
                    encoder_output_stride=16,
                    decoder_channels=256,
                    decoder_atrous_rates=(12, 24, 36),
                    in_channels=3,
                    classes=num_classes,
                    activation=None,
                    upsampling=4, 
                    aux_params=None)
    return model
def create_model_deeplabv3p(num_classes):
    model = DeepLabV3Plus(encoder_name='resnet50',
                        encoder_depth=5,
                        encoder_weights='imagenet',
                        encoder_output_stride=16,
                        decoder_channels=256,
                        decoder_atrous_rates=(12, 24, 36),
                        in_channels=3,
                        classes=num_classes,
                        activation=None,
                        upsampling=4, 
                        aux_params=None)
    return model

def create_model_unet(num_classes):
    model = Unet(encoder_name='resnet50',
                encoder_weights='imagenet',
                decoder_channels=(256, 128, 64, 32, 16),
                in_channels=3,
                classes=num_classes,
                activation=None,
                upsampling=4, 
    )
    return model
def create_model_unetplusplus(num_classes):
    model = UnetPlusPlus(encoder_name='vgg16',
                        encoder_weights='imagenet',
                        decoder_channels=(256, 128, 64, 32, 16),
                        in_channels=3,
                        classes=num_classes,
                        activation=None,
                        upsampling=4, 
    )
    return model
def create_model_upernet(num_classes):
    model = UPerNet(encoder_name='resnet50',
                    encoder_weights='imagenet',
                    decoder_channels=256,
                    in_channels=3,
                    classes=num_classes,
                    activation=None,
                    upsampling=4, 
    )
    return model

def  create_model_fpn(num_classes):
    model = FPN(encoder_name='resnet50',
                encoder_weights='imagenet',
                decoder_pyramid_channels=256,
                decoder_segmentation_channels=128,
                in_channels=3,
                classes=num_classes,
                activation=None,
                upsampling=4, 
    )
    return model
def create_model_pspnet(num_classes):
    model = PSPNet(encoder_name='resnet50',
                encoder_weights='imagenet',
                psp_out_channels=256,
                psp_pool_scales=(1, 2, 3, 6),
                in_channels=3,
                classes=num_classes,
                activation=None,
    )
    return model
def create_model_segformer(num_classes):
    model = Segformer(encoder_name='resnet50',
                    encoder_weights='imagenet',
                    encoder_depth=5,
                    decoder_channels=256,
                    in_channels=3,
                    classes=num_classes,
                    activation=None,
                    upsampling=4, 
    )
    return model
def create_model_linknet(num_classes):
    model = Linknet(encoder_name='resnet50',
                    encoder_weights='imagenet',
                    decoder_channels=256,
                    in_channels=3,
                    classes=num_classes,
                    activation=None,
                    upsampling=4, 
    )
    return model
def create_model_manet(num_classes):
    model = MAnet(encoder_name='resnet50',
                encoder_weights='imagenet',
                decoder_channels=256,
                in_channels=3,
                classes=num_classes,
                activation=None,
                upsampling=4, 
    )
    return model
def create_model_pan(num_classes):
    model = PAN(encoder_name='resnet50',
                encoder_weights='imagenet',
                decoder_channels=256,
                in_channels=3,
                classes=num_classes,
                activation=None,
                upsampling=4, 
    )
    return model

def create_model_dpt(num_classes):
    model = DPT(encoder_name='resnet50',
                encoder_weights='imagenet',
                encoder_depth=5,
                decoder_channels=256,
                in_channels=3,
                classes=num_classes,
                activation=None,
                upsampling=4, 
    )
    return model

model_map = {'fpn': create_model_fpn,
             'pspnet': create_model_pspnet,
             'unet': create_model_unet,
             'unetplusplus': create_model_unetplusplus,
             'deeplabv3': create_model_deeplabv3,
             'deeplabv3p': create_model_deeplabv3p,
             'upernet': create_model_upernet,
             'segformer': create_model_segformer,
             'linknet': create_model_linknet,
             'manet': create_model_manet,
             'pan': create_model_pan,
             'dpt': create_model_dpt,
            }
def create_model(model_name, num_classes):
    if model_name in model_map:
        return model_map[model_name](num_classes)
    else:
        raise ValueError(f"Invalid model name: {model_name}")

