import unittest
from flask import url_for
from app import create_app, db

class FlaskClientTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    self.client = self.app.test_client(use_cookies=True)
  
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()
  
  def test_core_index_page(self):
    # Form Validated
    response1 = self.client.post(url_for('core.index'),data= {
      'query': 'brownie'
    })
    self.assertTrue(response1.status_code == 302)

    # Form Not Validated
    response2 = self.client.post(url_for('core.index'),data= {
      'query':''
    })
    self.assertFalse(response2.status_code==302)
  
  def test_foods_list_page(self):
    # Common Filter
    response1 = self.client.get(url_for('foods.list',food_name='Brownie',filter='common'))
    self.assertTrue(response1.status_code == 200)
    data1 = response1.get_data(as_text=True)
    self.assertTrue('Search Results For Brownie' in data1)

    # Branded filter
    response2 = self.client.get(url_for('foods.list',food_name='Brownie',filter='branded'))
    self.assertTrue(response2.status_code == 200)
    data2 = response2.get_data(as_text=True)
    self.assertTrue('Search Results For Brownie' in data2)


