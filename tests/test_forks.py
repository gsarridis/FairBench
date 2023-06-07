import fairbench as fb
import numpy as np


def environment():
    fb.distributed()
    yield "distributed"
    fb.serial()
    yield "serial"


def test_fork_generation():
    for _ in environment():
        fork = fb.Fork(a=1)
        assert fork.a == 1
        fork = fb.Fork(a=1, b=2, c=3)
        assert fork.a == 1
        assert fork.b == 2
        assert fork.c == 3


def test_categories():
    for _ in environment():
        branches = fb.Fork(fb.categories@["Man", "Woman", "Man", "Woman"]).branches()
        assert "Man" in branches
        assert "Woman" in branches

        branches = fb.Fork(gender=fb.categories@{"Man": [0, 1], "Woman": [0, 1]}).branches()
        assert "genderMan" in branches
        assert "genderWoman" in branches

        branches = fb.Fork({"Man": [0, 1], "Woman": [0, 1]}).branches()
        assert "Man" in branches
        assert "Woman" in branches

        branches = fb.Fork(attr=fb.Categories(range(4))@[0, 1, 2, 0, 1]).branches()
        assert "attr0" in branches
        assert "attr1" in branches
        assert "attr2" in branches
        assert "attr3" in branches

        branches = fb.Fork(attr=fb.Categories(range(4))([0, 1, 2, 0, 1])).branches()
        assert "attr0" in branches
        assert "attr1" in branches
        assert "attr2" in branches
        assert "attr3" in branches


def test_intersectional():
    branches = fb.Fork(gender=fb.binary(np.array([0, 1, 0, 1])),  # same notation as bellow
                       race=fb.binary@np.array([1, 1, 0, 0])).intersectional().branches()
    assert len(branches) == 8

    branches = fb.Fork(gender=fb.binary(np.array([0, 1, 0, 1])),  # same notation as bellow
                       race=fb.binary@np.array([0, 1, 0, 1])).intersectional().branches()
    assert len(branches) == 6

    branches = fb.Fork(sensitive=fb.binary@np.array([0, 1, 0, 1]) & fb.binary@np.array([0, 1, 0, 1])).branches()
    assert len(branches) == 4

    branches = fb.Fork(sensitive=fb.binary@[0, 1, 0, 1] | fb.categories@["Man", "Woman", "Man", "Woman"]).branches()
    assert len(branches) == 4


def test_fork_operations():
    for _ in environment():
        fork = fb.Fork(a=1)
        assert (fork == 1).a
        assert not (fork == 0).a
        assert not (fork != 1).a
        assert (fork != 0).a
        assert (fork >= 1).a
        assert (fork >= 0).a
        assert not (fork <= 0).a
        assert (fork <= 1).a
        assert not (fork < 0).a
        assert not (fork < 1).a
        assert not (fork > 1).a
        assert (fork+2).a == 3
        assert (2+fork).a == 3
        assert (fork-2).a == -1
        assert (2-fork).a == 1
        assert (fork/2).a == 0.5
        assert (2/fork).a == 2
        assert (fork//2).a == 0
        assert (2//fork).a == 2
        assert (fork*2).a == 2
        assert (2*fork).a == 2
        assert (abs(-fork) == 1).a


def test_fork_getattr():
    for _ in environment():
        fork = fb.Fork(a=np.array([1, 2, 3]), b=np.array([2, 3, 4]), c=np.array([3, 4, 5]))
        sums = fork.sum()
        assert sums.a == 6
        assert sums.b == 9
        assert sums.c == 12


def test_fork_of_dicts():
    #for _ in environment():  # TODO: the following don't work for distributed
    fork = fb.Fork(a={"x": 1, "y": 2}, b={"x": 2, "y": 4})
    fork["z"] = fork.x + fork.y
    del fork["x"]
    del fork["y"]
    assert len(fork.a) == 1
    assert len(fork.b) == 1
    assert fork.a["z"] == 3
    assert fork.b["z"] == 6


def test_fork_of_iterable():
    for _ in environment():
        fork = fb.Fork(a={"1": 1, "2": 2, "3": 3}, b={"1": 3, "2": 4, "3": 5})
        a = dict()
        b = dict()
        for i, element in enumerate(fork.items()):
            assert element[0] in ["1", "2", "3"]
            a[element[0]] = element[1].a
            b[element[0]] = element[1].b
        assert b["3"] == 5
        assert a["1"] == 1


def test_fork_of_forks():
    for _ in environment():
        fork = fb.Fork(a=fb.Fork(x=1, y=2), b=fb.Fork(x=2, y=4))
        assert isinstance(fork.a, fb.Fork)
        assert isinstance(fork.b, fb.Fork)
        assert isinstance(fork.x, fb.Fork)
        assert isinstance(fork.y, fb.Fork)
        assert fork.x.a == fork.a.x
        assert fork.x.b == fork.b.x
        assert fork.y.a == fork.a.y
        assert fork.y.b == fork.b.y


def test_fork_to_array():
    import fairbench as fb
    import numpy as np

    sensitive = fb.Fork(gender=fb.categories@np.array([1, 0, 0, 1]),
                        race=fb.categories@np.array([0, 1, 2, 3]),
                        age=fb.categories@np.array([3, 1, 2, 0]))

    report = fb.multireport(predictions=np.array([0, 0, 1, 1]), labels=np.array([0, 1, 1, 0]), sensitive=sensitive)
    print(report)
