"""Tiny Transformer-like model with a frozen base and trainable adapter."""

from collections.abc import Iterator

import torch
from torch import Tensor, nn


class ResidualAdapter(nn.Module):
    """Small trainable bottleneck applied as a residual update."""

    def __init__(self, model_width: int, bottleneck_width: int, dropout: float) -> None:
        super().__init__()
        self.down = nn.Linear(model_width, bottleneck_width)
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(dropout)
        self.up = nn.Linear(bottleneck_width, model_width)

    def forward(self, hidden: Tensor) -> Tensor:
        update = self.up(self.dropout(self.activation(self.down(hidden))))
        return hidden + update


class TinyTransformerLanguageModel(nn.Module):
    """A local CPU model whose only trainable parameters belong to the adapter."""

    def __init__(
        self,
        *,
        vocabulary_size: int,
        sequence_length: int,
        model_width: int,
        attention_heads: int,
        transformer_layers: int,
        adapter_width: int,
        dropout: float,
    ) -> None:
        super().__init__()
        self.sequence_length = sequence_length
        self.token_embedding = nn.Embedding(vocabulary_size, model_width)
        self.position_embedding = nn.Embedding(sequence_length, model_width)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_width,
            nhead=attention_heads,
            dim_feedforward=model_width * 2,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=transformer_layers)
        self.adapter = ResidualAdapter(model_width, adapter_width, dropout)
        self.final_norm = nn.LayerNorm(model_width)
        self.output_head = nn.Linear(model_width, vocabulary_size, bias=False)
        self._freeze_base()

    def _freeze_base(self) -> None:
        for parameter in self.parameters():
            parameter.requires_grad_(False)
        for parameter in self.adapter.parameters():
            parameter.requires_grad_(True)

    def forward(self, input_ids: Tensor) -> Tensor:
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        if input_ids.shape[1] != self.sequence_length:
            raise ValueError(f"expected sequence length {self.sequence_length}")

        positions = torch.arange(self.sequence_length, device=input_ids.device)
        hidden = self.token_embedding(input_ids) + self.position_embedding(positions)
        hidden = self.encoder(hidden)
        hidden = self.adapter(hidden)
        return self.output_head(self.final_norm(hidden))

    def trainable_parameters(self) -> Iterator[nn.Parameter]:
        return (parameter for parameter in self.parameters() if parameter.requires_grad)

    def frozen_parameters(self) -> Iterator[nn.Parameter]:
        return (parameter for parameter in self.parameters() if not parameter.requires_grad)


def count_parameters(parameters: Iterator[nn.Parameter]) -> int:
    """Count scalar parameters without retaining an intermediate collection."""

    return sum(parameter.numel() for parameter in parameters)
