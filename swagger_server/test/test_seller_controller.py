from __future__ import absolute_import

from flask import json

from swagger_server.models.seller import seller  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSellerController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_seller_controller_create_car(self):
        """Test case for seller_controller_create_car

        Создать новую машину
        """
        body = seller()
        response = self.client.open(
            '/seller',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_seller_controller_delete_car(self):
        """Test case for seller_controller_delete_car

        Удалить машину
        """
        response = self.client.open(
            '/seller/{car_id}'.format(car_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_seller_controller_get_car(self):
        """Test case for seller_controller_get_car

        Получить машину по ID
        """
        response = self.client.open(
            '/seller/{car_id}'.format(car_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_seller_controller_get_cars(self):
        """Test case for seller_controller_get_cars

        Получить все машины
        """
        response = self.client.open(
            '/seller',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_seller_controller_update_car(self):
        """Test case for seller_controller_update_car

        Обновить машину
        """
        body = seller()
        response = self.client.open(
            '/seller/{car_id}'.format(car_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
