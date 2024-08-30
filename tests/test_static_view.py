def test_static_view():
    import numpy as np
    from stackview._static_view import StackViewNDArray
    image = StackViewNDArray(np.asarray([
        [1,2],
        [0,1]
    ]))

    uniques = np.unique(image)
    assert 0 in uniques
    assert 1 in uniques
    assert 2 in uniques

    assert len(uniques) == 3
