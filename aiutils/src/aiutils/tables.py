"""
Code adapted from: https://huggingface.co/spaces/nielsr/tatr-demo/blob/main/app.py
"""

import io
import csv
from copy import deepcopy

import torch
from torchvision import transforms
from transformers import AutoModelForObjectDetection
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Patch
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
import easyocr

from aiutils._singleton import SingletonMeta


reader = easyocr.Reader(["en"])


def box_cxcywh_to_xyxy(x):
    x_c, y_c, w, h = x.unbind(-1)
    b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
    return torch.stack(b, dim=1)


def rescale_bboxes(out_bbox, size):
    width, height = size
    boxes = box_cxcywh_to_xyxy(out_bbox)
    boxes = boxes * torch.tensor([width, height, width, height], dtype=torch.float32)
    return boxes


def outputs_to_objects(outputs, img_size, id2label):
    m = outputs.logits.softmax(-1).max(-1)
    pred_labels = list(m.indices.detach().cpu().numpy())[0]
    pred_scores = list(m.values.detach().cpu().numpy())[0]
    pred_bboxes = outputs["pred_boxes"].detach().cpu()[0]
    pred_bboxes = [elem.tolist() for elem in rescale_bboxes(pred_bboxes, img_size)]

    objects = []
    for label, score, bbox in zip(pred_labels, pred_scores, pred_bboxes):
        class_label = id2label[int(label)]
        if not class_label == "no object":
            objects.append(
                {
                    "label": class_label,
                    "score": float(score),
                    "bbox": [float(elem) for elem in bbox],
                }
            )

    return objects


class MaxResize(object):
    def __init__(self, max_size=800):
        self.max_size = max_size

    def __call__(self, image):
        width, height = image.size
        current_max_size = max(width, height)
        scale = self.max_size / current_max_size
        resized_image = image.resize(
            (int(round(scale * width)), int(round(scale * height)))
        )

        return resized_image


