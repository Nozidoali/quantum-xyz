from setuptools import setup, find_packages

setup(
    name="quantum-xyz",
    version="0.1.0",
    packages=find_packages(include=["quantum_xyz", "quantum_xyz.*"]),
    install_requires=[
        """
                            llist==0.7.1
                            matplotlib==3.7.1
                            numpy==1.23.5
                            pygraphviz==1.9
                            qiskit==0.43.1
                            qiskit_ibmq_provider==0.20.2
                            qiskit_terra==0.24.1
                            scipy==1.10.1
                            setuptools==67.8.0
                        """
    ],
)
