import os
import numpy as np
import pytest
from skimage.metrics import structural_similarity as ssim
from numpy.testing import assert_
from gpim import skgpr, gprutils

test_data = os.path.join(
    os.path.dirname(__file__), 'test_data/2D_testdata.npy')
test_expected_result = os.path.join(
    os.path.dirname(__file__), 'test_data/2D_reconst_skgpr.npy')
test_data3d = os.path.join(
    os.path.dirname(__file__), 'test_data/bepfm_test_data_sparse.npy')


@pytest.mark.parametrize('kernel', ['RBF', 'Matern52'])
def test_skgpr_2d(kernel):
    R = np.load(test_data)
    R_ = np.load(test_expected_result)
    X = gprutils.get_sparse_grid(R)
    X_true = gprutils.get_full_grid(R)
    mean, _ = skgpr.skreconstructor(
        X, R, X_true, kernel=kernel,
        lengthscale=[[1., 1.], [4., 4.]],
        grid_points_ratio=1., learning_rate=0.1,
        iterations=20, calculate_sd=False, num_batches=1,
        use_gpu=False, verbose=False).run()
    assert_(ssim(mean, R_) > 0.98)
    assert_(np.linalg.norm(mean - R_) < 1)


@pytest.mark.parametrize('kernel', ['RBF', 'Matern52'])
def test_skgpr_3d(kernel):  # sanity check only, due to comput cost
    R = np.load(test_data3d)
    X = gprutils.get_sparse_grid(R)
    X_true = gprutils.get_full_grid(R)
    (mean, sd), _ = skgpr.skreconstructor(
        X, R, X_true, kernel=kernel,
        lengthscale=None, grid_points_ratio=.25,
        learning_rate=0.1, iterations=2,
        num_batches=100, calculate_sd=True,
        use_gpu=False, verbose=True).run()
    assert_(mean.shape == sd.shape == R.flatten().shape)
    assert_(not np.isnan(mean).any())
    assert_(not np.isnan(sd).any())

