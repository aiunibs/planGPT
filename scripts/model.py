from dataclasses import dataclass
from typing import Optional, Tuple, Union, List, Callable, Iterable, Set
import torch
import torch.distributed as dist
import torch.utils.checkpoint
from torch.nn import CrossEntropyLoss
from transformers import GPT2LMHeadModel
from transformers.modeling_outputs import CausalLMOutputWithCrossAttentions
from transformers.generation import GreedySearchDecoderOnlyOutput
from transformers.generation import LogitsProcessorList
from transformers.generation import Constraint
from transformers.generation import StoppingCriteriaList, validate_stopping_criteria
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
import inspect
import warnings

# from SimulationMixin import SimulationMixin
from transformers.utils import logging

logger = logging.get_logger(__name__)


# class GPT2PModel(GPT2LMHeadModel, SimulationMixin):
class GPT2PModel(GPT2LMHeadModel):
    def __init__(self, config):
        super().__init__(config)

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        token_type_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        encoder_hidden_states: Optional[torch.Tensor] = None,
        encoder_attention_mask: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        actions_idx: Optional[torch.LongTensor] = None,
        eop_idx: Optional[torch.LongTensor] = None,
    ) -> Union[Tuple, CausalLMOutputWithCrossAttentions]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for language modeling. Note that the labels **are shifted** inside the model, i.e. you can set
            `labels = input_ids` Indices are selected in `[-100, 0, ..., config.vocab_size]` All labels set to `-100`
            are ignored (masked), the loss is only computed for labels in `[0, ..., config.vocab_size]`
        """
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )

        transformer_outputs = self.transformer(
            input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_attention_mask,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        hidden_states = transformer_outputs[0]

        # Set device for model parallelism
        if self.model_parallel:
            torch.cuda.set_device(self.transformer.first_device)
            hidden_states = hidden_states.to(self.lm_head.weight.device)

        lm_logits = self.lm_head(hidden_states)

        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n, but only for tokens after <|actions|>
            # The <|actions|> token could be in a different position for the examples
            # in the batch.
            loss_fct = (
                CrossEntropyLoss()
            )  # No need to specify ignore index, data collator already takes care of that

            logits_list = []
            labels_list = []
            for i in range(lm_logits.shape[0]):  # shape[0] is the batch size
                start_index = actions_idx[i].item()
                shift_logits = lm_logits[i, start_index:-1, :].contiguous()
                shift_labels = labels[i, 1 + start_index :].contiguous()
                logits_list.append(shift_logits)
                labels_list.append(shift_labels)

            length_of_first = logits_list[0].size(0)
            are_tensors_same_length = all(
                x.size(0) == length_of_first for x in logits_list
            )
            if are_tensors_same_length:
                final_lm_logits = torch.stack(logits_list, dim=0)
                final_labels = torch.stack(labels_list, dim=0)
            else:
                max_length = max(x.size(0) for x in logits_list)
                final_lm_logits = lm_logits.new_full(
                    [len(logits_list), max_length, logits_list[0].size(1)], 0.0
                )
                for i, single_logits in enumerate(logits_list):
                    final_lm_logits[i, : single_logits.size(0), :] = single_logits
                final_labels = labels.new_full([len(labels_list), max_length], -100)
                for i, single_labels in enumerate(labels_list):
                    final_labels[i, : single_labels.size(0)] = single_labels

            loss_fct = (
                CrossEntropyLoss()
            )  # No need to specify ignore index, data collator already takes care of that
            loss = loss_fct(
                final_lm_logits.view(-1, final_lm_logits.size(-1)),
                final_labels.view(-1),
            )

        if not return_dict:
            output = (lm_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output

        return CausalLMOutputWithCrossAttentions(
            loss=loss,
            logits=lm_logits,
            past_key_values=transformer_outputs.past_key_values,
            hidden_states=transformer_outputs.hidden_states,
            attentions=transformer_outputs.attentions,
            cross_attentions=transformer_outputs.cross_attentions,
        )
