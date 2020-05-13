import unittest
from nutritionix import search_item, get_common_nutrients, get_branded_nutrients, nutrient_categories

class BasicsTestCase(unittest.TestCase):

  def test_get_branded_nutrients(self):
    # nix_item_id returns correct food
    resp1 = get_branded_nutrients("513fc9e73fe3ffd40300109f")
    self.assertTrue(resp1["food_name"] == "Big Mac")

    # contains specific nutrient categories
    for nutrient in nutrient_categories:
      self.assertTrue(nutrient in resp1)
    
    # Test error handling for invalid requests
    resp2 = get_branded_nutrients("asdfasdf123123")
    self.assertTrue(resp2 is None)

  def test_get_common_nutrients(self):
    resp1 = get_common_nutrients('sushi')

    # food name is same as query
    self.assertTrue(resp1['food_name'] == 'sushi')

    # contains specific nutrient categories
    for nutrient in nutrient_categories:
      self.assertTrue(nutrient in resp1)
  
    # Test error handling for invalid requests
    resp2 = get_branded_nutrients("app")
    self.assertTrue(resp2 is None)

  def test_search_item(self):
    # does not return None
    self.assertFalse(search_item('orange') is None)

    # returns data dict of common and branded foods
    self.assertTrue('common' in search_item('apple'))
    self.assertTrue('branded' in search_item('apple'))