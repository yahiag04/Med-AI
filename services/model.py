from pathlib import Path

from PIL import Image
import torch

from models.pneumonia_net import PneumoniaNet
from transformations.pneumonia import test_transforms


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_model(weights_path: Path, device: torch.device) -> PneumoniaNet:
    model = PneumoniaNet().to(device)
    state = torch.load(str(weights_path), map_location=device)
    model.load_state_dict(state)
    model.eval()
    return model


def predict_image(model: PneumoniaNet, device: torch.device, image_path: Path) -> tuple[str, float]:
    img = Image.open(image_path).convert("L")
    x = test_transforms(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logit = model(x).squeeze()
        prob = torch.sigmoid(logit).item()
    label = "pneumonia" if prob >= 0.5 else "normal"
    return label, prob
