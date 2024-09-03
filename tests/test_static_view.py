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

def test_stackviewndarray_reshape():
    import numpy as np
    from stackview._static_view import StackViewNDArray

    labels = StackViewNDArray(np.asarray([[0, 1], [2, 0]]))
    new_labels = labels.reshape((1, 2, 2))

    print(new_labels)

    assert new_labels.shape == (1, 2, 2)

def test_stackviewndarray_transpose():
    import numpy as np
    from stackview._static_view import StackViewNDArray

    labels = StackViewNDArray(np.asarray([[0, 1], [2, 0]]))
    new_labels = labels.transpose()

    print(new_labels)

    assert new_labels.shape == (2, 2)

def test_stackviewndarray_expand_dims():
    import numpy as np
    from stackview._static_view import StackViewNDArray

    labels = StackViewNDArray(np.asarray([
        [0, 1],
        [2, 0]
    ]))

    labels = np.expand_dims(labels, axis=0)
    print(labels)
