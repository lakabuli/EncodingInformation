from jax import jit
import jax.numpy as np
import warnings

from .model_base_class import MeasurementNoiseModel


class AnalyticGaussianNoiseModel(MeasurementNoiseModel):
    """
    Analytical model for estimating the conditional entropy H(Y | X) when the noise proces
    is additive independent Gaussian noise at each pixel.
    """
    
    def __init__(self, sigma):
        """
        Initialize the AnalyticGaussianNoiseModel.

        Parameters
        ----------
        sigma : float
            Standard deviation of the Gaussian noise.
        """
        self.sigma = sigma

    def estimate_conditional_entropy(self, images=None):
        """
        Compute the conditional entropy H(Y | X) for Gaussian noise.

        Parameters
        ----------
        images : jax.Array, optional
            Unused in this model. The parameter is kept for compatibility.

        Returns
        -------
        float
            The computed conditional entropy, given by the formula:
            0.5 * log(2 * pi * e * sigma^2).
        """
        if images is not None:
            warnings.warn("The images argument is not used in the Analytic Gaussian noise model.")
        # Conditional entropy H(Y | X) for Gaussian noise
        return 0.5 * np.log(2 * np.pi * np.e * self.sigma**2)

class PoissonNoiseModel(MeasurementNoiseModel):
    """
    Poisson noise model for estimating the conditional entropy H(Y | X) from empirical data.
    """

    def estimate_conditional_entropy(self, images):
        """
        Compute the conditional entropy H(Y | X) for Poisson noise.

        Parameters
        ----------
        images : jax.Array
            A dataset of images, preferably clean. This is used to compute the conditional entropy.

        Returns
        -------
        float
            The average conditional entropy per pixel, computed using a Gaussian approximation.
        """
        # do the actual computation here
        images = images.reshape(-1, images.shape[-2] * images.shape[-1])
        n_pixels = images.shape[-1]
        
        # Conditional entropy H(Y | x) for Poisson noise
        gaussian_approx = 0.5 * (np.log(2 * np.pi * np.e) + np.log(images))
        gaussian_approx = np.where(images <= 0, 0, gaussian_approx)
        per_image_entropies = np.sum(gaussian_approx, axis=1) / n_pixels
        return np.mean(per_image_entropies) # h(y|x) per pixel


class AnalyticComplexPixelGaussianNoiseModel(MeasurementNoiseModel):
    """
    Analytical model for estimating the conditional entropy H(Y | X) with complex-valued pixels when the noise process is additive independent Gaussian noise at each pixel 
    with different standard deviation at each pixel.
    """

    def __init__(self, sigma_vec):
        """
        :param sigma_vec: Vector of standard deviations of the Gaussian noise at each pixel
        """
        self.sigma_vec = sigma_vec

    def estimate_conditional_entropy(self, images=None):
        # input vector here if it's complex-valued items will be half the length of the vector used in the other computations. this has the number of complex-valued pixels. 
        # D log2 2 pi e + 2 sum log_2 sigma_i -> instead, computing here in log space because final MI computation will convert it to log2
        # returning total conditional entropy here
        constant_term = self.sigma_vec.shape[0] * np.log(2 * np.pi * np.exp(1))
        sum_log_sigmas = 2 * np.sum(np.log(self.sigma_vec))
        return constant_term + sum_log_sigmas