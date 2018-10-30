# Pertubrations

The goal is to develop a method as follows:

- **Description:** develop a method for evaluating the stability of analyses, relating the output variation to imposed input variation.
- **Purpose:** to enable the study of relative stability of analyses with respect to arbitrary changes on the initial condition.
- **Goals:** a metric or method that enables characterizing the stability of tools or claims for the purposes of comparison and ultimate selection of tools or parameterizations that lead to more stable results.


In short, the types of comparisons that can be made are the following:

### 1. Data Perturbations
- **Description:** apply this method to evaluate the stability of neuroimaging processing tools with respect to the addition of noise
- **Type of change:** 1-voxel noise, rician noise, acquisition noise (from TRT datasets across aligned sessions), participant noise (from subjects in the same dataset/acquisition sequence)
- **Purpose:** verify the stability of neuroimaging processing tools
- **Input quantity:** aligned images
- **Output quantity:** domain specific feature (i.e. "truth" phenomenon or expected features)
- **Result:** a curve showing the stability of the feature above  with respect to different degrees of changes on input data


### 2. Data Permutations
- **Description:** apply this method to evaluate the stability of neuroimaging analyses with respect to changing datasets
- **Type of change:** datasets
- **Purpose:** evaluate the stability of tools or models across subjects
- **Input quantity:** aligned images
- **Output quantity:** domain specific fitted-model (i.e. clustering, activation map)
- **Result:** a curve showing the stability of the model with respect to changes in subject inclusion in a dataset


### 3. Tool Permutations
- **Description:** apply this method to evaluate the stability of neuroimaging analyses with respect to changing processing tools.
- **Type of change:** processing parameters or entire tools
- **Purpose:** compare the stability of results across parameter choices
- **Input quantity:** aligned images
- **Output quantity:** domain specific feature, summary statistic, or domain specific fitted model.
- **Result:** a curve illustrating the degree of tool/parameter dependence a specific claim or feature has
