from datasets.celeba import get_celeba
from datasets.utk_face import get_utk_face
from datasets.waterbirds import get_waterbirds
from datasets.imagenet9 import get_imagenet9
from tqdm import tqdm
from fairbench.bench.vision.pretrained import *


def celeba(
    classifier="flac",  # torch.nn.Module or string ("flac", "badd", "mavias")
    data_root=None,
    predict="predict",  # "predict" for class predictions, "probabilities" for probabilities
    device=None,  # "cpu" or "cuda" (GPU device, e.g., "cuda:0")
):
    """
    Evaluate a classifier on the CelebA dataset.

    Args:
        classifier: Either a PyTorch model or a string specifying the pretrained model ("flac", "badd", "mavias").
        data_root: Path to the CelebA dataset.
        predict: Whether to return class predictions ("predict") or class probabilities ("probabilities").
        device: The device to run the computation on. Default is "cuda" (uses GPU if available).

    Returns:
        y: True labels.
        yhat: Model outputs (predictions or probabilities).
    """
    import torch

    assert predict in {
        "predict",
        "probabilities",
    }, "Invalid predict value. Use 'predict' or 'probabilities'."

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    classifiers = {
        "flac": load_celeba_flac_model,
        "badd": load_celeba_badd_model,
        "mavias": load_celeba_mavias_model,
    }

    if isinstance(classifier, str):
        classifier = classifier.lower()
        assert (
            classifier in classifiers
        ), f"Available classifiers are: {list(classifiers)}"
        classifier = classifiers[classifier](device)
    assert isinstance(classifier, torch.nn.Module), "Classifier is not a torch model."

    # Prepare data loader
    test_loader = get_celeba(
        data_root, batch_size=64, target_attr="blonde", split="valid", aug=False
    )

    y, yhat, sens = [], [], []
    classifier = classifier.to(device)
    classifier.eval()
    with torch.no_grad():
        for images, labels, biases, _ in tqdm(test_loader):
            images, labels = images.to(device), labels.to(device)
            outputs = classifier(images)  # Forward pass

            if predict == "predict":
                preds = outputs.data.max(1, keepdim=True)[1].squeeze(1)
                yhat.extend(preds.cpu().tolist())
            elif predict == "probabilities":
                probs = torch.softmax(outputs, dim=1)
                yhat.extend(probs.cpu().tolist())

            y.extend(labels.cpu().tolist())
            sens.extend(biases.cpu().tolist())
    return y, yhat, sens


def utkface(
    classifier="flac",  # torch.nn.Module or string ("flac", "badd", "mavias")
    data_root=None,
    predict="predict",  # "predict" for class predictions, "probabilities" for probabilities
    device=None,  # "cpu" or "cuda" (GPU device, e.g., "cuda:0")
):
    """
    Evaluate a classifier on the UTKFace dataset.

    Args:
        classifier: Either a PyTorch model or a string specifying the pretrained model ("flac", "badd", "mavias").
        data_root: Path to the UTKFace dataset.
        predict: Whether to return class predictions ("predict") or class probabilities ("probabilities").
        device: The device to run the computation on. Default is "cuda" (uses GPU if available).

    Returns:
        y: True labels.
        yhat: Model outputs (predictions or probabilities).
    """
    import torch

    assert predict in {
        "predict",
        "probabilities",
    }, "Invalid predict value. Use 'predict' or 'probabilities'."

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    classifiers = {
        "flac": load_utkface_flac_model,
        "badd": load_utkface_badd_model,
        "mavias": load_utkface_mavias_model,
    }

    # Validate classifier argument
    if isinstance(classifier, str):
        classifier = classifier.lower()
        assert (
                classifier in classifiers
        ), f"Available classifiers are: {list(classifiers)}"
        classifier = classifiers[classifier](device)
    assert isinstance(classifier, torch.nn.Module), "Classifier is not a torch model."

    # Prepare data loader
    test_loader = get_utk_face(
        data_root, batch_size=64, bias_attr="race", split="test", aug=False
    )

    y, yhat, sens = [], [], []
    classifier = classifier.to(device)
    classifier.eval()

    with torch.no_grad():
        for images, labels, biases, _ in tqdm(test_loader):
            images, labels = images.to(device), labels.to(device)
            outputs = classifier(images)  # Forward pass

            if predict == "predict":
                preds = outputs.data.max(1, keepdim=True)[1].squeeze(1)
                yhat.extend(preds.cpu().tolist())
            elif predict == "probabilities":
                probs = torch.softmax(outputs, dim=1)
                yhat.extend(probs.cpu().tolist())

            y.extend(labels.cpu().tolist())
            sens.extend(biases.cpu().tolist())
    return y, yhat, sens


