import numpy as np


def is_all(variable):
    """Checks if the value of a variable is equal to 'all', 'All', or 'ALL'.

    The method returns True if the value of a variable is equal to 'all', 'All', or 'ALL'.

    Parameters
    ----------
    variable: Any
        Input variable to be compared with 'all', 'All', or 'ALL'.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/#the-any-type

    Returns
    -------
    Bool
        True if successful, False otherwise.

    Examples
    --------
    The method accepts any type. It returns True in case the value is 'all', 'All' or 'ALL'.

    >>> is_all('All')
    True

    >>> is_all([0, 1, 2])
    False

    """

    if isinstance(variable, str):
        return variable in ['all', 'All', 'ALL']

    return False


def is_iterable(variable):

    if isinstance(variable, (list, tuple, set, np.ndarray)):
        return True

    return False


def is_iterable_of_iterables(variable):

    if isinstance(variable, (list, tuple, set, np.ndarray)):
        return all([is_iterable(ii) for ii in variable])

    return False


def is_iterable_of_iterables_of_iterables(variable):

    if isinstance(variable, (list, tuple, set, np.ndarray)):
        return all([is_iterable_of_iterables(ii) for ii in variable])

    return False


def is_next(variable):

    if isinstance(variable, str):
        return variable in ['next', 'Next', 'NEXT']

    return False


def is_iterable_of_pairs(variable):

    output = False

    if isinstance(variable, np.ndarray):
        if len(variable.shape) == 2:
            if variable.shape[1] == 2:
                output = True
    elif isinstance(variable, (list, tuple, set)):
        for ii in variable:
            output = False
            if isinstance(ii, (list, tuple, set)):
                if len(ii) == 2:
                    output = True
            if not output:
                break

    return output


def is_iterable_of_integers(variable):

    output = False

    if isinstance(variable, np.ndarray):
        if len(variable.shape) == 1:
            if np.issubdtype(variable.dtype, np.integer):
                output = True
    elif isinstance(variable, (list, tuple, set)):
        if all(isinstance(ii, int) for ii in variable):
            output = True

    return output
