import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os.path as osp

# Define the directory and the image path
datadir = "/home/pi/Desktop/598_EverGreen"
image_path = osp.join(datadir, "rose.png")

# Define expanded flower classes
flower_classes = ['rose', 'tulip', 'daisy', 'sunflower', 'daffodil']

# Load a more lightweight model, e.g., MobileNetV2
model = models.mobilenet_v2(pretrained=True)
model.eval()  # Set the model to inference mode

# Optimize and enhance image transformations
transform = transforms.Compose([
    transforms.Resize(256),  # Increase slightly for better feature extraction
    transforms.CenterCrop(224),  # Standard size for MobileNet
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalization for MobileNet
])

def classify_image(image_path, model, transform):
    # Load and preprocess the image
    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension

    # Inference
    with torch.no_grad():
        outputs = model(image)
    # Get the prediction (simplified mapping to limited classes)
    _, predicted = torch.max(outputs, 1)
    predicted_class_index = predicted[0] % len(flower_classes)  # Modulo to limit to defined classes
    predicted_class = flower_classes[predicted_class_index]

    return predicted_class

def main():
    # Classify the image and print the predicted class
    predicted_class = classify_image(image_path, model, transform)
    print(f'Predicted Flower Type: {predicted_class}')

if __name__ == "__main__":
    main()
