import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import os
from tqdm import tqdm
import numpy as np
import pandas as pd
import torch.onnx

class BidirectionalGRU(nn.Module):
    """Bidirectional GRU for encoding sequences"""
    def __init__(self, embedding_dim, hidden_dim, num_layers=1, dropout=0.0): #layers could be one or two
        super(BidirectionalGRU, self).__init__()
        
        self.gru = nn.GRU(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
    
    def forward(self, embeddings, lengths):
        """
        Args:
            embeddings: Embedding tensors [batch_size, seq_len, embedding_dim]
            lengths: Length of each sequence in the batch
            
        Returns:
            encoding: GRU encoding [batch_size, hidden_dim*2]
        """
        # Pack padded sequence
        packed = nn.utils.rnn.pack_padded_sequence(
            embeddings, 
            lengths.cpu(),
            batch_first=True,
            enforce_sorted=False
        )
        
        # Forward through GRU
        _, hidden = self.gru(packed)
        
        # Get the last layer's forward and backward states
        hidden = hidden.transpose(0, 1)  # [num_layers*2, batch, hidden] -> [batch, num_layers*2, hidden]
        
        # Concatenate the last layer's forward and backward states
        last_forward = hidden[:, -2, :]
        last_backward = hidden[:, -1, :]
        encoding = torch.cat([last_forward, last_backward], dim=1)
        
        return encoding