class TableDetector(metaclass=SingletonMeta):
    def __init__(self):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        self._detection_transform = transforms.Compose(
            [
                MaxResize(800),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

        self._model = AutoModelForObjectDetection.from_pretrained(
            "microsoft/table-transformer-detection", revision="no_timm"
        ).to(self._device)

    def detect(self, image):
        """Return a list of detected tables in the image."""
        pixel_values = self._detection_transform(image).unsqueeze(0).to(self._device)

        with torch.no_grad():
            outputs = self._model(pixel_values)

        id2label = self._model.config.id2label
        id2label[len(self._model.config.id2label)] = "no object"
        detected_tables = outputs_to_objects(outputs, image.size, id2label)

        return detected_tables


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    image = Image.open(buf)
    return image


def visualize_detected_tables(img, det_tables):
    plt.imshow(img, interpolation="lanczos")

    fig = plt.gcf()
    fig.set_size_inches(20, 20)
    ax = plt.gca()

    for det_table in det_tables:
        bbox = det_table["bbox"]

        if det_table["label"] == "table":
            facecolor = (1, 0, 0.45)
            edgecolor = (1, 0, 0.45)
            alpha = 0.3
            linewidth = 2
            hatch = "//////"
        elif det_table["label"] == "table rotated":
            facecolor = (0.95, 0.6, 0.1)
            edgecolor = (0.95, 0.6, 0.1)
            alpha = 0.3
            linewidth = 2
            hatch = "//////"
        else:
            continue

        rect = patches.Rectangle(
            bbox[:2],
            bbox[2] - bbox[0],
            bbox[3] - bbox[1],
            linewidth=linewidth,
            edgecolor="none",
            facecolor=facecolor,
            alpha=0.1,
        )
        ax.add_patch(rect)
        rect = patches.Rectangle(
            bbox[:2],
            bbox[2] - bbox[0],
            bbox[3] - bbox[1],
            linewidth=linewidth,
            edgecolor=edgecolor,
            facecolor="none",
            linestyle="-",
            alpha=alpha,
        )
        ax.add_patch(rect)
        rect = patches.Rectangle(
            bbox[:2],
            bbox[2] - bbox[0],
            bbox[3] - bbox[1],
            linewidth=0,
            edgecolor=edgecolor,
            facecolor="none",
            linestyle="-",
            hatch=hatch,
            alpha=0.2,
        )
        ax.add_patch(rect)

    plt.xticks([], [])
    plt.yticks([], [])

    legend_elements = [
        Patch(
            facecolor=(1, 0, 0.45),
            edgecolor=(1, 0, 0.45),
            label="Table",
            hatch="//////",
            alpha=0.3,
        ),
        Patch(
            facecolor=(0.95, 0.6, 0.1),
            edgecolor=(0.95, 0.6, 0.1),
            label="Table (rotated)",
            hatch="//////",
            alpha=0.3,
        ),
    ]
    plt.legend(
        handles=legend_elements,
        bbox_to_anchor=(0.5, -0.02),
        loc="upper center",
        borderaxespad=0,
        fontsize=10,
        ncol=2,
    )
    plt.gcf().set_size_inches(10, 10)
    plt.axis("off")

    return fig2img(fig)


def crop_tables(image, tables):
    return [image.crop(table["bbox"]) for table in tables]


class TableStructureDetector(metaclass=SingletonMeta):
    """Detect the structure of a table in an image (rows and columns)"""

    def __init__(self):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        self._structure_model = AutoModelForObjectDetection.from_pretrained(
            "microsoft/table-transformer-structure-recognition-v1.1-all"
        ).to(self._device)

        self._structure_transform = transforms.Compose(
            [
                MaxResize(1000),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

    def detect(self, image_table):
        """Detect the structure of a single table"""
        pixel_values = (
            self._structure_transform(image_table).unsqueeze(0).to(self._device)
        )

        with torch.no_grad():
            outputs = self._structure_model(pixel_values)

        # postprocess to get individual elements
        id2label = self._structure_model.config.id2label
        id2label[len(self._structure_model.config.id2label)] = "no object"
        cells = outputs_to_objects(outputs, image_table.size, id2label)

        # visualize cells on cropped table
        image_table = deepcopy(image_table)

        draw = ImageDraw.Draw(image_table)

        for cell in cells:
            draw.rectangle(cell["bbox"], outline="red")

        return image_table, cells


def get_cell_coordinates_by_row(table_data):
    # Extract rows and columns
    rows = [entry for entry in table_data if entry["label"] == "table row"]
    columns = [entry for entry in table_data if entry["label"] == "table column"]

    # Sort rows and columns by their Y and X coordinates, respectively
    rows.sort(key=lambda x: x["bbox"][1])
    columns.sort(key=lambda x: x["bbox"][0])

    # Function to find cell coordinates
    def find_cell_coordinates(row, column):
        cell_bbox = [
            column["bbox"][0],
            row["bbox"][1],
            column["bbox"][2],
            row["bbox"][3],
        ]
        return cell_bbox

    # Generate cell coordinates and count cells in each row
    cell_coordinates = []

    for row in rows:
        row_cells = []
        for column in columns:
            cell_bbox = find_cell_coordinates(row, column)
            row_cells.append({"column": column["bbox"], "cell": cell_bbox})

        # Sort cells in the row by X coordinate
        row_cells.sort(key=lambda x: x["column"][0])

        # Append row information to cell_coordinates
        cell_coordinates.append(
            {"row": row["bbox"], "cells": row_cells, "cell_count": len(row_cells)}
        )

    # Sort rows from top to bottom
    cell_coordinates.sort(key=lambda x: x["row"][1])

    return cell_coordinates


def apply_ocr(cell_coordinates, cropped_table):
    # let's OCR row by row
    data = dict()
    max_num_columns = 0
    for idx, row in enumerate(cell_coordinates):
        row_text = []
        for cell in row["cells"]:
            # crop cell out of image
            cell_image = np.array(cropped_table.crop(cell["cell"]))
            # apply OCR
            result = reader.readtext(np.array(cell_image))
            if len(result) > 0:
                text = " ".join([x[1] for x in result])
                row_text.append(text)

        if len(row_text) > max_num_columns:
            max_num_columns = len(row_text)

        data[str(idx)] = row_text

    # pad rows which don't have max_num_columns elements
    # to make sure all rows have the same number of columns
    for idx, row_data in data.copy().items():
        if len(row_data) != max_num_columns:
            row_data = row_data + ["" for _ in range(max_num_columns - len(row_data))]
        data[str(idx)] = row_data

    # write to csv
    with open("output.csv", "w") as result_file:
        wr = csv.writer(result_file, dialect="excel")

        for row, row_text in data.items():
            wr.writerow(row_text)

    # return as Pandas dataframe
    # TODO: write to memory instead of disk
    try:
        df = pd.read_csv("output.csv")
    # TODO: this hapens in some pages, but we need a better way to handle this
    except Exception as e:
        return None, None

    return df, data
