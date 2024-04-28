import torch
import clip
from PIL import Image
from datetime import datetime

def classify_image(image_path, clip_model, clip_preprocess, device):
    # Define a small set of flower names directly in the code
    flower_classes = ['Rose', 'Daisy', 'Tulip', 'Sunflower', 'Orchid']
    
    image = Image.open(image_path)
    image_input = clip_preprocess(image).unsqueeze(0).to(device)
    
    # Create text inputs for CLIP
    text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}, a type of flower.") for c in flower_classes]).to(device)
    
    with torch.no_grad():
        image_features = clip_model.encode_image(image_input)
        text_features = clip_model.encode_text(text_inputs)
    
    # Normalize features
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)
    
    # Compute similarity and extract top results
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    top_values, top_indices = similarity[0].topk(5)
    
    print("\nTop predictions:\n")
    for value, index in zip(top_values, top_indices):
        print(f"{flower_classes[index]:>16s}: {100 * value.item():.2f}%")
    
    # Extract the most likely flower
    most_likely_value, most_likely_index = similarity[0].topk(1)
    most_likely_flower = flower_classes[most_likely_index[0]]
    probability = most_likely_value[0].item() * 100
    
    return most_likely_flower, probability

def main():
    device = "cuda" if torch.cuda.is_available() else 'cpu'
    clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
    
    # Image path for classification
    image_path = "/home/pi/Desktop/598_EverGreen/rose.png"
    
    # Classify the image and print the result
    most_likely_flower, probability = classify_image(image_path, clip_model, clip_preprocess, device)
    print(f'Identified Plant Type: {most_likely_flower} with a probability of {probability:.2f}%')

if __name__ == '__main__':
    main()
