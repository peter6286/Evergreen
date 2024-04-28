import torch
from torchvision import models, transforms
from PIL import Image

def classify_image(image_path, model, preprocess, device):
    # Update the flower classes to four
    flower_classes = ['Rose', 'Daisy', 'Tulip', 'Sunflower']  # Adding 'Sunflower' to make four classes
    
    image = Image.open(image_path)
    image_input = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(image_input)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        top_probability, top_class = probabilities.topk(1, dim=1)

    most_likely_flower = flower_classes[top_class[0][0]]
    probability = top_probability[0][0].item() * 100
    
    return most_likely_flower, probability

def main():
    device = torch.device('cpu')  # Use CPU for compatibility
    model = models.mobilenet_v2(pretrained=True)
    # Change the classifier to match four output classes
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 4)
    model = model.to(device)
    
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    # Correct image path for Raspberry Pi
    image_path = "/home/pi/Desktop/598_EverGreen/rose.png"
    most_likely_flower, probability = classify_image(image_path, model, preprocess, device)
    print(f'Identified Plant Type: {most_likely_flower} with a probability of {probability:.2f}%')

if __name__ == '__main__':
    main()
