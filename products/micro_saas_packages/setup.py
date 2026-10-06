#!/usr/bin/env python3
"""
Genesis Web3 Micro-Tooling Suite & SDK
Packaging Solana Token-2022 Harvester and Multi-Chain Resilient RPC Failover.
"""

from setuptools import setup, find_packages

setup(
    name="genesis-web3-tools",
    version="1.0.0",
    description="High-performance Web3 developer tooling: Solana Token-2022 Fee Harvester and Multi-Chain Resilient RPC Failover",
    author="Dexter Mos (@dextermos / @dextermostard)",
    author_email="dextermos@users.noreply.github.com",
    url="https://github.com/dextermos/genesis-bounty-hunter",
    packages=find_packages(),
    py_modules=[
        "tools.solana_fee_harvester",
        "tools.solana_metadata_extractor",
        "tools.rpc_resilient_failover"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.8",
)
