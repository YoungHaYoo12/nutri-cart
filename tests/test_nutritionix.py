import unittest
from nutritionix import search_item, get_common_nutrients, get_branded_nutrients

class BasicsTestCase(unittest.TestCase):

  def test_get_branded_nutrients(self):
    # nix_item_id returns correct food
    resp1 = get_branded_nutrients("513fc9e73fe3ffd40300109f")
    self.assertTrue(resp1["food_name"] == "Big Mac")

    # contains specific nutrient categories
    self.assertTrue('serving_qty' in resp1)
    self.assertTrue('serving_unit' in resp1)
    self.assertTrue('nf_calories' in resp1)
    self.assertTrue('nf_total_fat' in resp1)
    self.assertTrue('nf_saturated_fat' in resp1)
    self.assertTrue('nf_cholesterol' in resp1)
    self.assertTrue('nf_sodium' in resp1)
    self.assertTrue('nf_total_carbohydrate' in resp1)
    self.assertTrue('nf_dietary_fiber' in resp1)
    self.assertTrue('nf_sugars' in resp1)
    self.assertTrue('nf_protein' in resp1)

  def test_get_common_nutrients(self):
    resp1 = get_common_nutrients('sushi')

    # food name is same as query
    self.assertTrue(resp1['food_name'] == 'sushi')

    # contains specific nutrient categories
    self.assertTrue('serving_qty' in resp1)
    self.assertTrue('serving_unit' in resp1)
    self.assertTrue('nf_calories' in resp1)
    self.assertTrue('nf_total_fat' in resp1)
    self.assertTrue('nf_saturated_fat' in resp1)
    self.assertTrue('nf_cholesterol' in resp1)
    self.assertTrue('nf_sodium' in resp1)
    self.assertTrue('nf_total_carbohydrate' in resp1)
    self.assertTrue('nf_dietary_fiber' in resp1)
    self.assertTrue('nf_sugars' in resp1)
    self.assertTrue('nf_protein' in resp1)
  
  def test_search_item(self):
    # does not return None
    self.assertFalse(search_item('orange') is None)

    # returns data dict of common and branded foods
    self.assertTrue('common' in search_item('apple'))
    self.assertTrue('branded' in search_item('apple'))