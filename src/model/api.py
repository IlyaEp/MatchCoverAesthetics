import requests
import torch
import numpy as np
from typing import Dict, List, Optional
from PIL import Image
from transformers import AutoModel, AutoFeatureExtractor
from src.model.utils import SongRetrieval


class MatchCoverAPI:
    def __init__(self, model_name_or_path: str, device: Optional[str] = "cpu"):
        self.model = AutoModel.from_pretrained(model_name_or_path)
        self.device = device
        self.model.to(device)
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name_or_path)
        self.retriever = SongRetrieval(dim=self.model.config.hidden_size)

    def forward(self, image_url: str):
        image = Image.open(requests.get(image_url, stream=True).raw)
        inputs = self.feature_extractor(images=image, return_tensors="pt").to(self.device)
        return self.model(**inputs).pooler_output

    def fit(self, images: List[Dict[str, str]], index_fname: Optional[str] = None):
        if index_fname:
            self.retriever.read_file(
                index_fname, [f"{image['track_artists']} - {image['track_name']}" for image in images]
            )
        else:
            with torch.no_grad():
                embeddings = []
                ids = []

                for image in images:
                    embedding = self.forward(image["album_cover"])
                    embeddings.append(embedding.cpu().detach().numpy().ravel())
                    ids.append(f"{image['track_artists']} - {image['track_name']}")
                self.retriever.fit(np.asarray(embeddings), ids)

    def predict(self, image_url: str, n_songs: int) -> List[str]:
        with torch.no_grad():
            embedding = self.forward(image_url)
            return self.retriever.predict(embedding.cpu().detach().numpy(), n_songs)
