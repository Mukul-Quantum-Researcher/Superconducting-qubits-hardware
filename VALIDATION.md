# Validation

Run on 23 November 2026 in a Windows Python environment.

Python 3.14.6; numpy 2.3.5, scipy 1.17.1, matplotlib 3.10.9, qutip 5.3.0, pandas 2.3.3

The QuTiP-only ECR notebook completed all 23 code cells in order, with cleared prior outputs, in approximately 299 seconds. Figures and CSV were regenerated. Selected result: 154.4015 ns, coherent average fidelity about 0.99685 after virtual-Z optimisation and leakage about 5.69e-5. Lab-frame and rotating-frame CR checks completed.

This was a headless cell-order execution with captured stdout and Matplotlib figures; it did not use a Jupyter kernel. The original scqubits tutorial was retained and inspected but has not yet been rerun in this environment. HFSS or physical hardware was not involved.

Spectroscopy: 180 saved simulated chevron populations and 33 Rabi points were reanalysed. The fitted transition is about 5011.0265 MHz, the chevron drive frequency about 5.0003 MHz, and the independent Rabi refit about 4.9985 MHz. No fresh trajectory integration or measured-device result is claimed.
