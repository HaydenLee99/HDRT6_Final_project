import torch
from ultralytics import YOLO
import numpy as np
import flask

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())