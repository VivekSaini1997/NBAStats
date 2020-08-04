import scraper

def func(years):
    return scraper.load_agg_jsons(years)

def test_out_of_range():
    '''
        Tests that years out of acceptable range don't cause the program to crash.
    '''
    assert func([1994, 1995]) == dict()