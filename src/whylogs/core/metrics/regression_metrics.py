import math
from typing import List

from sklearn.utils.multiclass import type_of_target

from whylogs.proto import RegressionMetricsMessage

SUPPORTED_TYPES = ("regression")


class RegressionMetrics:

    def __init__(self,
                 prediction_field: str = None,
                 target_field: str = None):
        self.prediction_field = prediction_field
        self.target_field = target_field

        self.count = 0
        self.sum_abs_diff = 0.0
        self.sum_diff = 0.0
        self.sum2_diff = 0.0
        # to add later
        # self.nt_diff = whylogs.core.statistics.NumberTracker()

    def add(self, predictions: List[float],
            targets: List[float]):
        """
        Function adds predictions and targets computation of regression metrics.

        Args:
            predictions (List[float]):
            targets (List[float]):

        Raises:
            NotImplementedError: in case targets do not fall into continuous support
            ValueError: incase missing validation or predictions
        """
        tgt_type = type_of_target(targets)
        if tgt_type not in ("continuous"):
            raise NotImplementedError(f"target type: {tgt_type} not supported for these metrics")

        if not isinstance(targets, list):
            targets = [targets]
        if not isinstance(predictions, list):
            predictions = [predictions]

        if len(targets) != len(predictions):
            raise ValueError(
                "both targets and predictions need to have the same length")
        # need to vectorize this
        for idx, target in enumerate(targets):

            self.sum_abs_diff += abs(predictions[idx] - target)
            self.sum_diff += predictions[idx] - target
            self.sum2_diff += (predictions[idx] - target)**2
            # To add later
            # self.nt_diff.track(predictions[idx] - target)
            self.count += 1

    def mean_absolute_error(self):
        if self.count == 0:
            return None
        return self.sum_abs_diff / self.count

    def mean_squared_error(self):
        if self.count == 0:
            return None
        return self.sum2_diff / self.count

    def root_mean_squared_error(self):
        if self.count == 0:
            return None
        return math.sqrt(self.sum2_diff / self.count)

    def merge(self, other_reg_met):
        """
        Merge two seperate confusion matrix which may or may not overlap in labels.

        Args:
              other_reg_met : regression metrics to merge with self
        Returns:
              RegressionMetrics: merged regression metrics
        """
     
        if self.count == 0:
            return other_reg_met
        if other_reg_met.count == 0:
            return self

        new_reg = RegressionMetrics()
        new_reg.count = self.count + other_reg_met.count
        new_reg.sum_abs_diff = self.sum_abs_diff + other_reg_met.sum_abs_diff
        new_reg.sum_diff = self.sum_diff + other_reg_met.sum_diff
        new_reg.sum2_diff = self.sum2_diff + other_reg_met.sum2_diff

        return new_reg

    def to_protobuf(self, ):
        """
        Convert to protobuf

        Returns:
            TYPE: Protobuf Message
        """

        return RegressionMetricsMessage(
            prediction_field=self.prediction_field,
            target_field=self.target_field,
            count=self.count,
            sum_abs_diff=self.sum_abs_diff,
            sum_diff=self.sum_diff,
            sum2_diff=self.sum2_diff)

    @classmethod
    def from_protobuf(cls, message: RegressionMetricsMessage, ):
        if message.ByteSize() == 0:
            return None

        reg_met = RegressionMetrics()
        reg_met.count = message.count
        reg_met.sum_abs_diff = message.sum_abs_diff
        reg_met.sum_diff = message.sum_diff
        reg_met.sum2_diff = message.sum2_diff

        return reg_met