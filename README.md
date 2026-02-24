
---

# weird-image-filemaker

A Python-based toolkit for generating, mutating, hardening, and packaging collections of “weird” images. This repository provides command-line utilities and mutation pipelines to programmatically transform source images into collections of algorithmically-modified artifacts.

## 🧠 Overview

`weird-image-filemaker` is designed for workflows where large batches of modified media are needed — whether for creative data-augmentation, artistic experimentation, or algorithmic media exploration. It includes:

* deterministic mutation of image content
* generation of structured packs of output
* optional “hardening” to normalize or sanitize inputs
* automation via PowerShell scripting for packaging

## 📂 Repository Contents

| File                             | Purpose                                                  |
| -------------------------------- | -------------------------------------------------------- |
| `build_best20_weird_pack.py`     | Creates a standard pack of 20 mutated images             |
| `build_best24_weirder_pack.py`   | Creates a larger pack of 24 variants                     |
| `harden_image_intake_example.py` | Demonstrates input validation and sanitization           |
| `image_mutator_local.py`         | Core mutation engine applied to single or sets of images |
| `zip_best20_weird.ps1`           | PowerShell script to archive a pack into ZIP             |
| `LICENSE`                        | MIT open-source license                                  |

## 🚀 Features

* **Configurable mutation pipeline** — extendable image transformation functions
* **Batch generation** — produce arbitrarily many outputs
* **Output packaging** — automated ZIP creation via PowerShell
* **Example workflows** — starter scripts to integrate into larger automation

## 🛠️ Requirements

This project assumes a Python 3.8+ environment with the following libraries (typical examples ‒ install via `pip`):

```bash
pip install pillow numpy opencv-python
```

> You can pin versions in a `requirements.txt` for reproducibility.

## 📌 Usage

### 1) Mutate a single image

```bash
python image_mutator_local.py --input source.jpg --output-dir weirdout/ --mutations 10
```

This applies a configurable set of mutation operators to `source.jpg` and writes 10 results to `weirdout/`.

### 2) Build a 20-image pack

```bash
python build_best20_weird_pack.py --source-directory samples/ --destination packs/best20/
```

This generates a curated pack of 20 transformed images from all files in `samples/`.

### 3) Build a 24-image “weirder” pack

```bash
python build_best24_weirder_pack.py --source-directory samples/ --destination packs/best24/
```

Expands on the base pack with additional or more aggressive transformations.

### 4) Harden image intake

```bash
python harden_image_intake_example.py --input dirty_input.png --output clean_input.png
```

Applies input sanitization, color normalization, and optional structural repair.

### 5) Create a ZIP archive (Windows/PowerShell)

```powershell
.\zip_best20_weird.ps1 -PackDir ".\packs\best20" -OutZip ".\archives\pack20.zip"
```

## 📦 Output Structure

After running a build script, expected output layout:

```
packs/
  best20/
    weird_001.png
    weird_002.png
    ...
    weird_020.png
```

Optional ZIP archives:

```
archives/
  pack20.zip
  pack24.zip
```

## 📐 Extensibility

To add custom mutation logic:

1. Open `image_mutator_local.py`
2. Add a new transform function:

```python
def invert_colors(img: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(img)
```

3. Register it in the pipeline list.

## 🧪 Testing

Include a basic test suite (e.g., `tests/` directory) to continuously verify:

* image validity after mutation
* absence of exceptions for edge inputs
* deterministic reproducibility when using random seeds

## 🧾 License

This project is licensed under the **MIT License** — see `LICENSE` for details. ([GitHub][1])

---


[1]: https://github.com/kai9987kai/weird-image-filemaker "GitHub - kai9987kai/weird-image-filemaker"
