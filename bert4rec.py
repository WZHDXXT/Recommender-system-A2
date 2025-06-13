import torch
import torch.nn as nn
from transformers import BertModel, BertConfig

class BERT4Rec(nn.Module):
    def __init__(self, vocab_size, hidden_size=256, max_seq_length=100, num_layers=4, num_heads=4, dropout=0.2):
        super(BERT4Rec, self).__init__()

        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        self.hidden_size = hidden_size  # Set to 768 to match BERT's hidden size

        # item embedding
        self.item_embedding = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        # position embedding
        self.position_embedding = nn.Embedding(max_seq_length, hidden_size)

        # HuggingFace BERT config
        bert_config = BertConfig(
            vocab_size=vocab_size,
            hidden_size=hidden_size,  # Make sure hidden_size matches BERT's hidden size
            num_hidden_layers=num_layers,
            num_attention_heads=num_heads,
            intermediate_size=hidden_size * 4,
            max_position_embeddings=max_seq_length,
            hidden_dropout_prob=dropout,
            attention_probs_dropout_prob=dropout,
        )

        self.bert = BertModel(bert_config)
        self.output_layer = nn.Linear(hidden_size, vocab_size)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input_ids, masked_positions):
        device = input_ids.device
        batch_size, seq_len = input_ids.size()

        position_ids = torch.arange(seq_len, dtype=torch.long, device=device)
        position_ids = position_ids.unsqueeze(0).expand_as(input_ids)  # [batch, seq]
        
        # item embedding
        item_emb = self.item_embedding(input_ids)
        # position embedding
        pos_emb = self.position_embedding(position_ids)
        embeddings = item_emb + pos_emb
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)

        # attention mask for padding tokens
        attention_mask = input_ids.ne(0).long()  
        outputs = self.bert(inputs_embeds=embeddings, attention_mask=attention_mask)
        
        # final hidden representation
        sequence_output = outputs.last_hidden_state  
        
        # gather the hidden representation of masked_positions
        masked_output = self._gather_positions(sequence_output, masked_positions)

        # prediction over vocab
        logits = self.output_layer(masked_output)  # [batch, num_masked, vocab_size]

        return logits

    def _gather_positions(self, sequence_output, positions):

        # number of user and mask position
        batch_size, num_pos = positions.size()
        hidden_size = sequence_output.size(-1)

        # flatten index of masks
        flat_offsets = torch.arange(batch_size, device=positions.device) * sequence_output.size(1)
        flat_positions = (positions + flat_offsets.unsqueeze(1)).view(-1).long()

        # extract real words from the flat_positions of masks
        flat_seq_output = sequence_output.contiguous().view(-1, hidden_size)
        selected = flat_seq_output[flat_positions] 
        # back to the original shape of masks
        return selected.view(batch_size, num_pos, hidden_size)