# -*- coding: utf-8 -*-
# File   : rnn_utils.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 25/01/2018
# 
# This file is part of Jacinle.

from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from jactorch.functional.indexing import inverse_permutation


def rnn_with_length(rnn, seq_tensor, seq_lengths, initial_states, batch_first=True, sorted=False):
    perm_idx = None
    if not sorted:
        seq_lengths, perm_idx = seq_lengths.sort(0, descending=True)
        seq_tensor = seq_tensor[perm_idx]

    packed_input = pack_padded_sequence(seq_tensor, seq_lengths.data.cpu().numpy(), batch_first=batch_first)
    packed_output, last_output = rnn(packed_input, initial_states)
    output, _ = pad_packed_sequence(packed_output, batch_first=batch_first)

    if not sorted:
        perm_inv = inverse_permutation(perm_idx)
        output = output[perm_inv]
        if type(last_output) is tuple:
            last_output = tuple(map(lambda x: x.index_select(1, perm_inv), last_output))
        else:
            last_output = last_output.index_select(1, perm_inv)

    return output, last_output