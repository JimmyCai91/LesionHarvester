# --------------------------------------------------------
# Lesion Harvester
# Licensed under The MIT License [see LICENSE for details]
# Written by Jinzheng Cai
# -------------------------------------------------------

import os
import tqdm
import pickle
import numpy as np

from scipy import interpolate

from voc_eval_lib import voc_ap 


def IoU(detected_box, groundtruth_box):
  '''Compute overlaps or so called IoU between boxes.'''

  # measure the intersection area
  ixmin = np.maximum(groundtruth_box[:, 0], detected_box[0])
  iymin = np.maximum(groundtruth_box[:, 1], detected_box[1])
  ixmax = np.minimum(groundtruth_box[:, 2], detected_box[2])
  iymax = np.minimum(groundtruth_box[:, 3], detected_box[3])

  iwidth = np.maximum(ixmax - ixmin + 1., 0.)
  iheight = np.maximum(iymax - iymin + 1., 0.)
  inters = iwidth * iheight

  # measure the union area
  uni = ((detected_box[2] - detected_box[0] + 1.) * (detected_box[3] - detected_box[1] + 1.) +
        (groundtruth_box[:, 2] - groundtruth_box[:, 0] + 1.) *
        (groundtruth_box[:, 3] - groundtruth_box[:, 1] + 1.) - inters)

  overlaps = inters / np.maximum(1e-6, uni)
    
  return overlaps


def P3DIoU(recist_box, tracklet):
  '''
    P3D IoU Evaluation Metric
    input:
      recist_box (tuple): (z, [[x_min, y_min, x_max, y_max]])
      tracklet (dictionary): {z1: [x1_min, y1_min, x1_max, y1_max], 
                 z2: [x2_min, y2_min, x2_max, y2_max], ...}
    algorithm:
      if z == z_i and z_i in [z1, z2, ...]:
        return IoU([x_min, y_min, x_max, y_max], [xi_min, yi_min, xi_max, yi_max])
      else:
        return 0
  '''
  boxes = np.array([xy for _, xy in tracklet])
  zs = [z for z, _ in tracklet]
  z, xy = recist_box
  if z in zs:
    ovr = IoU(xy[0], boxes)[zs.index(z)]
  else:
    ovr = 0
  return ovr




if __name__ == '__main__':

    p3d_iou_thresh = 0.5

    ############################
    # Part1: load annotation
    ##############################
    annotation_dir = './annotation/Revised-Test1071.pkl'
    annotation = pickle.load(open(annotation_dir, 'rb'))

    volume_recs = {}
    for k in annotation.keys():
      volume_recs[k.replace('.annot','')] = []

    n_recist = 0
    for k, v in annotation.items():
        volume_id = k.replace('.annot','')
        if len(v) == 0:
          continue
        z_idxes = np.sort([z for z in v.keys()])
        for z in z_idxes:
          xys = v[z]
          for xy in xys:
            volume_recs[volume_id] += [(z, np.array(xy[:4]).reshape((1,-1)))]
            n_recist += 1

    ###############################
    # Part2: load detection result
    ##################################
    detections = pickle.load(open('./detection/detectedTest1071.pkl', 'rb'))

    volume_ids, det_confs, BB, pred_confs, gts = [], [], [], [], []
    for volume_id, data in tqdm.tqdm(detections.items()):

      if len(data) == 0:
        # No detection in current CT volume
        continue

      for v in data:

        confs, tracklet = [], []
        for z, xy in v:
          confs.append(xy[-1])
          tracklet.append((z, xy[:-1]))
        
        BB.append(tracklet)
        det_confs.append(np.array(confs).max())
        volume_ids.append(volume_id)

        overlaps = np.array([P3DIoU(recist, BB[-1]) for recist in volume_recs[volume_ids[-1]]])
        if (len(overlaps) > 0) and (overlaps.max() >= p3d_iou_thresh):
            gts.append(1)
        else:
            gts.append(0)

    det_confs = np.array(det_confs)
    gts = np.array(gts)


    ###########################
    # Part3: do evaluation 
    ###########################
    scores = det_confs
    ord = np.argsort(scores)[::-1]

    nImg = len(volume_recs)
    hits = {}
    for n, v in volume_recs.items():
        hits[n] = np.zeros((len(v),), dtype=bool)

    nHits = 0 
    nMissFPS = 0
    nMissAP = 0

    nPositive = 0
    tps = []
    fpsFPS = []
    fpsAP = []

    for i in ord:
      overlaps = np.array([P3DIoU(recist, BB[i]) for recist in volume_recs[volume_ids[i]]])
      if (len(overlaps) == 0) or (overlaps.max() < p3d_iou_thresh):
        nMissFPS += 1 
        nMissAP += 1
      else:
        nPositive += 1
        for j in range(len(overlaps)):
          if (overlaps[j] >= p3d_iou_thresh):
            if (not hits[volume_ids[i]][j]):
              hits[volume_ids[i]][j] = True 
              nHits += 1
            else:
              nMissAP += 1

      tps.append(nHits)
      fpsFPS.append(nMissFPS)
      fpsAP.append(nMissAP)

    npos = n_recist
    rec = np.array(tps) / float(npos)
    prec = np.array(tps) / np.maximum(np.array(tps)+np.array(fpsAP), np.finfo(np.float64).eps)
    ap = voc_ap(rec, prec, use_07_metric=False)
    print('Average precision (AP): {:.4f}'.format(ap)) 

    # FROC used in here (https://github.com/rsummers11/CADLab/tree/master/MULAN_universal_lesion_analysis) 
    # for evaluating lesion detection in DeepLesion. 
    # Code for evaluation: https://github.com/rsummers11/CADLab/blob/1192f13b1a6fc0beb3407534a9d3ef7b59df6ba0/lesion_detector_3DCE/rcnn/utils/evaluation.py.
    nGt = n_recist
    sens = np.array(tps, dtype=float) / nGt 
    fp_per_img = np.array(fpsFPS, dtype=float) / nImg 
    f = interpolate.interp1d(fp_per_img, sens, fill_value='extrapolate')
    res = f(np.array([0.125, 0.25, 0.5, 1, 2, 4, 8, 16]))
    print('\nSensitivity @', [0.125, 0.25, 0.5, 1, 2, 4, 8, 16], '\n average FPs per patient/volume:', ['{:.4f}'.format(re) for re in res]) 