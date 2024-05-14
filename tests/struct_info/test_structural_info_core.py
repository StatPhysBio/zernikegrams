import numpy as np

from zernikegrams.structural_info.structural_info_core import *

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
    a3 = np.array([-1, 0, 0])  # -1 instead of 1

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
        "N": np.array([0, 0, 0]),
        "CA": np.array([1, 0, 0]),
        "CB": np.array([0, 1, 0]),
        "CG": np.array([0, 0, 1]),
        "OD1": np.array([0, 1, 1]),
    }
    angles, vecs = get_chi_angles_and_norm_vecs("ASP", residue, "X")

    expected_angles = np.array([54.7356, 125.2643, np.nan, np.nan])
    expected_vecs = np.array(
        [
            [0, 0, -1],
            [t := -np.tan(np.pi / 6), t, t],
            [1, 0, 0],
            [np.nan, np.nan, np.nan],
            [np.nan, np.nan, np.nan],
        ]
    )

    a_mask = ~(np.isnan(expected_angles) | np.isnan(angles))
    v_mask = ~(np.isnan(expected_vecs) | np.isnan(vecs))

    assert np.allclose(
        expected_angles[a_mask], angles[a_mask], atol=1e-1
    ) and np.allclose(expected_vecs[v_mask], vecs[v_mask])


def test_get_chi_angles_and_norm_vecs_throws():
    residue = {
        "N": np.array([0, 0, 0]),
        "CA": np.array([1, 0, 0]),
        "CB": np.array([0, 1, 0]),
        "CG": np.array([0, 0, 1]),
        # "OD1": np.array([0, 1, 1]) <== missing atom
    }

    angles, vecs = get_chi_angles_and_norm_vecs("ASP", residue, "X")
    assert np.all(np.isnan(angles)) and np.all(np.isnan(vecs))


def test_get_info_from_protein_basic():
    pdb, (
        atom_names,
        elements,
        res_ids,
        coords,
        sasas,
        charges,
        res_ids_per_residue,
        angles,
        norm_vecs,
        is_multi_model,
    ) = get_structural_info_from_protein(
        pdb_file="tests/data/pdbs/1hmd.pdb",
        calculate_SASA=False,
        calculate_angles=False,
        calculate_charge=False,
        calculate_DSSP=False,
    )

    assert (
        sasas.size == 0
        and charges.size == 0
        and angles.size == 0
        and norm_vecs.size == 0
    )


def test_get_info_from_protein_shapes_align():
    pdb, (
        atom_names,
        elements,
        res_ids,
        coords,
        sasas,
        charges,
        res_ids_per_residue,
        angles,
        norm_vecs,
        is_multi_model,
    ) = get_structural_info_from_protein(
        pdb_file="tests/data/pdbs/1hmd.pdb",
        calculate_SASA=True,
        calculate_angles=True,
        calculate_charge=True,
        calculate_DSSP=True,
    )

    assert (
        sasas.shape[0]
        == charges.shape[0]
        == atom_names.shape[0]
        == elements.shape[0]
        != 0
    )
    assert angles.shape[0] == norm_vecs.shape[0] != 0
