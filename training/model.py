import torch.nn as nn
from transformers import (
    AutoTokenizer,
    AutoConfig,
    BertPreTrainedModel,
    BertModel
)


class Model(BertPreTrainedModel):
    """
    Class for our custom model that builds upon a pretrained BERT model.
    """
    def __init__(self, config):
        super().__init__(config)

        # Initialise a BERT model
        self.bert = BertModel(config)
        
        # Setup CLS layer for 3-class classification
        self.cls_layer = nn.Linear(config.hidden_size, 3)

    def forward(self, input_ids, attention_mask):
        # Feed input to BERT and obtain outputs.
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # Obtain representations of [CLS] heads.
        cls_reps = outputs.last_hidden_state[:, 0]
        # Put these representations to classification layer to obtain logits.
        logits = self.cls_layer(cls_reps)
        # Return logits.
        return logits
