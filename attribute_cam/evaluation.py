import numpy
import tqdm

def accetptable_mask_ratio(activation, mask, mask_size):
  # count pixels with activation and check whether they are within or outside of mask
  activated = activation>0
  count_activated = numpy.sum(activated)

  if count_activated:
    count_true_positive = numpy.sum(activated * mask > 0)
#        count_false_positive = count_activated - count_true_positive

    amr = count_true_positive/count_activated
    amr_corr = (amr * ((mask.size-mask_size)/mask.size))
  else:
    amr = 0.
    amr_corr = 0.

#    mask_relative = round((mask_size/mask.size), 2)

  return amr, amr_corr #, mask_relative, count_activated, count_true_positive, count_false_positive


def amr_statisics(celeba_dataset, filter_function, masks, mask_sizes):

  means = {}
  stds = {}
  for attribute in tqdm.tqdm(celeba_dataset.attributes):
    # compute AMR and corrected AMR for this attribute
    amr = []
    for image_index in celeba_dataset:
      if filter_function(image_index, attribute):
        activation, _ = celeba_dataset.load_cam(attribute, image_index)

        amr.append(accetptable_mask_ratio(activation,masks[attribute],mask_sizes[attribute]))

    # compute mean and std
    if amr:
      means[attribute] = numpy.mean(amr, axis=0)
      stds[attribute] = numpy.std(amr, axis=0)
    else:
      means[attribute] = [0,0]
      stds[attribute] = [0,0]

  return means, stds

# computes the error rates for the given ground truth and predictions, averaged over the complete dataset, and separately for all attributes
def error_rate(celeba_dataset, ground_truth, prediction, balanced=False):
  errors = {}
  for attribute in celeba_dataset.attributes:
    # compute items of the confusion matrix: positives, negatives, false-positives and false-negatives
    FP,P,FN,N = 0,0,0,0
    for image_index in celeba_dataset:
      gt = ground_truth[image_index][attribute]
      pr = prediction[image_index][attribute]
      if gt == 1:
        P += 1
        if pr < 0:
          FN += 1
      else:
        N += 1
        if pr >= 0:
          FP += 1
    # compute error rates based on these
    if balanced:
      errors[attribute] = (FN / N + FP / P) / 2
    else:
      errors[attribute] = (FN + FP) / (P+N)
  return errors
