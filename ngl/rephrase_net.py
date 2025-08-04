import torch
import torch.nn as nn
import torch.nn.functional as f

# Minimal character-level sequence to sequence rephraser
_CHARSET = sorted(set("abcdefghijklmnopqrstuvwxyz "))
_STOI = {c: i + 1 for i, c in enumerate(_CHARSET)}
_STOI["<pad>"] = 0
_ITOS = {i: c for c, i in _STOI.items()}

_PAIRS = [
    ("water is essential for life", "life requires water"),
    ("fire needs oxygen", "oxygen is required for fire"),
]

_MAX_LEN = max(len(src) for src, _ in _PAIRS)


class RephraseNet(nn.Module):
    def __init__(self, vocab_size: int, hidden_size: int = 64) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        out, _ = self.gru(emb)
        return self.fc(out)


_MODEL: RephraseNet | None = None


def _encode(text: str) -> list[int]:
    text = text.lower()
    return [_STOI.get(ch, 0) for ch in text.ljust(_MAX_LEN)]


def _decode(indices: list[int]) -> str:
    return "".join(_ITOS.get(i, "") for i in indices).strip()


def _train_model() -> RephraseNet:
    model = RephraseNet(len(_STOI))
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    data = [(_encode(src), _encode(tgt)) for src, tgt in _PAIRS]
    inp = torch.tensor([d[0] for d in data], dtype=torch.long)
    tgt = torch.tensor([d[1] for d in data], dtype=torch.long)
    for _ in range(100):
        opt.zero_grad()
        out = model(inp)
        loss = f.cross_entropy(out.reshape(-1, len(_STOI)), tgt.reshape(-1))
        loss.backward()
        opt.step()
    return model


def get_model() -> RephraseNet:
    global _MODEL
    if _MODEL is None:
        _MODEL = _train_model()
        _MODEL.eval()
    return _MODEL


def neural_rephrase(sentence: str) -> str:
    model = get_model()
    idx = torch.tensor([_encode(sentence)], dtype=torch.long)
    with torch.no_grad():
        out = model(idx)[0]
    pred = out.argmax(dim=-1).tolist()
    return _decode(pred)


__all__ = ["neural_rephrase"]
