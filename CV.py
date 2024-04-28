import torch
from torchvision import models, transforms
from PIL import Image

def classify_image(image_path, model, preprocess, device):
    # Define a smaller set of flower names directly in the code
    flower_classes = ['Rose', 'Daisy', 'Tulip']  # Adjusted to three classes
    
    image = Image.open(image_path)
    image_input = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(image_input)
        _, predicted = outputs.max(1)
    
    most_likely_flower = flower_classes[predicted[0]]
    probability = torch.nn.functional.softmax(outputs, dim=1)[0][predicted[0]].item() * 100
    
    return most_likely_flower, probability

def main():
    device = torch.device('cpu')  # Use CPU for compatibility
    model = models.mobilenet_v2(pretrained=True)
    # Adjust the number of classes to 3 in the final classifier layer
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 3)
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
