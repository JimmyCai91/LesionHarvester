# DeepLesion Annotation  
To harvest lesions from the [DeepLesion](https://nihcc.app.box.com/v/DeepLesion) dataset, we randomly select $844$ volumes from the original $14\,075$ training CT. These are then annotated by a board-certified radiologist. Of these, we select $744$ as $V_{M}$ ($5.3\%$) and leave another $100$ as an evaluation set for lesion harvesting. This latter subset, denoted $V_{H}^{test}$, is treated identically at $V_{H}$, meaning the algorithm only sees the original DeepLesion RECIST marks. After convergence, we can measure the precision and recall of the harvested lesions. In addition, we later measure detection performance on systems trained on our harvested lesions by also fully annotating $1,071$ of the testing CT volumes. These volumes, denoted $V_{D}^{test}$, are never seen in our harvesting framework.  

<!---
## ToDo
- [ ] Update evaluation code based on current annotations. 
--->

## Data Structure
|- annotation  
|- |- RECIST-Box-Train.pkl # In the official training split, boxes converted from RECIST marks.  
|- |- RECIST-Box-Valid.pkl # In the official validating split, boxes converted from RECIST marks.  
|- |- RECIST-Box-Test.pkl  # In the official testing split, boxes converted from RECIST marks.  
|- |- Revised-Train744.pkl # $V_{M}$  
|- |- Revised-Train100.pkl # $V_{H}^{test}$  
|- |- Revised-Test1071.pkl # $V_{D}^{test}$  
|- |- 3D-Box.pkl # 3D bounding box annotation of volumes selected from $V_{D}^{test}$.  
|  
|- DL_save_nifti.py 

## Usage 
1. Convert data formation from *png* to *nifti*:  
   Please download [**DL_save_nifti.py**](https://nihcc.app.box.com/v/DeepLesion/file/305578281723) from the official website of [DeepLesion](https://nihcc.app.box.com/v/DeepLesion). Then run, 
    ```python 
    python DL_save_nifti.py 
    ```
    It generates CT subvolumes named in the format of *PatientID_StudyID_ScanID_StartingSliceID_EndingSliceID.nii.gz*, for example "001344_01_01_012-024.nii.gz".

2. Read 2D box annotation
    ```python
    import pickle 
    annotation = pickle.load(open(dir_to_annotation_file, 'rb'))
    print(annotation['001344_01_01_012-024']) 
    # {6: [[215.383, 176.983, 267.122, 220.374, 6.0, 6.0]]} 
    ```
    Annotation of each CT volume is storied as **python dictionary**. The key-value pair is in the format of *{key: [[$x_{min}$, $y_{min}$, $x_{max}$, $y_{max}$, $z_{min}$, $z_{max}$]]}*. 

3. Read 3D box annotation
    ```python
    import pickle 
    annotation = pickle.load(open(dir_to_annotation_file, 'rb'))
    print(annotation['000001_01_01_103-115'])
    # [[224.11279125118176, 92.50398222171341, 241.87335205606877, 113.86161863265343, 5.0, 6.0], [234.21612865759417, 78.1168292149383, 256.46265925305823, 104.75412242792794, 5.0, 6.0]]
    ```
    Annotation of each CT volume is storied as **python list**. Each list element is in the format of *[$x_{min}$, $y_{min}$, $x_{max}$, $y_{max}$, $z_{min}$, $z_{max}$]*.

## Citation
If you find this repository useful for your research, please use the following BibTex entry. 
```
@inproceedings{cai2020harvester,
  title={Lesion Harvester: Iteratively Mining Unlabeled Lesions and Hard-Negative Examples at Scale},
  author={Jinzheng Cai, Adam P. Harrison, Youjing Zheng, Ke Yan, Yuankai Huo, Jing Xiao, Ling Yang, and Le Lu},
  booktitle={arXiv preprint arXiv:2001.07776},
  year={2020}
}
```