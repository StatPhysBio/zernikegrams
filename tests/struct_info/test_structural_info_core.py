import numpy as np

from src.structural_info.structural_info_core import  *

def test_get_chi_angle_basic():
    plane_norm_1 = np.array([0, 0, 1])
    plane_norm_2 = np.array([0, 1, 0])

    a2 = np.array([0, 0, 0])
    a3 = np.array([1, 0, 0])

    expected = -90
    chi = get_chi_angle(plane_norm_1, plane_norm_2, a2, a3)

    assert np.allclose(expected, chi)


def test_get_chi_angle_sign_flip1():
    plane_norm_1 = np.array([0, 0, 1])
    plane_norm_2 = np.array([0, 1, 0])

    a2 = np.array([0, 0, 0])
    a3 = np.array([-1, 0, 0]) # -1 instead of 1

    expected = 90
    chi = get_chi_angle(plane_norm_1, plane_norm_2, a2, a3)

    assert np.allclose(expected, chi)


def test_get_chi_angle_sign_flip2():
    plane_norm_1 = np.array([0, 0, 1])
    plane_norm_2 = np.array([0, 1, 0])

    # swap a2, a3 -> sign flips
    a3 = np.array([0, 0, 0])
    a2 = np.array([1, 0, 0])

    expected = 90
    chi = get_chi_angle(plane_norm_1, plane_norm_2, a2, a3)

    assert np.allclose(expected, chi)


def test_chi_angle_range_fuzzy():
    np.random.seed(0)
    for _ in range(100):
        plane_norm_1 = np.random.random((3,))
        plane_norm_2 = np.random.random((3,))
        a2 = np.random.random((3,))
        a3 = np.random.random((3,))

        chi = get_chi_angle(plane_norm_1, plane_norm_2, a2, a3)
        assert chi >= -180 and chi <= 180


def test_get_chi_angles_and_norm_vecs_basic():
    residue = {
        "N":   np.array([0, 0, 0]),
        "CA":  np.array([1, 0, 0]),
        "CB":  np.array([0, 1, 0]),
        "CG":  np.array([0, 0, 1]),
        "OD1": np.array([0, 1, 1])
    }
    angles, vecs = get_chi_angles_and_norm_vecs("ASP", residue, "X")

    expected_angles = np.array([54.7356, 125.2643, np.nan, np.nan])
    expected_vecs = np.array([
        [0, 0, -1],
        [t := -np.tan(np.pi / 6), t, t],
        [1, 0, 0], 
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan],
    ])

    a_mask = ~(np.isnan(expected_angles) | np.isnan(angles))
    v_mask = ~(np.isnan(expected_vecs) | np.isnan(vecs))

    assert np.allclose(expected_angles[a_mask], angles[a_mask], atol=1e-1) and \
           np.allclose(expected_vecs[v_mask], vecs[v_mask])
    

def test_get_chi_angles_and_norm_vecs_throws():
    residue = {
        "N":   np.array([0, 0, 0]),
        "CA":  np.array([1, 0, 0]),
        "CB":  np.array([0, 1, 0]),
        "CG":  np.array([0, 0, 1]),
        # "OD1": np.array([0, 1, 1]) <== missing atom
    }
    
    angles, vecs = get_chi_angles_and_norm_vecs("ASP", residue, "X")
    assert np.all(np.isnan(angles)) and np.all(np.isnan(vecs))
