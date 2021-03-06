# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

from scipy import linalg
import numpy as np

from qiskit.qasm import pi

from ..qfts.qft import set_up
from . import IQFT


class Standard(IQFT):
    """A normal standard IQFT."""

    CONFIGURATION = {
        'name': 'STANDARD',
        'description': 'Inverse QFT',
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'std_iqft_schema',
            'type': 'object',
            'properties': {
            },
            'additionalProperties': False
        }
    }

    def __init__(self, num_qubits):
        super().__init__()
        self._num_qubits = num_qubits

    def construct_circuit(self, mode, qubits=None, circuit=None):
        if mode == 'vector':
            # note the difference between QFT and DFT in the phase definition:
            # QFT: \omega = exp(2*pi*i/N) ; DFT: \omega = exp(-2*pi*i/N)
            # so linalg.dft is correct for IQFT
            return linalg.dft(2 ** self._num_qubits, scale='sqrtn')
        elif mode == 'circuit':
            circuit, qubits = set_up(circuit, qubits, self._num_qubits)

            for j in reversed(range(self._num_qubits)):
                circuit.u2(0, np.pi, qubits[j])
                for k in reversed(range(j)):
                    lam = -1.0 * pi / float(2 ** (j - k))
                    circuit.u1(lam / 2, qubits[j])
                    circuit.cx(qubits[j], qubits[k])
                    circuit.u1(-lam / 2, qubits[k])
                    circuit.cx(qubits[j], qubits[k])
                    circuit.u1(lam / 2, qubits[k])
            return circuit
        else:
            raise ValueError('Mode should be either "vector" or "circuit"')
