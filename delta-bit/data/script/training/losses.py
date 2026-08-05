import tensorflow as tf
from tensorflow import keras

class OversizeLoss(keras.losses.Loss):

    def __init__(self, weight=1.0, name="oversize_penalty"):
        super().__init__(name=name)
        self.weight = weight

    def call(self, y_true, y_pred):

        # flatten per sample
        y_true_f = tf.reshape(y_true, [tf.shape(y_true)[0], -1])
        y_pred_f = tf.reshape(y_pred, [tf.shape(y_pred)[0], -1])

        # false positive probabilities
        false_positive = tf.nn.relu(y_pred_f - y_true_f)

        fp_volume = tf.reduce_sum(false_positive, axis=1)

        #gt_volume = tf.reduce_sum(y_true_f, axis=1)

        penalty = tf.square(fp_volume)# - gt_volume)

        return self.weight * tf.reduce_mean(penalty)
    
    def get_config(self):
        config = super().get_config()
        config.update({
            "weight": self.weight,
        })
        return config

class DiceBCELoss(keras.losses.Loss):

    def __init__(
        self,
        smooth=1e-6,
        dice_weight=1.0,
        bce_weight=1.0,
        from_logits=False,
        name="dice_bce_loss"
    ):
        super().__init__(name=name)

        self.smooth = smooth
        self.dice_weight = dice_weight
        self.bce_weight = bce_weight
        self.from_logits = from_logits

        self.bce = keras.losses.BinaryCrossentropy(
            from_logits=from_logits
        )

    def call(self, y_true, y_pred):

        # Dice should use probabilities
        if self.from_logits:
            y_pred_prob = tf.nn.sigmoid(y_pred)
        else:
            y_pred_prob = y_pred

        # Flatten per sample
        y_true_f = tf.reshape(y_true, [tf.shape(y_true)[0], -1])
        y_pred_f = tf.reshape(y_pred_prob, [tf.shape(y_pred_prob)[0], -1])

        intersection = tf.reduce_sum(y_true_f * y_pred_f, axis=1)

        union = tf.reduce_sum(y_true_f + y_pred_f, axis=1)

        dice = (2.0 * intersection + self.smooth) / (union + self.smooth)

        dice_loss = 1.0 - tf.reduce_mean(dice)

        bce_loss = self.bce(y_true, y_pred)

        return (
            self.dice_weight * dice_loss
            + self.bce_weight * bce_loss
        )

    def get_config(self):
        config = super().get_config()
        config.update({
            "smooth": self.smooth,
            "dice_weight": self.dice_weight,
            "bce_weight": self.bce_weight,
            "from_logits": self.from_logits,
        })
        return config

class DiceBFocalLoss(keras.losses.Loss):

    def __init__(self, smooth=1e-6, name="dice_focal_loss"):
        super().__init__(name=name)
        self.smooth=smooth
        self.focal = keras.losses.BinaryFocalCrossentropy(
            from_logits=False
        )
    
    def call(self, y_true, y_pred):

        y_true_f = tf.reshape(y_true, [tf.shape(y_true)[0], -1])
        y_pred_f = tf.reshape(y_pred, [tf.shape(y_pred)[0], -1])

        intersection = tf.reduce_sum(y_true_f * y_pred_f, axis=1)

        union = tf.reduce_sum(y_true_f + y_pred_f, axis=1)

        dice = (2.0 * intersection + self.smooth) / (union + self.smooth)

        dice_loss = 1.0 - tf.reduce_mean(dice)

        focal_loss = self.focal(y_true, y_pred)

        return dice_loss + focal_loss
    
    def get_config(self):
        config = super().get_config()
        config.update({
            "smooth": self.smooth,
            "dice_weight": self.dice_weight,
            "bce_weight": self.bce_weight,
            "from_logits": self.from_logits,
        })
        return config



class DiceBFocalTverskyLoss(keras.losses.Loss):

    def __init__(self, alpha=0.7, beta=0.3, smooth=1e-6, name="focal_tversky_loss"):
        super().__init__(name=name)
        self.alpha=alpha
        self.beta=beta
        self.smooth=smooth
        self.focal = keras.losses.BinaryFocalCrossentropy(
            from_logits=False
        )
    
    def call(self, y_true, y_pred):

        y_true_f = tf.reshape(y_true, [tf.shape(y_true)[0], -1])
        y_pred_f = tf.reshape(y_pred, [tf.shape(y_pred)[0], -1])

        tp = tf.reduce_sum(y_true_f * y_pred_f, axis=1)

        fp = tf.reduce_sum((1.0 - y_true_f) * y_pred_f, axis=1)

        fn = tf.reduce_sum(y_true_f * (1.0 - y_pred_f), axis=1)

        tversky = (
            tp + self.smooth
        ) / (
            tp
            + self.alpha * fp
            + self.beta * fn
            + self.smooth
        )

        tversky_loss = 1.0 - tf.reduce_mean(tversky)

        focal_loss = self.focal(y_true, y_pred)

        return focal_loss + tversky_loss
    
    def get_config(self):
        config = super().get_config()

        config.update({
            "alpha": self.alpha,
            "beta": self.beta,
            "smooth": self.smooth,
        })

        return config

class CombinedLoss(keras.losses.Loss):

    def __init__(
        self,
        dice_loss,
        oversize_loss,
        name="combined_loss"
    ):
        super().__init__(name=name)

        self.dice_loss = dice_loss
        self.oversize_loss = oversize_loss

    def call(self, y_true, y_pred):

        return (
            self.dice_loss(y_true, y_pred)
            + self.oversize_loss(y_true, y_pred)
        )
    
    def get_config(self):
        config = super().get_config()

        config.update({
            "dice_loss": keras.saving.serialize_keras_object(
                self.dice_loss
            ),
            "oversize_loss": keras.saving.serialize_keras_object(
                self.oversize_loss
            )
        })

        return config
    
    @classmethod
    def from_config(cls, config):
        dice_loss = keras.saving.deserialize_keras_object(
            config.pop("dice_loss")
        )

        oversize_loss = keras.saving.deserialize_keras_object(
            config.pop("oversize_loss")
        )

        return cls(
            dice_loss=dice_loss,
            oversize_loss=oversize_loss,
            **config
        )