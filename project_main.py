import json
import os
import torch
import clip
from PIL import Image
import json
from torchvision.datasets import Flowers102
import os.path as osp

datadir = "/home/pi/Desktop/cv"

def load_flower_data(img_transform=None):
    if os.path.isdir(datadir + "/flowers-102"):
        do_download = False
    else:
        do_download = True
    train_set = Flowers102(root=datadir, split='train', transform=img_transform, download=do_download)
    test_set = Flowers102(root=datadir, split='val', transform=img_transform, download=do_download)
    classes = json.load(open(osp.join(datadir, "flowers102_classes.json")))
    return train_set, test_set, classes

def classify_image(image_path, clip_model, clip_preprocess, device, flower_classes):
    image = Image.open(image_path)
    image_input = clip_preprocess(image).unsqueeze(0).to(device)
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}, a type of flower.") for c in flower_classes]).to(device)
    with torch.no_grad():
        image_features = clip_model.encode_image(image_input)
        text_features = clip_model.encode_text(text_inputs)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    top_values, top_indices = similarity[0].topk(5)
    print("\nTop predictions:\n")
    for value, index in zip(top_values, top_indices):
        print(f"{flower_classes[index]:>16s}: {100 * value.item():.2f}%")
    most_likely_value, most_likely_index = similarity[0].topk(1)
    most_likely_flower = flower_classes[most_likely_index[0]]
    probability = most_likely_value[0].item() * 100
    return most_likely_flower, probability

def main():

    device = "cuda" if torch.cuda.is_available() else 'cpu'
    clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
    image_path = "/home/pi/Desktop/cv/Rose.jpg"
    flower_train, flower_test, flower_classes = load_flower_data()
    
    print('Captured image path:', image_path)
    most_likely_flower, probability = classify_image(image_path, clip_model, clip_preprocess, device, flower_classes)
    print(f'Identified Plant Type: {most_likely_flower} with a probability of {probability:.2f}%')
    


if __name__ == '__main__':
    main()
