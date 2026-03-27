"""
YOLO fine-tuning script. Single-file, single-GPU.
Usage: uv run train.py
"""

import time
import torch
from ultralytics import YOLO

# ---- CONFIGURATION (agent tunes these) ----
MODEL = "yolov11_defect_segmentation.pt"  # pretrained model: yolo11n/s/m/l/x
DATA = "v4_dataset/data.yaml"   # dataset YAML path
EPOCHS = 300                    # max epochs (capped by TIME)
TIME = 0.083                    # training time budget in hours (~5 min)
PATIENCE = 0                    # early stopping (0 = disabled, time is the budget)
IMGSZ = 640                     # input image size
BATCH = 16                      # batch size (-1 for auto)
OPTIMIZER = "auto"              # SGD, Adam, AdamW, NAdam, RAdam, auto
LR0 = 0.01                     # initial learning rate
LRF = 0.01                     # final LR as fraction of LR0
MOMENTUM = 0.937                # SGD momentum / Adam beta1
WEIGHT_DECAY = 0.0005           # L2 regularization
WARMUP_EPOCHS = 3.0             # LR warmup epochs
WARMUP_MOMENTUM = 0.8           # warmup initial momentum
COS_LR = False                  # cosine LR scheduler
BOX = 7.5                       # box loss weight
CLS = 0.5                       # classification loss weight
DFL = 1.5                       # distribution focal loss weight
CLOSE_MOSAIC = 10               # disable mosaic last N epochs
HSV_H = 0.015                   # HSV-Hue augmentation (0-1)
HSV_S = 0.7                     # HSV-Saturation (0-1)
HSV_V = 0.4                     # HSV-Value (0-1)
DEGREES = 0.0                   # rotation (0-180)
TRANSLATE = 0.1                 # translation (0-1)
SCALE = 0.5                     # scale (0-1)
SHEAR = 0.0                     # shear (-180 to 180)
FLIPLR = 0.5                    # horizontal flip prob
FLIPUD = 0.0                    # vertical flip prob
MOSAIC = 1.0                    # mosaic (0-1)
MIXUP = 0.0                     # mixup (0-1)
COPY_PASTE = 0.0                # copy-paste (0-1)
ERASING = 0.4                   # random erasing (0-1)
FREEZE = None                   # freeze first N layers (int or None)
AMP = True                      # automatic mixed precision
MULTI_SCALE = 0.0               # multi-scale training factor
# ---- END CONFIGURATION ----

t_start = time.time()

model = YOLO(MODEL)
results = model.train(
    data=DATA,
    epochs=EPOCHS,
    time=TIME,
    patience=PATIENCE,
    imgsz=IMGSZ,
    batch=BATCH,
    optimizer=OPTIMIZER,
    lr0=LR0,
    lrf=LRF,
    momentum=MOMENTUM,
    weight_decay=WEIGHT_DECAY,
    warmup_epochs=WARMUP_EPOCHS,
    warmup_momentum=WARMUP_MOMENTUM,
    cos_lr=COS_LR,
    box=BOX,
    cls=CLS,
    dfl=DFL,
    close_mosaic=CLOSE_MOSAIC,
    hsv_h=HSV_H,
    hsv_s=HSV_S,
    hsv_v=HSV_V,
    degrees=DEGREES,
    translate=TRANSLATE,
    scale=SCALE,
    shear=SHEAR,
    fliplr=FLIPLR,
    flipud=FLIPUD,
    mosaic=MOSAIC,
    mixup=MIXUP,
    copy_paste=COPY_PASTE,
    erasing=ERASING,
    freeze=FREEZE,
    amp=AMP,
    multi_scale=MULTI_SCALE,
)

metrics = model.trainer.metrics
map50_95 = metrics.get("metrics/mAP50-95(B)", 0.0)
map50 = metrics.get("metrics/mAP50(B)", 0.0)
precision = metrics.get("metrics/precision(B)", 0.0)
recall = metrics.get("metrics/recall(B)", 0.0)
epochs_completed = model.trainer.epoch + 1
peak_vram_mb = torch.cuda.max_memory_allocated() / 1024 / 1024 if torch.cuda.is_available() else 0.0
training_seconds = time.time() - t_start

print("---")
print(f"map50_95:         {map50_95:.6f}")
print(f"map50:            {map50:.6f}")
print(f"precision:        {precision:.6f}")
print(f"recall:           {recall:.6f}")
print(f"training_seconds: {training_seconds:.1f}")
print(f"peak_vram_mb:     {peak_vram_mb:.1f}")
print(f"model:            {MODEL.replace('.pt', '')}")
print(f"epochs_completed: {epochs_completed}")