def waterbirds(
    classifier="flac",  # torch.nn.Module or string ("flac", "badd", "mavias")
    data_root=None,
    predict="predict",  # "predict" for class predictions, "probabilities" for probabilities
    device="cuda",  # "cpu" or "cuda" (GPU device, e.g., "cuda:0")
):
    """
    Evaluate a classifier on the Waterbirds dataset.

    Args:
        classifier: Either a PyTorch model or a string specifying the pretrained model ("flac", "badd", "mavias").
        data_root: Path to the Waterbirds dataset.
        predict: Whether to return class predictions ("predict") or class probabilities ("probabilities").
        device: The device to run the computation on. Default is "cuda" (uses GPU if available).

    Returns:
        y: True labels.
        yhat: Model outputs (predictions or probabilities).
    """
    import torch

    # Validate predict argument
    if predict not in {"predict", "probabilities"}:
        raise ValueError("Invalid predict value. Use 'predict' or 'probabilities'.")

    # Validate and set device
    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA is not available. Falling back to CPU.")
        device = "cpu"
    elif device.startswith("cuda:"):
        gpu_index = int(device.split(":")[1])
        if not torch.cuda.is_available() or gpu_index >= torch.cuda.device_count():
            raise ValueError(f"Requested GPU device '{device}' is not available.")

    device = torch.device(device)

    # Validate classifier argument
    if isinstance(classifier, str):
        if classifier.lower() not in {"flac", "badd", "mavias"}:
            raise ValueError(
                "Invalid classifier name. Choose from 'flac', 'badd', or 'mavias'."
            )
        # Load pretrained models (dummy implementation, replace with actual loading logic)
        if classifier.lower() == "flac":
            classifier = load_waterbirds_flac_model(device)
        elif classifier.lower() == "badd":
            classifier = load_waterbirds_badd_model(device)
        elif classifier.lower() == "mavias":
            classifier = load_waterbirds_mavias_model(device)
    elif not isinstance(classifier, torch.nn.Module):
        raise TypeError(
            "Classifier must be a PyTorch model or one of the strings 'flac', 'badd', 'mavias'."
        )

    # Prepare data loader
    test_loader = get_waterbirds(data_root, batch_size=64)

    classifier = classifier.to(device)
    classifier.eval()

    y, yhat, sens = [], [], []

    with torch.no_grad():
        for images, _, labels, biases in tqdm(test_loader):
            images, labels = images.to(device), labels.to(device)
            outputs = classifier(images)  # Forward pass

            if predict == "predict":
                preds = outputs.data.max(1, keepdim=True)[1].squeeze(1)
                yhat.extend(preds.cpu().tolist())
            elif predict == "probabilities":
                probs = torch.softmax(outputs, dim=1)
                yhat.extend(probs.cpu().tolist())

            y.extend(labels.cpu().tolist())
            sens.extend(biases.cpu().tolist())
    return y, yhat, sens


def imagenet9(
    classifier="mavias",  # torch.nn.Module or string ("flac", "badd", "mavias")
    data_root=None,
    predict="predict",  # "predict" for class predictions, "probabilities" for probabilities
    device=NOne,  # "cpu" or "cuda" (GPU device, e.g., "cuda:0")
):
    """
    Evaluate a classifier on the ImageNet9 dataset.

    Args:
        classifier: Either a PyTorch model or a string specifying the pretrained model ("flac", "badd", "mavias").
        data_root: Path to the ImageNet9 dataset.
        predict: Whether to return class predictions ("predict") or class probabilities ("probabilities").
        device: The device to run the computation on. Default is "cuda" (uses GPU if available).

    Returns:
        y: True labels.
        yhat: Model outputs (predictions or probabilities).
    """
    import torch

    assert predict in {
        "predict",
        "probabilities",
    }, "Invalid predict value. Use 'predict' or 'probabilities'."

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    classifiers = {
        "flac": load_imagenet9_flac_model,
        "badd": load_imagenet9_badd_model,
        "mavias": load_imagenet9_mavias_model,
    }

    # Validate classifier argument
    if isinstance(classifier, str):
        classifier = classifier.lower()
        assert (
                classifier in classifiers
        ), f"Available classifiers are: {list(classifiers)}"
        classifier = classifiers[classifier](device)
    assert isinstance(classifier, torch.nn.Module), "Classifier is not a torch model."

    # Prepare data loader
    test_loader = get_imagenet9(data_root, batch_size=64, bench="mixed_rand")

    classifier = classifier.to(device)
    classifier.eval()

    y, yhat = [], []

    with torch.no_grad():
        for images, labels in tqdm(test_loader):
            images, labels = images.to(device), labels.to(device)
            outputs = classifier(images)  # Forward pass

            if predict == "predict":
                preds = outputs.data.max(1, keepdim=True)[1].squeeze(1)
                yhat.extend(preds.cpu().tolist())
            elif predict == "probabilities":
                probs = torch.softmax(outputs, dim=1)
                yhat.extend(probs.cpu().tolist())

            y.extend(labels.cpu().tolist())

    return y, yhat
