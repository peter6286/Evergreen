import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os.path as osp

# Define the directory and the image path
datadir = "/home/pi/Desktop/598_EverGreen"
image_path = osp.join(datadir, "rose.png")

# Define simplified flower classes
flower_classes = ['rose', 'tulip', 'daisy']

# Load a more lightweight model, e.g., MobileNetV2
model = models.mobilenet_v2(pretrained=True)
model.eval()  # Set the model to inference mode

# Define a simple transformation
transform = transforms.Compose([
    transforms.Resize(128),  # Smaller image size
    transforms.CenterCrop(128),
    transforms.ToTensor(),
])

def classify_image(image_path, model, transform):
    # Load and preprocess the image
    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension

    # Inference
    with torch.no_grad():
        outputs = model(image)
    # Get the prediction (for simplification, assume classes are the top categories)
    _, predicted = torch.max(outputs, 1)
    predicted_class = flower_classes[predicted[0] % len(flower_classes)]  # Modulo to limit to defined classes

    return predicted_class

def main():
    # Classify the image and print the predicted class
    predicted_class = classify_image(image_path, model, transform)
    print(f'Predicted Flower Type: {predicted_class}')

if __name__ == "__main__":
    main()
