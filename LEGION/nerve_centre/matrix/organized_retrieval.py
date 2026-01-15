import logging
import re
import umap
import numpy as np
from sklearn.mixture import GaussianMixture
import trio

from graphrag.utils import (
    get_llm_cache,
    get_embed_cache,
    set_embed_cache,
    set_llm_cache,
    chat_limiter,
)
from rag.utils import truncate


class RecursiveAbstractiveProcessing4TreeOrganizedRetrieval:
    def __init__(
        self, max_cluster, llm_model, embd_model, prompt, max_token=512, threshold=0.1
    ):
        self._max_cluster = max_cluster
        self._llm_model = llm_model
        self._embd_model = embd_model
        self._threshold = threshold
        self._prompt = prompt
        self._max_token = max_token

    async def _chat(self, system, history, gen_conf):
        response = get_llm_cache(self._llm_model.llm_name, system, history, gen_conf)
        if response:
            return response
        response = await trio.to_thread.run_sync(
            lambda: self._llm_model.chat(system, history, gen_conf)
        )
        # Remove any "<think>" tags and everything before it
        response = re.sub(r"^.*</think>", "", response, flags=re.DOTALL)
        if "**ERROR**" in response:
            raise Exception(response)
        set_llm_cache(self._llm_model.llm_name, system, response, history, gen_conf)
        return response

    async def _embedding_encode(self, txt):
        response = get_embed_cache(self._embd_model.llm_name, txt)
        if response is not None:
            return response
        embds, _ = await trio.to_thread.run_sync(lambda: self._embd_model.encode([txt]))
        if not embds or not embds[0]:
            raise Exception("Embedding error: No embedding returned.")
        embds = embds[0]
        set_embed_cache(self._embd_model.llm_name, txt, embds)
        return embds

    def _get_optimal_clusters(self, embeddings: np.ndarray, random_state: int):
        max_clusters = min(self._max_cluster, len(embeddings))
        n_clusters = np.arange(1, max_clusters)
        bics = []
        for n in n_clusters:
            gm = GaussianMixture(n_components=n, random_state=random_state)
            gm.fit(embeddings)
            bics.append(gm.bic(embeddings))
        optimal_clusters = n_clusters[np.argmin(bics)]
        return optimal_clusters

    async def __call__(self, chunks, random_state, callback=None):
        if len(chunks) <= 1:
            return []
        # Filter out empty chunks and embeddings
        chunks = [(s, a) for s, a in chunks if s and len(a) > 0]
        layers = [(0, len(chunks))]
        start, end = 0, len(chunks)

        async def summarize(ck_idx: list[int]):
            nonlocal chunks
            texts = [chunks[i][0] for i in ck_idx]
            len_per_chunk = max(1, int(
                (self._llm_model.max_length - self._max_token) / max(1, len(texts))
            ))
            cluster_content = "\n".join(
                [truncate(t, len_per_chunk) for t in texts]
            )
            async with chat_limiter:
                cnt = await self._chat(
                    "You're a helpful assistant.",
                    [
                        {
                            "role": "user",
                            "content": self._prompt.format(
                                cluster_content=cluster_content
                            ),
                        }
                    ],
                    {"temperature": 0.3, "max_tokens": self._max_token},
                )
            # Remove truncation notices (translated to English)
            cnt = re.sub(
                r"(······\nDue to length, the answer was truncated. Continue\?|For the content length reason, it stopped, continue\?)",
                "",
                cnt,
            )
            logging.debug(f"SUMMARY: {cnt}")
            embds = await self._embedding_encode(cnt)
            chunks.append((cnt, embds))

        labels = []
        while end - start > 1:
            embeddings = [embd for _, embd in chunks[start:end]]
            if len(embeddings) == 2:
                await summarize([start, start + 1])
                if callback:
                    callback(
                        msg=f"Cluster one layer: {end - start} -> {len(chunks) - end}"
                    )
                labels.extend([0, 0])
                layers.append((end, len(chunks)))
                start = end
                end = len(chunks)
                continue

            n_neighbors = max(2, int((len(embeddings) - 1) ** 0.8))
            n_components = min(12, max(2, len(embeddings) - 2))
            reduced_embeddings = umap.UMAP(
                n_neighbors=n_neighbors,
                n_components=n_components,
                metric="cosine",
            ).fit_transform(embeddings)
            n_clusters = self._get_optimal_clusters(reduced_embeddings, random_state)
            if n_clusters == 1:
                lbls = [0] * len(reduced_embeddings)
            else:
                gm = GaussianMixture(n_components=n_clusters, random_state=random_state)
                gm.fit(reduced_embeddings)
                probs = gm.predict_proba(reduced_embeddings)
                lbls = [np.where(prob > self._threshold)[0] for prob in probs]
                lbls = [lbl[0] if isinstance(lbl, np.ndarray) and len(lbl) > 0 else 0 for lbl in lbls]

            async with trio.open_nursery() as nursery:
                for c in range(n_clusters):
                    ck_idx = [i + start for i in range(len(lbls)) if lbls[i] == c]
                    assert ck_idx, "Cluster index list is empty"
                    nursery.start_soon(summarize, ck_idx)

            assert len(chunks) - end == n_clusters, f"{len(chunks) - end} vs. {n_clusters}"
            labels.extend(lbls)
            layers.append((end, len(chunks)))
            if callback:
                callback(
                    msg=f"Cluster one layer: {end - start} -> {len(chunks) - end}"
                )
            start = end
            end = len(chunks)