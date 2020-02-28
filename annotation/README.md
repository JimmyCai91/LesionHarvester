## Boxes 

### from Human Annotator
| File Name | Description |
|---|---|
| RECIST-Box-Train.pkl | In the official training split, boxes converted from RECIST marks. |
| RECIST-Box-Valid.pkl | In the official validating split, boxes converted from RECIST marks. |
| RECIST-Box-Test.pkl | In the official testing split, boxes converted from RECIST marks. |
| Revised-Train744.pkl | $V_{M}$ |
| Revised-Train100.pkl | $V_{H}^{test}$ |
| Revised-Test1071.pkl | $V_{D}^{test}$ |
| 3D-Box.pkl | 3D bounding box annotation of volumes selected from $V_{D}^{test}$. |

1. Basing on DeepLesion's implementation, we generate ground-truth bounding box by: RECIST marks -> pad 5px in each direction -> bounding boxes. 
2. We removed RECIST marks which are defined as being noisy by DeepLesion. 
3. Please use the updated version of RECIST-Box-Train.pkl, RECIST-Box-Test.pkl as these two files before commit 'e837df52a8173564222e5b3303a6eeb499795577' (02/28/2020) contains extra annotations from Reivsed-Train744.pkl and Revised-Test1071.pkl, respectively. 


### from Lesion Harvester 
| File Name | Description |
|---|---|
| MinedLesions.pkl | 9805 lesion candidates from 5316 CT sub-volumes from DeepLesion. |
| MinedHardNegatives.pkl | 26595 possible hard negatives mined from 10172 CT sub-volumes from DeepLesion. |
| HardNegatives.pkl | 7440 hard negatives mined from 744 CT sub-volumes from DeepLesion. |
| Detection.pkl | detected 112478 from 1071 CT sub-volumes. |




