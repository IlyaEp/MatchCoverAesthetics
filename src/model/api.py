import requests
import jsonlines
import torch
import os
from tqdm import tqdm
from typing import List, Optional
from PIL import Image
from transformers import AutoModel, AutoFeatureExtractor
from src.model.utils import SongRetriever


class MatchCoverAPI:
    def __init__(self, model_name_or_path: str, device: Optional[str] = "cpu"):
        self.model = AutoModel.from_pretrained(model_name_or_path)
        self.device = device
        self.model.to(device)
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name_or_path)
        self.retriever = SongRetriever(dim=self.model.config.hidden_size)

    def forward(self, image_url: str) -> torch.Tensor:
        """
        This methods loads image from given URL, passes it through model and returns pooler output as embedding.
        """
        with Image.open(requests.get(image_url, stream=True).raw) as image:
            image = image.convert("RGB")  # model expects image to have 3 channels
        inputs = self.feature_extractor(images=image, return_tensors="pt").to(self.device)
        return torch.mean(self.model(**inputs).last_hidden_state, dim=1)

    def fit(self, in_file_path: str, out_file_path: str, use_playlist: bool = True):
        """
        This method reads images metadata from `in_file_path` and constructs embeddings for playlist/album cover of each image.
        Resulting data is saved to `out_file_path`.

        :param in_file_path: path to input file; expected to be stored as jsonlines and contain `track_id` and `playlist_cover` or `image_cover` fields
        :param out_file_path: path to file to save data with embeddings, using torch.save (serialization/pickling)
        :param use_playlist: if True, construct embeddings of playlists covers; otherwise - of album covers
        """
        results = []
        with jsonlines.open(in_file_path, mode="r") as reader:
            images = list(reader)
        for image in tqdm(images, total=len(images), desc="Constructing embeddings for given songs"):
            try:
                image["embedding"] = (
                    self.forward(image[f"{'playlist' if use_playlist else 'album'}_cover"]).cpu().detach()
                )
                results.append(image)
            except Exception as e:  # various problems with input image are possible (e.g. url is expired)
                print(image)
                print(e)
                continue
        torch.save(results, out_file_path)

    def load_from_disk(self, root_dir: str, use_playlists: bool = True):
        """
        This method loads all pickled files from given directory and constructs index for neighbors search.
        """
        data = []
        for fname in tqdm(os.listdir(root_dir), total=len(os.listdir(root_dir)), desc="Reading data files"):
            cur_data = torch.load(os.path.join(root_dir, fname))
            data.extend(cur_data)

        if use_playlists:
            images = {}
            for image in data:
                if image["track_id"] in images:
                    images[image["track_id"]].append(image["embedding"])
                else:
                    images[image["track_id"]] = [image["embedding"]]
            for image in images:
                images[image] = torch.mean(torch.stack(images[image]), dim=0)
            data = [{"track_id": track_id, "embedding": images[track_id]} for track_id in images]

        self.retriever.load_from_dict(data)

    def predict(self, image_url: str, n_songs: int) -> List[str]:
        """
        This method returns internal Spotify ids of `n_songs` nearest neighbors of image from given URL.
        """
        with torch.no_grad():
            embedding = self.forward(image_url)
            return self.retriever.predict(embedding.cpu().detach().numpy(), n_songs)
