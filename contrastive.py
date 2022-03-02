import torchvision
import torch
from PIL import Image 
import torchvision.transforms as transforms
import os
import numpy as np

# MODEL_PATH = '/home/user/Documents/Master/contrastive_learning/tenpercent_resnet18.ckpt'
MODEL_PATH = "/home/simon/philipp/checkpoints/tenpercent_resnet18.ckpt"
RETURN_PREACTIVATION = False  # return features from the model, if false return classification logits
NUM_CLASSES = 4  # only used if RETURN_PREACTIVATION = False


def load_model_weights(model, weights):

    model_dict = model.state_dict()
    weights = {k: v for k, v in weights.items() if k in model_dict}
    if weights == {}:
        print('No weight could be loaded..')
    model_dict.update(weights)
    model.load_state_dict(model_dict)

    return model


def load_images(path):
    img_paths = [x for x in os.walk(path)][0][2]
    # print(img_paths)
    torch.device()
    img_paths = [os.path.join(path, x) for x in img_paths]
    # image = np.array(Image.open(os.path.join(path, img_paths[0])))
    images = np.array([np.reshape(np.array(Image.open(img).convert('RGB').resize((224,224))), (3,224,224)) for img in img_paths])
    # Define a transform to convert the image to tensor
    transform = transforms.ToTensor() 
    # Convert the image to PyTorch tensor 
    print(images.shape)
    # tensor = transform(images)
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    tensor = torch.from_numpy(images).float().to(device)

    # print the converted image tensor 
    # print(tensor)

    return tensor


model = torchvision.models.__dict__['resnet18'](pretrained=False)

state = torch.load(MODEL_PATH, map_location='cuda:0')

state_dict = state['state_dict']
for key in list(state_dict.keys()):
    state_dict[key.replace('model.', '').replace('resnet.', '')] = state_dict.pop(key)

model = load_model_weights(model, state_dict)

if RETURN_PREACTIVATION:
    model.fc = torch.nn.Sequential()
else:
    model.fc = torch.nn.Linear(model.fc.in_features, NUM_CLASSES)

model = model.cuda()

# images = torch.rand((10, 3, 224, 224), device='cuda')

# img_path = "/media/user/easystore/some_patches"
img_path = "/home/simon/philipp/some_patches"
images = load_images(img_path)

out = model(images)
print(out)